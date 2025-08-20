from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

DB_USER = "prod_readonly"
DB_PASSWORD = quote_plus("Read@3#4Callify!")
DB_HOST = "stage-callify-aurora-db.cluster-cvzws3bf6zm8.us-east-1.rds.amazonaws.com"
DB_NAME = "ReckSAASDBLive"

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    print("✅ Connected to ReckSAASDBLive!")
    result = conn.execute(text("SHOW TABLES;"))
    print("Tables:")
    for row in result:
        print("-", row[0])
