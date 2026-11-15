"""Q2 - OTP verification at a bank kiosk (three attempts, blank entry is not an attempt)."""
import sys

OTP = "123456"
LOCK = "LOCKED for 30 minutes"


def read_nonblank(source):
    """for + continue: skip blank entries. Returns None when the kiosk input ends."""
    for raw in source:
        if raw.strip() == "":
            continue                      # blank: skip it, do NOT count it
        return raw.strip()
    return None


# ---------- Design 1: while loop ----------
def verify_while(entries, otp=OTP, max_attempts=3):
    source = iter(entries)
    attempts = 0
    while attempts < max_attempts:
        raw = next(source, None)
        if raw is None:
            return "ABORTED (customer left)", attempts
        entry = raw.strip()
        if entry == "":
            continue                      # blank entry: back to the top, counter untouched
        attempts += 1                     # counted ONLY for a real (non-blank) entry
        if entry == otp:
            outcome = "GRANTED"
            break                         # correct OTP: leave the loop, skip the else clause
        else:
            pass                          # wrong OTP: nothing extra yet (placeholder for audit log)
    else:
        return LOCK, attempts             # loop ended normally => three wrong attempts
    return outcome, attempts


# ---------- Design 2: for loop with range(3) ----------
def verify_for(entries, otp=OTP, max_attempts=3):
    source = iter(entries)
    outcome = None
    attempt = 0
    for attempt in range(1, max_attempts + 1):
        entry = read_nonblank(source)     # 'continue' for blanks lives inside this helper
        if entry is None:
            outcome = "ABORTED (customer left)"
            attempt -= 1
            break
        if entry == otp:
            outcome = "GRANTED"
            break
        else:
            pass
    else:
        outcome = LOCK
    return outcome, attempt


# ---------- BUG demonstration: counter updated in the wrong place ----------
def verify_while_buggy(entries, otp=OTP, max_attempts=3):
    source = iter(entries)
    attempts = 0
    while attempts < max_attempts:
        raw = next(source, None)
        if raw is None:
            return "ABORTED (customer left)", attempts
        attempts += 1                     # BUG: counted before the blank check
        entry = raw.strip()
        if entry == "":
            continue                      # blank entry has already used up an attempt
        if entry == otp:
            return "GRANTED", attempts
    return LOCK, attempts


# ---------- Changed condition: two extra attempts after a correct security answer ----------
def verify_with_security(entries, security_ok, otp=OTP):
    source = iter(entries)
    attempts, limit, extended = 0, 3, False
    while attempts < limit:               # 'limit' can change while looping - range(3) cannot
        raw = next(source, None)
        if raw is None:
            return "ABORTED (customer left)", attempts
        entry = raw.strip()
        if entry == "":
            continue
        attempts += 1
        if entry == otp:
            return "GRANTED", attempts
        if attempts == limit and not extended:
            if security_ok():             # asked only once, after the 3rd wrong attempt
                limit += 2
                extended = True
    return LOCK, attempts


# ---------- Alternative concept: recursion ----------
def verify_rec(source, otp=OTP, attempt=1, max_attempts=3):
    if attempt > max_attempts:
        return LOCK, max_attempts
    entry = read_nonblank(source)
    if entry is None:
        return "ABORTED (customer left)", attempt - 1
    if entry == otp:
        return "GRANTED", attempt
    return verify_rec(source, otp, attempt + 1, max_attempts)


if __name__ == "__main__":
    scenarios = {
        "S1 correct at once": ["123456"],
        "S2 blanks then correct on 3rd": ["", "111111", "", "222222", "123456"],
        "S3 three wrong": ["1", "2", "3"],
        "S4 blanks + three wrong": ["", "", "", "1", "2", "3"],
        "S5 two wrong then correct": ["1", "2", "123456"],
    }
    print(f"{'scenario':<32}{'while':<28}{'for':<28}{'recursive':<28}{'buggy counter'}")
    for name, entries in scenarios.items():
        w = verify_while(entries)
        f = verify_for(entries)
        r = verify_rec(iter(entries))
        b = verify_while_buggy(entries)
        print(f"{name:<32}{str(w):<28}{str(f):<28}{str(r):<28}{b}")

    print("\nChanged condition (two extra attempts after a correct security answer):")
    three_wrong_then_ok = ["1", "2", "3", "4", "123456"]
    print("  security answer correct, OTP on 5th try :", verify_with_security(three_wrong_then_ok, lambda: True))
    print("  security answer wrong,   same entries    :", verify_with_security(three_wrong_then_ok, lambda: False))
    print("  security correct, five wrong             :", verify_with_security(["1", "2", "3", "4", "5"], lambda: True))
    print("  plain 3-attempt rule, same entries       :", verify_while(three_wrong_then_ok))

    print("\nStack space: all inputs wrong, a attempts allowed")
    print("  recursion limit =", sys.getrecursionlimit())
    for a in (500, 5000):
        wrong = ["0"] * a
        try:
            res = verify_rec(iter(wrong), max_attempts=a)
            print(f"  recursive a={a:<5}: {res}")
        except RecursionError:
            print(f"  recursive a={a:<5}: RecursionError (stack depth O(a) exceeded the limit)")
        print(f"  while     a={a:<5}: {verify_while(wrong, max_attempts=a)}")