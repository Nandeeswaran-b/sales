import mysql.connector
import random
from datetime import datetime, timedelta

def random_date(start, end): return start + timedelta(days=random.randint(0, int((end - start).days)))

names = ["Ramesh", "Sita", "John", "Alice", "Priya", "Amit", "Deepak", "Neha", "Rajesh", "Kavita"]
products = [("PS5", "Gaming", 49990), ("Monitor", "Accessories", 39900), ("Mouse", "Accessories", 900), ("Earbuds", "Audio", 2500)]
payments = ["Cash", "Credit Card", "UPI"]

c = mysql.connector.connect(host='localhost',user='root',password='root',database='sales_db')
cursor = c.cursor()
d1 = datetime.strptime('1/1/2023', '%m/%d/%Y')
d2 = datetime.strptime('4/3/2024', '%m/%d/%Y')

for i in range(50):
    c_name = random.choice(names) + " " + str(random.randint(1, 99))
    mobile = f"98{random.randint(10000000, 99999999)}"
    cursor.execute("INSERT INTO customers (name, mobile_no) VALUES (%s, %s)", (c_name, mobile))
    customer_id = cursor.lastrowid
    
    prod = random.choice(products)
    cursor.execute("SELECT id FROM products WHERE name=%s", (prod[0],))
    row = cursor.fetchone()
    if row: product_id = row[0]
    else:
        cursor.execute("INSERT INTO products (name, category, price) VALUES (%s, %s, %s)", (prod[0], prod[1], prod[2]))
        product_id = cursor.lastrowid

    qty = random.randint(1, 2)
    s_date = random_date(d1, d2).strftime('%Y-%m-%d')
    cursor.execute("INSERT INTO sales (product_id, customer_id, quantity, sale_date, total_price, mode_of_payment) VALUES (%s, %s, %s, %s, %s, %s)", (product_id, customer_id, qty, s_date, qty*prod[2], random.choice(payments)))

c.commit()
cursor.close()
c.close()
print("Done seeding")
