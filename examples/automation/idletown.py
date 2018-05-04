import traceback

import os
from pathlib import Path

from tgintegration import IntegrationTestClient

examples_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

client = IntegrationTestClient(
    session_name='my_account',
    bot_under_test='@IdleTownBot',
    max_wait_response=15,  # Maximum time in seconds to wait for a response from the bot
    min_wait_consecutive=None,  # Do not wait for more than one message
    global_delay=2.0,  # The @IdleTownBot has a spam limit of about 1.9s
    workdir=examples_dir  # Load configuration from parent folder
)
client.start()


def ascii_chars(text):
    return ''.join(x for x in text if str.isalpha(x) or str.isdigit(x)).strip()


def get_buttons(response):
    """
    Helper function to create a dictionary for easy access to keyboard buttons
    """
    res = {ascii_chars(b).lower(): b for b in response.keyboard_buttons}
    return res


while True:
    try:
        # Setup
        # client.clear_chat()
        start = client.send_command_await("start")

        # Extract keyboard buttons of /start response
        main_buttons = get_buttons(start)

        # Get World Exp if possible
        if 'worldexp' in main_buttons:
            worldexp = client.send_message_await(main_buttons['worldexp'])
            confirm_buttons = get_buttons(
                client.send_message_await(get_buttons(worldexp)['claimx1']))
            client.send_message_await(confirm_buttons['yes'])

        # Construct buildings
        build_buttons = get_buttons(client.send_message_await(main_buttons['buildings']))

        for building in ['lumbermill', 'goldmine', 'armory', 'smithy']:
            response_text = ""
            while "you don't have enough" not in response_text.lower():
                response_text = client.send_message_await(build_buttons[building]).full_text

        # Upgrade Hero Equipment
        hero = get_buttons(client.send_message_await(main_buttons["hero"]))
        equip_buttons = get_buttons(client.send_message_await(hero["equipment"]))

        # For every possible equipment, upgrade it until there are not enough resources left
        for equip in (b for k, b in equip_buttons.items() if 'up' in k):
            while True:
                response_text = client.send_message_await(equip).full_text
                if "you don't have enough" in response_text.lower():
                    break

        # Attack Player
        battle = get_buttons(client.send_message_await(main_buttons['battle']))
        arena = get_buttons(client.send_message_await(battle['arena']))
        normal_match = get_buttons(client.send_message_await(arena['normalmatch']))
        if 'fight' in normal_match:
            fight = get_buttons(client.send_message_await(normal_match['fight']))

        # Attack Boss
        bosses = get_buttons(client.send_message_await(battle['bosses']))
        if 'attackmax' in bosses:
            client.send_message_await(bosses['attackmax'])
    except KeyboardInterrupt:
        print('Done.')
        break
    except:
        traceback.print_exc()
        pass

client.stop()
