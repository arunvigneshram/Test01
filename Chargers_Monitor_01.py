from SQL_Config import mydb_config, mydb_status

# Setup the mysql database cursors
mycursor_config = mydb_config.cursor()
mycursor_status = mydb_status.cursor()


def session_log():
    # ID to hold the last checked id
    id = 0

    # Find the last checked row in the Chargers_Start_Stop table in the wallbox_status database
    mycursor_status.exectue(
        "SELECT MIN(id) FROM Chargers_Start_Stop WHERE entry_check = NULL")
    myresult = mycursor_status.fetchall()
    if len(myresult) > 0:
        id = myresult[0][0]

    # Get relevant charger start stop information form the Charger_Start_Stop table in the wallbox_status database
    mycursor_status.execute(
        f"SELECT id, charger_id, rfid, rfid_user_id, charger_start_stop, start_stop_time, energy_abs FROM Chargers_Start_Stop WHERE id >= {id}")
    myresult = mycursor_status.fetchall()

    for i in range(0, len(myresult)):
        first_charger_id = myresult[i][0]
        for j in range(i+1, len(myresult)):
            if myresult[j][0] == first_charger_id:
                second_charger_id = myresult[j][0]
            else:
                continue

            # Calculate the charge start stop session
            charger_id = first_charger_id
            rfid = myresult[i][2]
            rfid_user_id = myresult[i][3]
            charging_start_time = myresult[i][5]
            charging_stop_time = myresult[j][5]
            energy_consumed = myresult[j][6] - myresult[j][5]

            # Make the session log entry
            sql = f"""
                INSERT INTO Charging_Session (charger_id, rfid, rfid_user_id, charging_start_time, charging_stop_time, energy_consumed)
                VALUES (
                        {charger_id}, '{rfid}', {rfid_user_id}, '{charging_start_time}', '{charging_stop_time}',
                        {energy_consumed}
                        )
                """
            mycursor_status.execute(sql)

            # Change the entry_check in both the ids
            mycursor_status.execute(
                f"UPDATE Chargers_Start_Stop SET entry_check = 'CHECKED' WHERE id = {first_charger_id}")
            mycursor_status.execute(
                f"UPDATE Chargers_Start_Stop SET entry_check = 'CHECKED' WHERE id = {second_charger_id}")


while True:
    session_log()
