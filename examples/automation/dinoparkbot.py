import asyncio
import logging
import os
import random
import re
import traceback
from typing import Optional, Tuple, List

from tgintegration import InteractionClient, BotController, ReplyKeyboard

MAX_RUNS: Optional[int] = None
SESSION_NAME: str = "my_account"


async def main():
    # This example uses the configuration of `config.ini` (see examples/README)
    game = DinoParkGame(session_name=SESSION_NAME, log_level=logging.DEBUG)
    await game.start()
    for _ in range(MAX_RUNS or 999999):
        try:
            await asyncio.sleep(1.5)
            await game.buy_dinosaurs()
            await game.collect_diamonds()
            await game.sell_diamonds()
            await game.play_lucky_number()
            await game.get_bonus()
            await asyncio.sleep(90)
            await game.controller.clear_chat()
        except KeyboardInterrupt:
            break
        except:
            traceback.print_exc()

    await game.controller.client.stop()


examples_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class DinoParkGame:
    VALUE_PATTERN = re.compile(r"^.*?\s*(\w+): ([\d ]+).*$", re.MULTILINE)
    NUMBERS_ONLY_PATTERN = re.compile(r"\b(\d[\d ]+)\b")

    def __init__(self, session_name, log_level=logging.INFO):
        self.purchase_balance = None
        self.withdrawal_balance = None
        self.diamonds = None

        self.menu: Optional[ReplyKeyboard] = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(log_level)

        client = InteractionClient(
            session_name=session_name,
            global_action_delay=1.0,
            config_file=os.path.join(examples_dir, "config.ini"),
        )

        self.controller = BotController(
            peer="@DinoParkNextBot", client=client
        )

    async def start(self):
        await self.controller.initialize()
        await self._update_keyboard()
        await self.update_balance()

    async def _update_keyboard(self):
        start = await self.controller.send_command_await("start")
        self.menu = start.reply_keyboard

    def _extract_values(self, text):
        groups = self.VALUE_PATTERN.findall(text)
        try:
            return {g[0].lower(): str_to_int(g[1]) for g in groups}
        except KeyError:
            return {}

    async def update_balance(self):
        balance_menu = await self.menu.click(r".*Balance")
        values = self._extract_values(balance_menu.full_text)

        self.purchase_balance = values["purchases"]
        self.withdrawal_balance = values["withdrawals"]

        diamonds_menu = await self.menu.click(r".*Farm")
        diamonds_values = self._extract_values(diamonds_menu.full_text)

        self.diamonds = diamonds_values["total"]

        self.logger.debug(
            "Balance updated: +{} for purchases, +{} for withdrawals, +{} diamonds.".format(
                self.purchase_balance, self.withdrawal_balance, self.diamonds
            )
        )

    async def collect_diamonds(self):
        farm = await self.menu.click(".*Farm")
        collected = await farm.inline_keyboards[0].click(
            ".*Collect diamonds"
        )

        num_collected = self._extract_values(collected.full_text).get("collected", 0)
        self.diamonds += num_collected
        self.logger.info(
            "{} diamonds collected.".format(
                num_collected if num_collected > 0 else "No"
            )
        )

    async def sell_diamonds(self):
        market = await self.menu.click(r".*Marketplace")
        if not market.inline_keyboards:
            self.logger.debug("No selling available at the moment.")
            return

        await market.inline_keyboards[0].click(r"Sell diamonds.*")
        await self.update_balance()

    async def buy_dinosaurs(self):
        dinosaurs_menu = (
            await self.menu.click(r".*Dinosaurs")
        ).inline_keyboards[0]
        dinos = await dinosaurs_menu.click(r".*Buy dinosaurs")

        dino_costs: List[Tuple[int, int]] = []  # (KeyboardIndex, Cost)
        for n, msg in enumerate(dinos.messages):
            # "Worth" in the message has no colon (:) before the number, therefore we use the numbers only pattern
            values = self.NUMBERS_ONLY_PATTERN.findall(msg.caption)
            cost = str_to_int(values[0])
            dino_costs.append((n, cost))

        while True:
            affordable_dinos = (x for x in dino_costs if x[1] <= self.purchase_balance)
            most_expensive_affordable: Optional[Tuple[int, int]] = max(
                affordable_dinos, key=lambda v: v[1], default=None
            )

            if most_expensive_affordable is None:
                break

            dino_msg_index, dino_cost = most_expensive_affordable

            bought = await dinos.inline_keyboards[dino_msg_index].click(
                r".*Buy"
            )

            self.purchase_balance -= dino_cost
            self.logger.info(
                f"Bought dinosaur: {bought.full_text} -- Remaining balance: {self.purchase_balance}"
            )

    async def play_lucky_number(self):
        lucky_number = await (
            await self.menu.click(r".*Games")
        ).reply_keyboard.click(r".*Lucky number")

        bet = await lucky_number.reply_keyboard.click(r".*Place your bet")

        if "only place one bet per" in bet.full_text.lower():
            await bet.delete_all_messages()
            return
        await self.controller.send_message_await(str(random.randint(1, 30)))
        self.logger.debug("Bet placed.")

    async def get_bonus(self):
        bonus = await (
            await self.menu.click(r".*Games")
        ).reply_keyboard.click(r".*Bonus.*")
        if "already claimed" in bonus.full_text.lower():
            # Clean up
            await bonus.delete_all_messages()


def str_to_int(value: str) -> int:
    return int(value.replace(" ", ""))


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
