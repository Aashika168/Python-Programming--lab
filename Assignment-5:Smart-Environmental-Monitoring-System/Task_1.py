import csv
import sqlite3
from io import StringIO
import matplotlib
matplotlib.use("Agg")
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# B1.1 - Completed Starter Code (Cleaning & Min-Max)
# ==========================================
RAW = """station,date,pm25
Adyar,2026-10-01,48
Adyar,2026-10-02,NA
Adyar,2026-10-03,
Guindy,2026-10-01,95
Guindy,2026-10-02,-5
Guindy,2026-10-03,121
Guindy,2026-10-04,1200
"""

def load_clean(text):
    """Return (station, date, pm25) tuples for valid PM2.5 only."""
    rows = []
    reader = csv.DictReader(StringIO(text))
    required = {"station", "date", "pm25"}
    if not reader.fieldnames or not required.issubset(reader.fieldnames):
        raise ValueError("CSV must contain station, date and pm25 columns")

    for row in reader:
        raw_value = (row.get("pm25") or "").strip()
        if raw_value.upper() in ("", "NA", "N/A", "NULL"):
            continue
        try:
            pm25 = float(raw_value)
        except ValueError:
            continue
        if pm25 < 0 or pm25 > 999:
            continue
        station = (row.get("station") or "").strip()
        date = (row.get("date") or "").strip()
        if not station or not date:
            continue
        rows.append((station, date, pm25))
    return rows

def min_max(values):
    """Scale values to 0..1 and round to 3 decimal places."""
    if not values:
        return []
    low, high = min(values), max(values)
    if high == low:
        return [0.0 for _ in values]
    return [round((v - low) / (high - low), 3) for v in values]

clean = load_clean(RAW)
print("Cleaned records:", clean)
print("Min-Max scaled:", min_max([pm for _, _, pm in clean]))


# ==========================================
# B1.3 - Store and Query (SQLite Parameterised Queries)
# ==========================================
readings = [
    ("Adyar", "2026-10-01", 48.0),
    ("Guindy", "2026-10-01", 95.0),
    ("Guindy", "2026-10-03", 121.0),
    ("Adyar", "2026-10-04", 60.0),
]

con = sqlite3.connect(":memory:")
con.execute("""CREATE TABLE aq (
    station TEXT NOT NULL,
    day TEXT NOT NULL,
    pm25 REAL NOT NULL,
    UNIQUE(station, day)
)""")

con.executemany(
    "INSERT INTO aq(station, day, pm25) VALUES (?, ?, ?)",
    readings
)
con.commit()

def station_average(name):
    row = con.execute(
        "SELECT AVG(pm25) FROM aq WHERE station = ?",
        (name,)
    ).fetchone()
    return row[0]

print("Station averages (Adyar, Guindy):", station_average("Adyar"), station_average("Guindy"))
print("SQL injection test:", station_average("Adyar' OR '1'='1"))
con.close()


# ==========================================
# B1.4 - Visualise (Matplotlib Charts)
# ==========================================
sample_data = [
    ("Adyar", "2026-10-01", 9, 48.0, 29.0),
    ("Adyar", "2026-10-01", 18, 62.0, 27.5),
    ("Guindy", "2026-10-01", 9, 95.0, 30.2),
    ("Guindy", "2026-10-03", 18, 121.0, 31.0),
    ("Adyar", "2026-10-04", 9, 60.0, 28.5),
    ("Guindy", "2026-10-04", 18, 88.0, 29.8),
]
df = pd.DataFrame(sample_data, columns=["station", "date", "hour", "pm25", "temperature_c"])

# 1. Daily Mean PM2.5 Line Chart
daily = df.groupby("date")["pm25"].mean()
daily.plot(kind="line", marker="o", title="Daily Mean PM2.5")
plt.xlabel("Date")
plt.ylabel("PM2.5 (µg/m³)")
plt.tight_layout()
plt.savefig("pm25_daily_trend.png")
plt.close()

# 2. Mean PM2.5 by Station Bar Chart
station_mean = df.groupby("station")["pm25"].mean().sort_values()
station_mean.plot(kind="bar", title="Mean PM2.5 by Station")
plt.xlabel("Station")
plt.ylabel("PM2.5 (µg/m³)")
plt.tight_layout()
plt.savefig("pm25_by_station.png")
plt.close()

# 3. Temperature vs PM2.5 Scatter Plot
plt.scatter(df["temperature_c"], df["pm25"], alpha=0.6)
plt.title("Temperature vs PM2.5")
plt.xlabel("Temperature (°C)")
plt.ylabel("PM2.5 (µg/m³)")
plt.tight_layout()
plt.savefig("temperature_vs_pm25.png")
plt.close()

# 4. PM2.5 Distribution by Hour Box Plot
df.boxplot(column="pm25", by="hour")
plt.title("PM2.5 Distribution by Hour")
plt.suptitle("")
plt.xlabel("Hour of day")
plt.ylabel("PM2.5 (µg/m³)")
plt.tight_layout()
plt.savefig("pm25_by_hour.png")
plt.close()

print("All Task B1 charts saved successfully.")
```[cite: 6, 7, 8, 9]