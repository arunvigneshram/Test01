import mysql.connector

db_config = {"host": "localhost",
             "user": "evchargers", "password": "evchargers123"}

# Setup of the mysql connector to the wallbox_config database
mydb_config = mysql.connector.connect(
    host=db_config["host"],
    user=db_config["user"],
    password=db_config["password"],
    database="wallbox_config",
)

# Setup of the mysql connector to the wallbox_status database
mydb_status = mysql.connector.connect(
    host=db_config["host"],
    user=db_config["user"],
    password=db_config["password"],
    database="wallbox_status",
    autocommit=True,
)
