# Librerie DB
from mysql.connector import cursor, connect

# Variabili gloable che ci servirà quando faremo le query
mydb= None
cursor = None 

def TryConnect(host, user, password, database):
        # Prova a connetterti al DB, altrimenti dai errore
    try:
        global mydb, cursor
        mydb = connect(host=host, user=user, password=password, database=database)
        cursor = mydb.cursor()
    except Exception as e:
        print("Non è stato possibile connettersi al DB.")
        print(e)
        exit(-1)

def TryDisconnect():
    try:
        cursor.close()
        mydb.close()
    except Exception as e:
        ("Non è s tato possibile chiudere la connessione. ABORT.")
        print(e)
        exit(-1)

def GetAulette():
    query = "SELECT * FROM Auletta"
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows
