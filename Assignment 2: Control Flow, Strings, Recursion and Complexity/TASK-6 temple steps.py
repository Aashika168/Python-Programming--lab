"""Q6 - temple steps: call tree, correctness, growth, recursion limit, three-way comparison."""
import sys
import threading
import time
from functools import lru_cache

calls = 0


def ways_naive(n):
    global calls
    calls += 1
    if n <= 1:
        return 1
    return ways_naive(n - 1) + ways_naive(n - 2)


@lru_cache(maxsize=None)
def ways_memo(n):
    global calls
    calls += 1
    if n <= 1:
        return 1
    return ways_memo(n - 1) + ways_memo(n - 2)


def ways_loop(n):
    """Keeps only the last two values: O(n) time, O(1) extra space, no recursion."""
    prev, cur = 1, 1                     # ways(0), ways(1)
    for _ in range(n - 1):
        prev, cur = cur, prev + cur
    return cur


def call_tree(n, depth=0, lines=None):
    if lines is None:
        lines = []
    lines.append("    " * depth + f"ways({n})")
    if n > 1:
        call_tree(n - 1, depth + 1, lines)
        call_tree(n - 2, depth + 1, lines)
    return lines


def count_calls(fn, n):
    global calls
    calls = 0
    value = fn(n)
    return value, calls


if __name__ == "__main__":
    print("Call tree for n = 5 (indentation = depth):")
    tree = call_tree(5)
    print("\n".join(tree))
    print("total calls in the tree:", len(tree))
    from collections import Counter
    rep = Counter(line.strip() for line in tree)
    print("how often each sub-problem is computed:", dict(sorted(rep.items())))

    print("\nCorrectness n = 1..6   (hand-worked: 1, 2, 3, 5, 8, 13)")
    hand = [1, 2, 3, 5, 8, 13]
    for n in range(1, 7):
        ways_memo.cache_clear()
        a, b, c = ways_naive(n), ways_memo(n), ways_loop(n)
        print(f"  n={n}: hand={hand[n - 1]} naive={a} memo={b} loop={c}  {'OK' if hand[n - 1] == a == b == c else 'MISMATCH'}")

    print("\nGrowth investigation (predicted naive calls = 2*ways(n) - 1, memo calls = n + 1)")
    print(f"{'n':>4} {'predicted naive':>16} {'naive calls':>12} {'predicted memo':>15} {'memo calls':>11} {'naive time(s)':>14}")
    for n in (10, 20, 25, 30):
        ways_memo.cache_clear()
        t = time.perf_counter()
        v, nc = count_calls(ways_naive, n)
        tn = time.perf_counter() - t
        _, mc = count_calls(ways_memo, n)
        print(f"{n:>4} {2 * ways_loop(n) - 1:>16} {nc:>12} {n + 1:>15} {mc:>11} {tn:>14.4f}")

    print("\nRecursion limit:", sys.getrecursionlimit())
    ways_memo.cache_clear()
    try:
        ways_memo(1000)
        print("ways_memo(1000) with a fresh cache: worked")
    except RecursionError as err:
        print("ways_memo(1000) with a fresh cache -> RecursionError:", err)
    ways_memo.cache_clear()
    try:
        ways_memo(2000)
        print("ways_memo(2000) with a fresh cache: worked")
    except RecursionError as err:
        print("ways_memo(2000) with a fresh cache -> RecursionError:", err)

    # Option A: raise the limit (run in a thread with a bigger stack; falls back safely)
    def run_with_bigger_limit():
        sys.setrecursionlimit(5000)
        try:
            ways_memo.cache_clear()
            t = time.perf_counter()
            v = ways_memo(1000)
            out.append((v, time.perf_counter() - t))
        except BaseException as err:                 # never crash the whole program
            out.append((None, repr(err)))

    out = []
    for mb in (64, 16, 0):                           # 0 = default stack size
        try:
            threading.stack_size(mb * 1024 * 1024)
            th = threading.Thread(target=run_with_bigger_limit)
            th.start(); th.join()
            break
        except (ValueError, RuntimeError, MemoryError):
            continue                                 # this stack size is not allowed here, try smaller
    sys.setrecursionlimit(1000)
    v_memo, t_memo = out[0] if out else (None, "could not start thread")

    # Option B: loop
    t = time.perf_counter()
    v_loop = ways_loop(1000)
    t_loop = time.perf_counter() - t

    print("\nn = 1000 for all three versions")
    print(f"  naive recursion : not run - needs about 2*ways(1000)-1 = {2 * v_loop - 1:.3e} calls")
    t = time.perf_counter(); ways_naive(30); t30 = time.perf_counter() - t
    phi = (1 + 5 ** 0.5) / 2
    est = t30 * phi ** (1000 - 30)
    print(f"  naive estimate  : {t30:.3f} s at n=30, x phi^970 -> about {est:.3e} s (~{est / 3.15e7:.3e} years)")
    if v_memo is None:
        print(f"  memo (limit 5000, big thread stack): not possible on this computer ({t_memo})")
    else:
        print(f"  memo (limit 5000, big thread stack): {t_memo:.6f} s, equals loop result: {v_memo == v_loop}")
    print(f"  loop            : {t_loop:.6f} s")
    print(f"  ways(1000) has {len(str(v_loop))} digits and starts {str(v_loop)[:12]}...")