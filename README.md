TgIntegration
=============

<ins>An integration test and automation library for [Telegram Bots](https://core.telegram.org/bots) based on [Pyrogram](https://github.com/pyrogram/pyrogram).</ins>
<br />**Test your bot in realtime scenarios!**

**Are you a user of TgIntegration?** I'm actively looking for feedback and ways to improve the library, come and let me know in the [official group](https://t.me/TgIntegration)!

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/tgintegration)](https://pypi.org/project/tgintegration/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/tgintegration)](https://pypi.org/project/tgintegration/)
[![PyPI](https://img.shields.io/pypi/v/tgintegration)](https://pypi.org/project/tgintegration/)
![GitHub top language](https://img.shields.io/github/languages/top/josxa/tgintegration)
[![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/josxa/tgintegration/Build/master)](https://github.com/JosXa/tgintegration/actions?query=workflow%3ABuild)
[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/josxa/tgintegration/Docs?label=docs)](https://josxa.github.io/tgintegration)

[Features](#features) • [Requirements](#prerequisites) • [Installation](#installation) • [**Quick Start Guide**](#quick-start-guide) • [Test Frameworks](#integrating-with-test-frameworks)

- 📖 [Documentation](https://josxa.github.io/tgintegration/)
- 👥 [Telegram Chat](https://t.me/TgIntegration)
- 📄 Free software: [MIT License](https://tldrlegal.com/license/mit-license)
- [<img src="https://raw.githubusercontent.com/JosXa/tgintegration/master/docs/assets/pycharm-logos/icon-pycharm.svg" width="20" height="20" />]((https://www.jetbrains.com/?from=tgintegration)) Built with [PyCharm](https://www.jetbrains.com/?from=tgintegration)

Features
--------

▶️ [**See it in action!** 🎬](https://josxa.github.io/tgintegration/#see-it-in-action)

- 👤 Log into a Telegram user account and interact with bots or other users
- ✅ Write **realtime integration tests** to ensure that your bot works as expected! ▶️ [Pytest examples](https://github.com/JosXa/tgintegration/tree/master/examples/pytest)
- ⚡️ **Automate any interaction** on Telegram! ▶️ [Automatically play @IdleTownBot](https://github.com/JosXa/tgintegration/blob/master/examples/automation/idletown.py) | [More examples](https://github.com/JosXa/tgintegration/tree/master/examples/automation)
- 🛡 Fully typed for safety and **autocompletion** with your favorite IDE
- 🐍 Built for modern Python (3.8+) with high test coverage


Prerequisites
-------------

[Same as Pyrogram](https://github.com/pyrogram/pyrogram#requirements):

- A [Telegram API key](https://docs.pyrogram.ml/start/ProjectSetup#api-keys).
- A user session (seeing things happen in your own account is great for getting started)
- But: **Python 3.8** or higher!

A basic understanding of async/await and [asynchronous context managers](https://docs.python.org/3/library/contextlib.html#contextlib.asynccontextmanager) is assumed, as TgIntegration heavily relies on the latter to automate conversations.


Installation
------------

All hail pip!

$ `pip install tgintegration --upgrade`

<br />
<details><summary><i>Feeling adventurous?</i></summary><p>

For bleeding edge, install the master branch:

$ `pip install git+https://github.com/JosXa/tgintegration.git`

</p></details>


Quick Start Guide
-----------------

_You can [follow along by running the example](https://github.com/JosXa/tgintegration/blob/master/examples/readme_example/readmeexample.py) ([README](https://github.com/JosXa/tgintegration/blob/master/examples/README.md))_

#### Setup

Suppose we want to write integration tests for [@BotListBot](https://t.me/BotListBot) by sending it a couple of
messages and checking that it responds the way it should.

After [configuring a Pyrogram **user client**](https://docs.pyrogram.org/intro/setup),
let's start by creating a `BotController`:

``` python
from tgintegration import BotController

controller = BotController(
    peer="@BotListBot",      # The bot under test is https://t.me/BotListBot 🤖
    client=client,           # This assumes you already have a Pyrogram user client available
    max_wait=8,              # Maximum timeout for responses (optional)
    wait_consecutive=2,      # Minimum time to wait for more/consecutive messages (optional)
    raise_no_response=True,  # Raise `InvalidResponseError` when no response is received (defaults to True)
    global_action_delay=2.5  # Choosing a rather high delay so we can observe what's happening (optional)
)

await controller.clear_chat()  # Start with a blank screen (⚠️)
```

Now, let's send `/start` to the bot and wait until exactly three messages have been received by using the asynchronous `collect` context manager:

``` python
async with controller.collect(count=3) as response:
    await controller.send_command("start")

assert response.num_messages == 3  # Three messages received, bundled under a `Response` object
assert response.messages[0].sticker  # The first message is a sticker
```

The result should look like this:

![image](https://raw.githubusercontent.com/JosXa/tgintegration/master/docs/assets/start_botlistbot.png)

Examining the buttons in the response...

``` python
# Get first (and only) inline keyboard from the replies
inline_keyboard = response.inline_keyboards[0]

# Three buttons in the first row
assert len(inline_keyboard.rows[0]) == 3
```

We can also press the inline keyboard buttons, for example based on a regular expression:

``` python
examples = await inline_keyboard.click(pattern=r".*Examples")
```

As the bot edits the message, `.click()` automatically listens for "message edited" updates and returns
the new state as another `Response`.

![image](https://raw.githubusercontent.com/JosXa/tgintegration/master/docs/assets/examples_botlistbot.png)

``` python
assert "Examples for contributing to the BotList" in examples.full_text
```

#### Error handling

So what happens when we send an invalid query or the peer fails to respond?

The following instruction will raise an `InvalidResponseError` after `controller.max_wait` seconds.
This is because we passed `raise_no_response=True` during controller initialization.

``` python
try:
    async with controller.collect():
        await controller.send_command("ayylmao")
except InvalidResponseError:
    pass  # OK
```

Let's explicitly set `raise_` to `False` so that no exception occurs:

``` python
async with controller.collect(raise_=False) as response:
    await client.send_message(controller.peer_id, "Henlo Fren")
```

In this case, _tgintegration_ will simply emit a warning, but you can still assert
that no response has been received by using the `is_empty` property:

``` python
assert response.is_empty
```


Integrating with Test Frameworks
--------------------------------

### [pytest](https://docs.pytest.org/en/stable/index.html)

Pytest is the recommended test framework for use with _tgintegration_. You can
[browse through several examples](https://github.com/JosXa/tgintegration/tree/master/examples/pytest)
and _tgintegration_ also uses pytest for its own test suite.

### unittest

I haven't tried out the builtin `unittest` library in combination with _tgintegration_ yet,
but theoretically I don't see any problems with it.
If you do decide to try it, it would be awesome if you could tell me about your
experience and whether anything could be improved 🙂
Let us know at 👉 https://t.me/TgIntegration or in an issue.
