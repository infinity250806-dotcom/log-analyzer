import random
from datetime import datetime, timedelta

levels = ["INFO", "WARNING", "ERROR"]
messages = [
    "User logged in",
    "Database connection failed",
    "Timeout occurred",
    "File uploaded successfully",
    "High memory usage",
    "Disk space low"
]

with open("big_logs.txt", "w", encoding="utf-8") as f:
    start_time = datetime.now()

    for i in range(50000):  # 🔥 increase to 100000 if needed
        time = start_time + timedelta(seconds=i)

        log = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {random.choice(levels)} {random.choice(messages)}\n"
        f.write(log)

print("✅ Big log file created!")