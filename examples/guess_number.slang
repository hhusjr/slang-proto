func println(x) {
    print(x + "\n");
}

println("欢迎来到Slang猜数游戏！");
println("输入你想玩的数字范围：（空格隔开的两个整数），系统会在区间内随机生成一的数字给你猜！");
let range_numbers = readln();

let num = rand(int(range_numbers[0]), int(range_numbers[1]));

let ok = 0;

while !ok {
    let numbers = readln();
    let cur = int(numbers[0]);

    if cur < num {
        println("小了啊！");
    } else {
        if cur > num {
            println("大了啊！");
        } else {
            println("对啦！再见！");
            let ok = 1;
        }
    }
}