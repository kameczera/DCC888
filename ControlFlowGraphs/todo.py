from lang import *


def test_min(m, n):
    """
    Stores in the variable 'answer' the minimum of 'm' and 'n'

    Examples:
        >>> test_min(3, 4)
        3
        >>> test_min(4, 3)
        3
    """
    env = Env({"m": m, "n": n, "x": m, "zero": 0})
    m_min = Add("answer", "m", "zero")
    n_min = Add("answer", "n", "zero")
    p = Lth("p", "n", "m")
    b = Bt("p", n_min, m_min)
    p.add_next(b)
    interp(p, env)
    return env.get("answer")


def test_fib(n):
    """
    Stores in the variable 'answer' the n-th number of the Fibonacci sequence.

    Examples:
        >>> test_fib(2)
        2
        >>> test_fib(3)
        3
        >>> test_fib(6)
        13
    """
    env = Env({"c": 0, "N": n, "fib0": 0, "fib1": 1, "zero": 0, "one": 1})
    i0 = Lth("p", "c", "N")
    i2 = Add("aux", "fib1", "zero")
    i3 = Add("fib1", "aux", "fib0")
    i4 = Add("fib0", "aux", "zero")
    i5 = Add("c", "c", "one")
    i6 = Add("answer", "fib1", "zero")
    i1 = Bt("p", i2, i6)
    i0.add_next(i1)
    i2.add_next(i3)
    i3.add_next(i4)
    i4.add_next(i5)
    i5.add_next(i0)
    interp(i0, env)
    return env.get("answer")


def test_min3(x, y, z):
    """
    Stores in the variable 'answer' the minimum of 'x', 'y' and 'z'

    Examples:
        >>> test_min3(3, 4, 5)
        3
        >>> test_min3(5, 4, 3)
        3
    """
    env = Env({"x" : x, "y": y, "z": z, "zero": 0})
    x_min = Add("answer", "x", "zero")
    y_min = Add("answer", "y", "zero")
    z_min = Add("answer", "z", "zero")
    prev_min = Add("answer", "answer", "zero") 

    start = Lth("p", "x", "y")
    branch1 = Bt("p", x_min, y_min)
    cmp1 = Lth("p", "answer", "z")
    branch2 = Bt("p", prev_min, z_min)

    start.add_next(branch1)
    x_min.add_next(cmp1)
    y_min.add_next(cmp1)
    cmp1.add_next(branch2)
    
    interp(start, env)

    return env.get("answer")


def test_div(m, n):
    """
    Stores in the variable 'answer' the integer division of 'm' and 'n'.

    Examples:
        >>> test_div(30, 4)
        7
        >>> test_div(4, 3)
        1
        >>> test_div(1, 3)
        0
    """
    # TODO: Implement this method
    env = Env({"m": m, "n": n, "zero": 0, "n_neg": -n, "one": 1})
   
    start = Add("answer", "zero", "zero")
    finish = Add("answer", "answer", "zero")
    sub = Add("m", "m", "n_neg")
    
    cmp = Lth("p", "m", "n")
    branch1 = Bt("p", finish, sub)
    update_ans = Add("answer", "answer", "one")

    start.add_next(cmp)
    cmp.add_next(branch1)
    sub.add_next(update_ans)
    update_ans.add_next(cmp)

    interp(start, env)
    return env.get("answer")


def test_fact(n):
    """
    Stores in the variable 'answer' the factorial of 'n'.

    Examples:
        >>> test_fact(3)
        6
    """
    # TODO: Implement this method
    env = Env({"n": n, "zero": 0, "one_neg": -1, "one": 1})

    start = Add("answer", "zero", "one") 
    finish = Add("answer", "answer", "zero")
    mul = Mul("answer", "answer", "n")
    change_n = Add("n", "n", "one_neg")

    cmp = Lth("p", "zero", "n")
    branch = Bt("p", mul, finish)
    
    start.add_next(cmp)
    cmp.add_next(branch)
    mul.add_next(change_n)
    change_n.add_next(cmp)

    interp(start, env)
    return env.get("answer")
