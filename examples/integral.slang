func println(x) {
    print(x + "\n");
}

func calc(x) {
    let s = 1;
    let res = 0;
    loop i from 0 to n {
        let res = res + a[i] * s;
        let s = s * x;
    }
    ret res;
}

println("使用微积分【几何意义】的微积分计算器");
println("式子：y=a0x^0+a1x^1+...+anx^n，你需要在第一行输入n的值，然后第二行给出n+1个数字：a0, a1, ..., an");
let numbers = readln();
let n = int(numbers[0]);
let numbers = readln();
let a = Array;
loop i from 0 to n {
    let a[i] = floatval(numbers[i]);
}

println("请给出积分区间（空格隔开的两个数）：");
let numbers = readln();
let dx = 0.01;
let ldim = floatval(numbers[0]);
let rdim = floatval(numbers[1]);
let ans = 0;
while ldim < rdim {
    let ans = ans + calc(ldim);
    let ldim = ldim + dx;
    println(ldim);
}
println(ans);
