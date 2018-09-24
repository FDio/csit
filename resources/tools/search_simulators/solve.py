def solve(A, b):
    """Solve a system of linear equations. Inputs are edited."""
    n = len(b)
#    print "n", n
    for i in range(n):
        c = 1.0 / A[i][i]
        A[i][i] = 1.0
        for j in range(i + 1, n):
            A[i][j] *= c
        b[i] *= c
        for k in range(i + 1, n):
            c = A[k][i]
            A[k][i] = 0.0
            for j in range(i + 1, n):
                A[k][j] -= c * A[i][j]
            b[k] -= c * b[i]
    for i in range(n - 1, -1, -1):
        for k in range(i):
            c = A[k][i]
            A[k][i] = 0.0
            b[k] -= c * b[i]
    return b
