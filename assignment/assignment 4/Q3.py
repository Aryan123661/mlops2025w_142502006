

import time
from sqlalchemy import (
    create_engine, MetaData, Table, Column, Integer, String, DateTime, DECIMAL, ForeignKey
)
from sqlalchemy.exc import SQLAlchemyError
from pymongo import MongoClient
from datetime import datetime

print("\n===== SQL (SQLite via SQLAlchemy) CRUD Performance =====")

engine = create_engine("sqlite:///:memory:", echo=False, future=True)
metadata = MetaData()

customer = Table(
    "Customer", metadata,
    Column("CustomerID", Integer, primary_key=True),
    Column("Country", String(100))
)

invoice = Table(
    "Invoice", metadata,
    Column("InvoiceNo", String(20), primary_key=True),
    Column("InvoiceDate", DateTime),
    Column("CustomerID", Integer, ForeignKey("Customer.CustomerID"))
)

product = Table(
    "Product", metadata,
    Column("StockCode", String(20), primary_key=True),
    Column("Description", String(200)),
    Column("UnitPrice", DECIMAL(10, 2))
)

invoice_details = Table(
    "InvoiceDetails", metadata,
    Column("InvoiceNo", String(20), ForeignKey("Invoice.InvoiceNo")),
    Column("StockCode", String(20), ForeignKey("Product.StockCode")),
    Column("Quantity", Integer)
)

metadata.create_all(engine)
conn = engine.connect()

# CREATE
start = time.time()
try:
    conn.execute(customer.insert().values(CustomerID=17850, Country="United Kingdom"))
    conn.execute(invoice.insert().values(InvoiceNo="536365", InvoiceDate=datetime(2010, 12, 1, 8, 26), CustomerID=17850))
    conn.execute(product.insert().values(StockCode="85123A", Description="WHITE HANGING HEART T-LIGHT HOLDER", UnitPrice=2.55))
    conn.execute(invoice_details.insert().values(InvoiceNo="536365", StockCode="85123A", Quantity=6))
except SQLAlchemyError as e:
    print("SQL CREATE error:", e)
end = time.time()
print("SQL CREATE took:", end - start, "seconds")

# READ
start = time.time()
result = conn.execute(invoice.select().where(invoice.c.CustomerID == 17850)).fetchone()
end = time.time()
print("SQL READ result:", result)
print("SQL READ took:", end - start, "seconds")

# UPDATE
start = time.time()
conn.execute(invoice.update().where(invoice.c.InvoiceNo == "536365").values(InvoiceDate=datetime(2010, 12, 2, 9, 0)))
end = time.time()
print("SQL UPDATE took:", end - start, "seconds")

# DELETE
start = time.time()
conn.execute(invoice.delete().where(invoice.c.InvoiceNo == "536365"))
end = time.time()
print("SQL DELETE took:", end - start, "seconds")


# ---------------------- MongoDB ----------------------
print("\n===== MongoDB CRUD Performance =====")

client = MongoClient("mongodb://localhost:27017", maxPoolSize=50, serverSelectionTimeoutMS=5000)
db = client["RetailDB_Q3"]
transactions = db["Transactions"]

# Clean collection
transactions.delete_many({})

transaction_doc = {
    "InvoiceNo": "536365",
    "InvoiceDate": datetime(2010, 12, 1, 8, 26),
    "CustomerID": 17850,
    "Country": "United Kingdom",
    "Items": [
        {"StockCode": "85123A", "Description": "WHITE HANGING HEART T-LIGHT HOLDER", "Quantity": 6, "UnitPrice": 2.55}
    ]
}

# CREATE
start = time.time()
transactions.insert_one(transaction_doc)
end = time.time()
print("MongoDB CREATE took:", end - start, "seconds")

# READ
start = time.time()
doc = transactions.find_one({"CustomerID": 17850})
end = time.time()
print("MongoDB READ result:", doc)
print("MongoDB READ took:", end - start, "seconds")

# UPDATE
start = time.time()
transactions.update_one({"InvoiceNo": "536365"}, {"$set": {"Country": "France"}})
end = time.time()
print("MongoDB UPDATE took:", end - start, "seconds")

# DELETE
start = time.time()
transactions.delete_one({"InvoiceNo": "536365"})
end = time.time()
print("MongoDB DELETE took:", end - start, "seconds")
