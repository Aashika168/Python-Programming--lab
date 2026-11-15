"""
Task 6 - College Fest Registration Desk (complete program)

The design (Stage 4) is a PACKAGE, so this one program builds the whole
project on disk, runs the desk, runs the tests and the benchmark:

    fest_registration/
        main.py              run(): orchestration, duplicate set, exceptions
        test_fest.py         tests for R1-R9
        data/                CSE.txt ECE.txt MECH.txt CIVIL.txt (EEE.txt missing on purpose)
        fest/
            __init__.py
            reader.py        read_department(path) -> yields (line_no, line)
            validator.py     InvalidRegistration, valid_email, parse_registration
            writer.py        write_master, write_event_files, write_summary, write_errors

Run:  python task6_complete.py
"""
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("fest_registration")

FILES = {}

# ---------------------------------------------------------------
# fest/__init__.py
# ---------------------------------------------------------------
FILES["fest/__init__.py"] = r'''"""fest package - college fest registration desk."""
'''

# ---------------------------------------------------------------
# fest/reader.py
# ---------------------------------------------------------------
FILES["fest/reader.py"] = r'''"""reader.py - generator: one line in memory at a time."""


def read_department(path):
    """Yield (line_number, stripped_line) for every non-empty line.
    FileNotFoundError / PermissionError / UnicodeDecodeError travel to the caller."""
    with open(path, encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if line:
                yield line_no, line
'''

# ---------------------------------------------------------------
# fest/validator.py
# ---------------------------------------------------------------
FILES["fest/validator.py"] = r'''"""validator.py - validation rules using string methods only."""


class InvalidRegistration(Exception):
    """A registration line broke one of the rules."""


def valid_email(email):
    if " " in email or email.count("@") != 1:
        return False
    local, domain = email.split("@")
    if not local or "." not in domain:
        return False
    if domain.startswith(".") or domain.endswith(".") or ".." in domain:
        return False
    return True


def parse_registration(line):
    """Return a dict for a good line, else raise InvalidRegistration."""
    parts = [p.strip() for p in line.split(",")]
    if len(parts) != 5:
        raise InvalidRegistration(f"expected 5 fields, found {len(parts)}")
    reg, name, dept, email, events = parts
    if not (reg.isdigit() and len(reg) == 9):
        raise InvalidRegistration(f"bad register number '{reg}'")
    if not name:
        raise InvalidRegistration("empty name")
    if not valid_email(email):
        raise InvalidRegistration(f"invalid e-mail '{email}'")
    event_list = [e.strip().title() for e in events.split(";") if e.strip()]
    if not event_list:
        raise InvalidRegistration("no events chosen")
    return {"reg": reg, "name": name, "dept": dept.upper(),
            "email": email.lower(), "events": event_list}
'''

# ---------------------------------------------------------------
# fest/writer.py
# ---------------------------------------------------------------
FILES["fest/writer.py"] = r'''"""writer.py - all output files (every file opened with 'with')."""
from pathlib import Path


def write_master(master, out):
    with open(Path(out) / "master_list.csv", "w", encoding="utf-8") as f:
        f.write("reg_no,name,dept,email,events\n")
        for r in master:
            f.write(f"{r['reg']},{r['name']},{r['dept']},{r['email']},{';'.join(r['events'])}\n")


def write_event_files(master, out):
    """One file per event, listing exactly the accepted participants who chose it."""
    ev_dir = Path(out) / "events"
    ev_dir.mkdir(exist_ok=True)
    by_event = {}
    for r in master:
        for ev in r["events"]:
            by_event.setdefault(ev, []).append(r)
    for ev, people in by_event.items():
        fname = ev.replace(" ", "_") + ".txt"
        with open(ev_dir / fname, "w", encoding="utf-8") as f:
            f.write(f"Participants for {ev}\n")
            for p in people:
                f.write(f"{p['reg']}  {p['name']}  {p['dept']}\n")
    return by_event


def write_summary(path, stats, by_event):
    with open(path, "w", encoding="utf-8") as f:
        f.write("FEST REGISTRATION SUMMARY\n")
        for key, value in stats.items():
            f.write(f"{key}: {value}\n")
        f.write("Participants per event:\n")
        for ev in sorted(by_event):
            f.write(f"  {ev}: {len(by_event[ev])}\n")


def write_errors(path, errors):
    with open(path, "w", encoding="utf-8") as f:
        for name, line_no, reason, raw in errors:
            f.write(f"{name} | line {line_no} | {reason} | {raw}\n")
'''

# ---------------------------------------------------------------
# main.py
# ---------------------------------------------------------------
FILES["main.py"] = r'''"""main.py - orchestrates the registration desk. Never stops for a bad line or file."""
import sys
from pathlib import Path
from fest.reader import read_department
from fest.validator import parse_registration, InvalidRegistration
from fest import writer

DEPARTMENTS = ["CSE", "ECE", "EEE", "MECH", "CIVIL"]


def run(data_dir, out_dir):
    out = Path(out_dir)
    out.mkdir(exist_ok=True)
    seen, master, errors = set(), [], []
    stats = {"lines read": 0, "valid & unique": 0, "duplicates removed": 0,
             "invalid lines": 0, "missing/unreadable files": 0}
    for dept in DEPARTMENTS:
        path = Path(data_dir) / f"{dept}.txt"
        try:
            for line_no, line in read_department(path):
                stats["lines read"] += 1
                try:
                    rec = parse_registration(line)
                except InvalidRegistration as err:
                    errors.append((path.name, line_no, str(err), line))
                    stats["invalid lines"] += 1
                    continue
                if rec["reg"] in seen:                      # O(1) set lookup
                    errors.append((path.name, line_no, "duplicate register number", line))
                    stats["duplicates removed"] += 1
                    continue
                seen.add(rec["reg"])
                master.append(rec)
                stats["valid & unique"] += 1
        except FileNotFoundError:
            errors.append((path.name, 0, "department file missing", ""))
            stats["missing/unreadable files"] += 1
        except (PermissionError, UnicodeDecodeError) as err:
            errors.append((path.name, 0, f"unreadable file: {type(err).__name__}", ""))
            stats["missing/unreadable files"] += 1
    writer.write_master(master, out)
    by_event = writer.write_event_files(master, out)
    writer.write_summary(out / "summary_report.txt", stats, by_event)
    writer.write_errors(out / "error_log.txt", errors)
    return master, by_event, stats, errors


if __name__ == "__main__":
    master, by_event, stats, errors = run(sys.argv[1] if len(sys.argv) > 1 else "data", "output")
    print((Path("output") / "summary_report.txt").read_text(), end="")
    print("\n--- error_log.txt ---")
    print((Path("output") / "error_log.txt").read_text(), end="")
    print("\n--- master_list.csv ---")
    print((Path("output") / "master_list.csv").read_text(), end="")
    print("\n--- event files ---", sorted(p.name for p in (Path("output") / "events").iterdir()))
'''

# ---------------------------------------------------------------
# data/  (EEE.txt is missing on purpose)
# ---------------------------------------------------------------
FILES["data/CSE.txt"] = """192311001,Asha,CSE,asha@simats.edu,Coding;Quiz
192311002,Ravi,CSE,ravi@simats.edu,Quiz;Dance
192311003,Meena,CSE,meena@simats.edu,Coding
"""
FILES["data/ECE.txt"] = """192311004,Karthik,ECE,karthik@simats.edu,Robotics;Quiz
192311002,Ravi,ECE,ravi@simats.edu,Quiz
192311005,Esha,ECE,esha.simats.edu,Dance
192311006,Farah,ECE,farah@simats.edu
"""
FILES["data/MECH.txt"] = """192311007,Gopal,MECH,gopal@simats.edu,Robotics
192311008,Hema,MECH,hema@@simats.edu,Quiz
192311009,Imran,MECH,imran@simats.edu,Coding;Robotics
"""
FILES["data/CIVIL.txt"] = """192311010,Janani,CIVIL,janani@simats.edu,Dance;Quiz
192311011,Kavin,CIVIL,kavin@simats.edu,Coding
"""

# ---------------------------------------------------------------
# test_fest.py  (R1 - R9)
# ---------------------------------------------------------------
FILES["test_fest.py"] = r'''"""Tests for requirements R1-R9."""
import tempfile
from pathlib import Path
from fest.validator import valid_email, parse_registration, InvalidRegistration
from main import run

GOOD = "192311001,Asha,CSE,asha@simats.edu,Coding;Quiz"


def reject(line):
    try:
        parse_registration(line)
    except InvalidRegistration:
        return True
    return False


def test_R1_valid_line_accepted():
    r = parse_registration(GOOD)
    assert r["reg"] == "192311001" and r["events"] == ["Coding", "Quiz"]


def test_R3_email_rules():
    for bad in ("esha.simats.edu", "hema@@simats.edu", "a b@x.com", "@x.com",
                "a@xcom", "a@.com", "a@x..com", "a@x."):
        assert not valid_email(bad), bad
    assert valid_email("asha@simats.edu")


def test_R4_damaged_line():
    assert reject("192311001,Asha,CSE,asha@simats.edu")             # 4 fields
    assert reject(GOOD + ",extra")                                  # 6 fields


def test_R5_field_rules():
    assert reject("12345,Asha,CSE,asha@simats.edu,Quiz")            # reg not 9 digits
    assert reject("19231100A,Asha,CSE,asha@simats.edu,Quiz")        # not digits
    assert reject("192311001,,CSE,asha@simats.edu,Quiz")            # empty name
    assert reject("192311001,Asha,CSE,asha@simats.edu,;")           # no events


def test_R2_R6_R7_R8_R9_full_run():
    with tempfile.TemporaryDirectory() as d:
        data = Path(d) / "data"
        data.mkdir()
        (data / "CSE.txt").write_text(
            GOOD + "\n" + GOOD + "\n" +                             # duplicate (R2)
            "192311002,Ravi,CSE,bad-email,Quiz\n", encoding="utf-8")
        # ECE, EEE, MECH, CIVIL missing -> R6, R9 (no crash)
        master, by_event, stats, errors = run(data, Path(d) / "out")
        assert len(master) == 1                                     # R2: first kept
        assert stats["duplicates removed"] == 1
        assert stats["invalid lines"] == 1
        assert stats["missing/unreadable files"] == 4               # R6
        assert stats["valid & unique"] + stats["duplicates removed"] \
            + stats["invalid lines"] == stats["lines read"]         # R8
        ev_file = Path(d) / "out" / "events" / "Coding.txt"         # R7
        assert "192311001" in ev_file.read_text(encoding="utf-8")


def test_demo_data_numbers():
    master, by_event, stats, errors = run("data", "output_test")
    assert (stats["lines read"], stats["valid & unique"],
            stats["duplicates removed"], stats["invalid lines"]) == (12, 8, 1, 3)
    assert stats["missing/unreadable files"] == 1                   # EEE.txt


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print("PASS", name)
    print(f"{len(tests)} tests passed")
'''


# ---------------------------------------------------------------
# Build the project, run the desk, run the tests
# ---------------------------------------------------------------
def build():
    for rel, text in FILES.items():
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def run_script(script):
    out = subprocess.run([sys.executable, script], cwd=ROOT, capture_output=True, text=True)
    print(out.stdout, end="")
    if out.returncode:
        print(out.stderr)


# ---------------------------------------------------------------
# Alternative concept: list search vs set for duplicate detection
# ---------------------------------------------------------------
def duplicate_check_list(ids):
    earlier, dups = [], 0
    for reg in ids:
        if reg in earlier:             # linear search, O(n)
            dups += 1
        else:
            earlier.append(reg)
    return dups


def duplicate_check_set(ids):
    seen, dups = set(), 0
    for reg in ids:
        if reg in seen:                # hash lookup, O(1) average
            dups += 1
        else:
            seen.add(reg)
    return dups


def benchmark():
    print(f"{'n':<10}{'List search':<16}{'Set of seen numbers'}")
    for n in (8000, 16000):
        ids = [str(192000000 + i) for i in range(n)]       # all unique: worst case for the list
        t = time.perf_counter(); d1 = duplicate_check_list(ids); t1 = time.perf_counter() - t
        t = time.perf_counter(); d2 = duplicate_check_set(ids); t2 = time.perf_counter() - t
        assert d1 == d2
        print(f"{n:<10}{t1:<16.4f}{t2:.4f}")


if __name__ == "__main__":
    build()

    print("=== Stage 5: run the desk on the test data ===")
    run_script("main.py")

    print("\n=== Tests ===")
    run_script("test_fest.py")

    print("\n=== Alternative: list search vs set (duplicate check) ===")
    benchmark()