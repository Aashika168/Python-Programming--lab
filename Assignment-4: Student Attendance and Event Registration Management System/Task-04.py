"""
Task 4 - File and Exception Forensics (complete program)
Defective program : buggy_save_returns / buggy_process
4.1 / 4.2         : evidence for each defect
4.3               : repaired program (with + logging)
4.4               : prevention rules (as comments)
Alternative       : manual try/finally version + open-file leak test
Run:  python task4_complete.py
"""
import logging
import os
import sys


# ---------------------------------------------------------------
# Sample data: three daily files of returned books
# ---------------------------------------------------------------
def create_sample_data(folder="days"):
    os.makedirs(folder, exist_ok=True)
    days = {
        "day1.txt": ["Operating Systems", "Compilers", "AI"],
        "day2.txt": ["Databases", "Networks"],
        "day3.txt": ["Python Programming", "Data Structures", "Algorithms"],
    }
    for name, books in days.items():
        with open(os.path.join(folder, name), "w", encoding="utf-8") as f:
            f.write("\n".join(books))


# ---------------------------------------------------------------
# DEFECTIVE program (as given)
# ---------------------------------------------------------------
def buggy_save_returns(books):
    log = open("returns.log", "w")
    for b in books:
        log.write(b)
    log.close()


def buggy_process(day_file):
    try:
        books = open(day_file).read().split("\n")
        buggy_save_returns(books)
    except FileNotFoundError:
        print("missing")


# ---------------------------------------------------------------
# Task 4.3 - REPAIRED program
# ---------------------------------------------------------------
logging.basicConfig(filename="errors.log", level=logging.ERROR,
                    format="%(asctime)s %(levelname)s %(message)s")


def save_returns(books, log_name="returns.log"):
    with open(log_name, "a", encoding="utf-8") as log:      # append, auto-close
        for b in books:
            log.write(str(b) + "\n")                       # newline after each title


def process(day_file):
    try:
        with open(day_file, encoding="utf-8") as f:
            books = [line.strip() for line in f if line.strip()]
        save_returns(books)
    except FileNotFoundError:
        logging.error("missing day file: %s", day_file)
        print("missing:", day_file)
    except (OSError, UnicodeDecodeError, TypeError) as err:
        logging.error("failed on %s: %r", day_file, err, exc_info=True)
        print("error logged for", day_file)


# ---------------------------------------------------------------
# Alternative concept: manual open/close with try/finally
# ---------------------------------------------------------------
def save_returns_finally(books, log_name="returns.log"):
    log = open(log_name, "a", encoding="utf-8")
    try:
        for b in books:
            log.write(str(b) + "\n")
    finally:
        log.close()                 # runs even if write() raises


# ---------------------------------------------------------------
# Task 4.2 - evidence for each defect of the buggy program
# ---------------------------------------------------------------
def evidence():
    if os.path.exists("returns.log"):
        os.remove("returns.log")

    print("--- Defects 1 and 2: run process() for three days ---")
    for day in ("days/day1.txt", "days/day2.txt", "days/day3.txt"):
        buggy_process(day)
    print("returns.log contains:", repr(open("returns.log").read()))
    print("  -> only day 3 survives ('w' truncates) and titles are glued together (no newline)")

    print("\n--- Defect 3: write() fails (a book record that is not text) ---")
    try:
        buggy_save_returns(["Good book", None, "Another"])
    except TypeError as e:
        tb = sys.exc_info()[2]
        log = tb.tb_next.tb_frame.f_locals["log"]       # file object left inside the function
        print("exception escaped process():", type(e).__name__, "-", e)
        print("log.closed =", log.closed, " <- file object was never closed")
        print("buffered data lost? file now holds:", repr(open("returns.log").read()))
        log.close()

    print("\n--- Defect 4: only FileNotFoundError handled; no message saved ---")
    try:
        original = globals()["buggy_save_returns"]
        globals()["buggy_save_returns"] = lambda b: 1 / 0      # simulate another failure
        buggy_process("days/day1.txt")
    except ZeroDivisionError as e:
        print("unhandled", type(e).__name__, "crashes the program; nothing written to any error log")
    finally:
        globals()["buggy_save_returns"] = original
    os.remove("returns.log")


# ---------------------------------------------------------------
# Repaired program demonstration
# ---------------------------------------------------------------
def repaired_demo():
    if os.path.exists("returns.log"):
        os.remove("returns.log")
    open("errors.log", "w").close()         # empty it (the logging handler keeps it open)
    for day in ("days/day1.txt", "days/day2.txt", "days/day3.txt", "days/day_missing.txt"):
        process(day)
    print("returns.log contains:")
    print(open("returns.log").read(), end="")
    print("errors.log contains:")
    print(open("errors.log").read(), end="")
    logging.shutdown()


# ---------------------------------------------------------------
# Alternative: files left open after 20 failing calls (measured)
# ---------------------------------------------------------------
def leaked_files(save_fn, calls=20):
    """Call save_fn 20 times with a bad book record; count file objects left open.
    The exceptions are kept (as a logger or test framework would) so the frames,
    and the file objects inside them, stay alive."""
    kept, still_open = [], 0
    for _ in range(calls):
        try:
            save_fn(["Good book", None, "Another"], "leak_test.log")
        except TypeError as e:
            kept.append(e)
            log = e.__traceback__.tb_next.tb_frame.f_locals["log"]
            if not log.closed:
                still_open += 1
    for e in kept:                              # clean up the leaked originals
        log = e.__traceback__.tb_next.tb_frame.f_locals["log"]
        if not log.closed:
            log.close()
    if os.path.exists("leak_test.log"):
        os.remove("leak_test.log")
    return still_open


def original_with_name(books, log_name):
    log = open(log_name, "w")
    for b in books:
        log.write(b)                            # TypeError on None
    log.close()


def leak_test():
    print(f"{'Version':<32}{'Files left open after 20 failing calls'}")
    print(f"{'Original: open(); close()':<32}{leaked_files(original_with_name)}")
    print(f"{'Manual try/finally':<32}{leaked_files(save_returns_finally)}")
    print(f"{'with statement':<32}{leaked_files(save_returns)}")


# ---------------------------------------------------------------
# Task 4.4 - prevention rules
# ---------------------------------------------------------------
# Rule 1: open every file with a 'with' statement, so it is closed on every path,
#         and choose the mode deliberately ('a' for logs that grow, 'w' only when
#         replacing is intended).
# Rule 2: handle specific exceptions and always record the failure (timestamp,
#         file, reason) in an error log - never print-and-forget or pass; write
#         records with an explicit newline.


# ---------------------------------------------------------------
# Main
# ---------------------------------------------------------------
if __name__ == "__main__":
    create_sample_data()

    print("=== Task 4.2: evidence of the defects ===")
    evidence()

    print("\n=== Task 4.3: repaired program ===")
    repaired_demo()

    print("\n=== Alternative: open-file leak test ===")
    leak_test()