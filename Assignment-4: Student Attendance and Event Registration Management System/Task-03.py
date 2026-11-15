"""
Task 3 - Design the Error Handling (complete program)
3.1 : failure demo (each failure provoked, real exception printed)
3.2 : custom exception InvalidRecord
3.3 : complete try / except / else / finally  (process_file)
3.4 : misuse experiment (except Exception: pass)
TODO: parse_line and summarise completed
Alt : EAFP vs LBYL benchmark
Run:  python task3_complete.py
"""
import os
import tempfile
import time
from pathlib import Path


# ---------------------------------------------------------------
# Task 3.2 - custom exception and where it is RAISED
# ---------------------------------------------------------------
class InvalidRecord(Exception):
    """Raised when a line of the attendance file is not in the expected format."""


def parse_line(line):
    """'192311001,2026-10-08,P' -> ('192311001', '2026-10-08', 'P')
    Raises InvalidRecord for a bad line."""
    parts = line.strip().split(",")
    try:
        reg, date, status = parts            # ValueError if not exactly 3 fields
    except ValueError as err:
        # raise ... from ... keeps the original cause
        raise InvalidRecord(f"expected 3 fields, found {len(parts)}") from err
    if status not in ("P", "A"):
        raise InvalidRecord(f"invalid status '{status}'")
    return reg, date, status


# ---------------------------------------------------------------
# Task 3.3 - complete try statement; InvalidRecord is HANDLED here
# ---------------------------------------------------------------
def process_file(path):
    present = absent = 0
    errors = []
    f = None
    try:
        f = open(path, encoding="utf-8")
        lines = f.readlines()
    except FileNotFoundError as err:
        raise FileNotFoundError(f"attendance file missing: {path}") from err
    except PermissionError:
        print(f"[skip] permission denied: {path}")
        return 0, 0, [(0, "permission denied")]
    except UnicodeDecodeError as err:
        print(f"[skip] wrong encoding: {path}")
        return 0, 0, [(0, f"wrong encoding: {err.reason}")]
    else:
        # runs only if the file opened and was read without exception
        if not lines:
            print(f"[warn] empty file: {path}")
        for n, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            try:
                _, _, status = parse_line(line)
            except InvalidRecord as err:
                errors.append((n, str(err)))
            else:
                if status == "P":
                    present += 1
                else:
                    absent += 1
        return present, absent, errors
    finally:
        # always runs, even after return/raise
        if f is not None:
            f.close()
            print(f"[finally] closed {Path(path).name}")


# ---------------------------------------------------------------
# Complete the Code - TODO 1 (parse_line above) and TODO 2 (summarise)
# ---------------------------------------------------------------
def summarise(path):
    present, absent, errors = 0, 0, []
    try:
        with open(path, encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                try:
                    _, _, status = parse_line(line)
                except InvalidRecord as err:
                    errors.append((line_no, str(err)))
                else:
                    if status == "P":
                        present += 1
                    else:
                        absent += 1
    except FileNotFoundError:
        errors.append((0, f"file not found: {path}"))
    return present, absent, errors


def complete_code_demo():
    data = ("192311001,2026-10-08,P\n192311002,2026-10-08,A\n"
            "192311003,2026-10-08\n192311004,2026-10-08,L\n")
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False,
                                     encoding="utf-8") as tmp:
        tmp.write(data)
    print(summarise(tmp.name))
    os.remove(tmp.name)
    print(summarise("no_such_file.csv"))     # missing-file test


# ---------------------------------------------------------------
# Task 3.1 - provoke each failure and print the real exception
# ---------------------------------------------------------------
def failure_demo():
    def show(label, fn):
        try:
            fn()
            print(f"{label:<32}no exception")
        except Exception as e:
            print(f"{label:<32}{type(e).__name__}: {e}")

    def bad_encoding():
        with open("bad_enc.csv", "wb") as f:
            f.write(b"192311001,2026-10-01,\xff\xfe\n")
        try:
            open("bad_enc.csv", encoding="utf-8").read()
        finally:
            os.remove("bad_enc.csv")

    def permission():
        with open("locked.csv", "w") as f:
            f.write("x\n")
        os.chmod("locked.csv", 0o000)
        try:
            if hasattr(os, "geteuid") and os.geteuid() == 0:   # root ignores permissions
                raise RuntimeError("cannot be triggered by the root user")
            open("locked.csv")
        finally:
            os.chmod("locked.csv", 0o600)
            os.remove("locked.csv")

    def unpack_too_few():
        reg, date, status = "1,2026-10-01".split(",")   # only 2 values

    def empty_file():
        open("empty.csv", "w").close()
        try:
            print(f"{'Empty file':<32}no exception, lines =", len(open("empty.csv").readlines()))
        finally:
            os.remove("empty.csv")

    show("Missing folder (os.listdir)", lambda: os.listdir("no_such_folder"))
    show("Missing file", lambda: open("no_such_file.csv"))
    show("Path is a folder", lambda: open("."))
    show("Wrong encoding", bad_encoding)
    show("Permission denied", permission)
    show("Too few fields (unpack)", unpack_too_few)
    show("Missing field (index)", lambda: "1,2".split(",")[2])
    show("Non-numeric value int('P')", lambda: int("P"))
    show("Wrong status (parse_line)", lambda: parse_line("1,2026-10-01,L"))
    empty_file()


# ---------------------------------------------------------------
# Task 3.4 - misuse experiment
# ---------------------------------------------------------------
LINES = ["1,2026-10-01,P", "2,2026-10-01,A", "3,2026-10-01", "4,2026-10-01,L"]


def good():
    present = absent = 0
    for line in LINES:
        try:
            _, _, s = parse_line(line)
        except InvalidRecord:
            pass
        else:
            if s == "P": present += 1
            else: absent += 1
    return present, absent


def misused():
    present = absent = 0
    for line in LINES:
        try:
            _, _, s = parse_line(line)
            if s == "P": presnt += 1          # <-- typing error: 'presnt'
            else: absent += 1
        except Exception:
            pass
    return present, absent


# ---------------------------------------------------------------
# Alternative concept: EAFP (try/except) vs LBYL (if checks)
# ---------------------------------------------------------------
def eafp(lines):
    p = a = bad = 0
    for line in lines:
        try:
            _, _, s = parse_line(line)
        except InvalidRecord:
            bad += 1
        else:
            if s == "P": p += 1
            else: a += 1
    return p, a, bad


def lbyl(lines):
    p = a = bad = 0
    for line in lines:
        parts = line.strip().split(",")
        if len(parts) == 3 and parts[2] in ("P", "A"):
            if parts[2] == "P": p += 1
            else: a += 1
        else:
            bad += 1
    return p, a, bad


def benchmark(n=200000):
    print(f"{n:,} lines")
    print(f"{'Bad lines':<14}{'EAFP (raise/catch)':<22}{'LBYL (if checks)':<20}")
    for label, every in (("Rare (0.1%)", 1000), ("Common (50%)", 2)):
        lines = [("1,2026-10-01" if i % every == 0 else "1,2026-10-01,P") for i in range(n)]
        t = time.perf_counter(); r1 = eafp(lines); t1 = time.perf_counter() - t
        t = time.perf_counter(); r2 = lbyl(lines); t2 = time.perf_counter() - t
        assert r1 == r2
        print(f"{label:<14}{t1:<22.3f}{t2:<20.3f}")


# ---------------------------------------------------------------
# Main
# ---------------------------------------------------------------
if __name__ == "__main__":
    print("=== Task 3.1: failures provoked ===")
    failure_demo()

    print("\n=== Task 3.3: process_file (try/except/else/finally) ===")
    with open("day.csv", "w", encoding="utf-8") as f:
        f.write("1,2026-10-01,P\n2,2026-10-01,A\n3,2026-10-01\n4,2026-10-01,L\n")
    print(process_file("day.csv"))
    os.remove("day.csv")
    try:
        process_file("missing.csv")
    except FileNotFoundError as err:
        print("FileNotFoundError:", err, "| cause:", type(err.__cause__).__name__)

    print("\n=== Task 3.4: misuse experiment ===")
    print("specific except   :", good())
    print("except Exception  :", misused(), "  <- silently wrong, no error shown")

    print("\n=== Complete the Code (TODO 1 and 2) ===")
    complete_code_demo()

    print("\n=== Alternative: EAFP vs LBYL ===")
    benchmark()