=========================
telegram-integration-test
=========================


.. image:: https://img.shields.io/pypi/v/telegram-integration-test.svg
        :target: https://pypi.python.org/pypi/telegram-integration-test

.. image:: https://img.shields.io/travis/JosXa/telegram-integration-test.svg
        :target: https://travis-ci.org/JosXa/telegram-integration-test

.. image:: https://readthedocs.org/projects/telegram-integration-test/badge/?version=latest
        :target: https://telegram-integration-test.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/JosXa/telegram-integration-test/shield.svg
     :target: https://pyup.io/repos/github/JosXa/telegram-integration-test/
     :alt: Updates


An Integration Test Framework for `bots on Telegram Messenger <https://core.telegram.org/bots>`_
on top of `Pyrogram <https://github.com/pyrogram/pyrogram>`_.


* Free software: MIT license
* Documentation: https://telegram-integration-test.readthedocs.io.


Features
--------

* Log into a Telegram user account and interact with bots
* Abstractions to send messages and retrieve the bot's responses

Installation
------------

All hail pip!

.. code-block:: console

    $ pip install telegram-integration-test

Requirements
------------

`Same as Pyrogram <https://github.com/pyrogram/pyrogram#requirements>`_:

-   Python 3.4 or higher.
-   A `Telegram API key <https://docs.pyrogram.ml/start/ProjectSetup#api-keys>`_.

Usage
-----

Suppose we want to test the `@BotListBot <https://t.me/BotListBot>`_ by sending it a couple of
messages and asserting that its responses look about right:

.. code-block:: python

    client = IntegrationTestClient(
        bot_under_test='@BotListBot',
        session_name='your-name.session',
        api_id=API_ID,
        api_hash=API_HASH,
        phone_number="+0123456789",
        max_wait_response=15,  # maximum timeout for bot responses, seconds
        min_wait_consecutive=2  # minimum wait time for more than one message
    )
    client.start()  # This is based off a regular Pyrogram Client
    client.clear_chat()  # Let's start with a blank screen

    # Send /start to the bot_under_test and "await" exactly three messages
    response = client.send_command_await("start", num_expected=3)
    assert response.num_messages == 3

.. image:: docs/images/start_botlistbot.jpg
    :width: 200px
    :align: center
    :height: 100px
    :alt: alternate text

.. code-block:: python
    test


Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

