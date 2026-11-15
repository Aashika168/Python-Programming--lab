"""Q1 - State Electricity Subsidy Eligibility.

Rule:
  units <= 100            -> full subsidy
  101 <= units <= 200     -> partial subsidy ONLY IF the household holds a ration card
  units > 200             -> subsidy ONLY IF a member is above 80 years of age
"""
import timeit

FULL, PARTIAL, ELDERLY, NONE = "FULL", "PARTIAL", "ELDERLY", "NONE"


def check_input(units):
    if not isinstance(units, int) or units < 0:
        raise ValueError("units must be a whole number >= 0")


# ---------- (1) separate if statements: the developer's BUGGY version ----------
def subsidy_buggy_ifs(units, card, elder):
    """No lower bound on the second rule, so households <= 100 units with a
    ration card satisfy TWO conditions and receive two subsidies."""
    check_input(units)
    result = []
    if units <= 100:
        result.append(FULL)
    if units <= 200 and card:          # BUG: should be 101 <= units <= 200
        result.append(PARTIAL)
    if units > 200 and elder:
        result.append(ELDERLY)
    return result or [NONE]


# ---------- (2) separate if statements, repaired with chained comparisons ----------
def subsidy_separate_fixed(units, card, elder):
    """Correct, but only because every condition was made mutually exclusive by hand."""
    check_input(units)
    result = []
    if 0 <= units <= 100:
        result.append(FULL)
    if 101 <= units <= 200 and card:
        result.append(PARTIAL)
    if units > 200 and elder:
        result.append(ELDERLY)
    return result or [NONE]


# ---------- (3) if-elif-else: exactly one branch can run ----------
def subsidy_elif(units, card, elder):
    check_input(units)
    if units <= 100:
        return FULL
    elif 101 <= units <= 200 and card:
        return PARTIAL
    elif units > 200 and elder:
        return ELDERLY
    else:
        return NONE


# ---------- Design decision: nested if (for comparison) ----------
def subsidy_nested(units, card, elder):
    check_input(units)
    if units <= 100:
        return FULL
    else:
        if units <= 200:
            if card:
                return PARTIAL
            else:
                return NONE
        else:
            if elder:
                return ELDERLY
            else:
                return NONE


# ---------- Alternative A: match-case (Python 3.10+) ----------
def subsidy_match(units, card, elder):
    check_input(units)
    match (units, card, elder):
        case (u, _, _) if u <= 100:
            return FULL
        case (u, True, _) if 101 <= u <= 200:
            return PARTIAL
        case (u, _, True) if u > 200:
            return ELDERLY
        case _:
            return NONE


# ---------- Alternative B: table of (upper limit, who qualifies, decision) ----------
INF = float("inf")
SLABS = [(100, "everyone", FULL), (200, "ration", PARTIAL), (INF, "elder", ELDERLY)]


def subsidy_table(units, card, elder, slabs=SLABS):
    check_input(units)
    for upper, needs, decision in slabs:        # at most k iterations
        if units <= upper:
            ok = needs == "everyone" or (needs == "ration" and card) or (needs == "elder" and elder)
            return decision if ok else NONE
    return NONE


if __name__ == "__main__":
    # eight households chosen BEFORE running: (units, ration card, member above 80)
    households = [
        (50, False, False),
        (100, True, False),    # boundary: buggy version gives two subsidies
        (101, True, False),    # boundary
        (101, False, False),   # boundary
        (200, True, False),    # boundary
        (200, False, False),   # boundary
        (201, True, False),    # boundary: ration card does not help above 200
        (201, False, True),    # boundary: elderly member
    ]
    print(f"{'units':>5} {'card':>5} {'80+':>5} | {'separate ifs (buggy)':<22} {'separate (fixed)':<17} "
          f"{'if-elif-else':<13}")
    print("-" * 75)
    for u, c, e in households:
        print(f"{u:>5} {str(c):>5} {str(e):>5} | {str(subsidy_buggy_ifs(u, c, e)):<22} "
              f"{str(subsidy_separate_fixed(u, c, e)):<17} {subsidy_elif(u, c, e):<13}")

    # exhaustive comparison over 0..400 units and all flag combinations
    bad_buggy = 0
    total = 0
    for u in range(0, 401):
        for c in (False, True):
            for e in (False, True):
                total += 1
                ref = subsidy_elif(u, c, e)
                assert subsidy_nested(u, c, e) == ref
                assert subsidy_match(u, c, e) == ref
                assert subsidy_table(u, c, e) == ref
                assert subsidy_separate_fixed(u, c, e) == [ref]
                if subsidy_buggy_ifs(u, c, e) != [ref]:
                    bad_buggy += 1
    print(f"\nChecked {total} cases: nested, match-case, table, fixed-ifs all equal if-elif-else.")
    print(f"Buggy separate-if version disagrees in {bad_buggy} of {total} cases "
          f"(households with >1 result: "
          f"{sum(len(subsidy_buggy_ifs(u, c, e)) > 1 for u in range(401) for c in (False, True) for e in (False, True))}).")

    # time per decision for k slabs (worst case: last slab)
    print("\nTime per decision (microseconds), worst-case input")
    n = 20000
    t = timeit.timeit(lambda: subsidy_elif(250, False, True), number=n) / n * 1e6
    print(f"  if-elif-else (k=3)  : {t:.3f}")
    t = timeit.timeit(lambda: subsidy_match(250, False, True), number=n) / n * 1e6
    print(f"  match-case   (k=3)  : {t:.3f}")
    for k in (3, 30, 300, 3000):
        slabs = [(10 * i, "everyone", FULL) for i in range(1, k)] + [(INF, "elder", ELDERLY)]
        t = timeit.timeit(lambda: subsidy_table(10 ** 7, False, True, slabs), number=n // 10) / (n // 10) * 1e6
        print(f"  slab table   (k={k:<4}): {t:.3f}")