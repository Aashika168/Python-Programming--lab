"""
Task 1 - File-Processing Design Review (complete program)
Part 1.1 : original (defective) script, kept as a function for comparison
Part 1.2 : repaired script
Part 1.3 : alternative (readlines) and read-mode benchmark
Run:  python task1_complete.py
"""
import sys
import time
import tracemalloc
from decimal import Decimal, InvalidOperation


# ---------------------------------------------------------------
# Sample data (mess_oct.txt): paise amounts, text amount, short line, blank line
# ---------------------------------------------------------------
def create_sample_file(filename="mess_oct.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("192311001,Asha,500\n")
        f.write("192311002,Ravi,800\n")
        f.write("192311003,Meena,1250.50\n")     # paise -> int() fails
        f.write("192311004,Kiran,1275.25\n")     # paise -> int() fails
        f.write("192311005,Hema,abc\n")          # text amount
        f.write("192311006,Surya\n")             # short line
        f.write("\n")                            # trailing blank line


# ---------------------------------------------------------------
# Task 1.1 - ORIGINAL script (defective, reconstructed from the diagnosis)
# ---------------------------------------------------------------
def original_script(path):
    f = open(path)                      # hard-coded path in the real script, never closed
    data = f.read()                     # whole file in memory
    total = 0
    report = ""
    for line in data.split("\n"):
        try:
            parts = line.split(",")
            total += int(parts[2])      # fails for paise
            report = report + parts[1] + str(parts[2])   # repeated +, no separator
        except:                         # bare except hides every error
            pass
    print(report)
    print("Total:", total)


# ---------------------------------------------------------------
# Task 1.2 - REPAIRED script
# ---------------------------------------------------------------
def total_mess_bills(filename):
    """Return (total, valid_records, rejected).
    rejected is a list of (line_number, raw_line, reason)."""
    total = Decimal("0")
    records, rejected = [], []
    with open(filename, encoding="utf-8") as f:          # closed automatically
        for line_no, line in enumerate(f, start=1):      # one line in memory
            line = line.strip()
            if not line:                                 # blank / trailing line
                continue
            parts = [p.strip() for p in line.split(",")]
            try:
                reg, name, amount_text = parts           # ValueError if not 3 fields
                amount = Decimal(amount_text)            # exact money, handles paise
            except ValueError:
                rejected.append((line_no, line, f"expected 3 fields, found {len(parts)}"))
            except InvalidOperation:
                rejected.append((line_no, line, f"invalid amount '{amount_text}'"))
            else:
                total += amount
                records.append((reg, name, amount))
    return total, records, rejected


def fixed_main(filename):
    try:
        total, records, rejected = total_mess_bills(filename)
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return
    except PermissionError:
        print(f"No permission to read: {filename}")
        return

    report = "\n".join(f"{reg:<10}{name:<10}{amt:>10}" for reg, name, amt in records)
    print(report)
    print("Total:", total)
    print(f"Rejected lines: {len(rejected)}")
    for line_no, text, reason in rejected:
        print(f"  line {line_no}: {text!r} -> {reason}")


# ---------------------------------------------------------------
# Task 1.3 - Alternative concept (read everything first) + benchmark
# ---------------------------------------------------------------
def total_with_readlines(filename):
    """Same logic, but the whole file is loaded first: O(file size) memory."""
    total = Decimal("0")
    with open(filename, encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines:
        parts = [p.strip() for p in line.strip().split(",")]
        if len(parts) != 3:
            continue
        try:
            total += Decimal(parts[2])
        except InvalidOperation:
            continue
    return total


def make_big_file(filename="big.txt", n=50000):
    with open(filename, "w", encoding="utf-8") as f:
        for i in range(n):
            f.write(f"{192300000 + i},Student{i},{1000 + i % 500}.50\n")


def measure(label, fn):
    tracemalloc.start()
    t = time.perf_counter()
    fn()
    elapsed = time.perf_counter() - t
    peak_kb = tracemalloc.get_traced_memory()[1] / 1024
    tracemalloc.stop()
    print(f"{label:<20}{elapsed:.4f} s   {peak_kb:>10,.1f} KB")


def benchmark(filename="big.txt"):
    def style_read():
        with open(filename, encoding="utf-8") as f:
            for _ in f.read().split("\n"):
                pass

    def style_readlines():
        with open(filename, encoding="utf-8") as f:
            for _ in f.readlines():
                pass

    def style_iterate():
        with open(filename, encoding="utf-8") as f:
            for _ in f:
                pass

    print(f"{'Style':<20}{'Time':<12}{'Peak memory':>12}")
    measure("f.read().split()", style_read)
    measure("f.readlines()", style_readlines)
    measure("for line in f", style_iterate)


# ---------------------------------------------------------------
# Main
# ---------------------------------------------------------------
if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else "mess_oct.txt"
    if len(sys.argv) == 1:
        create_sample_file(filename)

    print("=== Original script (silent, wrong) ===")
    original_script(filename)

    print("\n=== Repaired script ===")
    fixed_main(filename)

    print("\n=== readlines version total ===")
    print("Total:", total_with_readlines(filename))

    print("\n=== Benchmark: 50,000 lines ===")
    make_big_file()
    benchmark()