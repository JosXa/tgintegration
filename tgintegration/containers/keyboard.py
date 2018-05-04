import weakref

from pyrogram import Message

# TODO

class Keyboard:
    def __init__(self, client, inline_keyboard, reply_keyboard):
        self._client = weakref.ref(client)

        self.inline_keyboard = inline_keyboard
        self.reply_keyboard = reply_keyboard

    @classmethod
    def from_message(cls, client, message: Message) -> 'Keyboard':
        pass


    def find_button(self):
        pass


