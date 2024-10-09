env_vars = {
  # Get From my.telegram.org
  "API_HASH": "7e250aaf4f19530d1debaebace4454bc",
  # Get From my.telegram.org
  "API_ID": "28585290",
  #Get For @BotFather
  "BOT_TOKEN": "7366951774:7366951774:AAGcGkpPdmsyjgPSujyn5l7RMGguvYwGDJw",
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
  "THUMB": ""
}

dbname = env_vars.get('DATABASE_URL_PRIMARY') or env_vars.get('DATABASE_URL') or 'sqlite:///test.db'

if dbname.startswith('postgres://'):
    dbname = dbname.replace('postgres://', 'postgresql://', 1)
    
