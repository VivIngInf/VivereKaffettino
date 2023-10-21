import os
from dotenv import load_dotenv, find_dotenv

token : str = ""
host : str = ""
username : str = ""
password : str = ""
database : str = ""

async def LoadConfigs() -> None:
    """LOAD_CONFIG: Carichiamo le stringhe dal file '.env' """
    
    load_dotenv(find_dotenv()) # Carichiamo il file di ambiente dove sono stati salvati i file di config

    global token, host, username, password, database

    token = os.environ.get("BOT_TOKEN")
    host = os.environ.get("DB_HOST")
    username = os.environ.get("DB_USERNAME")
    password = os.environ.get("DB_PASSWORD")
    database = os.environ.get("DB_DATABASE")

    return None

def GetToken() -> str : return token
def GetDBHost() -> str : return host
def GetDBUsername() -> str : return username
def GetDBPassword() -> str : return password
def GetDBDatabase() -> str : return database