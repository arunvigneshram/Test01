import mysql.connector
from SQL_Config import db_config

# Setup of the mysql connector to the database
mydb = mysql.connector.connect(
    host=db_config["host"],
    user=db_config["user"],
    password=db_config["password"],
    database="wallbox_config",
    autocommit=True
)

# Setup cursor
mycursor = mydb.cursor()

# Create User_Data table and insert values
# Include active inactive status
sql = """
    CREATE TABLE IF NOT EXISTS User_Data (
        user_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        user_name VARCHAR(25) NOT NULL,
        user_rfid VARCHAR(25) NOT NULL
        )
    """
mycursor.execute(sql)
sql = """
    INSERT INTO User_Data (user_name, user_rfid)
    VALUES
        ('Elias', '04:60:B5:72:3B:74:81')
    """
mycursor.execute(sql)

# Dispaly the User_Data table contents
print("01. The content of the User_Data database is as follows.")
mycursor.execute("SELECT * FROM User_Data")
myresult = mycursor.fetchall()
for x in myresult:
    print("\t", x)
print(f"\tThe total number of {mycursor.rowcount} rows in User_Data.")

# Create Chargers_Config table and insert values
sql = """
    CREATE TABLE IF NOT EXISTS Chargers_Config (
        charger_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        charger_ip VARCHAR(15) NOT NULL,
        port VARCHAR(6) NOT NULL,
        distributor VARCHAR(1) NOT NULL,
        current_limit int NOT NULL
    )
    """
mycursor.execute(sql)
sql = """
    INSERT INTO Chargers_Config (charger_ip, port, distributor, current_limit)
    VALUES ("127.0.0.1", "5000", "A", 16)
    """
mycursor.execute(sql)

# Dispaly the Chargers_Config table contents
print("02. The content of the Chargers_Config database is as follows.")
mycursor.execute("SELECT * FROM Chargers_Config")
myresult = mycursor.fetchall()
for x in myresult:
    print("\t", x)
print(f"\tThe total number of {mycursor.rowcount} rows in Chargers_Config.")

# Create Distibutor_Config table and insert values
sql = """
    CREATE TABLE IF NOT EXISTS Distributors_Config (
        distibutor_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        distributor VARCHAR(1) NOT NULL,
        distributor_type VARCHAR(4) NOT NULL,
        power_limit int NOT NULL,
        current_limit int NOT NULL
    )
    """
mycursor.execute(sql)
sql = """
    INSERT INTO Distributors_Config (distributor, distributor_type, power_limit, current_limit)
    VALUES 
        ("A", "sub", 120, 150),
        ("B", "sub", 120, 150),
        ("C", "sub", 120, 150),
        ("M", "main", 200, 265)
    """
mycursor.execute(sql)

# Dispaly the Chargers_Config table contents
print("03. The content of the Distributors_Config database is as follows.")
mycursor.execute("SELECT * FROM Distributors_Config")
myresult = mycursor.fetchall()
for x in myresult:
    print("\t", x)
print(
    f"\tThe total number of {mycursor.rowcount} rows in Distributors_Config.")

# Closing the cursor and database connection
mycursor.close()
mydb.close()
