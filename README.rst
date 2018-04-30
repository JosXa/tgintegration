=========================
tgintegration
=========================

WORK IN PROGRESS. Take bugs with a grain of salt.

.. image:: https://img.shields.io/pypi/v/tgintegration.svg
    :target: https://pypi.python.org/pypi/tgintegration

.. image:: https://img.shields.io/travis/JosXa/tgintegration.svg
    :target: https://travis-ci.org/JosXa/tgintegration

.. image:: https://readthedocs.org/projects/tgintegration/badge/?version=latest
    :target: https://tgintegration.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/JosXa/tgintegration/shield.svg
    :target: https://pyup.io/repos/github/JosXa/tgintegration/
     :alt: Updates


        An Integration Test Framework for `Bots on Telegram Messenger <https://core.telegram.org/bots>`_
on top of `Pyrogram <https://github.com/pyrogram/pyrogram>`_.


* Free software: MIT license
.. * Documentation: https://tgintegration.readthedocs.io.


Features
--------

* Log into a Telegram user account and interact with bots
* Capable of sending messages and retrieving the bot's responses

Installation
------------

All hail pip!

.. code-block:: console

    $ pip install tgintegration

Requirements
------------

`Same as Pyrogram <https://github.com/pyrogram/pyrogram#requirements>`_:

-   Python 3.4 or higher.
-   A `Telegram API key <https://docs.pyrogram.ml/start/ProjectSetup#api-keys>`_.

Usage
-----

**Note**: The importable package is called ``tgintegration``!

Suppose we want to write integration tests for `@BotListBot <https://t.me/BotListBot>`_
by sending it a couple of messages and asserting that it responds the way it should.
First, let's create an ``IntegrationTestClient``:

.. code-block:: python

    from tgintegration import IntegrationTestClient

    client = IntegrationTestClient(
        bot_under_test='@BotListBot',
        session_name='your-name.session',
        api_id=API_ID,  # See requirements
        api_hash=API_HASH,
        phone_number="+0123456789",
        max_wait_response=15,  # maximum timeout for bot responses
        min_wait_consecutive=2  # minimum time to wait for consecutive messages
    )

    client.start()
    client.clear_chat()  # Let's start with a blank screen

Now let's send the ``/start`` command to the ``bot_under_test`` and "await" exactly three messages:

.. code-block:: python

    response = client.send_command_await("start", num_expected=3)

    assert response.num_messages == 3
    assert response.messages[0].sticker

Should look like this:

.. raw:: html

    <img src="https://github.com/JosXa/tgintegration/blob/master/docs/images/start_botlistbot.png" alt="Sending /start to @BotListBot" width="400">

Let's examine these buttons in the response...

.. code-block:: python

    second_message = response[1]

    # Three buttons in the first row
    assert len(second_message.reply_markup.inline_keyboard[0]) == 3

We can also find and press the inline keyboard buttons:

.. code-block:: python

    # Click the first button matching the pattern
    examples = response.press_inline_button(pattern=r'.*Examples')

    assert "Examples for contributing to the BotList" in examples.full_text

As the bot edits the message, ``press_inline_button`` automatically listens for ``MessageEdited``
updates and picks up on the edit, returning it as ``Response``.

.. raw:: html

    <img src="https://github.com/JosXa/tgintegration/blob/master/docs/images/examples_botlistbot.png" alt="Sending /start to @BotListBot" width="400">

So what happens when we send an invalid query or the bot fails to respond?

.. code-block:: python

    try:
        # The following instruction will raise an `InvalidResponseError` after
        # `client.max_wait_response` seconds
        client.send_command_await("ayylmao")
    except InvalidResponseError:
        print("Raised.")

The ``IntegrationTestClient`` is based off a regular Pyrogram ``Client``, meaning that,
in addition to the ``*_await`` methods, all normal calls still work:

.. code-block:: python

    client.send_message(client.bot_under_test, "Hello Pyrogram")
    client.send_message_await("Hello Pyrogram")  # This automatically uses the bot_under_test as the peer
    client.send_voice_await("files/voice.ogg")
    client.send_video_await("files/video.mp4")

Custom awaitable actions
========================

The main logic for the timeout between sending a message and receiving a response from the user
is handled in the ``act_await_response`` method:

.. code-block:: python

    def act_await_response(self, action: AwaitableAction) -> Response: ...

It expects an ``AwaitableAction`` which is a plan for a message to be sent, while the
``IntegrationTestClient`` just makes it easy and removes a lot of the boilerplate code to
create these actions.

After executing the action, the client collects all incoming messages that match the ``filters``
and adds them to the response. Thus you can think of a ``Response`` object as a collection of
messages returned by the peer in reaction to the executed ``AwaitableAction``.

.. code-block:: python

    from tgintegration import AwaitableAction, Response
    from pyrogram import Filters

    peer = '@BotListBot'

    action = AwaitableAction(
        func=client.send_message,
        kwargs=dict(
            chat_id=peer,
            text="**Hello World**",
            parse_mode='markdown'
        ),
        # Wait for messages only by the peer we're interacting with
        filters=Filters.user(peer) & Filters.incoming,
        # Time out and raise after 15 seconds
        max_wait=15
    )

    response = client.act_await_response(action)  # type: Response



Integrating with test frameworks
--------------------------------

TODO

* py.test
* unittest


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

