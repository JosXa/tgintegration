from tgintegration import IntegrationTestClient


def test_commands(client: IntegrationTestClient):
    # The IntegrationTestClient automatically loads the available commands and we test them all here
    for c in client.command_list:
        res = client.send_command_await(c.command)
        assert not res.empty
