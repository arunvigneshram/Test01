import requests
import mysql.connector
from SQL_Config import db_config

# Setup of the mysql connector to the wallbox_config database
mydb_config = mysql.connector.connect(
    host=db_config["host"],
    user=db_config["user"],
    password=db_config["password"],
    database="wallbox_config"
)
mycursor_config = mydb_config.cursor()

# Setup of the mysql connector to the wallbox_status database
mydb_status = mysql.connector.connect(
    host=db_config["host"],
    user=db_config["user"],
    password=db_config["password"],
    database="wallbox_status",
    autocommit=True
)
mycursor_status = mydb_status.cursor()

while True:
    # Necessary variables
    charger_id = []
    charger_current_state = []
    charger_ip = []
    distributors = []
    current_limit = []

    # Get the chargers data form Chargers_Config in wallbox_config database
    mycursor_status.execute(
        "SELECT charger_id, charger_current_state FROM Chargers_Data")
    chargers_data = mycursor_status.fetchall()
    print("01. Charger Data read form the database.")
    print(chargers_data)

    for charger in chargers_data:
        # Get the charger_id from charger
        charger_id.append(charger[0])
        charger_current_state.append(charger[1])

        # Get the Chargers_Config from wallbox_config database for the charger_id
        mycursor_config.execute(
            f"SELECT charger_ip, distibutor, current_limit FROM Chargers_Config WHERE charger_id = {charger_id}")
        myresult = mycursor_config.fetchall()

        # Store the relevant information
        charger_ip.append(myresult[0][0])
        distributors.append(myresult[0][1])
        current_limit.append(myresult[0][2])

    # Get the distributor current limit for each of the distributor
    distributor_A = 150
    distributor_B = 150
    distributor_C = 150
    distributor_M = 265

    number_of_chargers = len(charger_id)
    number_of_super_chargers = 0

    for limit in current_limit:
        if limit > 16:
            number_of_super_chargers = number_of_super_chargers + 1

    number_of_normal_chargers = number_of_chargers - number_of_super_chargers

    total_requirment = 0

    for index, current_state in enumerate(charger_current_state):
        if current_state == "READY" or current_state == "CHARGING":
            total_requirment = total_requirment + current_limit[index]

    
    