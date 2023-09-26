# Librerie DB
import mysql.connector

# Variabili gloable che ci servirà quando faremo le query
mydb= None
cursor = None 

def TryConnect(host, user, password, database):
        # Prova a connetterti al DB, altrimenti dai errore
    try:
        mydb = mysql.connector.connect(host, user, password, database)
        cursor = mydb.cursor()
    except:
        print("Non è stato possibile connettersi al DB.")
        exit(-1)
        