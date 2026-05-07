import os
from pymongo import MongoClient

# ---------------- CONNECT ----------------
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

db = client["logdb"]
collection = db["logs"]

# Optional: clear old data
collection.delete_many({})

print("Starting ingestion...")

# ---------------- PARSER ----------------
def parse_log(line):
    line = line.strip()

    parts = line.split(" ", 3)

    if len(parts) < 4:
        return None

    return {
        "timestamp": parts[0] + " " + parts[1],
        "level": parts[2],
        "message": parts[3]
    }

# ---------------- INGEST ----------------
logs_to_insert = []

with open("big_logs.txt", "r", encoding="utf-8") as file:
    for line in file:
        log = parse_log(line)

        if log:
            logs_to_insert.append(log)

# ---------------- BULK INSERT ----------------
if logs_to_insert:
    collection.insert_many(logs_to_insert)

print(f"Inserted {len(logs_to_insert)} logs into MongoDB!")