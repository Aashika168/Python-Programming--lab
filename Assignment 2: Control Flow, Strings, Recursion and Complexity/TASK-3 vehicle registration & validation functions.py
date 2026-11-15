def normalise(text):
    """'tn 09 ab 1234' -> 'TN09AB1234' (spaces and hyphens removed, upper case)."""
    # TODO 1 (done): remove spaces and hyphens and convert to upper case using string methods
    return text.strip().replace(" ", "").replace("-", "").upper()


def is_valid(reg):
    """Valid form: 2 letters, 2 digits, 1 or 2 letters, 4 digits (e.g. TN09AB1234)."""
    # TODO 2 (done): check the length is 9 or 10, then check each part using slicing
    # with isalpha() and isdigit()
    if len(reg) not in (9, 10):
        return False
    series_end = len(reg) - 4                 # series is reg[4:series_end] (1 or 2 letters)
    return (reg[:2].isalpha()                 # state: 2 letters
            and reg[2:4].isdigit()            # district: 2 digits
            and reg[4:series_end].isalpha()   # series: 1 or 2 letters
            and reg[series_end:].isdigit())   # number: last 4 digits


for raw in ["tn 09 ab 1234", "KA-01-M-0007", "TN9AB1234", "TN 22 1234 AB"]:
    reg = normalise(raw)
    print(f"{raw:15} -> {reg:11} {'valid' if is_valid(reg) else 'INVALID'}")
    """Q3 - extended: formatting, six predicted inputs, immutability / slicing, regex alternative, timing."""
import re
import timeit


def normalise(text):
    return text.strip().replace(" ", "").replace("-", "").upper()


def is_valid(reg):
    if len(reg) not in (9, 10):
        return False
    series_end = len(reg) - 4
    return (reg[:2].isalpha() and reg[2:4].isdigit()
            and reg[4:series_end].isalpha() and reg[series_end:].isdigit())


def format_receipt(reg):
    """'TN09AB1234' -> 'TN 09 AB 1234' (only for a valid, normalised number)."""
    if not is_valid(reg):
        raise ValueError(f"not a valid registration number: {reg!r}")
    return " ".join([reg[:2], reg[2:4], reg[4:-4], reg[-4:]])


PATTERN = re.compile(r"[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}")


def is_valid_regex(reg):
    return PATTERN.fullmatch(reg) is not None


if __name__ == "__main__":
    six = ["tn 09 ab 1234", "TN-09-AB-1234", "Tn09Ab1234", "KA-01-M-0007",
           "TN 9 AB 1234", "TN 09 AB 12X4"]
    print("Six inputs: normalise -> valid? -> receipt format")
    for raw in six:
        reg = normalise(raw)
        ok = is_valid(reg)
        shown = format_receipt(reg) if ok else "-"
        print(f"  {raw!r:18} -> {reg:11} {'valid' if ok else 'INVALID':8} {shown}")

    print("\nImmutability")
    text = "tn09ab1234"
    up = text.upper()
    print("  text =", text, "| text.upper() returns", up, "| text afterwards:", text)
    print("  id(text) == id(up)?", id(text) == id(up))
    try:
        text[0] = "T"
    except TypeError as err:
        print("  text[0] = 'T' ->", type(err).__name__ + ":", err)

    print("\nSlicing")
    for s in ("KA01M0007", "TN09AB1234"):
        print(f"  s = {s!r} (len {len(s)}):  s[-4:] = {s[-4:]!r}   s[4:-4] = {s[4:-4]!r}")

    print("\nHomoglyph check (Cyrillic K and A look like Latin K and A)")
    cyr = "\u041a\u0410-01-M-0007"
    print("  typed text      :", cyr, "| all ASCII?", cyr.isascii())
    print("  is_valid(normalise(...)) :", is_valid(normalise(cyr)), "(isalpha() accepts any script)")
    print("  is_valid_regex(normalise(...)):", is_valid_regex(normalise(cyr)), "(regex [A-Z] is ASCII only)")

    print("\nSlicing version and regex version agree on all test inputs:")
    tests = six + ["TN09AB123", "TN09ABC1234", "", "T", "TN09AB1234 "]
    same = all(is_valid(normalise(t)) == is_valid_regex(normalise(t)) for t in tests)
    print("  agree:", same)

    n = 200000
    reg = "TN09AB1234"
    t1 = timeit.timeit(lambda: is_valid(reg), number=n) / n * 1e6
    t2 = timeit.timeit(lambda: is_valid_regex(reg), number=n) / n * 1e6
    t3 = timeit.timeit(lambda: re.fullmatch(r"[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}", reg), number=n) / n * 1e6
    print(f"\nTime per validation (microseconds, {n} runs): slicing {t1:.3f} | compiled regex {t2:.3f} | re.fullmatch {t3:.3f}")