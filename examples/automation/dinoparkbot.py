import asyncio
import logging
import os
import random
import re
import traceback
from typing import List
from typing import Optional
from typing import Tuple

from pyrogram import Client
from pyrogram import filters as f

from tgintegration import BotController
from tgintegration import ReplyKeyboard

# This example uses the configuration of `config.ini` (see examples/README)

MAX_RUNS: int = -1  # No limit
SESSION_NAME: str = "tgintegration_examples"
examples_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def create_client(session_name: str) -> Client:
    return Client(
        session_name=session_name,
        workdir=examples_dir,
        config_file=os.path.join(examples_dir, "config.ini"),
    )


def create_game_controller(client: Client = None) -> "DinoParkGame":
    return DinoParkGame(client or create_client(SESSION_NAME), log_level=logging.INFO)


class DinoParkGame(BotController):
    BOT_NAME = "@DinoParkNextBot"
    VALUE_PATTERN = re.compile(r"^.*?\s*(\w+): ([\d ]+).*$", re.MULTILINE)
    NUMBERS_ONLY_PATTERN = re.compile(r"\b(\d[\d ]+)\b")

    def __init__(self, client, log_level=logging.INFO):
        super().__init__(client, peer=self.BOT_NAME, global_action_delay=1.0)

        self.purchase_balance = None
        self.withdrawal_balance = None
        self.diamonds = None

        self.menu: Optional[ReplyKeyboard] = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(log_level)

    async def perform_full_run(self):
        await self.start()
        await self.buy_dinosaurs()
        await self.collect_diamonds()
        await self.sell_diamonds()
        await self.play_lucky_number()
        await self.get_bonus()

    async def start(self):
        await self.initialize()
        await self.reset()
        await self.update_balance()

    async def reset(self):
        async with self.collect(f.regex(r"Welcome")) as start:
            await self.send_command("start")
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
        await self.reset()
        farm = await self.menu.click(".*Farm")
        collected = await farm.inline_keyboards[0].click(".*Collect diamonds")

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

    async def buy_dinosaurs(self, limit: int = 5):
        dinosaurs_menu = (await self.menu.click(r".*Dinosaurs")).inline_keyboards[0]
        dinos = await dinosaurs_menu.click(r".*Buy dinosaurs")

        dino_costs: List[Tuple[int, int]] = []  # (KeyboardIndex, Cost)
        for n, msg in enumerate(dinos.messages):
            # "Worth" in the message has no colon (:) before the number, therefore we use the numbers only pattern
            values = self.NUMBERS_ONLY_PATTERN.findall(msg.caption)
            cost = str_to_int(values[0])
            dino_costs.append((n, cost))

        num_bought = 0
        while num_bought < limit:
            affordable_dinos = (x for x in dino_costs if x[1] <= self.purchase_balance)
            most_expensive_affordable: Optional[Tuple[int, int]] = max(
                affordable_dinos, key=lambda v: v[1], default=None
            )

            if most_expensive_affordable is None:
                break

            dino_msg_index, dino_cost = most_expensive_affordable

            bought = await dinos.inline_keyboards[dino_msg_index].click(r".*Buy")

            self.purchase_balance -= dino_cost
            self.logger.info(
                f"Bought dinosaur: {bought.full_text} -- Remaining balance: {self.purchase_balance}"
            )
            num_bought += 1

    async def play_lucky_number(self):
        games = await self.menu.click(r".*Games")
        lucky_number = await games.reply_keyboard.click(r".*Lucky number")
        bet = await lucky_number.reply_keyboard.click(r".*Place your bet")

        if "only place one bet per" in bet.full_text.lower():
            await bet.delete_all_messages()
            return

        await self.client.send_message(self.peer_id, str(random.randint(1, 30)))
        self.logger.debug("Bet placed.")

    async def get_bonus(self):
        await self.reset()
        menu = await self.menu.click(r".*Games")
        bonus = await menu.reply_keyboard.click(r".*Bonus.*")

        if "already claimed" in bonus.full_text.lower():
            # Clean up
            await bonus.delete_all_messages()


def str_to_int(value: str) -> int:
    return int(value.replace(" ", ""))


async def main():
    game = create_game_controller()
    await game.start()

    runs = 0
    while True:
        try:
            await asyncio.sleep(1.5)
            await game.perform_full_run()
            await asyncio.sleep(60)
            await game.clear_chat()
        except KeyboardInterrupt:
            break
        except BaseException:
            traceback.print_exc()
        finally:
            runs += 1
            if 0 < MAX_RUNS <= runs:
                break


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
