Telegram Print Bot
A Telegram bot that allows authorized users to send text, images, PDFs, or Word documents (.docx) and print them directly on a Windows system with customizable font size and orientation.
Features

Supported Inputs:
Text: Send plain text messages, select a font size (11–20 pt), and choose portrait or landscape orientation.
Images: Send images (.jpg, .jpeg, .png) for direct printing with orientation selection.
PDFs: Send PDF files, which are rendered as images and printed page by page with orientation selection.
Word Documents: Send .docx files for printing with original formatting and orientation selection.


User Authorization: Restricts access to a predefined list of Telegram user IDs for security.
Interactive Interface: Prompts users for font size (for text) and orientation (for all inputs) via Telegram inline keyboards.
Unicode Support: Handles special characters (e.g., üñíçødé, straight quotes) for text printing.
Multi-page Printing: Supports multi-page text and PDF printing, with automatic pagination and word wrapping.
Error Handling: Logs errors and ensures cleanup of temporary files and resources.

Prerequisites

Operating System: Windows (due to pywin32 dependency for printing).
Python: Version 3.8 or higher.
Printer: A default printer configured on the Windows system.
Telegram Bot Token: Obtain from BotFather on Telegram.
Authorized User IDs: Telegram user IDs of allowed users (obtain by messaging @userinfobot).

Setup

Clone the Repository:
git clone https://github.com/Gauthampro7/telegram-print.git
cd telegram-print


Install Dependencies:Create a virtual environment (optional but recommended) and install the required packages:
python -m venv venv
.\venv\Scripts\activate  # On Windows
pip install -r requirements.txt

The requirements.txt includes:
python-telegram-bot==21.4
pywin32==306
Pillow==10.4.0
PyMuPDF==1.24.10
python-docx==1.1.2
psutil==6.0.0


Configure the Bot:

Create a config.ini file in the project root with the following template:[TELEGRAM]
TOKEN = your_bot_token_here
AUTHORIZED_USERS = [your_user_id_1, your_user_id_2]


Replace your_bot_token_here with your Telegram bot token.
Replace [your_user_id_1, your_user_id_2] with a list of authorized Telegram user IDs (e.g., [123456789, 987654321]).


Example:[TELEGRAM]
TOKEN = 1234567890:AAFxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AUTHORIZED_USERS = [5382194762, 7932433627]




Run the Bot:
python bot.py

The bot will start polling for Telegram messages and print supported inputs from authorized users.


Usage

Start the Bot:

Send /start to the bot in Telegram to verify it’s running. Only authorized users (listed in config.ini) can interact with the bot.


Send Content:

Text: Send a text message. The bot will prompt for a font size (11–20 pt) and orientation (portrait or landscape), then print the text with word wrapping and multi-page support if needed.
Images: Send an image (.jpg, .jpeg, .png). The bot will prompt for confirmation and orientation, then print the image scaled to fit the page.
PDFs: Send a PDF file. The bot will prompt for confirmation and orientation, render each page as an image, and print.
Word Documents: Send a .docx file. The bot will prompt for confirmation and orientation, then print using Microsoft Word’s formatting.


Follow Prompts:

For text, select a font size and orientation via inline keyboards.
For files, confirm printing and select orientation.
The bot will notify you once printing is complete.



Security Notes

Bot Token: The Telegram bot token in config.ini is sensitive. Do not commit config.ini to a public Git repository. Add it to .gitignore:config.ini


Consider providing a config.ini.example with placeholder values for others to copy and configure.


Exposed Token: If you previously committed the token in your script, assume it’s compromised. Revoke it via BotFather and generate a new one. To remove it from Git history:
Install git-filter-repo:pip install git-filter-repo


Clone a fresh copy: git clone --mirror <your-repo-url>.
Rewrite history: git filter-repo --replace-text <(echo 'your_old_token==>REDACTED').
Force-push: git push origin --force --all.
Contact your Git host (e.g., GitHub support) to purge cached commits.


Authorized Users: Only include trusted user IDs in AUTHORIZED_USERS to prevent unauthorized access.

Troubleshooting

Printing Issues:
Text Rendering: If special characters (e.g., It's, network's) look incorrect, ensure your printer supports the Arial font. Test with a virtual PDF printer (e.g., Microsoft Print to PDF) to isolate driver issues.
Single Page Printing: If text is cut off, verify the print_text function uses multi-page logic (already implemented in the latest version).
Orientation Errors: Ensure you select the correct orientation (portrait/landscape) when prompted. The bot resets orientation for each job to avoid conflicts.


Configuration Errors:
If you see Error reading configuration, check config.ini for correct syntax (e.g., valid list for AUTHORIZED_USERS).
Example error: AUTHORIZED_USERS = 123, 456 is invalid; use [123, 456].


Logs: Check logs (printed to console or a file if configured) for errors. The script logs detailed errors with tracebacks.
Dependencies: If a module is missing, run pip install -r requirements.txt again or verify your Python version (3.8+).

Contributing
Contributions are welcome! Submit pull requests to improve features, fix bugs, or enhance documentation. Ensure changes are tested on a Windows system with a configured printer.
License
This project is licensed under the MIT License.