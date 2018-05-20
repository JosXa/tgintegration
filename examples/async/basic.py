"""
Before running this example, go to @IdleTownBot and set up your account first:


"""
import asyncio
import os

from tgintegration.interactionclientasync import InteractionClientAsync

examples_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# This example uses the configuration of `config.ini` (see examples/README)
client = InteractionClientAsync(
    session_name='my_account',
    workdir=examples_dir,  # Load configuration from parent folder
    config_file=os.path.join(examples_dir, 'config.ini')
)

client.load_config()
client.start()

loop = asyncio.get_event_loop()


async def main():
    res = await client.send_message_await("josxa", "lul")
    print(res.full_text)


if __name__ == '__main__':
    loop.run_until_complete(main())
