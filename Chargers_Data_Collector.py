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
        rfid_check = 0
        phase_check = 0
        charger_current_check = "WAITING"

        # Get the chargers information
        charger_id = charger[0]
        charger_ip = charger[1]
        port = charger[2]

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
            f"SELECT user_id FROM User_Data WHERE rfid = '{rfid}'")
        myresult = mycursor_config.fetchall()
        if len(myresult) > 0:
            rfid_check = 1

        # Perform phases_check
        if phases_connected[0] == True and phases_connected[1] == True and phases_connected[2] == True:
            phase_check = 1

        # Check the existing charger_current_state form the Charger_Data
        mycursor_status.execute(
            f"SELECT charger_current_state FROM Chargers_Data WHERE charger_id = {charger_id}")
        myresult = mycursor_status.fetchall()
        if len(myresult) > 0:
            existing_charger_current_state = myresult[0][0]
            entry_exists = True

        # Perform the final charger_current_check
        if iec61851_state == 2 and charger_state == 1 and error_state == 0:
            if existing_charger_current_state == "CHARGING":
                continue
            else:
                charger_current_state = "WAITING"
        else:
            charger_current_state = "ERROR"

        print(f"{rfid}, {rfid_last_seen}, {phases}, {iec61851_state}, {charger_state}, {error_state}, {rfid_check}, {phase_check}, {charger_current_state}")

        # Store all the values in the database
        if entry_exists:
            sql = f"""
                UPDATE Chargers_Data
                SET
                rfid = '{rfid}',
                rfid_last_seen = {rfid_last_seen},
                phases = '{phases}',
                iec61851_state = {iec61851_state},
                charger_state = {charger_state},
                error_state = {error_state},
                rfid_check = {rfid_check},
                phase_check = {phase_check},
                charger_current_state = '{charger_current_check}'
                WHERE charger_id = {charger_id}
                """
        else:
            sql = f"""
                INSERT INTO Chargers_Data (charger_id, rfid, rfid_last_seen, phases, iec61851_state, charger_state, error_state, rfid_check, phase_check, charger_current_state)
                VALUES (
                    {charger_id}, '{rfid}', {rfid_last_seen}, '{phases}', {iec61851_state}, {charger_state}, {error_state}, {rfid_check}, {phase_check}, '{charger_current_check}'
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
