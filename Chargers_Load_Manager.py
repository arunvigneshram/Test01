import requests
from SQL_Config import mydb_config, mydb_status

# Setup the mysql database cursors
mycursor_config = mydb_config.cursor()
mycursor_status = mydb_status.cursor()


def load_balancer():
    # Get the list of the chargers currently active
    mycursor_status.execute(
        "SELECT charger_id, charger_ip, port, distibutor, current_limit, rfid, charger_current_state FROM Chargers_Data")
    chargers = mycursor_status.fetchall()
    print("01. Chargers Data read form the database.")
    print(chargers)

    # Update the Charging_Load Database
    for charger in chargers:
        # Store the necessary data
        charger_id = charger[0][0]
        rfid = charger[0][5]
        charger_current_state = charger[0][6]

        # Load them all into the Charging_Load table in wallbox_status database
        mycursor_status.execute(
            f"SELECT charger_id FROM Charging_Load")
        does_exist = mycursor_status.fetchall()

        if len(does_exist) > 0:
            mycursor_status.execute(
                f"UPDATE Charging_Load SET charger_id = {charger_id}, rfid = '{rfid}', charger_current_state = '{charger_current_state}'")
        else:
            sql = f"""
                INSERT INTO Charging_Load (charger_id, rfid)
                VALUES (
                    {charger_id}, '{rfid}'
                    )
                """
            mycursor_status.execute(sql)

    # Identify the non charging and set them to zero
    mycursor_status.execute(
        "SELECT charger_id, charger_current_state FROM Charging_Load")
    chargers_load = mycursor_status.fetchall()

    for charger in chargers_load:
        charger_id = charger[0][0]
        charger_current_state = charger[0][1]

        if charger_current_state != "CHARGING":
            mycursor_config.execute(
                f"UPDATE Charging_Load SET allowed_current = 0")
            requests.put(
                f"http://{charger_id}:{80}/evse/external_current_update", json={"current": 0})

        else:
            mycursor_config.execute(
                f"UPDATE Charging_Load SET allowed_current = 16")
            requests.put(
                f"http://{charger_id}:{80}/evse/external_current_update", json={"current": 16000})

    # Load balance the CHARGING chargers
    distributor_A = 150
    distributor_B = 150
    distributor_C = 150
    distributor_M = 265


def test_chargers():
    pass
    # Get the first of Charging_Unchanged chargers

    # Acknowledge in the database

    # Ignore the charger if it's at maximum

    # Try to run the chargers at higher amps from reserved current

    # Check the change in values or mark it as charged
