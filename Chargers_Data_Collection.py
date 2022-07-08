# import asyncio
import pandas as pd
import websocket
import json
import mysql.connector as myc
import Charger_Configuration as config


# Get IP address and generate the urls
connections = []
ips = []
for charger in config.chargers:
    connections.append(f"ws://{charger['ip']}:{charger['port']}/ws")
    ips.append(charger["ip"])
print(f"The IP Addresses of the chargers are, {ips}.")
print(f"The Connections made from the IP addresses are, {connections}.")

# Dataframe columns
column_names = ["charger_id", "ip_address", "distributor", "capacity",
                "charger_status", "phases", "rfid", "last_seen", "meter_value"]

while True:
    # Create dataframe for every cycle
    chargers_data_df = pd.DataFrame(columns=column_names)
    print(chargers_data_df)

    # Run on all chargers and get the data
    for i, connection in enumerate(connections):
        # Recieve data from websocket
        ws = websocket.create_connection(connection)
        results = ws.recv()

        # Process the recieved data form websocket
        charger_data = json.loads("[" + results.replace("}\n{", "},\n{") + "]")

        # Extract the required data in state variables
        for item in charger_data:
            if item["topic"] == "evse/state":
                iec61851_state = item["payload"]["iec61851_state"]
                charger_state = item["payload"]["charger_state"]
                error_state = item["payload"]["error_state"]
            if item["topic"] == "meter/phases":
                phase_1 = item["payload"]["phases_connected"][0]
                phase_2 = item["payload"]["phases_connected"][1]
                phase_3 = item["payload"]["phases_connected"][2]
            if item["topic"] == "nfc/seen_tags":
                tag_id = item["payload"][0]["tag_id"]
                last_seen = item["payload"][0]["last_seen"]
            if item["topic"] == "meter/values_update":
                energy_rel = item["payload"]["energy_rel"]

        if phase_1 and phase_2 and phase_3:
            phase_state = True

        if iec61851_state == 1 and charger_state == 2 and error_state == 0 and phase_state:
            ready_state = "READY"
        else:
            ready_state = "WAITING"

        if phase_state == False:
            ready_state = "FAILED"

        chargers_data_df = chargers_data_df.append({"charger_id": config.chargers[i]["id"],
                                                    "ip_address": config.chargers[i]["ip"],
                                                    "distributor": config.chargers[i]["distributor"],
                                                    "capacity": config.chargers[i]['current_limit'],
                                                    "charger_status": ready_state,
                                                    "phases": phase_state,
                                                    "rfid": tag_id,
                                                    "last_seen": last_seen,
                                                   "meter_value": energy_rel},
                                                   ignore_index=True)

    chargers_data_df.set_index("charger_id", inplace=True)
    print(chargers_data_df)

    # Save dataframe as pickle
    chargers_data_df.to_pickle("./chargers_data_df.pkl")

# async def handle_socket(url, ):
#     async with websockets.connect(url) as websocket:
#         async for message in websocket:
#             print(message)


# async def handler():
#     await asyncio.wait([handle_socket(uri) for uri in connections])

# asyncio.get_event_loop().run_until_complete(handler())
