import requests
import time
from SQL_Config import mydb_config, mydb_status

# Setup the mysql database cursors
mycursor_config = mydb_config.cursor()
mycursor_status = mydb_status.cursor()

while True:
    # Get the chargers data form Chargers_Config in wallbox_config database
    mycursor_config.execute("SELECT * FROM Chargers_Config")
    chargers_config = mycursor_config.fetchall()
    print("01. Chargers Configuration read form the database.")
    print(chargers_config)

    # Access the status of the chargers form the acquired chargers_config
    for charger in chargers_config:
        # Set check variables
        rfid_check = False
        phase_check = False
        entry_exists = False

        # Get the chargers information
        charger_id = charger[0]
        charger_ip = charger[1]
        port = charger[2]
        distributor = charger[3]
        current_limit = charger[4]

        # Request chargers for evse/state and nfc/seen_tags
        try:
            evse_state = requests.get(
                f"http://{charger_ip}:{port}/evse/state").json()
            nfc_seen_tags = requests.get(
                f"http://{charger_ip}:{port}/nfc/seen_tags").json()
            meter_phases = requests.get(
                f"http://{charger_ip}:{port}/meter/phases").json()
        except Exception as e:
            print(e)

        # Process the collected information
        iec61851_state = evse_state["iec61851_state"]
        charger_state = evse_state["charger_state"]
        error_state = evse_state["error_state"]
        rfid = nfc_seen_tags[0]["tag_id"]
        rfid_last_seen = nfc_seen_tags[0]["last_seen"]
        phases_connected = meter_phases["phases_connected"]
        phases = f"{phases_connected[0]} | {phases_connected[1]} | {phases_connected[2]}"

        # Perform phases_check
        if phases_connected[0] == True and phases_connected[1] == True and phases_connected[2] == True:
            phase_check = True

        # Check the existing charger_current_state form the Charger_Data
        mycursor_status.execute(
            f"SELECT charger_current_state FROM Chargers_Data WHERE charger_id = {charger_id}")
        myresult = mycursor_status.fetchall()
        if len(myresult) > 0:
            existing_charger_current_state = myresult[0][0]
            entry_exists = True
        else:
            existing_charger_current_state = "WAITING"
        print(existing_charger_current_state)

        if iec61851_state == 2 and charger_state == 3 and error_state == 0:
            if existing_charger_current_state != "CHARGING":
                charger_current_state = "READY"
            if existing_charger_current_state == "CHARGING" and rfid_last_seen < 10:
                charger_current_state = "STOPPED"

        if iec61851_state == 1 and charger_state == 1 and error_state == 0:
            if existing_charger_current_state != "READY":
                charger_current_state = "WAITING"

        # Perform phase related error check
        if not phase_check or error_state != 0:
            charger_current_state = "ERROR"
        else:
            if existing_charger_current_state == "STOPPED":
                charger_current_state = "WAITING"

        # # Perform the final charger_current_check
        # if iec61851_state == 1 and charger_state == 1 and error_state == 0:
        #     if existing_charger_current_state != "READY":
        #         charger_current_state = "WAITING"

        # if iec61851_state == 2 and charger_state == 3 and error_state == 0:
        #     if existing_charger_current_state == "CHARGING" and rfid_last_seen < 10:
        #         charger_current_state = "STOPPED"
        #     elif existing_charger_current_state == "CHARGING":
        #         charger_current_state = "CHARGING"

        # if existing_charger_current_state == None or existing_charger_current_state == "WAITING":
        #     charger_current_state = "WAITING"

        # # Perform phase related error check
        # if not phase_check or error_state != 0:
        #     charger_current_state = "ERROR"
        # else:
        #     if existing_charger_current_state == "STOPPED":
        #         charger_current_state = "WAITING"

        print(f"{rfid}, {rfid_last_seen}, {phases}, {iec61851_state}, {charger_state}, {error_state}, {rfid_check}, {phase_check}, {charger_current_state}")

        # Store all the values in the database
        if entry_exists:
            sql = f"""
                UPDATE Chargers_Data
                SET
                charger_ip = '{charger_ip}',
                port = {port},
                distributor = '{distributor}',
                current_limit = {current_limit},
                rfid = '{rfid}',
                rfid_last_seen = {rfid_last_seen},
                phases = '{phases}',
                iec61851_state = {iec61851_state},
                charger_state = {charger_state},
                error_state = {error_state},
                rfid_check = {rfid_check},
                phase_check = {phase_check},
                charger_current_state = '{charger_current_state}'
                WHERE charger_id = {charger_id}
                """
            mycursor_status.execute(sql)
            print("Yes")

        else:
            sql = f"""
                INSERT INTO Chargers_Data (charger_id, charger_ip, port, distributor, current_limit, rfid, rfid_last_seen, phases, iec61851_state, charger_state, error_state, rfid_check, phase_check, charger_current_state)
                VALUES (
                    {charger_id}, '{charger_ip}', {port}, '{distributor}', {current_limit}, '{rfid}', {rfid_last_seen}, '{phases}', {iec61851_state}, {charger_state}, {error_state}, {rfid_check}, {phase_check}, '{charger_current_state}'
                    )
                """
            mycursor_status.execute(sql)

    print("DONE")
    time.sleep(1)
