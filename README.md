# WechatReply

利用 WechatPCAPI 实现的微信自动回复机器人

## 需要配合 [WeChatPCAPI](https://github.com/Manfiel/WechatPCAPI) 来实现

### 环境依赖

- windows系统
- python3.7.4 64位
- 安装 WeChatPCAPI 中的 [Wechat-V2.7.1.82.exe](https://github.com/Manfiel/WechatPCAPI/tree/master/src/Wechat-V2.7.1.82.exe)
  版本
    - 如果已安装新版微信需要覆盖安装

### 相关功能

- 已封装简单的 web 服务，支持接口调用
- 对功能及定时任务进行插件化处理
    - 插件的自行注册已实现，使用时仅需要关注业务逻辑即可
- 使用 ws 进行消息通信，分离微信登录与监听回调服务

### 依赖安装

```bash
pip install -r requirements.txt
```

### 启动及关闭服务

#### 服务启动

1. 执行微信与监听服务不进行分离的版本

> python one_click_manager.py

2. 执行微信与监听服务进行分离的版本

- 一键全部启动

> .\debug.bat 或者 .\debug.bat startup 或者 .\debug.bat startup all

- 启动单个服务

> .\debug.bat startup monitor (监听服务) 或者 .\debug.bat startup web (微信以及web服务)

#### 服务关闭

- 关闭所有服务

> .\debug.bat shutdown 或者 .\debug.bat shutdown all

- 关闭单个服务

> .\debug.bat shutdown monitor (监听服务) 或者 .\debug.bat shutdown web (微信以及web服务)

#### 服务重启

- 重启所有服务

> .\debug.bat restart 或者 .\debug.bat restart all

- 重启单个服务

> .\debug.bat restart monitor (监听服务) 或者 .\debug.bat restart web (微信以及web服务)

### 插件

默认自定义插件目录 [wechat/plugins](wechat/plugins)

当前 monitor 包中已经实现了插件自行注册，我们可以自行扩展插件

示例：

```python
# wechat/plugin/hello.py
from monitor.plugin.on import on_keyword  # 导入关键词类型事件响应器

"""
on_keyword 功能，匹配消息关键词
:param chat_type: 消息类型，chatroom|person, 不填两者都会监听
:param keywords: 消息关键词
:param _any: 与或关系，存在还是全部
:return: 
"""
# priority 为优先级，数值越低优先级越高，block 是否阻断消息继续传递，默认 True，为 False 时还需继续传递至下一层事件处理
hello = on_keyword(keywords={'hello', '你好', '早'}, priority=2, block=True)


@hello.handle()
async def hello(message):
    if message.group:
        # 两种回复方式 handle.finish 发送后直接结束当前响应器
        message.wx.send_text(message.group, '你好')
        # await hello.finish('你好')
    else:
        # message.wx.send_text(message.user, 'hello')
        await hello.finish('hello')


# wechat/plugin/weather.py
import random
from monitor.plugin.on import on_command

weather = on_command("天气", priority=2, block=True)


@weather.handle()
async def handle_first_receive(message, state):
    args = message.strip(state)
    if args:
        state["city"], state["time"] = args  # 如果用户发送了参数则直接赋值


# got 获取参数的值，prompt 为查询不到该参数时自动回复的问题
@weather.got("city", prompt="你想查询哪个城市的天气呢？")
async def handle_city(message, state):
    city = state["city"]  # got 回复会存储到当前state中
    if city not in ["上海", "北京"]:
        # reject 发送一条消息给当前交互用户并暂停事件响应器，在接收用户新的一条消息后重新运行当前处理函数
        await weather.reject("你想查询的城市暂不支持，请重新输入！")


# got 获取参数的值，prompt 为查询不到该参数时自动回复的问题
@weather.got("time", prompt="你想查询几号的？")
async def handle_time(message, state):
    time = state["time"]
    city = state["city"]
    city_weather = await get_weather(city, time)
    await weather.finish(city_weather)


async def get_weather(city: str, time: str):
    _weather = random.choice(['晴天', '雨天', '多云', '大风'])
    return f"{city}{time}的天气是{_weather}"
```

以上插件我们编写完毕后，存入插件目录，服务会在启动时自行加载

### 定时任务

当前定时任务存放于 [wechat/tasks](wechat/tasks) 目录中，当前使用 [apscheduler](https://apscheduler.readthedocs.io/en/3.x/) 实现，具体使用见文档。

### 可优化

- [ ] 文本编码，发送小表情