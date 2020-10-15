import asyncio
import sys

from decouple import config

from cicd import generate_configini_from_gh_secrets
from examples.automation import dinoparkbot, idletown

if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    generate_configini_from_gh_secrets.generate()
    session_name = config("SESSION_STRING")

    example_module = sys.argv[0]

    dinoparkbot.MAX_RUNS = 1
    dinoparkbot.SESSION_NAME = session_name

    idletown.MAX_RUNS = 1
    idletown.SESSION_NAME = session_name

    loop.run_until_complete(dinoparkbot.main())
    loop.run_until_complete(idletown.main())
