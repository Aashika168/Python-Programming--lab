import re
import sqlite3
import time
import statistics
from collections import Counter

# ==========================================
# B4.1 - Lexicon Sentiment Scorer & Extractive Summariser
# ==========================================
print("=== B4.1: Sentiment Scoring ===")

POSITIVE = {"good", "clean", "fast", "helpful", "improved"}
NEGATIVE = {"bad", "dirty", "slow", "rude", "smoke", "broken"}
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
    value = score(text)
    return "positive" if value > 0 else "negative" if value < 0 else "neutral"

complaints = [
    "Roads are clean and the bus was fast.",
    "Smoke from the factory, air is bad.",
    "The staff were not helpful.",
    "Not bad, service improved.",
    "The road is dirty and the bus is slow.",
    "The air is good today.",
]

for item in complaints:
    print(f"{label(item):8} | {item}")


print("\n=== B4.1: Extractive Summariser ===")

STOP = {
    "the", "a", "an", "and", "or", "but", "is", "are", "was",
    "were", "to", "of", "in", "on", "for", "it", "this", "that"
}

def summarise(text, top_k=2):
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    tokenised = [
        [w.lower() for w in re.findall(r"[A-Za-z0-9]+", s) if w.lower() not in STOP]
        for s in sentences
    ]
    frequencies = Counter(w for sentence in tokenised for w in sentence)
    scores = [sum(frequencies[w] for w in words) for words in tokenised]
    chosen = sorted(range(len(sentences)), key=lambda i: scores[i], reverse=True)[:top_k]
    return " ".join(sentences[i] for i in sorted(chosen))

example = (
    "Residents report heavy smoke near the factory. "
    "The smoke causes breathing discomfort. "
    "The park was clean yesterday."
)
print(summarise(example, top_k=2))


# ==========================================
# B4.2 - Database Index Benchmark & EXPLAIN QUERY PLAN
# ==========================================
print("\n=== B4.2: Database Index Check ===")

con = sqlite3.connect(":memory:")
con.execute("""
    CREATE TABLE readings (
        reading_id INTEGER PRIMARY KEY,
        station_id INTEGER NOT NULL,
        reading_date TEXT NOT NULL,
        pm25 REAL NOT NULL
    )
""")

# Populate sample dataset (100,000 rows across 112 stations)
sample_rows = [
    ((i % 112) + 1, f"2026-10-{(i % 28) + 1:02d}", float((i * 13) % 250))
    for i in range(100_000)
]
con.executemany(
    "INSERT INTO readings(station_id, reading_date, pm25) VALUES (?, ?, ?)",
    sample_rows
)
con.commit()

query = "SELECT AVG(pm25) FROM readings WHERE station_id = ? AND reading_date = ?"
params = (42, "2026-10-15")

# Measure before index
before_times = []
for _ in range(15):
    t0 = time.perf_counter()
    con.execute(query, params).fetchone()
    before_times.append((time.perf_counter() - t0) * 1000)

plan_before = con.execute("EXPLAIN QUERY PLAN " + query, params).fetchall()

# Create composite index
con.execute("""
    CREATE INDEX idx_readings_station_day
    ON readings (station_id, reading_date)
""")

# Measure after index
after_times = []
for _ in range(15):
    t0 = time.perf_counter()
    con.execute(query, params).fetchone()
    after_times.append((time.perf_counter() - t0) * 1000)

plan_after = con.execute("EXPLAIN QUERY PLAN " + query, params).fetchall()

print(f"Median query time BEFORE index: {statistics.median(before_times):.4f} ms")
print("Query plan BEFORE index:", plan_before)
print(f"Median query time AFTER index : {statistics.median(after_times):.4f} ms")
print("Query plan AFTER index :", plan_after)

con.close()
```[cite: 12, 13]

This script runs the lexicon sentiment classifier and extractive summariser for **B4.1**[cite: 12, 13], then creates the `idx_readings_station_day` composite index and compares both `EXPLAIN QUERY PLAN` and median query latency before and after indexing for **B4.2**[cite: 13].

Let me know if you also want the Word document (`CSA0821_Assignment5.docx`) updated with your own name (`Aashika Jaithoon P`), register number (`1921260018`), or GitHub repository URL (`[https://github.com/Aashika168/Python-Programming--lab](https://github.com/Aashika168/Python-Programming--lab)`), or if you want your actual terminal outputs inserted into the tables.