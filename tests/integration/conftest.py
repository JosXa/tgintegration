# @pytest.yield_fixture(scope="session", autouse=True)
# async def test_lock(client):
#     """
#     Ensures that tests are always executed sequentially, i.e. there should always be running only one at a time.
#     """
#     await client.send_message("@TgIntegrationBuildLock")
#
#
# @dataclass
# class _LockMessage:
#     started: datetime
#     last_ping: datetime
#     agent: str
#     client_id: int
#
#     def render_html(self):
#         lines = [
#             f"Started: {self.started.utctimetuple()}",
#             f"Started: {self.last_ping.utctimetuple()}",
#             f"Agent: {self.agent}",
#             f"Client ID: {self.client_id}",
#         ]
#         return "\n".join(lines)
#
#     @classmethod
#     def parse_text(self, text: str) -> "_LockMessage":
#         return _LockMessage()
#
#
# class TelegramTestLock:
#     def __init__(self, client: Client):
#         self.client = client
#         self._locked: Optional[bool] = None
#
#         super().__init__()
#
#     async def get_or_create_lock_channel(self) -> Chat:
#         me = await self.client.get_me()
#         uid = me.id
#         title = f"Test Locks For {uid}"
#         username = title.replace(" ", "")
#
#         try:
#             return await self.client.get_chat(username)
#         except:
#             description = "Locks"  # TODO
#             channel = await self.client.create_channel(title, description=description)
#
#             await self.client.update_chat_username(channel.id, username)
#
#             return channel
#
#     async def _check(self, channel: Chat):
#         async for m in self.client.iter_history(channel.id, limit=200):
#             try:
#                 json_data = json.loads(m.text)
#             except:
#                 continue
#
#     async def acquire(self):
#         pass
#
#     def locked(self) -> bool:
#         pass
#
#     async def release(self):
#         raise NotImplementedError()  # TODO
