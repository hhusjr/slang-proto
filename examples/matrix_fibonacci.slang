let MOD = 10000007;

func mul_mat(M1, M2, row1, col1, row2, col2) {
    if col1 - row2 {
        print("Should be m*n and n*p.\n");
        ret 0;
    }
    let M = Array;
    loop i from 1 to row1 {
        loop j from 1 to col2 {
            let M[i][j] = 0;
            loop k from 1 to col1 {
                let M[i][j] = (M[i][j] + M1[i][k] * M2[k][j]) % MOD;
            }
        }
    }
    ret M;
}

func mul_quickpower(M, row, times) {
    let unit = Array;
    if !times {
        loop i from 1 to row {
            loop j from 1 to row {
                let unit[i][j] = 0;
            }
        }
        loop i from 1 to row {
            let unit[i][i] = 1;
        }
        ret unit;
    }
    if times % 2 {
        ret mul_mat(M, mul_quickpower(M, row, times - 1), row, row, row, row);
    }
    let tmp = mul_quickpower(M, row, times / 2);
    ret mul_mat(tmp, tmp, row, row, row, row);
}

func get_fib(n) {
    let a = Array;
    let a[1][1] = 1; let a[1][2] = 1; let a[1][3] = 0;
    let a[2][1] = 0; let a[2][2] = 1; let a[2][3] = 1;
    let a[3][1] = 0; let a[3][2] = 1; let a[3][3] = 0;

    let unit = Array;
    let unit[1][1] = 2; let unit[2][1] = 1; let unit[3][1] = 1;
    let res = mul_mat(mul_quickpower(a, 3, n - 3), unit, 3, 3, 3, 1);
    ret res[1][1];
}

let idx = 1000000000000000000;
print("虽然有点慢，但是在5秒内一定能出来。斐波那契数列第" + idx + "项的值除以" + MOD + "的余数。\n");
print(get_fib(idx) + "\n");
