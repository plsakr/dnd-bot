
replies = []


class ReplyHolder:

    def __init__(self, user_id, on_reply):
        self.user_id = user_id
        self.on_reply = on_reply

    async def perform_reply(self, msg_user_id, reply):
        global replies
        if msg_user_id == self.user_id:
            await self.on_reply(reply)
            replies.remove(self)
