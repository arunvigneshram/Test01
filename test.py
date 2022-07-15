import mysql.connector
import requests
from SQL_Config import db_config

# Setup of the mysql connector to the database
mydb = mysql.connector.connect(
    host=db_config["host"],
    user=db_config["user"],
    password=db_config["password"],
    database="wallbox_status",
    autocommit=True
)

# Setup cursor
mycursor = mydb.cursor()

mycursor.execute(
    "SELECT charger_current_state FROM Chargers_Data WHERE charger_id = 1")
myresult = mycursor.fetchall()
print(myresult)
# print(myresult[0][0])

charger_ip = "127.0.0.1"
port = "5000"
evse_state = requests.get(f"http://{charger_ip}:{port}/evse/state").json()
print(evse_state)

mycursor.execute("SELECT * FROM Chargers_Data")
myresult = mycursor.fetchall()
print(myresult)

sql = f""" INSERT INTO Chargers_Data (charger_id, rfid, rfid_last_seen, phases, iec61851_state, charger_state, error_state, rfid_check, phase_check, charger_current_state)
VALUES (
    1, "00:34:34:53:53:56", 34, "True | True | True",
     0, 0, 0, 1, 1, "CHARGING"
)
"""
mycursor.execute(sql)
print("SUCCESS!")


sql = f"SELECT * FROM Chargers_Data"
mycursor.execute(sql)
myresult = mycursor.fetchall()
print(myresult)

# Closing the cursor and database connection
mycursor.close()
mydb.close()
