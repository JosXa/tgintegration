"""
A tgintegration script plays Idle Town for you (@IdleTownBot).

This example uses a `config.ini` file for configuration (see examples/README).
It also expects that you have set up the bot with a town name and English as language.
"""
import asyncio
import logging
import traceback
from pathlib import Path
from typing import Dict
from decouple import config

from pyrogram import Client
from pyrogram import filters as f

from tgintegration import BotController
from tgintegration.containers.responses import Response

examples_dir = Path(__file__).parent.parent.absolute()
SESSION_NAME: str = "tgintegration_examples"

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)
log = logging.getLogger(__name__)


# This example uses the configuration of `config.ini` (see examples/README)
def create_client(session_name: str = SESSION_NAME) -> Client:
    return Client(
        name=session_name,
        api_id=config("API_ID"),
        api_hash=config("API_HASH"),
        session_string=config("SESSION_STRING"),
        workdir=str(examples_dir),
    )


def create_game_controller(client: Client = None) -> BotController:
    return BotController(
        peer="@IdleTownBot",
        client=client or create_client(),
        global_action_delay=2.0,  # The @IdleTownBot has a spam limit of about 1.9s
        max_wait=8,  # Maximum time in seconds to wait for a response from the bot
        wait_consecutive=None,  # Do not wait for more than one message
    )


def ascii_chars(text: str) -> str:
    return "".join(x for x in text if str.isalpha(x) or str.isdigit(x)).strip()


def get_buttons(response: Response) -> Dict[str, str]:
    """
    Helper function to create a dictionary for easy access to keyboard buttons
    """
    return {ascii_chars(b).lower(): b for b in response.keyboard_buttons}


async def perform_full_run(controller: BotController, max_upgrades_per_type: int = 5):
    # Setup
    await controller.clear_chat()
    await asyncio.sleep(2)

    async def restart() -> Response:
        async with controller.collect(f.text) as start:
            await controller.send_command("restart", add_bot_name=False)
        return start

    # Extract keyboard buttons of /start response
    main_menu = get_buttons(await restart())

    async def click_button(menu: Dict[str, str], key: str) -> Dict[str, str]:
        async with controller.collect() as response:  # type: Response
            await controller.client.send_message(controller.peer_id, menu[key])

        return get_buttons(response)

    # Get World Exp if possible
    if "worldexp" in main_menu:
        worldexp_menu = await click_button(main_menu, "worldexp")
        confirm_menu = await click_button(worldexp_menu, "claimx1")
        await click_button(confirm_menu, "yes")

    # Construct buildings
    build_menu = await click_button(main_menu, "buildings")

    for building in ["lumbermill", "goldmine", "armory", "smithy"]:
        num_upgraded = 0
        while num_upgraded < max_upgrades_per_type:
            async with controller.collect() as build_response:
                await controller.client.send_message(
                    controller.peer_id, build_menu[building]
                )

            if "you don't have enough" in build_response.full_text.lower():
                break
            num_upgraded += 1

    # Upgrade Hero Equipment
    hero_menu = await click_button(main_menu, "hero")
    equip_menu = await click_button(hero_menu, "equipment")

    # For every possible equipment, upgrade it until there are not enough resources left
    for equip_button in (k for k in equip_menu.keys() if k.startswith("up")):
        num_upgraded = 0
        while num_upgraded < max_upgrades_per_type:
            async with controller.collect() as upgrade_response:
                await controller.client.send_message(
                    controller.peer_id, equip_menu[equip_button]
                )
            if "you don't have enough" in upgrade_response.full_text.lower():
                break
            num_upgraded += 1

    # Attack Player
    battle_menu = await click_button(main_menu, "battle")
    arena_menu = await click_button(battle_menu, "arena")
    normal_match_menu = await click_button(arena_menu, "normalmatch")

    if "fight" in normal_match_menu:
        await click_button(normal_match_menu, "fight")

    # Attack Boss
    bosses_menu = await click_button(battle_menu, "bosses")
    if "attackmax" in bosses_menu:
        await click_button(bosses_menu, "attackmax")


async def main():
    controller = create_game_controller()
    await controller.initialize()

    while True:
        try:
            await perform_full_run(controller)
        except KeyboardInterrupt:
            print("Done.")
            break
        except BaseException:
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
