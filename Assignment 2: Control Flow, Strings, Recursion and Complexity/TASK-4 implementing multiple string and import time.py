import time

items = [f"Item{i}:Rs{i % 50}" for i in range(200_000)]


def build_plus(parts):
    text = ""
    for p in parts:
        text += p + ";"
    return text


def build_join(parts):
    # TODO 1 (done): build the same text using a single str.join() call
    return ";".join(parts) + ";"


start = time.perf_counter(); a = build_plus(items); t_plus = time.perf_counter() - start
start = time.perf_counter(); b = build_join(items); t_join = time.perf_counter() - start
print("same text:", a == b, "| length:", len(b))
print(f"+= time: {t_plus:.4f} s  join time: {t_join:.4f} s")
"""Q4 - three ways to build a long statement, plus StringIO, file and the 'defeated optimisation' case."""
import io
import os
import sys
import tempfile
import time


def build_plus(n):
    text = ""
    for i in range(n):
        text += f"Item{i}:Rs{i % 50}" + ";"
    return text


def build_join(n):
    parts = [f"Item{i}:Rs{i % 50}" for i in range(n)]
    return ";".join(parts) + ";"


def build_fstring_join(n):
    return "".join(f"Item{i}:Rs{i % 50};" for i in range(n))     # f-string per line, joined once


def build_stringio(n):
    buf = io.StringIO()
    for i in range(n):
        buf.write(f"Item{i}:Rs{i % 50};")
    return buf.getvalue()


def build_file(n, path):
    with open(path, "w", encoding="utf-8") as fh:
        for i in range(n):
            fh.write(f"Item{i}:Rs{i % 50};")


class Holder:
    text = ""


def build_plus_unoptimised(n):
    """+= on an attribute: CPython cannot use its in-place trick, so each step copies the whole string."""
    h = Holder()
    h.text = ""
    for i in range(n):
        h.text += f"Item{i}:Rs{i % 50}" + ";"
    return h.text


def timed(fn, *args):
    t = time.perf_counter()
    out = fn(*args)
    return time.perf_counter() - t, out


if __name__ == "__main__":
    print("Python", sys.version.split()[0])
    sizes = (1_000, 10_000, 200_000)
    tmp = os.path.join(tempfile.gettempdir(), "statement_q4.txt")
    print(f"\n{'lines':>8} | {'+= (local)':>11} {'join':>9} {'f-str+join':>11} {'StringIO':>9} {'file':>9}  (seconds, best of 3)")
    reference = {}
    for n in sizes:
        row = []
        for fn in (build_plus, build_join, build_fstring_join, build_stringio):
            best = min(timed(fn, n)[0] for _ in range(3))
            reference.setdefault(n, timed(fn, n)[1])
            assert timed(fn, n)[1] == reference[n]
            row.append(best)
        best_file = min(timed(build_file, n, tmp)[0] for _ in range(3))
        row.append(best_file)
        print(f"{n:>8} | {row[0]:>11.4f} {row[1]:>9.4f} {row[2]:>11.4f} {row[3]:>9.4f} {row[4]:>9.4f}")
    os.remove(tmp)

    print("\n+= on an attribute (optimisation defeated): seconds")
    prev = None
    for n in (1_000, 10_000, 50_000, 100_000):
        t, out = timed(build_plus_unoptimised, n)
        ratio = "" if prev is None else f"   x{t / prev[1]:.1f} time for x{n / prev[0]:.0f} lines"
        print(f"{n:>8} lines: {t:.4f} s{ratio}")
        prev = (n, t)

    print("\nMemory held at the end (bytes): final string ~", len(reference[200_000]),
          "| list of 200000 parts ~", sys.getsizeof([f'Item{i}:Rs{i % 50}' for i in range(200_000)]) +
          sum(sys.getsizeof(f'Item{i}:Rs{i % 50}') for i in range(200_000)))

    print("\nComplete-the-code program, three runs (200,000 items):")
    items = [f"Item{i}:Rs{i % 50}" for i in range(200_000)]

    def bp(parts):
        text = ""
        for p in parts:
            text += p + ";"
        return text

    def bj(parts):
        return ";".join(parts) + ";"

    tp, tj = [], []
    for run in range(3):
        s = time.perf_counter(); a = bp(items); x = time.perf_counter() - s
        s = time.perf_counter(); b = bj(items); y = time.perf_counter() - s
        tp.append(x); tj.append(y)
        print(f"  run {run + 1}: same text: {a == b} | length: {len(b)} | += {x:.4f} s  join {y:.4f} s")
    print(f"  average: += {sum(tp) / 3:.4f} s   join {sum(tj) / 3:.4f} s")