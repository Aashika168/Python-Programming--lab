import csv
import os
import sqlite3

# ==========================================
# B2.1 - File-Format Failures & Validation
# ==========================================
def read_station_csv(path):
    try:
        with open(path, "r", newline="", encoding="utf-8-sig") as f:
            sample = f.read(2048)
            if not sample.strip():
                raise ValueError("File is empty")
            f.seek(0)
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
            except csv.Error:
                dialect = csv.excel
            reader = csv.DictReader(f, dialect=dialect)
            required = {"station", "date", "pm25"}
            if not reader.fieldnames or not required.issubset(reader.fieldnames):
                raise ValueError("Missing required CSV columns")
            return list(reader)
    except UnicodeDecodeError as exc:
        raise ValueError("Unsupported text encoding") from exc
    except FileNotFoundError:
        raise ValueError("Input file does not exist")


print("=== B2.1: Adversarial File-Format Tests ===")

# Create temporary adversarial test files
test_files = {
    "missing_col.csv": "station,date,pm10\nAdyar,2026-10-01,80\n",
    "wrong_delim.csv": "station;date;pm25\nAdyar;2026-10-01;48\n",
    "empty.csv": "",
}

for fname, content in test_files.items():
    with open(fname, "w", encoding="utf-8") as f:
        f.write(content)

# Test 1: Missing pm25 column
try:
    read_station_csv("missing_col.csv")
except ValueError as e:
    print("Missing column test -> Raised ValueError:", e)

# Test 2: Semicolon delimiter (detected cleanly by Sniffer)
rows_semicolon = read_station_csv("wrong_delim.csv")
print("Semicolon delimiter test -> Parsed rows:", rows_semicolon)

# Test 3: Empty file
try:
    read_station_csv("empty.csv")
except ValueError as e:
    print("Empty file test -> Raised ValueError:", e)

# Test 4: Different encoding (invalid UTF-8 bytes)
with open("bad_encoding.csv", "wb") as f:
    f.write(b"station,date,pm25\nAdyar\xff,2026-10-01,48\n")

try:
    read_station_csv("bad_encoding.csv")
except ValueError as e:
    print("Bad encoding test -> Raised ValueError:", e)

# Clean up temporary test files
for fname in list(test_files.keys()) + ["bad_encoding.csv"]:
    if os.path.exists(fname):
        os.remove(fname)


# ==========================================
# B2.2 - SQL Injection Test
# ==========================================
print("\n=== B2.2: SQL Injection Defence Test ===")

con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE aq (station TEXT NOT NULL, day TEXT NOT NULL, pm25 REAL NOT NULL)")
con.executemany(
    "INSERT INTO aq VALUES (?, ?, ?)",
    [("Adyar", "2026-10-01", 48.0), ("Guindy", "2026-10-01", 95.0)]
)

malicious_input = "Adyar' OR '1'='1"

# Unsafe string formatting (vulnerable)
unsafe_rows = con.execute(f"SELECT * FROM aq WHERE station = '{malicious_input}'").fetchall()
print("Unsafe query result (leaks all rows):", unsafe_rows)

# Parameterised SQL query (safe)
safe_rows = con.execute("SELECT * FROM aq WHERE station = ?", (malicious_input,)).fetchall()
print("Parameterised query result (blocked):", safe_rows)
con.close()


# ==========================================
# B2.3 - Sentiment Adversarial Tests
# ==========================================
print("\n=== B2.3: Sentiment Adversarial Tests ===")

POSITIVE = {"good", "clean", "fast", "helpful", "improved", "great"}
NEGATIVE = {"bad", "dirty", "slow", "rude", "smoke", "broken", "terrible"}
NEGATORS = {"not", "never", "no"}

def score(text):
    words = text.lower().replace(".", " ").replace(",", " ").split()
    total = 0
    previous = None
    for word in words:
        value = 1 if word in POSITIVE else -1 if word in NEGATIVE else 0
        if previous in NEGATORS:
            value *= -1
        total += value
        previous = word
    return total

def label(text):
    val = score(text)
    return "positive" if val > 0 else "negative" if val < 0 else "neutral"

adversarial_complaints = [
    ("Sarcasm", "Great, another day of smoke."),
    ("Double/window negation", "The service is not very bad."),
    ("Mixed opinion", "The roads are clean, but smoke is terrible."),
]

for case_type, text in adversarial_complaints:
    print(f"{case_type:22} | predicted={label(text):8} (score={score(text):2}) | {text}")
```[cite: 9, 10, 12]

This script automatically creates and cleans up the test CSV files for **B2.1**[cite: 9, 10], demonstrates the SQL injection defence for **B2.2**[cite: 10], and runs the sarcasm, negation, and mixed-opinion test cases for **B2.3**[cite: 10]. Let me know when you are ready for **Task B3**.