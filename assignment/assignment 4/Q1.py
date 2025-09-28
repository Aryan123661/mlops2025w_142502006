
import pandas as pd
from sqlalchemy import (
    create_engine, MetaData, Table, Column, Integer, String, DateTime, DECIMAL,
    ForeignKey, PrimaryKeyConstraint
)

EXCEL_FILE = "Online Retail.xlsx"   
SQLITE_DB_PATH = "retail.db"
MIN_INVOICE_DETAILS = 1000

def load_clean_dataframe(filepath):
    df = pd.read_excel(filepath, engine="openpyxl")

    df.columns = [c.strip() for c in df.columns]

    df = df.dropna(subset=["CustomerID"])
    df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]
    df = df[(df["Quantity"] > 0) & (df["UnitPrice"] >= 0)]

    df["InvoiceNo"] = df["InvoiceNo"].astype(str)
    df["StockCode"] = df["StockCode"].astype(str)
    df["Description"] = df["Description"].astype(str)
    df["Quantity"] = df["Quantity"].astype(int)
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["UnitPrice"] = df["UnitPrice"].astype(float)
    df["CustomerID"] = df["CustomerID"].astype(int)
    df["Country"] = df["Country"].astype(str)

    print(f"Cleaned dataset has {len(df)} rows.")
    return df
def create_schema(engine):
    metadata = MetaData()

    customer = Table(
        "Customer", metadata,
        Column("CustomerID", Integer, primary_key=True),
        Column("Country", String(100))
    )

    product = Table(
        "Product", metadata,
        Column("StockCode", String(20), primary_key=True),
        Column("Description", String(500)),
        Column("UnitPrice", DECIMAL(10, 2))
    )

    invoice = Table(
        "Invoice", metadata,
        Column("InvoiceNo", String(20), primary_key=True),
        Column("InvoiceDate", DateTime),
        Column("CustomerID", Integer, ForeignKey("Customer.CustomerID"))
    )

    invoice_details = Table(
        "InvoiceDetails", metadata,
        Column("InvoiceNo", String(20), ForeignKey("Invoice.InvoiceNo")),
        Column("StockCode", String(20), ForeignKey("Product.StockCode")),
        Column("Quantity", Integer),
        PrimaryKeyConstraint("InvoiceNo", "StockCode")
    )

    metadata.create_all(engine)
    return {"Customer": customer, "Product": product, "Invoice": invoice, "InvoiceDetails": invoice_details}

def insert_data(engine, tables, df, min_invoice_details=1000):
    conn = engine.connect()

    customers = df[["CustomerID", "Country"]].drop_duplicates()
    conn.execute(tables["Customer"].insert().prefix_with("OR IGNORE"), customers.to_dict("records"))

    products = df[["StockCode", "Description", "UnitPrice"]].drop_duplicates()
    conn.execute(tables["Product"].insert().prefix_with("OR IGNORE"), products.to_dict("records"))

    invoice_details_count = 0
    for inv_no, group in df.groupby("InvoiceNo"):
        inv_row = {
            "InvoiceNo": inv_no,
            "InvoiceDate": group.iloc[0]["InvoiceDate"].to_pydatetime(),
            "CustomerID": int(group.iloc[0]["CustomerID"])
        }
        conn.execute(tables["Invoice"].insert().prefix_with("OR IGNORE"), inv_row)

        details = group[["InvoiceNo", "StockCode", "Quantity"]].to_dict("records")
        conn.execute(tables["InvoiceDetails"].insert().prefix_with("OR IGNORE"), details)

        invoice_details_count += len(details)
        if invoice_details_count >= min_invoice_details:
            break

    print(f"Inserted at least {invoice_details_count} invoice detail rows.")
    conn.close()

def main():
    df = load_clean_dataframe(EXCEL_FILE)

    engine = create_engine(f"sqlite:///{SQLITE_DB_PATH}", echo=False, future=True)
    tables = create_schema(engine)
    insert_data(engine, tables, df, MIN_INVOICE_DETAILS)

    print("Database ready at:", SQLITE_DB_PATH)

if __name__ == "__main__":
    main()
