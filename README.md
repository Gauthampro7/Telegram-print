Telegram Print Bot
A Telegram bot that enables authorized users to send text, images, PDFs, or Word documents (.docx) for direct printing on a Windows system, with options to select font size and page orientation.
Features

Supported Inputs:
Text: Send plain text messages, choose a font size (11–20 pt), and select portrait or landscape orientation. Supports multi-line text with word wrapping and automatic pagination.
Images: Send images (.jpg, .jpeg, .png) for printing, scaled to fit the page, with orientation selection.
PDFs: Send PDF files, rendered as images and printed page by page with orientation selection.
Word Documents: Send .docx files, printed with original formatting and orientation selection.


User Authorization: Restricts access to a predefined list of Telegram user IDs for security.
Interactive Interface: Uses inline keyboards to prompt for font size (text only) and orientation (all inputs).
Unicode Support: Handles special characters (e.g., It's, üñíçødé) by converting smart quotes to straight quotes and using the Arial font.
Error Handling: Logs errors, cleans up temporary files, and ensures proper resource management.
Windows Compatibility: Leverages pywin32 for direct printer access on Windows systems.

Prerequisites

Operating System: Windows (required for pywin32 printing functionality).
Python: Version 3.8 or higher.
Printer: A default printer configured in Windows.
Telegram Bot Token: Obtain from BotFather on Telegram.
Authorized User IDs: Telegram user IDs of allowed users (find yours by messaging @userinfobot).

Installation

Clone the Repository:
git clone https://github.com/Gauthampro7/telegram-print.git
cd telegram-print


Set Up a Virtual Environment (recommended):
python -m venv venv
.\venv\Scripts\activate  # On Windows


Install Dependencies:
pip install -r requirements.txt

The requirements.txt contains:
python-telegram-bot==21.4
pywin32==306
Pillow==10.4.0
PyMuPDF==1.24.10
python-docx==1.1.2
psutil==6.0.0


Configure the Bot:

Copy config.ini.example to config.ini:copy config.ini.example config.ini


Edit config.ini to include your Telegram bot token and authorized user IDs:[TELEGRAM]
TOKEN = your_bot_token_here
AUTHORIZED_USERS = [your_user_id_1, your_user_id_2]


Example:[TELEGRAM]
TOKEN = 1234567890:AAFxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AUTHORIZED_USERS = [5382194762, 7932433627]


Note: Do not commit config.ini to Git (it’s excluded via .gitignore).




Run the Bot:
python bot.py



Usage

Start the Bot:

Send /start to the bot on Telegram. Only users listed in AUTHORIZED_USERS can interact with it.


Send Content:

Text: Send a text message (e.g., Hello, world!\nThis is a test.). The bot will prompt for a font size (11–20 pt) and orientation (portrait or landscape), then print with word wrapping and multi-page support if needed.
Images: Send an image (.jpg, .jpeg, .png). The bot will prompt for confirmation and orientation, then print the image scaled to fit.
PDFs: Send a PDF file. The bot will prompt for confirmation and orientation, render each page as an image, and print.
Word Documents: Send a .docx file. The bot will prompt for confirmation and orientation, then print using Microsoft Word’s formatting.


Follow Prompts:

Select options via inline keyboards (font size for text, orientation for all inputs).
Receive confirmation once printing is complete.



Security

Bot Token: The Telegram bot token in config.ini is sensitive. Never commit config.ini to a public repository. It’s excluded by .gitignore:config.ini


Previously Exposed Token: If your token was previously committed (e.g., hardcoded in the script), it’s likely compromised. To mitigate:
Revoke the old token via BotFather and generate a new one.
Update config.ini with the new token.
Remove the token from Git history:pip install git-filter-repo
git clone --mirror https://github.com/Gauthampro7/telegram-print.git
cd telegram-print.git
git filter-repo --replace-text <(echo 'your_old_token==>REDACTED')
git push origin --force --all


Replace your_old_token with the exposed token (e.g., 7689905059:AAH1VRLiYeUJ0KOVDGMLgMvSMuwkFIz80HQ).
Contact GitHub support to purge cached commits.




Authorized Users: Only include trusted user IDs in AUTHORIZED_USERS to prevent unauthorized access.

Troubleshooting

Text Rendering Issues:
If characters like It's or network's appear incorrect, the bot converts smart quotes (’) to straight quotes (') using Arial font. Test with a virtual PDF printer (e.g., Microsoft Print to PDF) to isolate printer driver issues.
For unsupported characters (e.g., emojis), consider adding preprocessing to remove them (edit print_text function).


Printing Errors:
Single Page: If text is cut off, verify the print_text function uses the latest multi-page logic.
Orientation: Confirm orientation selection (portrait/landscape) via inline keyboards. The bot resets orientation per job.
Permission Errors: Run the script as administrator if you see Access is denied errors for printer access.


Configuration Errors:
If you see Error reading configuration, ensure config.ini exists and has correct syntax:
TOKEN is a valid string.
AUTHORIZED_USERS is a Python list (e.g., [123456789, 987654321]).


Example error: AUTHORIZED_USERS = 123, 456 is invalid; use [123, 456].


Logs: Check console or log file for errors (includes tracebacks for debugging).
Dependencies: If modules are missing, re-run pip install -r requirements.txt or verify Python version (3.8+).

Contributing
Contributions are welcome! To contribute:

Fork the repository.
Create a feature branch (git checkout -b feature/YourFeature).
Commit changes (git commit -m 'Add YourFeature').
Push to the branch (git push origin feature/YourFeature).
Open a pull request.

Please test changes on a Windows system with a configured printer.
License
This project is licensed under the MIT License. See the LICENSE file for details.