import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
import win32print
import win32ui
import win32con
from PIL import Image
import os
import logging
import time
import fitz  # PyMuPDF
from docx import Document
import win32com.client
import psutil
import pywintypes
import traceback
import configparser

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

TOKEN = config.get('Telegram', 'TOKEN')
AUTHORIZED_USERS = list(map(int, config.get('Telegram', 'AUTHORIZED_USERS').split(',')))

user_messages = {}
user_files = {}
user_orientations = {}
user_font_sizes = {}

def check_authorized_user(update):
    user_id = update.effective_user.id
    logger.info("Checking authorization for user %s", user_id)
    return user_id in AUTHORIZED_USERS

async def start(update, context):
    logger.info("Received /start command from user %s", update.effective_user.id)
    if not check_authorized_user(update):
        await update.message.reply_text("Sorry, you are not authorized to use this bot.")
        return
    await update.message.reply_text("Welcome! Send me a text, image, Word file (.docx), or PDF, and I'll print it.")

def create_font_size_keyboard():
    keyboard = [
        [InlineKeyboardButton(f"{i} pt", callback_data=str(i)) for i in range(11, 14)],
        [InlineKeyboardButton(f"{i} pt", callback_data=str(i)) for i in range(14, 17)],
        [InlineKeyboardButton(f"{i} pt", callback_data=str(i)) for i in range(17, 21)],
    ]
    return InlineKeyboardMarkup(keyboard)

def create_confirmation_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("Yes", callback_data="yes"), InlineKeyboardButton("No", callback_data="no")]])

def create_orientation_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("Portrait", callback_data="portrait"), InlineKeyboardButton("Landscape", callback_data="landscape")]])

import win32gui  # Add this import if not already present

def print_text(text, font_size):
    try:
        # Preprocess text to replace smart quotes and apostrophes with straight ones
        text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("–", "-").replace("…", "...")

        printer_name = win32print.GetDefaultPrinter()
        hprinter = win32print.OpenPrinter(printer_name)
        # Get default devmode
        devmode = win32print.GetPrinter(hprinter, 2)["pDevMode"]
        # Get orientation
        user_id = next((k for k, v in user_orientations.items() if v is not None), None)
        orientation = user_orientations.get(user_id, "portrait")
        # Set orientation in devmode
        devmode.Orientation = win32con.DMORIENT_LANDSCAPE if orientation == "landscape" else win32con.DMORIENT_PORTRAIT
        # Create raw DC with custom devmode
        hdc_raw = win32gui.CreateDC("WINSPOOL", printer_name, devmode)
        # Create PyCDC from handle
        hdc = win32ui.CreateDCFromHandle(hdc_raw)
        hdc.StartDoc('Telegram Print Job')

        # Set up font with proper DPI scaling and Unicode support
        font = win32ui.CreateFont({
            "name": "Arial",  # Switched to Arial for better compatibility and character rendering
            "height": int(font_size * -1 * (hdc.GetDeviceCaps(win32con.LOGPIXELSY) / 72)),  # DPI-aware height
            "weight": win32con.FW_NORMAL,
            "charset": win32con.DEFAULT_CHARSET,  # Unicode support
        })
        hdc.SelectObject(font)

        # Define margins and printable area
        margin_left = 100
        margin_top = 100
        margin_right = 100
        margin_bottom = 100
        printable_width = hdc.GetDeviceCaps(win32con.HORZRES) - margin_left - margin_right
        page_height = hdc.GetDeviceCaps(win32con.VERTRES) - margin_top - margin_bottom

        # Formatting flags for DrawText
        format_flags = win32con.DT_LEFT | win32con.DT_WORDBREAK | win32con.DT_EXTERNALLEADING | win32con.DT_NOPREFIX

        pos = 0  # Current position in the text
        while pos < len(text):
            hdc.StartPage()
            rect = [margin_left, margin_top, margin_left + printable_width, margin_top + page_height]

            # Binary search to find the maximum text length that fits the page
            low = pos
            high = len(text)
            fit_end = pos
            while low <= high:
                mid = (low + high) // 2
                sub_text = text[pos:mid]
                calc_rect = list(rect)
                hdc.DrawText(sub_text, calc_rect, format_flags | win32con.DT_CALCRECT)
                computed_height = calc_rect[3] - calc_rect[1]
                if computed_height <= page_height:
                    fit_end = mid
                    low = mid + 1
                else:
                    high = mid - 1

            if fit_end == pos:
                # No more text fits (edge case for very long unbreakable lines)
                logger.warning("Unable to fit remaining text starting at position %d", pos)
                break

            # Adjust fit_end back to the last word boundary to avoid splitting words
            if fit_end < len(text) and text[fit_end] not in (' ', '\n'):
                last_space = text.rfind(' ', pos, fit_end)
                if last_space != -1:
                    fit_end = last_space + 1  # Move to after the space

            # Draw the fitting portion of the text
            sub_text = text[pos:fit_end]
            hdc.DrawText(sub_text, rect, format_flags)

            pos = fit_end
            hdc.EndPage()

        hdc.EndDoc()
        hdc.DeleteDC()
        logger.info("Text printed successfully with font size %s pt", font_size)
    except Exception as e:
        logger.error("Printing error: %s", str(e))
        traceback.print_exc()  # Log full traceback for debugging
    finally:
        if 'hprinter' in locals():
            win32print.ClosePrinter(hprinter)

def print_image(image_path):
    """Render and print an image silently without dialogs."""
    try:
        from PIL import ImageWin
        logger.info("Printing image silently: %s", image_path)
        printer_name = win32print.GetDefaultPrinter()
        hprinter = win32print.OpenPrinter(printer_name)
        # Get default devmode
        devmode = win32print.GetPrinter(hprinter, 2)["pDevMode"]
        # Get orientation
        user_id = next((k for k, v in user_orientations.items() if v is not None), None)
        orientation = user_orientations.get(user_id, "portrait")
        # Set orientation in devmode
        devmode.Orientation = win32con.DMORIENT_LANDSCAPE if orientation == "landscape" else win32con.DMORIENT_PORTRAIT
        # Create raw DC with custom devmode
        hdc_raw = win32gui.CreateDC("WINSPOOL", printer_name, devmode)
        # Create PyCDC from handle
        pdc = win32ui.CreateDCFromHandle(hdc_raw)

        img = Image.open(image_path)
        hdc = pdc.CreateCompatibleDC()
        pdc.StartDoc(image_path)
        pdc.StartPage()

        printable_area = pdc.GetDeviceCaps(win32con.HORZRES), pdc.GetDeviceCaps(win32con.VERTRES)
        img_width, img_height = img.size

        scale = min(printable_area[0] / img_width, printable_area[1] / img_height)
        scaled_width = int(img_width * scale)
        scaled_height = int(img_height * scale)

        dib = ImageWin.Dib(img)
        dib.draw(pdc.GetHandleOutput(), (0, 0, scaled_width, scaled_height))

        pdc.EndPage()
        pdc.EndDoc()
        pdc.DeleteDC()

        logger.info("✅ Image printed successfully (no dialogs).")
    except Exception as e:
        logger.error("Silent image print failed: %s", str(e))
    finally:
        if 'hprinter' in locals():
            win32print.ClosePrinter(hprinter)

def print_docx(docx_path):
    try:
        word = win32com.client.Dispatch("Word.Application")
        doc = word.Documents.Open(os.path.abspath(docx_path))
        user_id = next((k for k, v in user_orientations.items() if v is not None), None)
        orientation = user_orientations.get(user_id, "portrait")
        doc.PageSetup.Orientation = 1 if orientation == "landscape" else 0
        doc.PrintOut()
        time.sleep(2)
        doc.Close(False)
        word.Quit()
        for proc in psutil.process_iter():
            if proc.name() == "WINWORD.EXE":
                proc.kill()
    except Exception as e:
        logger.error("DOCX print error: %s", str(e))

def print_pdf(pdf_path):
    """Render each PDF page as an image and send to system print handler."""
    try:
        logger.info(">>> Rendering and printing PDF via image path: %s", pdf_path)
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x scaling for quality
            img_path = f"temp_page_{page_num}.png"
            pix.save(img_path)
            print_image(img_path)
            os.remove(img_path)
        doc.close()
        logger.info("✅ All PDF pages rendered and printed as images.")
    except Exception as e:
        logger.error("❌ PDF rendering and printing failed: %s", str(e))




async def handle_text(update, context):
    """Handle incoming text messages."""
    logger.info("Received text message from user %s: %s", update.effective_user.id, update.message.text)
    if not check_authorized_user(update):
        return
    user_id = update.effective_user.id
    text = update.message.text
    user_messages[user_id] = text
    keyboard = create_font_size_keyboard()
    await update.message.reply_text("Please select a font size:", reply_markup=keyboard)

async def handle_document(update, context):
    """Handle incoming document messages (Word, PDF)."""
    logger.info("Received document from user %s", update.effective_user.id)
    if not check_authorized_user(update):
        return
    user_id = update.effective_user.id
    document = update.message.document
    file = await document.get_file()
    temp_dir = os.path.join(os.path.dirname(__file__), "temp")
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, document.file_name)
    try:
        await file.download_to_drive(file_path)
        user_files[user_id] = file_path
        file_extension = document.file_name.split('.')[-1].lower()
        message = f"Received {document.file_name}. Confirm printing? (This will print the text content for PDFs, original formatting for .docx)"
        keyboard = create_confirmation_keyboard()
        await update.message.reply_text(message, reply_markup=keyboard)
    except PermissionError as e:
        logger.error("Permission denied downloading file: %s", str(e))
        await update.message.reply_text("Error: Unable to save the file due to permission issues. Please try again or check folder permissions.")
    except Exception as e:
        logger.error("Error downloading file: %s", str(e))
        await update.message.reply_text("Error: Failed to download the file. Please try again.")

async def handle_image(update, context):
    """Handle incoming image messages."""
    logger.info("Received image from user %s", update.effective_user.id)
    if not check_authorized_user(update):
        return
    user_id = update.effective_user.id
    photo = update.message.photo[-1]
    file = await photo.get_file()
    temp_dir = os.path.join(os.path.dirname(__file__), "temp")
    os.makedirs(temp_dir, exist_ok=True)
    image_path = os.path.join(temp_dir, f"image_{user_id}.jpg")
    try:
        await file.download_to_drive(image_path)
        user_files[user_id] = image_path
        keyboard = create_confirmation_keyboard()
        await update.message.reply_text("Received image. Confirm printing?", reply_markup=keyboard)
    except PermissionError as e:
        logger.error("Permission denied downloading image: %s", str(e))
        await update.message.reply_text("Error: Unable to save the image due to permission issues. Please try again or check folder permissions.")
    except Exception as e:
        logger.error("Error downloading image: %s", str(e))
        await update.message.reply_text("Error: Failed to download the image. Please try again.")

async def font_size_callback(update, context):
    """Handle font size selection."""
    query = update.callback_query
    logger.info("Received font size selection from user %s: %s", query.from_user.id, query.data)
    user_id = query.from_user.id
    if user_id not in AUTHORIZED_USERS:
        await query.message.reply_text("Sorry, you are not authorized to use this bot.")
        return
    # Store font size
    user_font_sizes[user_id] = int(query.data)
    # Clear any lingering orientation from previous jobs
    if user_id in user_orientations:
        del user_orientations[user_id]
    # Prompt for orientation
    keyboard = create_orientation_keyboard()
    await query.message.edit_text("Please select orientation:", reply_markup=keyboard)

async def confirmation_callback(update, context):
    """Handle confirmation for printing files."""
    query = update.callback_query
    logger.info("Received confirmation from user %s: %s", query.from_user.id, query.data)
    user_id = query.from_user.id
    if user_id not in AUTHORIZED_USERS:
        await query.message.reply_text("Sorry, you are not authorized to use this bot.")
        return
    if user_id in user_files:
        file_path = user_files[user_id]
        if query.data == "yes":
            keyboard = create_orientation_keyboard()
            user_orientations[user_id] = None  # Reset orientation
            await query.message.edit_text("Please select orientation:", reply_markup=keyboard)
        else:  # "no"
            await query.message.edit_text("Printing canceled.")
            # Retry file deletion if locked
            max_attempts = 10
            attempt = 0
            while attempt < max_attempts:
                try:
                    os.remove(file_path)
                    logger.info("Temporary file %s deleted successfully", file_path)
                    break
                except OSError as e:
                    if e.winerror == 32:  # File in use
                        attempt += 1
                        time.sleep(2)  # Increased delay to 2 seconds
                        logger.warning("Attempt %d: File %s is still in use, retrying...", attempt, file_path)
                    else:
                        logger.error("Error deleting file %s: %s", file_path, str(e))
                        break
            if attempt == max_attempts:
                logger.error("Failed to delete file %s after %d attempts", file_path, max_attempts)
            del user_files[user_id]
            del user_orientations[user_id]

async def orientation_callback(update, context):
    """Handle orientation selection for printing."""
    query = update.callback_query
    logger.info("Received orientation selection from user %s: %s", query.from_user.id, query.data)
    user_id = query.from_user.id
    if user_id not in AUTHORIZED_USERS:
        await query.message.reply_text("Sorry, you are not authorized to use this bot.")
        return
    orientation = query.data
    user_orientations[user_id] = orientation
    if user_id in user_files:
        file_path = user_files[user_id]
        if file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            print_image(file_path)
            await query.message.edit_text("Image printed successfully with orientation %s!" % query.data.capitalize())
        elif file_path.lower().endswith('.docx'):
            print_docx(file_path)
            await query.message.edit_text("Word document printed successfully with original formatting and orientation %s!" % query.data.capitalize())
        elif file_path.lower().endswith('.pdf'):
            print_pdf(file_path)
            await query.message.edit_text("PDF printed successfully with orientation %s!" % query.data.capitalize())
        else:
            await query.message.edit_text("Unsupported file format.")
        # Retry file deletion if locked
        max_attempts = 10
        attempt = 0
        while attempt < max_attempts:
            try:
                os.remove(file_path)
                logger.info("Temporary file %s deleted successfully", file_path)
                break
            except OSError as e:
                if e.winerror == 32:  # File in use
                    attempt += 1
                    time.sleep(2)  # Increased delay to 2 seconds
                    logger.warning("Attempt %d: File %s is still in use, retrying...", attempt, file_path)
                else:
                    logger.error("Error deleting file %s: %s", file_path, str(e))
                    break
        if attempt == max_attempts:
            logger.error("Failed to delete file %s after %d attempts", file_path, max_attempts)
        del user_files[user_id]
        del user_orientations[user_id]
    elif user_id in user_messages:
        text = user_messages[user_id]
        font_size = user_font_sizes[user_id]
        print_text(text, font_size)
        await query.message.edit_text(f"Text printed successfully with font size {font_size} pt and orientation {orientation.capitalize()}!")
        del user_messages[user_id]
        del user_font_sizes[user_id]
        del user_orientations[user_id]
    await query.message.delete()

async def error_handler(update, context):
    """Handle errors."""
    logger.error("Update %s caused error %s", update, context.error)
    if update and update.message:
        await update.message.reply_text("An error occurred. Please try again.")

def main():
    """Run the bot."""
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    application.add_handler(CallbackQueryHandler(font_size_callback, pattern="^[0-9]+$"))
    application.add_handler(CallbackQueryHandler(confirmation_callback, pattern="^(yes|no)$"))
    application.add_handler(CallbackQueryHandler(orientation_callback, pattern="^(portrait|landscape)$"))
    application.add_error_handler(error_handler)

    application.run_polling()

if __name__ == "__main__":
    logger.info("Bot starting...")
    main()