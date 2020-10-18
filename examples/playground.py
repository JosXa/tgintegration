import asyncio
from pathlib import Path

from pyrogram import Client
from pyrogram import filters as f

from tgintegration import BotController

examples_dir = Path(__file__).parent
print(examples_dir)

# This example uses the configuration of `config.ini` (see examples/README)
client = Client(
    "tgintegration_examples",
    config_file=str(examples_dir / "config.ini"),
    workdir=str(examples_dir),
)


controller = BotController(peer="@deerspangle", client=client, raise_no_response=False)


async def main():
    await controller.initialize()

    while True:
        async with controller.collect(
            f.chat("@TgIntegration"), max_wait=30
        ) as response:
            await client.send_message(
                "@TgIntegration",
                "Hi @deerspangle! Please say something in the next 30 seconds...",
            )

        await client.send_message(
            "@TgIntegration",
            "You did not reply :("
            if response.empty
            else f"You replied with: {response.full_text}",
        )


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
