env_vars = {
  # Get From my.telegram.org
  "API_HASH": "7e250aaf4f19530d1debaebace4454bc",
  # Get From my.telegram.org
  "API_ID": "28585290",
  #Get For @BotFather
  "BOT_TOKEN": "7366951774:AAGw1QMwF8CXFAMnJxY5nh_G-sG9qeMBOEo",
  # Get For tembo.io
  "DATABASE_URL_PRIMARY": "postgresql://postgres:X0v6RMf715n1yNLO@currently-joyous-scup.data-1.use1.tembo.io:5432/postgres",
  # Logs Channel Username Without @
  "CACHE_CHANNEL": "crystalxmanga_logs",
  # Force Subs Channel username without @
  "CHANNEL": "crystalbotdevelopment",
  # {chap_num}: Chapter Number
  # {chap_name} : Manga Name
  # Ex : Chapter {chap_num} {chap_name} @crystalxmanga_bot
  "FNAME": "Chapter {chap_num} | {chap_name}  @crystalxmanga_bot",
  # Put Thumb Link 
  "THUMB": "",
  # Welcome Command Message
  "START_MESSAGE": """
🎉 *Welcome to CrystalX Manga Bot!*

This bot helps you find and download manga chapters easily.

📚 *How to use:*
Just type the name of a manga you want to read. For example:
`One Piece`

✨ *Main features:*
• Search and download manga chapters
• Get chapters in PDF or CBZ format
• Subscribe to manga for updates

ℹ️ Use /help to see all available commands and more detailed instructions.

📢 Join @crystalbotdevelopment for bot updates.

Happy reading! 📖
""",
  "UPDATES_URL": "https://t.me/crystalbotdevelopment",
  "REPO_URL": "https://github.com/",
  # Replace with your actual image URL
  "WELCOME_IMAGE_URL": "",
  "HELP_MESSAGE": """
📚 *CrystalX Manga Bot Help*

Here are the main commands and features:

🔍 *Search:* Simply type a manga name
Example: `One Piece`

📥 *Download:* Click on a chapter to download

📋 *Commands:*
/start - Start the bot
/help - Show this help message
/subs - List your subscriptions
/cancel - Cancel a subscription

⚙️ *Options:*
/options - Set your preferred output format (PDF/CBZ)

💡 *Tips:*
• Use precise manga names for better results
• Subscribe to manga to get notified of new chapters

For more help or to report issues, contact @YourSupportUsername
""",
}

dbname = env_vars.get('DATABASE_URL_PRIMARY') or env_vars.get('DATABASE_URL') or 'sqlite:///test.db'

if dbname.startswith('postgres://'):
    dbname = dbname.replace('postgres://', 'postgresql://', 1)
    
