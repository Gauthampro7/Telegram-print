# Telegram Print Bot

A Telegram bot that allows authorized users to send text messages, images, Word documents (.docx), or PDFs, and print them directly from a Windows device. The bot supports font size selection for text, orientation (portrait/landscape) for images/PDFs/Word/docs, and handles multi-page printing for long texts and PDFs.

## Features

- **Authorized Access**: Only specified user IDs can use the bot.
- **Text Printing**: Send text messages, select font size (11-20 pt), and orientation; supports multi-line text with word wrapping and pagination across multiple pages.
- **Image Printing**: Send images (JPEG/PNG), confirm printing, select orientation; scales images to fit the page.
- **PDF Printing**: Send PDFs, confirm, select orientation; renders each page as an image and prints.
- **Word Document Printing**: Send .docx files, confirm, select orientation; prints with original formatting.
- **Silent Printing**: No print dialogs; uses Windows printing APIs.
- **Logging**: Detailed logging for debugging.
- **Temporary File Cleanup**: Automatically deletes temporary files after printing, with retries for locked files.

## Prerequisites

- **Operating System**: Windows (due to dependency on `pywin32` for printing).
- **Python**: Version 3.8 or higher.
- **Telegram Bot Token**: Create a bot via [BotFather](https://t.me/botfather) on Telegram.
- **Authorized User IDs**: Your Telegram user IDs (find yours by messaging `@userinfobot`).
- **Printer**: A default printer set up on your Windows machine.
- **Dependencies**: Listed in `requirements.txt` (installed via pip).

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Gauthampro7/telegram-print.git
   cd telegram-print
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Create a `config.ini` file in the project root with the following content (replace placeholders with your values):
   ```ini
   [TELEGRAM]
   # Your Telegram bot token
   TOKEN = your_bot_token_here

   # List of authorized Telegram user IDs (as a Python list)
   AUTHORIZED_USERS = [your_user_id_1, your_user_id_2]
   ```
   - Example:
     ```ini
     [TELEGRAM]
     TOKEN = 7689905059:AAH1VRLiYeUJ0KOVDGMLgMvSMuwkFIz80HQ
     AUTHORIZED_USERS = [5382194762, 7932433627, 1819756593]
     ```

2. Ensure the script reads from `config.ini` (as per your code snippet).

## Running the Bot

Run the bot script:
```bash
python bot.py  # Replace with your script name if different
```

- The bot will start polling for Telegram updates.
- Logs will be printed to the console (configured via `logging`).

## Usage

1. **Start the Bot**: Message `/start` to your bot on Telegram. If authorized, you'll see a welcome message.

2. **Print Text**:
   - Send a text message.
   - Select font size from the inline keyboard.
   - Select orientation (portrait/landscape).
   - The text will print with the chosen settings, handling multi-lines and pagination.

3. **Print Images**:
   - Send an image (JPEG/PNG).
   - Confirm printing ("Yes/No").
   - Select orientation.
   - The image will print scaled to fit the page.

4. **Print PDFs**:
   - Send a PDF file.
   - Confirm printing.
   - Select orientation.
   - Each page renders as an image and prints.

5. **Print Word Documents (.docx)**:
   - Send a .docx file.
   - Confirm printing.
   - Select orientation.
   - Prints with original formatting.

- **Authorization**: Only users in `AUTHORIZED_USERS` can interact; others get a rejection message.
- **Orientation**: Defaults to portrait if not selected.
- **Temporary Files**: Stored in a `temp` directory (created automatically) and deleted after printing.

## Troubleshooting

- **Permission Errors**: Run the script as administrator if printer access is denied.
- **Printing Issues**: Ensure your default printer is set and functional. Check logs for errors (e.g., orientation failures).
- **Character Rendering**: Special characters (e.g., smart quotes) are preprocessed; if issues persist, try different fonts in the code.
- **Dependencies**: If `pywin32` fails, ensure it's installed correctly (may require Visual C++ redistributable).
- **Logs**: Check console or log files for detailed errors (logging level: INFO).

## Contributing

Contributions are welcome! Fork the repo, make changes, and submit a pull request. For major changes, open an issue first.

## License

This project is licensed under the MIT License.