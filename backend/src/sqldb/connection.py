import mysql.connector

def connect():
    mydb = mysql.connector.connect(
    host="localhost",
    user="nez",
    password="1234",
    database="atlas"
    )

    print(mydb)
    return mydb