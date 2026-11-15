"""
Task 5 - The Same Utility Organised Four Ways (complete program)

Task 5 is about FILE ORGANISATION, so this one program builds all four
organisations on disk, runs each of them and compares the results:

    data/                         sample attendance files (shared)
    a_single_script/attendance_app.py
    b_one_module/attendance_module.py + main.py
    c_three_modules/reader.py, stats.py, report.py, main.py
    d_package/attendance/__init__.py, reader.py, stats.py, report.py + main.py

Then it runs the import-timing benchmark (single script vs package).
Run:  python task5_complete.py
"""
import importlib
import os
import subprocess
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------
# The functions (written once, placed in different files below)
# ---------------------------------------------------------------
READER_FN = r'''def read_records(folder):
    """Return ({reg: [(date, status), ...]}, [damaged lines])."""
    records, errors = {}, []
    for path in sorted(Path(folder).glob("attendance_*.csv")):
        with open(path, encoding="utf-8") as f:
            for n, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                parts = line.split(",")
                if len(parts) != 3 or parts[2] not in ("P", "A"):
                    errors.append((path.name, n, line))
                    continue
                reg, date, status = parts
                records.setdefault(reg, []).append((date, status))
    return records, errors
'''

STATS_FN = r'''def percentage(statuses):
    """statuses: list of (date, status) -> attendance percentage."""
    present = sum(1 for _, s in statuses if s == "P")
    return 100 * present / len(statuses)


def below_threshold(records, limit=75.0):
    return {r: percentage(v) for r, v in sorted(records.items()) if percentage(v) < limit}


def consecutive_absent(records, n=3):
    """NEW REQUIREMENT: students absent for n or more consecutive recorded days."""
    result = []
    for reg, days in sorted(records.items()):
        run = best = 0
        for _, status in sorted(days):
            run = run + 1 if status == "A" else 0
            best = max(best, run)
        if best >= n:
            result.append((reg, best))
    return result
'''

REPORT_FN = r'''def write_percentage_report(records, filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("reg_no,percentage\n")
        for reg, v in sorted(records.items()):
            f.write(f"{reg},{percentage(v):.2f}\n")


def write_consecutive_report(rows, filename):
    """NEW REQUIREMENT: second report."""
    with open(filename, "w", encoding="utf-8") as f:
        f.write("reg_no,max_consecutive_absent\n")
        for reg, best in rows:
            f.write(f"{reg},{best}\n")
'''

PATH_IMPORT = "from pathlib import Path\n\n\n"


def write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------
# Sample data (shared by all four organisations)
# ---------------------------------------------------------------
def create_sample_data(folder="data"):
    Path(folder).mkdir(exist_ok=True)
    pattern = {
        "192311001": "PPPPP",   # 100%
        "192311002": "PAPPP",   # 80%
        "192311003": "PAAAP",   # 40%, three consecutive absences
        "192311004": "PPAPP",   # 80%
    }
    for d in range(5):
        date = f"2026-10-0{d + 1}"
        with open(Path(folder) / f"attendance_{date}.csv", "w", encoding="utf-8") as f:
            for reg, p in pattern.items():
                f.write(f"{reg},{date},{p[d]}\n")


# ---------------------------------------------------------------
# (a) One script
# ---------------------------------------------------------------
def build_a():
    code = (
        '"""(a) everything in one script."""\n'
        + PATH_IMPORT + READER_FN + "\n\n" + STATS_FN + "\n\n" + REPORT_FN
        + '''

def main():
    import os
    os.makedirs("output_a", exist_ok=True)
    records, errors = read_records("../data")
    write_percentage_report(records, "output_a/percentage.csv")
    rows = consecutive_absent(records)                                # NEW
    write_consecutive_report(rows, "output_a/absent_3_days.csv")      # NEW
    print("(a) single script | below 75%:", list(below_threshold(records)))
    print("(a) single script | absent >=3 days:", rows)


if __name__ == "__main__":
    main()
'''
    )
    write("a_single_script/attendance_app.py", code)


# ---------------------------------------------------------------
# (b) One module + main script
# ---------------------------------------------------------------
def build_b():
    write("b_one_module/attendance_module.py",
          '"""(b) the reusable functions."""\n' + PATH_IMPORT + READER_FN + "\n\n" + STATS_FN + "\n\n" + REPORT_FN)
    write("b_one_module/main.py", '''import os
import attendance_module as am

os.makedirs("output_b", exist_ok=True)
records, errors = am.read_records("../data")
am.write_percentage_report(records, "output_b/percentage.csv")
rows = am.consecutive_absent(records)                                 # NEW
am.write_consecutive_report(rows, "output_b/absent_3_days.csv")       # NEW
print("(b) one module    | below 75%:", list(am.below_threshold(records)))
print("(b) one module    | absent >=3 days:", rows)
''')


# ---------------------------------------------------------------
# (c) Three modules in one folder
# ---------------------------------------------------------------
def build_c():
    write("c_three_modules/reader.py", '"""reader.py"""\n' + PATH_IMPORT + READER_FN)
    write("c_three_modules/stats.py", '"""stats.py"""\n\n\n' + STATS_FN)
    write("c_three_modules/report.py",
          '"""report.py"""\nfrom stats import percentage\n\n\n' + REPORT_FN)
    write("c_three_modules/main.py", '''import os
import reader, stats, report


def main():
    os.makedirs("output_c", exist_ok=True)
    records, errors = reader.read_records("../data")
    report.write_percentage_report(records, "output_c/percentage.csv")
    rows = stats.consecutive_absent(records)                          # NEW
    report.write_consecutive_report(rows, "output_c/absent_3_days.csv")   # NEW
    print("(c) three modules | below 75%:", list(stats.below_threshold(records)))
    print("(c) three modules | absent >=3 days:", rows)


if __name__ == "__main__":
    main()
''')


# ---------------------------------------------------------------
# (d) Package
# ---------------------------------------------------------------
def build_d():
    write("d_package/attendance/__init__.py", '__version__ = "1.0"\n')
    write("d_package/attendance/reader.py", '"""attendance.reader"""\n' + PATH_IMPORT + READER_FN)
    write("d_package/attendance/stats.py", '"""attendance.stats"""\n\n\n' + STATS_FN)
    write("d_package/attendance/report.py",
          '"""attendance.report"""\nfrom .stats import percentage          # relative import\n\n\n' + REPORT_FN)
    write("d_package/main.py", '''import os
import attendance.stats                    # style 1: full dotted name
from attendance import reader, report      # style 2: module imported from the package
from attendance.stats import percentage    # style 3: single function imported

os.makedirs("output_d", exist_ok=True)
records, errors = reader.read_records("../data")
report.write_percentage_report(records, "output_d/percentage.csv")
rows = attendance.stats.consecutive_absent(records)                       # NEW
report.write_consecutive_report(rows, "output_d/absent_3_days.csv")       # NEW
print("(d) package       | below 75%:", list(attendance.stats.below_threshold(records)))
print("(d) package       | absent >=3 days:", rows)
print("(d) three import styles ->", attendance.stats.percentage([("d", "P"), ("e", "A")]),
      percentage([("d", "P"), ("e", "A")]), reader.__name__)
''')


# ---------------------------------------------------------------
# Run all four organisations
# ---------------------------------------------------------------
def run_all():
    jobs = [("a_single_script", "attendance_app.py"), ("b_one_module", "main.py"),
            ("c_three_modules", "main.py"), ("d_package", "main.py")]
    for folder, entry in jobs:
        out = subprocess.run([sys.executable, entry], cwd=folder, capture_output=True, text=True)
        print(out.stdout, end="")
        if out.returncode:
            print(out.stderr)


# ---------------------------------------------------------------
# Task 5.2 - files changed for the new requirement
# ---------------------------------------------------------------
def show_change_effort():
    print(f"{'Organisation':<18}{'Files changed':<16}Which files")
    print(f"{'(a) One script':<18}{1:<16}attendance_app.py")
    print(f"{'(b) One module':<18}{2:<16}attendance_module.py, main.py")
    print(f"{'(c) Three modules':<18}{3:<16}stats.py, report.py, main.py")
    print(f"{'(d) Package':<18}{3:<16}attendance/stats.py, attendance/report.py, main.py")


# ---------------------------------------------------------------
# Alternative concept: single script vs package (import timing)
# ---------------------------------------------------------------
def _fresh_import_ms(folder, statement, runs=30):
    """Average import time in a fresh interpreter (-B: no .pyc, so both compile from source)."""
    code = ("import time; t = time.perf_counter(); " + statement +
            "; print((time.perf_counter() - t) * 1000)")
    times = []
    for _ in range(runs):
        out = subprocess.run([sys.executable, "-B", "-c", code], cwd=folder,
                             capture_output=True, text=True)
        times.append(float(out.stdout))
    return sum(times) / len(times)


def benchmark_import():
    t_script = _fresh_import_ms("a_single_script", "import attendance_app")
    t_package = _fresh_import_ms(
        "d_package", "import attendance.reader, attendance.stats, attendance.report")
    print(f"Single script, first import      : {t_script:.2f} ms")
    print(f"Package (3 sub-modules), first   : {t_package:.2f} ms")

    sys.path.insert(0, str(Path("d_package").resolve()))
    importlib.import_module("attendance.stats")
    n = 100000
    t = time.perf_counter()
    for _ in range(n):
        importlib.import_module("attendance.stats")          # served from sys.modules
    t_repeat = (time.perf_counter() - t) / n * 1e6
    print(f"Package, repeat import (cached)  : {t_repeat:.3f} microseconds")

    pkg_lines = [len(p.read_text().splitlines())
                 for p in sorted(Path("d_package/attendance").glob("*.py"))]
    print("Lines in (a) attendance_app.py   :",
          len(Path("a_single_script/attendance_app.py").read_text().splitlines()))
    print("Lines per package file (d)       :", pkg_lines)


# ---------------------------------------------------------------
# Main
# ---------------------------------------------------------------
if __name__ == "__main__":
    create_sample_data()
    build_a(); build_b(); build_c(); build_d()

    print("=== Task 5.1: four organisations, same data, same results ===")
    run_all()

    print("\n=== Task 5.2: effort to add the 'absent 3 days' report ===")
    show_change_effort()

    print("\n=== Alternative: single script vs package ===")
    benchmark_import()