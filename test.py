def main():
    n = 7
    e = [[0 for col in range(n+2)] for row in range(n+2)]
    w = [[0 for col in range(n+2)] for row in range(n+2)]
    root = [[0 for col in range(n+2)] for row in range(n+2)]

    '''
    q = [0.05, 0.10, 0.05, 0.05, 0.05, 0.10]
    p = [0, 0.15, 0.10, 0.05, 0.10, 0.20]
    '''
    q = [0.06, 0.06, 0.06, 0.06, 0.05, 0.05, 0.05, 0.05]
    p = [0, 0.04, 0.06, 0.08, 0.02, 0.10, 0.12, 0.14]

    for i in range(1, n + 2):
        e[i][i-1] = q[i-1]
        w[i][i-1] = q[i-1]

    for l in range(1, n + 1):
        for i in range(1, n - l + 2):
            j = i + l - 1
            e[i][j] = 300
            w[i][j] = w[i][j - 1] + p[j] + q[j]

            for r in range(i, j + 1):
                t = e[i][r-1]+e[r+1][j]+w[i][j]
                if t < e[i][j]:
                    e[i][j] = t
                    root[i][j] = r

    print(e)
    print(w)
    print(root)


if __name__ == '__main__':
    main()
