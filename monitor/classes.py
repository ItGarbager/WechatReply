class Message:
    def __init__(self, data, chat_type, group, user, msg, wx=None):
        self.data = data
        self.chat_type = chat_type
        self.group = group
        self.user = user
        self.msg = msg
        self.wx = wx

    def get_message(self):
        return self.msg
