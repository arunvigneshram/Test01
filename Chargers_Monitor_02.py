from datetime import datetime
import requests
from SQL_Config import mydb_config, mydb_status

# Setup the mysql database cursors
mycursor_config = mydb_config.cursor()
mycursor_status = mydb_status.cursor()


def charging_status():
    # Get the chargers data form Chargers_Data in wallbox_status database
    mycursor_status.execute(
        "SELECT charger_id, charger_ip, port, rfid, charger_current_state FROM Chargers_Data WHERE charger_current_state = 'CHARGING'")
    chargers = mycursor_status.fetchall()
    print("01. Chargers Data read form the database.")
    print(chargers)

    for charger in chargers:
        # Store the relevant information
        charger_id = charger[0]
        charger_ip = charger[1]
        port = charger[2]
        rfid = charger[3]
        charging_state = charger[4]

        # Get the user_id for the given rfid
        mycursor_config.execute(
            f"SELECT user_id FROM User_Data WHERE user_rfid = '{rfid}'")
        myresult = mycursor_config.fetchall()
        if len(myresult) > 0:
            rfid_user_id = myresult[0][0]

        # Get the utc time now
        charging_state_time = datetime.utcnow().strftime("%H:%M:%S")

        # Get port details form the Chargers_Config
        mycursor_config.execute(
            f"SELECT port, charger_ip FROM Chargers_Config WHERE charger_id = '{charger_id}'")
        myresult = mycursor_config.fetchall()
        if len(myresult) > 0:
            port = myresult[0][0]
            charger_ip = myresult[0][1]

        # Get the energy_abs form the charger
        evse_state = requests.get(
            f"http://{charger_ip}:{port}/meter/values").json()
        energy_abs = evse_state["energy_abs"]

        print(charger_id, charger_ip
        )

        # Store all the relevant information inside the database
        sql = f"""
            INSERT INTO Charging_Status (charger_id, rfid, rfid_user_id, charging_state, charging_state_time, energy_abs)
            VALUES (
                    {charger_id}, '{rfid}', {rfid_user_id}, '{charging_state}', '{charging_state_time}',
                    {energy_abs}
                    )
            """
        mycursor_status.execute(sql)


while True:
    charging_status()
