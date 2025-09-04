import csv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import asyncio

# -------------------------
# Database connection setup
# -------------------------
DB_URL = "mysql+aiomysql://root:2004@localhost:3306/callify"
engine = create_async_engine(DB_URL, echo=False)

# -------------------------
# Config
# -------------------------
CHUNK_SIZE = 5000        # how many rows per DB fetch
FILE_ROW_LIMIT = 200000  # max rows per CSV
TABLE_NAME = "campaigntemplates"


async def export_campaign_templates():
    async with engine.connect() as conn:
        offset = 0
        file_count = 1
        row_count = 0

        # Open first CSV file
        csv_file = open(f"{TABLE_NAME}_{file_count}.csv", "w", newline="", encoding="utf-8")
        writer = None

        while True:
            # Fetch required columns only
            query = text(f"""
                SELECT tplid, title, subtitle, titlelong
                FROM {TABLE_NAME}
                LIMIT :limit OFFSET :offset
            """)
            result = await conn.execute(query, {"offset": offset, "limit": CHUNK_SIZE})
            rows = result.mappings().all()

            if not rows:
                break

            if writer is None:
                # Custom headers
                writer = csv.DictWriter(csv_file, fieldnames=["tplid", "title", "subtitle_titlelong"])
                writer.writeheader()

            for row in rows:
                # Merge subtitle + titlelong
                combined = f"{row['subtitle'] or ''} {row['titlelong'] or ''}".strip()

                writer.writerow({
                    "tplid": row["tplid"],
                    "title": row["title"],
                    "subtitle_titlelong": combined
                })
                row_count += 1

                # Split into new CSV if limit reached
                if row_count >= FILE_ROW_LIMIT:
                    csv_file.close()
                    file_count += 1
                    row_count = 0
                    csv_file = open(f"{TABLE_NAME}_{file_count}.csv", "w", newline="", encoding="utf-8")
                    writer = csv.DictWriter(csv_file, fieldnames=["tplid", "title", "subtitle_titlelong"])
                    writer.writeheader()

            offset += CHUNK_SIZE

        csv_file.close()
        print(f"✅ Finished exporting {TABLE_NAME}")


async def main():
    await export_campaign_templates()
    await engine.dispose()   # ✅ properly close async connections


if __name__ == "__main__":
    asyncio.run(main())
