import re
from os import environ

# Bot information
API_ID = int(environ.get('API_ID', ''))
API_HASH = environ.get('API_HASH', '')
BOT_TOKEN = environ.get('BOT_TOKEN', '')
PORT = int(environ.get('PORT', '80'))

# Bot Admins
ADMINS = [int(admin) for admin in environ.get('ADMINS', '').split()]

# Channels
INDEX_CHANNELS = [int(index_channel) for index_channel in environ.get('INDEX_CHANNELS', '').split() if index_channel]
AUTH_CHANNEL = [int(auth_channel) for auth_channel in environ.get('AUTH_CHANNEL', '').split() if auth_channel]
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', ''))
SUPPORT_GROUP = int(environ.get('SUPPORT_GROUP', ''))

# Other settings
OPENAI_API = environ.get('OPENAI_API', '')

# MongoDB information
DATABASE_URL = environ.get('DATABASE_URL', '')
DATABASE_NAME = environ.get('DATABASE_NAME', 'Cluster0')
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'Files')

# Links
SUPPORT_LINK = environ.get('SUPPORT_LINK', 'https://t.me/+h62PmWJ6mAIwMjQ1')
UPDATES_LINK = environ.get('UPDATES_LINK', 'https://t.me/TSNM_Offical')
FILMS_LINK = environ.get('FILMS_LINK', '')

# Bot settings
AUTO_FILTER = environ.get('AUTO_FILTER', 'True').lower() in ['true', 'yes', '1', 'enable', 'y']
IMDB = environ.get('IMDB', 'False').lower() in ['true', 'yes', '1', 'enable', 'y']
SPELL_CHECK = environ.get('SPELL_CHECK', 'True').lower() in ['true', 'yes', '1', 'enable', 'y']
SHORTLINK = environ.get('SHORTLINK', 'False').lower() in ['true', 'yes', '1', 'enable', 'y']
DELETE_TIME = int(environ.get('DELETE_TIME', '3600'))
AUTO_DELETE = environ.get('AUTO_DELETE', 'False').lower() in ['true', 'yes', '1', 'enable', 'y']
WELCOME = environ.get('WELCOME', 'False').lower() in ['true', 'yes', '1', 'enable', 'y']
PROTECT_CONTENT = environ.get('PROTECT_CONTENT', 'False').lower() in ['true', 'yes', '1', 'enable', 'y']
LONG_IMDB_DESCRIPTION = environ.get('LONG_IMDB_DESCRIPTION', 'False').lower() in ['true', 'yes', '1', 'enable', 'y']
LINK_MODE = environ.get('LINK_MODE', 'True').lower() in ['true', 'yes', '1', 'enable', 'y']
CACHE_TIME = int(environ.get('CACHE_TIME', '300'))
MAX_BTN = int(environ.get('MAX_BTN', '10'))
LANGUAGES = [language.lower() for language in environ.get('LANGUAGES', 'english hindi telugu tamil kannada malayalam').split()]

# Stream features
BIN_CHANNEL = int(environ.get('BIN_CHANNEL', ''))
URL = environ.get('URL', '')
if URL:
    if URL.startswith(('https://', 'http://')):
        if not URL.endswith("/"):
            URL += '/'
    elif is_valid_ip(URL):
        URL = f'http://{URL}/'
    else:
        print('Error - URL is not valid, exiting now')
        exit()
else:
    print('Error - URL is missing, exiting now')
    exit()

# Add your password variable
PASSWORD = environ.get('PASSWORD', '123')
