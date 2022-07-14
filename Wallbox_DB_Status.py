import mysql.connector
from SQL_Config import db_config

# Setup of the mysql connector to the database
mydb = mysql.connector.connect(
    host=db_config["host"],
    user=db_config["user"],
    password=db_config["password"],
    database="wallbox_status",
    autocommit=True
)

# Setup cursor
mycursor = mydb.cursor()

# Create Chargers_Data table
sql = """
    CREATE TABLE IF NOT EXISTS Chargers_Data (
        charger_id INT NOT NULL PRIMARY KEY,
        rfid VARCHAR(25) NOT NULL,
        rfid_last_seen int NOT NULL,
        phases VARCHAR(50) NOT NULL,
        allowed_current int,
        iec61851_state int NOT NULL,
        charger_state int NOT NULL,
        error_state int NOT NULL,
        rfid_check BOOLEAN NOT NULL,
        phase_check BOOLEAN NOT NULL,
        low_state_check BOOLEAN,
        charger_current_state VARCHAR(10) NOT NULL
        )
    """
mycursor.execute(sql)
print("01. Chargers_Data database created.")

# Create Chargers_Start_Stop table
sql = """
    CREATE TABLE IF NOT EXISTS Chargers_Start_Stop (
        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        charger_id INT NOT NULL,
        rfid VARCHAR(25) NOT NULL,
        rfid_user_id INT NOT NULL,
        charger_start_stop BOOLEAN NOT NULL,
        external_state_change BOOLEAN,
        external_user_id INT,
        start_stop_time VARCHAR(50) NOT NULL,
        energy_abs int NOT NULL,
        entry_check VARCHAR(10)
        )
    """
mycursor.execute(sql)
print("02. Chargers_Start_Stop database created.")

# Create Charging_Status table
sql = """
    CREATE TABLE IF NOT EXISTS Charging_Status (
        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        charger_id INT NOT NULL,
        rfid VARCHAR(25) NOT NULL,
        rfid_user_id INT NOT NULL,
        charging_state VARCHAR(10) NOT NULL,
        charging_state_time VARCHAR(50) NOT NULL,
        energy_abs int NOT NULL
        )
    """
mycursor.execute(sql)
print("03. Charging_Status database created.")

# Create Charging_Session table
sql = """
    CREATE TABLE IF NOT EXISTS Charging_Session (
        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        charger_id INT NOT NULL,
        rfid VARCHAR(25) NOT NULL,
        rfid_user_id INT NOT NULL,
        charging_start_time VARCHAR(50) NOT NULL,
        charging_stop_time VARCHAR(50) NOT NULL,
        charging_time VARCHAR(50) NOT NULL,
        energy_consumed int NOT NULL
        )
    """
mycursor.execute(sql)
print("04. Charging_Session database created.")

# Closing the cursor and database connection
mycursor.close()
mydb.close()
