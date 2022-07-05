# import asyncio
import pandas as pd
import websocket
import json
import mysql.connector as myc
import Charger_Configuratation as config


# Get IP address and generate the urls
connections = []
ips = []
for charger in config.chargers:
    connections.append(f"ws://{charger['ip']}:80/ws")
    ips.append(charger["ip"])
print(f"The IP Addresses of the chargers are, {ips}.")
print(f"The Connections made from the IP addresses are, {connections}.")

# Dataframe columns
column_names = ["charger_id", "ip_address", "distributor", "capacity",
                "charger_status", "low_state", "phases", "rfid", "last_seen"]

while True:
    # Create dataframe for every cycle
    chargers_status = pd.DataFrame(columns=column_names)
    print(chargers_status)

    for i, connection in enumerate(connections):
        ws = websocket.create_connection(f"ws://{ips[i]}/ws")
        ws_dict = json.loads(ws)

        phase_d = True
        for phase in ws_dict[]:
            if phase != True:
                phase_d = False

        if ws.dict[] == 1 and ws.dict[] == 2 and ws.dict[] == 0:
            charger_status_d = "READY"

        chargers_status = chargers_status.append({"charger_id": config.chargers[i]["id"],
                                                  "ip_address": config.chargers[i]["ip"],
                                                  "distributor": config.chargers[i]["distributor"],
                                                  "capacity": f"{config.chargers[i]['current_limit']} A",
                                                  "charger_status": charger_status_d,
                                                  "low_state": None,
                                                  "phases": phase_d,
                                                  "rfid": ws.dict[],
                                                  "last_seen": ws.dict[]},
                                                 ignore_index=True)

    # chargers_status.set_index("charger_id", inplace=True)

    # Save dataframe as pickle
    chargers_status.to_pickle("./chargers_status.pkl")

# async def handle_socket(url, ):
#     async with websockets.connect(url) as websocket:
#         async for message in websocket:
#             print(message)


# async def handler():
#     await asyncio.wait([handle_socket(uri) for uri in connections])

# asyncio.get_event_loop().run_until_complete(handler())
