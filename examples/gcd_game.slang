func gcd(a, b) {
    if !b {
        ret a;
    }
    ret gcd(b, a % b);
}

func work() {
    print("\n求n个数的最大公约数。\n请输入n：");
    let numbers = readln();
    let n = int(numbers[0]);
    if n < 2 {
        cmd("clear");
        print("请至少输入两个整数。\n");
        work();
        ret 0;
    }

    print("\n请输入这" + n + "个数字：");
    let numbers = readln();
    let a = Array;
    loop i from 0 to n - 1 {
        let a[i] = int(numbers[i]);
    }

    let ans = gcd(a[1], a[1]);
    loop i from 2 to n - 1 {
        let ans = gcd(ans, a[i]);
    }

    print("答案是" + ans + "\n想要继续吗（Y/N）？\n");
    let inputs = readln();
    if inputs[0] == "N" {
        print("再见！\n")
        ret 0;
    }

    work();
}

work();