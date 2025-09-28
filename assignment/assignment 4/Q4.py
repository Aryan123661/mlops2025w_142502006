from pymongo import MongoClient
import datetime

client = MongoClient("mongodb://localhost:27017/?replicaSet=rs0")

db = client["RetailDB_Q4"]
transactions = db["Transactions"]

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

transactions.insert_one(transaction_doc)

print("✅ Inserted transaction into replica set cluster")
print("Stored doc:", transactions.find_one({"InvoiceNo": "536365"}))
