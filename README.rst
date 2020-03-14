=============
TgIntegration
=============

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

No more mocking of every single Bot API object, just test your bot in real-world scenarios.

* Free software: MIT license

.. * Documentation: https://tgintegration.readthedocs.io.


Features
--------

* Log into a Telegram user account and interact with bots
* Send messages and wait for the response
* Perform inline queries and match the expected result
* Automate everything about Telegram bots

Installation
------------

All hail pip!

.. code-block:: console

    $ pip install tgintegration --upgrade

Requirements
------------

`Same as Pyrogram <https://github.com/pyrogram/pyrogram#requirements>`_:

-   Python 3.4 or higher.
-   A `Telegram API key <https://docs.pyrogram.ml/start/ProjectSetup#api-keys>`_.

Usage
-----

Suppose we want to write integration tests for `@BotListBot <https://t.me/BotListBot>`_
by sending it a couple of messages and asserting that it responds the way it should.
First, let's create a ``BotController``:

.. code-block:: python

    from tgintegration import BotController

    client = BotController(
        bot_under_test='@BotListBot',
        session_name='my_account',  # Arbitrary file path to the Pyrogram session file
        api_id=API_ID,  # See "Requirements" above, ...
        api_hash=API_HASH,  # alternatively use a `config.ini` file
        max_wait_response=15,  # Maximum timeout for bot responses
        min_wait_consecutive=2  # Minimum time to wait for consecutive messages
    )

    client.start()
    client.clear_chat()  # Let's start with a blank screen

Now let's send the ``/start`` command to the ``bot_under_test`` and "await" exactly three messages:

.. code-block:: python

    response = client.send_command_await("start", num_expected=3)

    assert response.num_messages == 3
    assert response.messages[0].sticker  # First message is a sticker

The result should look like this:

.. image:: https://github.com/JosXa/tgintegration/blob/master/docs/images/start_botlistbot.png
    :alt: Sending /start to @BotListBot

Let's examine these buttons in the response...

.. code-block:: python

    # Extract first (and only) inline keyboard from the replies
    inline_keyboard = response.inline_keyboards[0]

    # Three buttons in the first row
    assert len(inline_keyboard.rows[0]) == 3

We can also query and press the inline keyboard buttons:

.. code-block:: python

    # Click the first button matching the pattern
    examples = response.inline_keyboards[0].press_button_await(pattern=r'.*Examples')

    assert "Examples for contributing to the BotList" in examples.full_text

As the bot edits the message, ``press_button_await`` automatically listens for ``MessageEdited``
updates and picks up on the edit, returning it as ``Response``.

.. image:: https://github.com/JosXa/tgintegration/blob/master/docs/images/examples_botlistbot.png
    :alt: Get Examples from @BotListBot

So what happens when we send an invalid query or the bot fails to respond?

.. code-block:: python

    try:
        # The following instruction will raise an `InvalidResponseError` after
        # `client.max_wait_response` seconds. This is because we passed `raise_no_response = True`
        # in the client initialization.
        client.send_command_await("ayylmao", raise_=True)
    except InvalidResponseError:
        print("Raised.")  # Ok

The ``BotController`` is based off a regular Pyrogram ``Client``, meaning that,
in addition to the ``send_*_await`` methods, all normal Pyro methods still work:

.. code-block:: python

    client.send_message(client.bot_under_test, "Hello from Pyrogram")

    # `send_*_await` methods automatically use the `bot_under_test` as peer:
    res = client.send_message_await("Hello from TgIntegration", max_wait=2, raise_=False)
    # If `raise_` is explicitly set to False, no exception is raised:
    assert res.empty
    # Note that when no response is expected and no validation thereof is necessary, ...
    client.send_photo_await("media/photo.jpg", max_wait=0, raise_=False)
    client.send_voice_await("media/voice.ogg", max_wait=0, raise_=False)
    # ... it makes more sense to use the "unawaitable" methods:
    client.send_photo(client.bot_under_test, "media/photo.jpg")
    client.send_voice(client.bot_under_test, "media/voice.ogg")




Custom awaitable actions
========================

The main logic for the timeout between sending a message and receiving a response from the user
is handled in the ``act_await_response`` method:

.. code-block:: python

    def act_await_response(self, action: AwaitableAction) -> Response: ...

It expects an ``AwaitableAction`` which is a plan for a message to be sent, while the
``BotController`` just makes it easy and removes a lot of the boilerplate code to
create these actions.

After executing the action, the client collects all incoming messages that match the ``filters``
and adds them to the response. Thus you can think of a ``Response`` object as a collection of
messages returned by the peer in reaction to the executed ``AwaitableAction``.

.. code-block:: python

    from tgintegration import AwaitableAction, Response
    from pyrogram import filters

    peer = '@BotListBot'

    action = AwaitableAction(
        func=client.send_message,
        kwargs=dict(
            chat_id=peer,
            text="**Hello World**",
            parse_mode="markdown"
        ),
        # Wait for messages only by the peer we're interacting with
        filters=filters.user(peer) & filters.incoming,
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

