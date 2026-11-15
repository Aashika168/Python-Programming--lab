"""
Task 2 - Biometric attendance files (complete program)
2.1/2.2 : data model + file operations (process_folder)
2.3     : single-pass dictionary implementation
2.4     : trace on a 3-line file
Alt     : re-read every file for every student + benchmark
Run:  python task2_complete.py
"""
import time
from pathlib import Path

THRESHOLD = 75.0


# ---------------------------------------------------------------
# Sample data: 5 daily files, 2 damaged lines
# ---------------------------------------------------------------
def create_sample_data(folder="data"):
    folder = Path(folder)
    folder.mkdir(exist_ok=True)
    students = ["192311001", "192311002", "192311003", "192311004"]
    # P/A pattern per student for the 5 days
    pattern = {
        "192311001": "PPPPP",   # 100%
        "192311002": "PAPPP",   # 80%
        "192311003": "PAAPA",   # 40%  -> below 75
        "192311004": "PPAPP",   # 80%
    }
    for d in range(5):
        date = f"2026-10-0{d + 1}"
        with open(folder / f"attendance_{date}.csv", "w", encoding="utf-8") as f:
            for s in students:
                f.write(f"{s},{date},{pattern[s][d]}\n")
            if d == 1:
                f.write(f"192311005,{date}\n")        # damaged: missing field
            if d == 3:
                f.write(f"192311005,{date},X\n")      # damaged: wrong status
            f.write("\n")                             # blank line (ignored)


# ---------------------------------------------------------------
# Task 2.3 - implementation: single pass, dictionary of counts
# ---------------------------------------------------------------
def process_folder(folder, out_dir):
    folder, out_dir = Path(folder), Path(out_dir)
    out_dir.mkdir(exist_ok=True)
    counts = {}      # reg_no -> [present, total]
    errors = []      # (file name, line number, reason, raw line)

    for path in sorted(folder.glob("attendance_*.csv")):
        with open(path, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                parts = line.split(",")
                if len(parts) != 3:
                    errors.append((path.name, line_no, f"expected 3 fields, found {len(parts)}", line))
                    continue
                reg, date, status = (p.strip() for p in parts)
                if status not in ("P", "A"):
                    errors.append((path.name, line_no, f"invalid status '{status}'", line))
                    continue
                rec = counts.setdefault(reg, [0, 0])
                rec[1] += 1
                if status == "P":
                    rec[0] += 1

    low = []
    with open(out_dir / "attendance_report.csv", "w", encoding="utf-8") as rep:
        rep.write("reg_no,present,total,percentage\n")
        for reg in sorted(counts):
            present, total = counts[reg]
            pct = 100 * present / total
            rep.write(f"{reg},{present},{total},{pct:.2f}\n")
            if pct < THRESHOLD:
                low.append((reg, pct))

    with open(out_dir / "below_75.txt", "w", encoding="utf-8") as f:
        f.write("Students below 75% attendance\n")
        for reg, pct in low:
            f.write(f"{reg}  {pct:.2f}%\n")

    with open(out_dir / "error_log.txt", "w", encoding="utf-8") as f:
        for name, no, reason, raw in errors:
            f.write(f"{name} | line {no} | {reason} | {raw!r}\n")
    return counts, low, errors


# ---------------------------------------------------------------
# Task 2.4 - trace on a small file
# ---------------------------------------------------------------
def trace_demo():
    lines = ["101,2026-10-01,P", "102,2026-10-01", "101,2026-10-01,A"]
    counts, errors = {}, []
    print(f"{'Line':<5}{'Content':<20}{'Decision':<28}State")
    for n, line in enumerate(lines, start=1):
        parts = line.split(",")
        if len(parts) != 3:
            decision = f"{len(parts)} fields: damaged"
            errors.append(("attendance_2026-10-01.csv", n,
                           f"expected 3 fields, found {len(parts)}", line))
        else:
            reg, _, status = parts
            rec = counts.setdefault(reg, [0, 0])
            rec[1] += 1
            if status == "P":
                rec[0] += 1
            decision = f"3 fields, status {status}: valid"
        print(f"{n:<5}{line:<20}{decision:<28}counts={counts}, errors={len(errors)}")
    low = [(r, 100 * p / t) for r, (p, t) in counts.items() if 100 * p / t < THRESHOLD]
    print("end  low =", low)


# ---------------------------------------------------------------
# Alternative concept: re-read every file once per student
# ---------------------------------------------------------------
def per_student_reread(folder, students):
    result = {}
    for s in students:                                            # s times
        present = total = 0
        for path in sorted(Path(folder).glob("attendance_*.csv")):  # f times
            with open(path, encoding="utf-8") as f:
                for line in f:                                    # l times
                    parts = line.strip().split(",")
                    if len(parts) == 3 and parts[0] == s and parts[2] in ("P", "A"):
                        total += 1
                        present += parts[2] == "P"
        result[s] = [present, total]
    return result


def benchmark(s=60, f=20, l=60, folder="bench_data"):
    """s students, f files, l lines per file."""
    folder = Path(folder)
    folder.mkdir(exist_ok=True)
    students = [f"1923{i:05d}" for i in range(s)]
    for d in range(f):
        with open(folder / f"attendance_2026-10-{d + 1:02d}.csv", "w", encoding="utf-8") as fh:
            for i in range(l):
                fh.write(f"{students[i % s]},2026-10-{d + 1:02d},{'P' if (i + d) % 4 else 'A'}\n")

    t = time.perf_counter()
    single, _, _ = process_folder(folder, "bench_out")
    t_single = time.perf_counter() - t

    t = time.perf_counter()
    reread = per_student_reread(folder, students)
    t_reread = time.perf_counter() - t

    assert all(single.get(k, [0, 0]) == v for k, v in reread.items() if v[1]), "results differ"
    print(f"s={s}, f={f}, l={l}")
    print(f"Single pass with dictionary : {t_single:.4f} s")
    print(f"Re-read per student         : {t_reread:.4f} s")
    print(f"Slower by a factor of       : {t_reread / t_single:.1f}")


# ---------------------------------------------------------------
# Main
# ---------------------------------------------------------------
if __name__ == "__main__":
    create_sample_data()

    print("=== Task 2.3: process five daily files ===")
    counts, low, errors = process_folder("data", "output")
    print("== attendance_report.csv ==")
    print(open("output/attendance_report.csv").read(), end="")
    print("== below_75.txt ==")
    print(open("output/below_75.txt").read(), end="")
    print("== error_log.txt ==")
    print(open("output/error_log.txt").read(), end="")

    print("\n=== Task 2.4: trace ===")
    trace_demo()

    print("\n=== Alternative: re-read per student vs single pass ===")
    benchmark()