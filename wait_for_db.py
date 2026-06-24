import time
import pymysql

while True:
    try:
        pymysql.connect(
            host="mysql",
            user="root",
            password="root123",
            database="infratech"
        )
        print("MySQL is ready!")
        break
    except Exception as e:
        print("Waiting for MySQL...")
        time.sleep(2)