# Librerie DB
from mysql.connector import cursor, connect

# Variabili gloable che ci servirà quando faremo le query
mydb= None
cursor = None 

def TryConnect(host, user, password, database):
        # Prova a connetterti al DB, altrimenti dai errore
    try:
        global mydb, cursor
        mydb = connect(host, user, password, database)
        cursor = mydb.cursor()
    except:
        print("Non è stato possibile connettersi al DB.")
        exit(-1)

def TryDisconnect():
    try:
        cursor.close()
        mydb.close()
    except:
        ("Non è s tato possibile chiudere la connessione. ABORT.")
        exit(-1)

def GetAulette():
    query = "SELECT * FROM Auletta"
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows
