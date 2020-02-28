import logging
import os
import random
import re
import time
import traceback
from typing import Optional

from tgintegration import InteractionClient, BotController, ReplyKeyboard

examples_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class DinoParkGame:
    VALUE_PATTERN = re.compile(r'^.*?\s*(\w+): ([\d ]+).*$', re.MULTILINE)
    NUMBERS_ONLY_PATTERN = re.compile(r'\b(\d[\d ]+)\b')

    def __init__(self, session_name, log_level=logging.INFO):
        self.purchase_balance = None
        self.withdrawal_balance = None
        self.diamonds = None

        self.menu = None  # type: Optional[ReplyKeyboard]
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(log_level)

        client = InteractionClient(
            session_name=session_name,
            global_action_delay=1.0,
            config_file=os.path.join(examples_dir, 'config.ini')
        )

        self.controller = BotController(
            bot_under_test='@DinoParkNextBot',
            client=client
        )

        self.controller.start()

        self._update_keyboard()
        self.update_balance()

    def _update_keyboard(self):
        start = self.controller.send_command_await("start")
        self.menu = start.reply_keyboard

    def _extract_values(self, text):
        groups = self.VALUE_PATTERN.findall(text)
        try:
            return {g[0].lower(): str_to_int(g[1]) for g in groups}
        except KeyError:
            return {}

    def update_balance(self):
        balance_menu = self.menu.press_button_await(r'.*Balance')
        values = self._extract_values(balance_menu.full_text)

        self.purchase_balance = values['purchases']
        self.withdrawal_balance = values['withdrawals']

        diamonds_menu = self.menu.press_button_await(r'.*Farm')
        diamonds_values = self._extract_values(diamonds_menu.full_text)

        self.diamonds = diamonds_values['total']

        self.logger.debug(
            "Balance updated: +{} for purchases, +{} for withdrawals, +{} diamonds.".format(
                self.purchase_balance,
                self.withdrawal_balance,
                self.diamonds
            ))

    def collect_diamonds(self):
        farm = self.menu.press_button_await(".*Farm")
        collected = farm.inline_keyboards[0].press_button_await(".*Collect diamonds")

        num_collected = self._extract_values(collected.full_text).get('collected', 0)
        self.diamonds += num_collected
        self.logger.info(
            "{} diamonds collected.".format(num_collected if num_collected > 0 else 'No'))

    def sell_diamonds(self):
        market = self.menu.press_button_await(r'.*Marketplace')
        if not market.inline_keyboards:
            self.logger.debug("No selling available at the moment.")
            return
        sold_msg = market.inline_keyboards[0].press_button_await(r'Sell diamonds.*')

        values = self.VALUE_PATTERN.findall(sold_msg.full_text)
        sold = str_to_int(values[0][1])
        plus_purchase = str_to_int(values[1][1])
        plus_withdrawal = str_to_int(values[2][1])

        self.diamonds -= sold
        self.purchase_balance += plus_purchase
        self.withdrawal_balance += plus_withdrawal

        self.logger.info(
            "{} diamonds sold, +{} to purchase balance, +{} to withdrawal balance.".format(
                sold, plus_purchase, plus_withdrawal
            ))

    def buy_dinosaurs(self):
        """
        Buy the best affordable dinosaurs
        """
        dinos = self.menu.press_button_await(
            r'.*Dinosaurs'
        ).inline_keyboards[0].press_button_await(
            r'.*Buy dinosaurs'
        )

        # Build up a list of cost per dino
        dino_cost_sequence = []
        for msg in dinos.messages:
            # "Worth" in the message has no colon (:) before the number, therefore we use a numbers
            # only pattern
            values = self.NUMBERS_ONLY_PATTERN.findall(msg.caption)
            cost = str_to_int(values[0])
            dino_cost_sequence.append(cost)

        while True:
            try:
                can_afford_id = next(x[0] for x
                                     in reversed(list(enumerate(dino_cost_sequence)))
                                     if x[1] <= self.purchase_balance)
            except StopIteration:
                self.logger.debug("Can't afford any dinosaurs.")
                # Can not afford any
                break

            bought = dinos.inline_keyboards[can_afford_id].press_button_await(r'.*Buy')
            self.logger.info("Bought dinosaur: " + bought.full_text)

    def play_lucky_number(self):
        lucky_number = self.menu.press_button_await(
            r'.*Games'
        ).reply_keyboard.press_button_await(
            r'.*Lucky number'
        )

        bet = lucky_number.reply_keyboard.press_button_await(r'.*Place your bet')

        if 'only place one bet per' in bet.full_text.lower():
            self.logger.debug("Already betted in this round")

            # Clean up
            self.controller.delete_messages(
                self.controller.peer_id,
                [bet.messages[0].message_id, bet.action_result.message_id]
            )
            return
        self.controller.send_message_await(str(random.randint(1, 30)))
        self.logger.debug("Bet placed.")


def str_to_int(value: str):
    return int(value.replace(' ', ''))


if __name__ == '__main__':
    # This example uses the configuration of `config.ini` (see examples/README)
    game = DinoParkGame(session_name='my_account', log_level=logging.DEBUG)
    while True:
        try:
            game.controller.clear_chat()
            time.sleep(1.5)
            game.buy_dinosaurs()
            game.collect_diamonds()
            game.sell_diamonds()
            game.play_lucky_number()
            time.sleep(60)
        except KeyboardInterrupt:
            break
        except:
            traceback.print_exc()

    game.controller.stop()
