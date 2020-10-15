import asyncio
from pathlib import Path

from tgintegration import BotController, Response, ResponseCollectorClient

examples_dir = Path(__file__).parent
print(examples_dir)

# This example uses the configuration of `config.ini` (see examples/README)
client = ResponseCollectorClient(
    "tgintegration_examples",
    config_file=str(examples_dir / "config.ini"),
    workdir=str(examples_dir),
)


controller = BotController(peer="@BotListBot", client=client)


async def main():
    await controller.initialize()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
