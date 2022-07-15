from datetime import datetime
import requests
from SQL_Config import mydb_config, mydb_status

# Setup the mysql database cursors
mycursor_config = mydb_config.cursor()
mycursor_status = mydb_status.cursor()


def identify_unchanged():
    # Get the list of the chargers charging
    mycursor_status.execute(
        "SELECT charger_id, rfid, charger_current_state FROM Chargers_Data WHERE charger_current_state = 'CHARGING'")
    chargers = mycursor_status.fetchall()
    print("01. Chargers Data read form the database.")
    print(chargers)

    # Loop through the chargers
    for charger in chargers:
        charger_id = charger[0][0]

    # Check the Charging_Status table in wallbox_status

    # Identify the unchanged and put them in Charging_Unchanged
