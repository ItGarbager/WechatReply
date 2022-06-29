from monitor.plugin.on import on_command

# priority 为优先级，数值越低优先级越高，block 是否阻断消息继续传递，默认 True，为 False 时还需继续传递至下一层事件处理
weather = on_command("天气", priority=2, block=True)


@weather.handle()
async def handle_first_receive(message, state):
    args = message.strip(state)
    print(args)
    if args:
        state["city"] = args[0]  # 如果用户发送了参数则直接赋值


@weather.got("city", prompt="你想查询哪个城市的天气呢？")
async def handle_city(message, state):
    city = state["city"]
    if city not in ["上海", "北京"]:
        await weather.reject("你想查询的城市暂不支持，请重新输入！")


@weather.got("time", prompt="你想查询几号的？")
async def handle_time(message, state):
    time = state["time"]
    city = state["city"]
    city_weather = await get_weather(city, time)
    await weather.finish(city_weather)


async def get_weather(city: str, time: str):
    return f"{city}{time}的天气是..."
