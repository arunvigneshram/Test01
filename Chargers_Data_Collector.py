import requests
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
        # Database entry existance
        entry_exists = False

        # Set check variables
        rfid_check = False
        phase_check = False
        charger_current_state = "WAITING"

        # Get the chargers information
        charger_id = charger[0]
        charger_ip = charger[1]
        port = charger[2]
        distributor = charger[3]
        current_limit = charger[4]

        # Request chargers for evse/state and nfc/seen_tags
        evse_state = requests.get(
            f"http://{charger_ip}:{port}/evse/state").json()
        nfc_last_seen = requests.get(
            f"http://{charger_ip}:{port}/nfc/last_seen").json()
        meter_phases = requests.get(
            f"http://{charger_ip}:{port}/meter/phases").json()

        # Process the collected information
        iec61851_state = evse_state["iec61851_state"]
        charger_state = evse_state["charger_state"]
        error_state = evse_state["error_state"]
        rfid = nfc_last_seen[0]["tag_id"]
        rfid_last_seen = nfc_last_seen[0]["last_seen"]
        phases_connected = meter_phases["phases_connected"]
        phases = f"{phases_connected[0]} | {phases_connected[1]} | {phases_connected[2]}"

        # Perform rfid_check
        mycursor_config.execute(
            f"SELECT user_id FROM User_Data WHERE user_rfid = '{rfid}'")
        myresult = mycursor_config.fetchall()
        if len(myresult) > 0:
            rfid_check = True

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

        # Perform phase related error check
        if not phase_check:
            charger_current_state = "ERROR"
        else:
            charger_current_state = "WAITING"

        # Perform the final charger_current_check
        if iec61851_state == 2 and charger_state == 1 and error_state == 0:
            if existing_charger_current_state == "CHARGED" or existing_charger_current_state == "STOPPED":
                if rfid_last_seen < 100:
                    charger_current_state = "WAITING"
            elif existing_charger_current_state == "READY":
                charger_current_state = "READY"
            elif existing_charger_current_state == "CHARGING":
                charger_current_state = "CHARGING"

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
        else:
            sql = f"""
                INSERT INTO Chargers_Data (charger_id, charger_ip, port, distributor, current_limit, rfid, rfid_last_seen, phases, iec61851_state, charger_state, error_state, rfid_check, phase_check, charger_current_state)
                VALUES (
                    {charger_id}, '{charger_ip}', {port}, '{distributor}', {current_limit}, '{rfid}', {rfid_last_seen}, '{phases}', {iec61851_state}, {charger_state}, {error_state}, {rfid_check}, {phase_check}, '{charger_current_state}'
                    )
                """
        mycursor_status.execute(sql)

    print("DONE")


#

# # Get IP address and generate the urls
# connections = []
# ips = []
# for charger in config.chargers:
#     connections.append(f"ws://{charger['ip']}:{charger['port']}/ws")
#     ips.append(charger["ip"])
# print(f"The IP Addresses of the chargers are, {ips}.")
# print(f"The Connections made from the IP addresses are, {connections}.")

# # Dataframe columns
# column_names = ["charger_id", "ip_address", "distributor", "capacity",
#                 "charger_status", "phases", "rfid", "last_seen", "meter_value"]

# while True:
#     # Create dataframe for every cycle
#     chargers_data_df = pd.DataFrame(columns=column_names)
#     print(chargers_data_df)

#     # Run on all chargers and get the data
#     for i, connection in enumerate(connections):
#         # Recieve data from websocket
#         ws = websocket.create_connection(connection)
#         results = ws.recv()

#         # Process the recieved data form websocket
#         charger_data = json.loads("[" + results.replace("}\n{", "},\n{") + "]")

#         # Extract the required data in state variables
#         for item in charger_data:
#             if item["topic"] == "evse/state":
#                 iec61851_state = item["payload"]["iec61851_state"]
#                 charger_state = item["payload"]["charger_state"]
#                 error_state = item["payload"]["error_state"]
#             if item["topic"] == "meter/phases":
#                 phase_1 = item["payload"]["phases_connected"][0]
#                 phase_2 = item["payload"]["phases_connected"][1]
#                 phase_3 = item["payload"]["phases_connected"][2]
#             if item["topic"] == "nfc/seen_tags":
#                 tag_id = item["payload"][0]["tag_id"]
#                 last_seen = item["payload"][0]["last_seen"]
#             if item["topic"] == "meter/values_update":
#                 energy_rel = item["payload"]["energy_rel"]

#         if phase_1 and phase_2 and phase_3:
#             phase_state = True

#         if iec61851_state == 1 and charger_state == 2 and error_state == 0 and phase_state:
#             ready_state = "READY"
#         else:
#             ready_state = "WAITING"

#         if phase_state == False:
#             ready_state = "FAILED"

#         chargers_data_df = chargers_data_df.append({"charger_id": config.chargers[i]["id"],
#                                                     "ip_address": config.chargers[i]["ip"],
#                                                     "distributor": config.chargers[i]["distributor"],
#                                                     "capacity": config.chargers[i]['current_limit'],
#                                                     "charger_status": ready_state,
#                                                     "phases": phase_state,
#                                                     "rfid": tag_id,
#                                                     "last_seen": last_seen,
#                                                    "meter_value": energy_rel},
#                                                    ignore_index=True)

#     chargers_data_df.set_index("charger_id", inplace=True)
#     print(chargers_data_df)

#     # Save dataframe as pickle
#     chargers_data_df.to_pickle("./chargers_data_df.pkl")
