import csv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import asyncio

DB_URL = "mysql+aiomysql://root:2004@localhost:3306/callify"
engine = create_async_engine(DB_URL, echo=False)

CHUNK_SIZE = 5000      # how many rows per DB fetch
FILE_ROW_LIMIT = 200000  # max rows per CSV

async def export_table(table_name: str):
    async with engine.connect() as conn:
        offset = 0
        file_count = 1
        row_count = 0
        csv_file = open(f"{table_name}_{file_count}.csv", "w", newline="", encoding="utf-8")
        writer = None

        while True:
            query = text(f"SELECT * FROM {table_name} LIMIT :limit OFFSET :offset")
            result = await conn.execute(query, {"offset": offset, "limit": CHUNK_SIZE})
            rows = result.mappings().all()

            if not rows:
                break

            if writer is None:
                writer = csv.DictWriter(csv_file, fieldnames=rows[0].keys())
                writer.writeheader()

            for row in rows:
                writer.writerow(dict(row))
                row_count += 1

                if row_count >= FILE_ROW_LIMIT:
                    csv_file.close()
                    file_count += 1
                    row_count = 0
                    csv_file = open(f"{table_name}_{file_count}.csv", "w", newline="", encoding="utf-8")
                    writer = csv.DictWriter(csv_file, fieldnames=rows[0].keys())
                    writer.writeheader()

            offset += CHUNK_SIZE

        csv_file.close()
        print(f"✅ Finished exporting {table_name}")



async def main():
    await export_table("jobinvite")
    await engine.dispose()   # ✅ properly close async connections

if __name__ == "__main__":
    asyncio.run(main())