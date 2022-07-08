import Charger_Configuration as config
import pandas as pd

ips = []
for charger in config.chargers:
    ips.append(charger["ip"])
print(f"The IP Addresses of the chargers are, {ips}.")

# Import pickled dataframe
chargers_status_df = pd.read_pickle("./chargers_status.pkl")
print("Imported chargers status dataframe successfully.")

# Get 

