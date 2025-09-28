
from pymongo import MongoClient, errors
import datetime

try:
    client = MongoClient("mongodb://localhost:27017/",
                         maxPoolSize=50,
                         serverSelectionTimeoutMS=5000)
    db = client["RetailDB"]

    client.admin.command("ping")
    print("✅ Connected to MongoDB")

except errors.ServerSelectionTimeoutError as e:
    print("❌ MongoDB connection failed:", e)
    exit(1)

transactions_coll = db["Transactions"]   
customers_coll = db["Customers"]        

transaction_doc = {
    "InvoiceNo": "536365",
    "InvoiceDate": datetime.datetime(2010, 12, 1, 8, 26),
    "CustomerID": 17850,
    "Country": "United Kingdom",
    "Items": [
        {"StockCode": "85123A", "Description": "WHITE HANGING HEART T-LIGHT HOLDER", "Quantity": 6, "UnitPrice": 2.55},
        {"StockCode": "71053", "Description": "WHITE METAL LANTERN", "Quantity": 6, "UnitPrice": 3.39}
    ]
}

customer_doc = {
    "CustomerID": 17850,
    "Country": "United Kingdom",
    "Transactions": [
        {
            "InvoiceNo": "536365",
            "InvoiceDate": datetime.datetime(2010, 12, 1, 8, 26),
            "Items": [
                {"StockCode": "85123A", "Description": "WHITE HANGING HEART T-LIGHT HOLDER", "Quantity": 6, "UnitPrice": 2.55},
                {"StockCode": "71053", "Description": "WHITE METAL LANTERN", "Quantity": 6, "UnitPrice": 3.39}
            ]
        }
    ]
}

try:
    transactions_coll.insert_one(transaction_doc)
    customers_coll.insert_one(customer_doc)
    print("✅ Documents inserted successfully")
except errors.PyMongoError as e:
    print("❌ Insert failed:", e)

print("Transaction-centric doc:", transactions_coll.find_one({"InvoiceNo": "536365"}))
print("Customer-centric doc:", customers_coll.find_one({"CustomerID": 17850}))
