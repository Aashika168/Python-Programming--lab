def add_item_buggy(item, order=[]):
    order.append(item)
    return order


def add_item(item, order=None):
    # TODO 1 (done): create a new empty list when order is None, append the item, return the list
    if order is None:
        order = []
    order.append(item)
    return order


print(add_item_buggy("Tea"), add_item_buggy("Vada"))
print(add_item("Tea"), add_item("Vada"))

print(add_item_buggy.__defaults__)      # the single list created when 'def' ran
print(add_item.__defaults__)
"""Q5 - Functions, parameters and scope (canteen order system)."""

GST_RATE = 0.05
PRICES = {"Tea": 12.0, "Vada": 15.0, "Dosa": 40.0, "Coffee": 15.0}


# ---------- correct design ----------
def add_item(item, order=None, qty=1):
    """item: positional, order: default None (new list per call), qty: keyword with default."""
    if order is None:
        order = []
    order.extend([item] * qty)
    return order


def bill(order, gst_rate=GST_RATE):
    """Returns TWO values (a tuple): the total before tax and the GST."""
    subtotal = sum(PRICES[i] for i in order)
    gst = round(subtotal * gst_rate, 2)
    return subtotal, gst


# ---------- alternative 1: caller always passes the list ----------
def add_item_explicit(order, item):
    order.append(item)
    return order


# ---------- alternative 2: closure keeps one list per customer ----------
def new_customer():
    order = []                       # enclosing (nonlocal) variable

    def add(item):
        order.append(item)
        return list(order)           # return a copy so callers cannot alter the order
    return add


# ---------- scope demonstrations ----------
counter = 0                          # global


def read_global():
    return counter                   # reading a global needs no keyword


def bump_without_global():
    try:
        counter += 1                 # makes 'counter' LOCAL for the whole function -> error
    except UnboundLocalError as err:
        return f"UnboundLocalError: {err}"


def bump_with_global():
    global counter
    counter += 1
    return counter


def make_counter():
    count = 0

    def inc():
        nonlocal count               # rebind the variable of the enclosing function
        count += 1
        return count
    return inc


def local_shadow():
    counter = 99                     # a new LOCAL name, global untouched
    return counter


if __name__ == "__main__":
    print("--- default-parameter bug explained ---")
    def add_item_buggy(item, order=[]):
        order.append(item)
        return order
    print("defaults before any call:", add_item_buggy.__defaults__)
    a = add_item_buggy("Tea")
    b = add_item_buggy("Vada")
    print("a =", a, " b =", b, " a is b:", a is b)
    print("defaults after two calls :", add_item_buggy.__defaults__)

    print("\n--- three customers in sequence, independent orders ---")
    c1 = add_item("Tea")
    c1 = add_item("Vada", c1)
    c2 = add_item("Dosa", qty=2)                  # keyword argument
    c3 = add_item(order=None, item="Coffee")      # keywords in any order
    print("customer 1:", c1)
    print("customer 2:", c2)
    print("customer 3:", c3)
    print("defaults of add_item:", add_item.__defaults__)
    assert c1 == ["Tea", "Vada"] and c2 == ["Dosa", "Dosa"] and c3 == ["Coffee"]

    print("\n--- returning more than one value ---")
    total, gst = bill(c1)
    print(f"customer 1 total = {total}, GST = {gst}, payable = {total + gst}")
    print("raw return value:", bill(c1), type(bill(c1)).__name__)

    print("\n--- scope: local / global / nonlocal ---")
    print("read_global():", read_global())
    print("bump_without_global():", bump_without_global())
    print("bump_with_global():", bump_with_global(), "| global counter now", counter)
    print("local_shadow():", local_shadow(), "| global counter still", counter)
    inc = make_counter()
    print("nonlocal counter:", inc(), inc(), inc())

    print("\n--- alternatives ---")
    o = []
    add_item_explicit(o, "Tea"); add_item_explicit(o, "Vada")
    print("explicit list    :", o)
    cust_a, cust_b = new_customer(), new_customer()
    cust_a("Tea"); cust_b("Dosa")
    print("closure customer A:", cust_a("Vada"), "| customer B:", cust_b("Coffee"))