from tgintegration import BotIntegrationClient


def test_commands(client: BotIntegrationClient):
    # The BotController automatically loads the available commands and we test them all here
    for c in client.command_list:
        res = client.send_command_await(c.command)
        assert not res.empty, "Bot did not respond to command /{}.".format(c.command)
