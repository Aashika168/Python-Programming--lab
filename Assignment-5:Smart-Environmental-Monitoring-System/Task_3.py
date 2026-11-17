import sqlite3
import time
import statistics
import cProfile
import pstats
import io
from collections import defaultdict
import pandas as pd

# ==========================================
# B3.1 - Correctness on Small Data
# ==========================================
print("=== B3.1: Correctness on Small Data ===")

rows = [
    ("Adyar", "2026-10-01", 48.0),
    ("Guindy", "2026-10-01", 95.0),
    ("Guindy", "2026-10-03", 121.0),
    ("Adyar", "2026-10-04", 60.0),
]

# 1. Plain Python: running sum and count
acc = defaultdict(lambda: [0.0, 0])
for station, day, pm25 in rows:
    acc[(station, day)][0] += pm25
    acc[(station, day)][1] += 1
loop_result = {k: v[0] / v[1] for k, v in acc.items()}

# 2. pandas groupby
df = pd.DataFrame(rows, columns=["station", "day", "pm25"])
pandas_result = df.groupby(["station", "day"])["pm25"].mean().to_dict()

# 3. SQL GROUP BY
con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE aq(station TEXT, day TEXT, pm25 REAL)")
con.executemany("INSERT INTO aq VALUES (?, ?, ?)", rows)
sql_result = {
    (station, day): mean
    for station, day, mean in con.execute(
        "SELECT station, day, AVG(pm25) FROM aq GROUP BY station, day"
    )
}
con.close()

assert loop_result == pandas_result == sql_result
for k in sorted(loop_result):
    print(k, loop_result[k])
print("All three methods agree.")


# ==========================================
# B3.2 - Benchmark at Three Data Sizes (Median of 5 Runs)
# ==========================================
print("\n=== B3.2: Benchmark at Three Data Sizes ===")

def make_data(n):
    stations = ["Adyar", "Guindy", "Teynampet", "Velachery"]
    return [
        (stations[i % 4], f"2026-10-{(i % 28) + 1:02d}", float((i * 17) % 250))
        for i in range(n)
    ]

def loop_group(data):
    sums, counts = {}, {}
    for s, d, v in data:
        key = (s, d)
        sums[key] = sums.get(key, 0.0) + v
        counts[key] = counts.get(key, 0) + 1
    return {k: sums[k] / counts[k] for k in sums}

def pandas_group(data):
    frame = pd.DataFrame(data, columns=["station", "day", "pm25"])
    return frame.groupby(["station", "day"])["pm25"].mean()

# Warm up
warm = make_data(100)
loop_group(warm)
pandas_group(warm)

print(f"{'Rows':>10} | {'Python loop (median s)':>22} | {'pandas (median s)':>18}")
print("-" * 58)

for n in (1_000, 100_000, 1_000_000):
    data = make_data(n)
    loop_times = []
    pandas_times = []

    for _ in range(5):
        start = time.perf_counter()
        loop_group(data)
        loop_times.append(time.perf_counter() - start)

        start = time.perf_counter()
        pandas_group(data)
        pandas_times.append(time.perf_counter() - start)

    med_loop = statistics.median(loop_times)
    med_pandas = statistics.median(pandas_times)
    print(f"{n:10,d} | {med_loop:22.4f} | {med_pandas:18.4f}")


# ==========================================
# B3.3 - cProfile Summary (on 1,000,000 rows)
# ==========================================
print("\n=== B3.3: cProfile Top Functions (1,000,000 rows) ===")

large_data = make_data(1_000_000)
profiler = cProfile.Profile()
profiler.enable()
loop_group(large_data)
profiler.disable()

stream = io.StringIO()
stats = pstats.Stats(profiler, stream=stream).sort_stats("cumulative")
stats.print_stats(5)
print(stream.getvalue().strip())
```[cite: 10, 11]

This script verifies agreement across all three methods for **B3.1**[cite: 10], computes the 5-run median benchmark times for `1,000`, `100,000`, and `1,000,000` rows for **B3.2**[cite: 10, 11], and prints the top `cProfile` cumulative functions for **B3.3**[cite: 11]. Let me know when you are ready for **Task B4**.