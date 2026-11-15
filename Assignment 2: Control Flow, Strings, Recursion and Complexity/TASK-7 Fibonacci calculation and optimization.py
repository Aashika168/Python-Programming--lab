"""Q7 - Diagnose, redesign and validate: temple-step counter (from Q6).

Original  : plain recursion  ways_naive(n) = ways_naive(n-1) + ways_naive(n-2)
Redesign  : bottom-up loop that keeps only the last two values (no recursion, no cache)
Extra     : fast doubling, O(log n) big-number steps, to show the next trade-off.
"""
import sys
import time
import tracemalloc

calls = 0
additions = 0


def ways_naive(n):
    global calls, additions
    calls += 1
    if n <= 1:
        return 1
    additions += 1
    return ways_naive(n - 1) + ways_naive(n - 2)


def ways_loop(n):
    """Exploit: ways(n) depends ONLY on ways(n-1) and ways(n-2)."""
    a, b = 1, 1                          # ways(0), ways(1)
    for _ in range(n - 1):
        a, b = b, a + b
    return b if n >= 1 else 1


def fib_pair(k):
    """Return (F(k), F(k+1)) by fast doubling."""
    if k == 0:
        return 0, 1
    a, b = fib_pair(k // 2)
    c = a * (2 * b - a)
    d = a * a + b * b
    return (d, c + d) if k % 2 else (c, d)


def ways_doubling(n):
    return fib_pair(n + 1)[0]            # ways(n) = F(n+1)


def best_time(fn, n, repeat=3):
    best = None
    for _ in range(repeat):
        t = time.perf_counter()
        v = fn(n)
        dt = time.perf_counter() - t
        best = dt if best is None or dt < best else best
    return v, best


if __name__ == "__main__":
    print("A. Diagnosis of the ORIGINAL (counts of calls and additions)")
    print(f"{'n':>4} {'calls':>10} {'additions':>10} {'distinct sub-problems':>22} {'time(s)':>9}")
    prev = None
    for n in (10, 20, 25, 30, 32):
        calls = additions = 0
        v, dt = best_time(ways_naive, n, repeat=1)
        c = calls // 1
        calls = additions = 0
        ways_naive(n)
        ratio = "" if prev is None else f"  calls x{calls / prev:.1f}"
        print(f"{n:>4} {calls:>10} {additions:>10} {n + 1:>22} {dt:>9.4f}{ratio}")
        prev = calls

    print("\nE. Original vs redesigned, same inputs")
    print(f"{'n':>5} | {'naive calls':>12} {'loop additions':>15} | {'naive time':>11} {'loop time':>11} {'doubling time':>14} | same answer")
    for n in (10, 20, 25, 30, 32):
        calls = 0
        v1, t1 = best_time(ways_naive, n, repeat=1)
        v2, t2 = best_time(ways_loop, n, repeat=5)
        v3, t3 = best_time(ways_doubling, n, repeat=5)
        calls = 0
        ways_naive(n)
        print(f"{n:>5} | {calls:>12} {n - 1:>15} | {t1:>11.6f} {t2:>11.8f} {t3:>14.8f} | {v1 == v2 == v3}")
    for n in (1000, 10000, 100000):
        v2, t2 = best_time(ways_loop, n, repeat=3)
        v3, t3 = best_time(ways_doubling, n, repeat=3)
        print(f"{n:>5} | {'infeasible':>12} {n - 1:>15} | {'-':>11} {t2:>11.8f} {t3:>14.8f} | {v2 == v3}")

    print("\nCorrectness: loop = doubling = naive for n = 0..25, loop = doubling for n = 0..1999")
    assert all(ways_loop(n) == ways_naive(n) == ways_doubling(n) for n in range(0, 26))
    assert all(ways_loop(n) == ways_doubling(n) for n in range(0, 2000))
    print("  all equal")

    print("\nPeak extra memory (tracemalloc) for n = 1000")
    tracemalloc.start()
    ways_loop(1000)
    _, peak_loop = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    from functools import lru_cache

    @lru_cache(maxsize=None)
    def memo(n):
        return 1 if n <= 1 else memo(n - 1) + memo(n - 2)

    tracemalloc.start()
    for i in range(1001):          # fill the cache bottom-up: depth stays 2, no RecursionError
        memo(i)
    _, peak_memo = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"  loop            : {peak_loop} bytes")
    print(f"  memoised (cache): {peak_memo} bytes (cache holds 1001 results)")
    print(f"  plain recursion or memo(1000) called directly needs about 1000 nested calls; loop uses 1 frame")