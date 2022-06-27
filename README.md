# WechatReply

利用 WechatPCAPI 实现的微信自动回复

## 需要配合 [WeChatPCAPI](https://github.com/Manfiel/WechatPCAPI) 来实现

### 环境依赖

- windows系统
- python3.7.4 64位
- 安装 WeChatPCAPI 中的 [Wechat-V2.7.1.82.exe](https://github.com/Manfiel/WechatPCAPI/tree/master/src/Wechat-V2.7.1.82.exe)
  版本
    - 如果已完成微信需要覆盖安装

### 相关功能

- 已封装简单的 web 服务，支持接口调用
- 对功能及定时任务进行插件化处理
    - 插件的自行注册已实现，使用时仅需要关注业务逻辑即可
### 启动及关闭服务
#### 服务启动
1. 执行微信与监听服务不进行分离的版本
> python one_click_manager.py
2. 执行微信与监听服务进行分离的版本
- 一键全部启动
> .\debug.bat 或者 .\debug.bat start
- 启动单个服务
> .\debug.bat start monitor (监听服务) 或者 .\debug.bat start web (微信以及web服务)
#### 服务关闭
关闭就直接杀的 python 和 wechat 的服务，若存在其他 python 应用请勿使用
- 关闭所有服务
> .\debug.bat stop
- 关闭单个服务
> .\debug.bat stop python 或者 .\debug.bat stop wechat


### 插件

当前 wechat 包中已经实现了插件自行注册，我们可以自行扩展插件

示例：

```python
# wechat/plugins/hello.py
from wechat.monitor.plugins.on import on_keyword  # 导入关键词类型事件响应器

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
        message.wx.send_text(message.group, '你好')
    else:
        message.wx.send_text(message.user, 'hello')
```

以上插件我们编写完毕后，存入插件目录，服务会在启动时自行加载

默认插件目录 [wechat/plugins/](wechat/tasks)

### 定时任务

当前定时任务存放于 [wechat/tasks/](wechat/tasks) 目录中，当前使用 [apscheduler](https://apscheduler.readthedocs.io/en/3.x/) 实现，具体使用见文档。


### 可优化
- 添加消息中间件，登录监听隔离
- 文本编码，发送小表情