env_vars = {
  # Get From my.telegram.org
  "API_HASH": "7e250aaf4f19530d1debaebace4454bc",
  # Get From my.telegram.org
  "API_ID": "28585290",
  #Get For @BotFather
  "BOT_TOKEN": "7366951774:AAGw1QMwF8CXFAMnJxY5nh_G-sG9qeMBOEo",
  # Get For tembo.io
  "DATABASE_URL_PRIMARY": "postgresql://postgres:PqlMxuIq3i9sDvvr@quizzically-moving-weimaraner.data-1.use1.tembo.io:5432/postgres",
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
  "WELCOME_MESSAGE": (
        "<b>Welcome to the best manga pdf bot in Telegram!</b>\n"
        "\n"
        "How to use? Just type the name of some manga you want to keep up to date.\n"
        "\n"
        "For example:\n"
        "<code>One Piece</code>\n"
        "\n"
        "Check /help for more information.\n"
        "\n"
        "<i>Features:</i>\n"
        "• <u>Fast downloads</u>\n"
        "• <u>High-quality PDFs</u>\n"
        "• <u>Regular updates</u>\n"
        "\n"
        "Join our channel for <a href='{updates_url}'>latest updates</a>!\n"
        "\n"
        "<b>Enjoy reading your favorite manga!</b> 📚🎉"
    ),
  "UPDATES_URL": "https://t.me/crystalbotdevelopment",
  "REPO_URL": "https://github.com/",
  # Replace with your actual image URL
  "WELCOME_IMAGE_URL": ""
}

dbname = env_vars.get('DATABASE_URL_PRIMARY') or env_vars.get('DATABASE_URL') or 'sqlite:///test.db'

if dbname.startswith('postgres://'):
    dbname = dbname.replace('postgres://', 'postgresql://', 1)
    
