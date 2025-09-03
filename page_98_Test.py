import mysql.connector

# เชื่อมต่อ MariaDB
conn = mysql.connector.connect(
    host="localhost",      # หรือ IP ของ server
    user="root",           # username
    password="1234", 
    database="rpisql"   # ชื่อฐานข้อมูล
)

cursor = conn.cursor()

# ดึงข้อมูลทั้งหมดจากตาราง pd_item
cursor.execute("SELECT * FROM pd_item;")
rows = cursor.fetchall()

# แสดงผลข้อมูล
for row in rows:
    print(row)

# ปิดการเชื่อมต่อ
cursor.close()
conn.close()
