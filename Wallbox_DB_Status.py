import mysql.connector
from SQL_Config import db_config

# Setup of the mysql connector to the database
mydb_status = mysql.connector.connect(
    host=db_config["host"],
    user=db_config["user"],
    password=db_config["password"],
    database="wallbox_status",
    autocommit=True
)

# Setup cursor
mycursor = mydb_status.cursor()

# Create Chargers_Data table
sql = """
    CREATE TABLE IF NOT EXISTS Chargers_Data (
        charger_id INT NOT NULL PRIMARY KEY,
        charger_ip VARCHAR(15) NOT NULL,
        port INT NULL NULL,
        distributor VARCHAR(1) NOT NULL,
        current_limit INT NOT NULL,
        rfid VARCHAR(25) NOT NULL,
        rfid_last_seen INT NOT NULL,
        session_id INT,
        phases VARCHAR(50) NOT NULL,
        allowed_current int,        
        iec61851_state int NOT NULL,
        charger_state int NOT NULL,
        error_state int NOT NULL,
        rfid_check BOOLEAN NOT NULL,
        phase_check BOOLEAN NOT NULL,
        charger_current_state VARCHAR(10) NOT NULL,
        verified BOOLEAN NOT NULL
        )
    """
mycursor.execute(sql)
print("01. Chargers_Data database created.")

# Create Charging_Status table
sql = """
    CREATE TABLE IF NOT EXISTS Charging_Status (
        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        session_id INT NOT NULL,
        charger_id INT NOT NULL,
        rfid VARCHAR(25) NOT NULL,
        rfid_user_id INT NOT NULL,
        charging_state_time VARCHAR(50) NOT NULL,
        energy_abs int NOT NULL,
        verified BOOLEAN NOT NULL
        )
    """
mycursor.execute(sql)
print("02. Charging_Status database created.")

# Create Charging_Session table
sql = """
    CREATE TABLE IF NOT EXISTS Charging_Session (
        session_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        charger_id INT NOT NULL,
        rfid VARCHAR(25) NOT NULL,
        rfid_user_id INT NOT NULL,
        charging_start_time VARCHAR(50) NOT NULL,
        charging_stop_time VARCHAR(50) NOT NULL,
        charging_time VARCHAR(50) NOT NULL,
        energy_abs_start INT NOT NULL,
        energy_abs_stop INT NOT NULL,
        energy_consumed INT NOT NULL,
        verified BOOLEAN NOT NULL
        )
    """
mycursor.execute(sql)
print("03. Charging_Session database created.")

# Create Charging_Load table
sql = """
    CREATE TABLE IF NOT EXISTS Charging_Load (
        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        charger_id INT NOT NULL,
        allowed_current INT NOT NULL,
        charger_current_state VARCHAR(10) NOT NULL,
        verified BOOLEAN NOT NULL
        )
    """
mycursor.execute(sql)
print("04. Charging_Load database created.")

# Closing the cursor and database connection
mycursor.close()
mydb_status.close()
