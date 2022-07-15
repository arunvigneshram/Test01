import requests
from datetime import datetime
from SQL_Config import mydb_config, mydb_status

# Setup the mysql database cursors
mycursor_config = mydb_config.cursor()
mycursor_status = mydb_status.cursor()


# Function to start charging and stop charging

def start_charging(charger_id, charger_ip, port, rfid, rfid_user_id, energy_abs):
    # Start Charging Request
    requests.put(
        f"http://{charger_ip}:{port}/start_charging", json={})

    # Note the utc time
    start_stop_time = datetime.utcnow().strftime("%H:%M:%S")

    # Log the start session into the Chargers_Start_Stop table in wallbox_status database
    sql = f"""
            INSERT INTO Chargers_Start_Stop (charger_id, rfid, rfid_user_id, charger_start_stop, start_stop_time, energy_abs)
            VALUES (
                    {charger_id}, '{rfid}', {rfid_user_id}, 'START', '{start_stop_time}', {energy_abs}
                    )
        """
    mycursor_status.execute(sql)

    # Change the charger_current_status in Chargers_Data table in wallbox_status database
    sql = f"""
            UPDATE Chargers_Data
            SET
            charger_current_state = 'CHARGING'
            WHERE charger_id = {charger_id}
        """
    mycursor_status.execute(sql)


def stop_charging(charger_id, charger_ip, port, rfid, rfid_user_id, energy_abs, charger_current_state):
    # Stop Charging Request
    requests.put(
        f"http://{charger_ip}:{port}/stop_charging", json={})

    # Note the utc time
    start_stop_time = datetime.utcnow().strftime("%H:%M:%S")

    # Log the start session into the Chargers_Start_Stop table in wallbox_status database
    sql = f"""
    INSERT INTO Chargers_Start_Stop (charger_id, rfid, rfid_user_id, charger_start_stop, start_stop_time, energy_abs)
    VALUES (
            {charger_id}, '{rfid}', {rfid_user_id}, 'STOP', '{start_stop_time}', {energy_abs}
        )
    """
    mycursor_status.execute(sql)

    # Error stop and other stop variation
    status = "STOPPED"
    if charger_current_state == "ERROR":
        status = "ERROR"

    # Change the charger_current_status in Chargers_Data table in wallbox_status database
    sql = f"""
            UPDATE Chargers_Data
            SET
            charger_current_state = '{status}'
            WHERE charger_id = {charger_id}
        """
    mycursor_status.execute(sql)


while True:
    # Get the chargers data form Chargers_Data in wallbox_status database
    mycursor_status.execute("SELECT * FROM Chargers_Data")
    chargers_data = mycursor_status.fetchall()
    print("01. Chargers Data read form the database.")
    print(chargers_data)

    # Start and stop the chargers based on the updated information
    for charger in chargers_data:
        # Database entry existance
        entry_exists = False
        rfid_valid = False

        # Store the charger data
        charger_id = charger[0]
        charger_ip = charger[1]
        port = charger[2]
        rfid = charger[5]
        rfid_check = charger[12]
        phase_check = charger[13]
        low_state_check = charger[14]
        charger_current_state = charger[15]

        # Check rfid in User_Data table in wallbox_config database
        mycursor_config.execute(
            f"SELECT user_id FROM User_Data WHERE user_rfid = '{rfid}'")
        myresult = mycursor_config.fetchall()
        if len(myresult) > 0:
            rfid_user_id = myresult[0][0]
            rfid_valid = True
        else:
            print("rfid Invalid!")

        # Declare Ready state for charging
        if rfid_valid and charger_current_state == "WAITING":
            charger_current_state = "READY"
            sql = f"""
                UPDATE Chargers_Data
                SET
                charger_current_state = '{charger_current_state}'
                WHERE charger_id = {charger_id}
                """
            mycursor_status.execute(sql)

        # Request charger for the meter values
        evse_state = requests.get(
            f"http://{charger_ip}:{port}/meter/values").json()
        energy_abs = evse_state["energy_abs"]

        # Charger Start Stop Logic
        if rfid_valid and rfid_check and phase_check:
            # Start Charging Process
            if charger_current_state == "READY":
                start_charging(charger_id, charger_ip, port,
                               rfid, rfid_user_id, energy_abs)

                # Stop Charging Process
            if charger_current_state == "ERROR":
                stop_charging(charger_id, charger_ip, port,
                              rfid, rfid_user_id, energy_abs, charger_current_state)
