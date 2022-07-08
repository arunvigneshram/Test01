import Charger_Configuration as config
from SQL_Configuration import db_config
from datetime import datetime
import mysql.connector
import pandas as pd

# ips = []
# for charger in config.chargers:
#     ips.append(charger["ip"])
# print(f"The IP Addresses of the chargers are, {ips}.")

# Import pickled dataframe
chargers_data_df = pd.read_pickle("./chargers_data_df.pkl")
print("Imported chargers status dataframe successfully.")
print(chargers_data_df)

# Setup of the mysql connector to the database
mydb = mysql.connector.connect(
    host=db_config["host"],
    user=db_config["user"],
    password=db_config["password"],
    database="evchargers"
)

mycursor = mydb.cursor()
mycursor.execute("SELECT * FROM User_Data")
myresult = mycursor.fetchall()

for x in myresult:
    print(x)

# Create the charger status dataframe
column_names = ["charger_id", "rfid", "distributor", "last_seen", "charger_status", "capacity", "rfid_check"
                "charging_status", "start_time", "user_name", "end_time", "meter_value", "low_state", "checked"]
chargers_status_df = pd.DataFrame(columns=column_names)

# Loop throught the chargers_data dataframe -- Change to index method
for index, row in chargers_data_df.itterows():

    # Fill the values of the chargers_status_df from chargers_data_df
    chargers_status_df.append({
        "charger_id": row["charger_id"],
        "rfid": row["rfid"],
        "distibutor": row["distributor"],
        "last_seen": row["last_seen"],
        "charger_status": row["charger_status"],
        "capacity": row["capacity"],
        "meter_value": row["meter_value"]
    }, ignore_index=True
    )

    # Check rfid with the user database
    rfid = row["rfid"]
    mycursor.execute(f"SELECT * FROM User_Date WHERE rfid = {rfid}")
    myresult = mycursor.fetchall()

    if rfid == myresult[2]:
        chargers_status_df.loc[chargers_status_df["charger_id"] == row["charger_id"], ["rfid_check", "user_name"]] = ["PASS", myresult[1]]
    else:
        chargers_data_df.loc["rfid_check"] = "FAIL"

    # Start Charging
    if chargers_status_df.loc["rfid_check"] == "PASS":
        # Reset meter

        chargers_status_df[["charging_status", "start_time"]] = ["CHARGING", datetime.now()]
        
    
