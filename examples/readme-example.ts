import { ChatController, InvalidResponseError } from "@tgintegration/core";
import { createClient } from "./utils.js";

/**
 * Full version of the GitHub README example.
 */
async function main() {
  const client = await createClient();

  // We are going to run tests on https://t.me/BotListBot (or any other bot)
  // Note: BotListBot might be down, replace with your target bot.
  const peer = "@BotListBot";

  const controller = new ChatController(client, peer, {
    globalActionDelay: 2500, // 2.5s delay to follow along
  });

  await controller.initialize();

  console.log("Clearing chat to start with a blank screen...");
  await controller.clearChat();

  console.log("Sending /start and waiting for exactly 3 messages...");
  const response = await controller.collect(
    {
      minMessages: 3,
      maxMessages: 3,
      maxWait: 8000,
    },
    async () => {
      await controller.sendCommand("start");
    },
  );

  if (response.count !== 3) {
    throw new Error(`Expected 3 messages, got ${response.count}`);
  }
  console.log("Three messages received, bundled as a `Response`.");

  // Check for sticker
  if (response.messages[0].media?.type === "sticker") {
    console.log("First message is a sticker.");
  }

  console.log("Let's examine the buttons in the response...");
  const inlineKeyboards = response.inlineKeyboards;
  if (inlineKeyboards.length > 0) {
    const kb = inlineKeyboards[0];
    // In legacy code, rows[0] had 3 buttons.
    if (kb.buttons[0].length === 3) {
      console.log("Yep, there are three buttons in the first row.");
    }

    // Click button by pattern
    console.log("Clicking button matching 'Examples'...");
    try {
      const clickResult = await kb.click(/.*Examples/);

      if (clickResult.answered) {
        console.log("Button click was acknowledged by the bot!");
      }
    } catch (_e) {
      console.log(
        "Could not find or click button (bot might be down or changed).",
      );
    }
  }

  console.log(
    "So what happens when we send an invalid query or the peer fails to respond?",
  );

  try {
    console.log("Expecting unhandled command to raise InvalidResponseError...");
    await controller.collect(
      {
        maxWait: 8000,
        throwOnTimeout: true,
      },
      async () => {
        await controller.sendCommand("ayylmao");
      },
    );
  } catch (e) {
    if (e instanceof InvalidResponseError) {
      console.log("Ok, raised as expected.");
    } else {
      throw e;
    }
  }

  // If `throwOnTimeout` is false (default), no exception is raised
  const noReplyResponse = await controller.collect(
    {
      maxWait: 3000,
      throwOnTimeout: false,
    },
    async () => {
      console.log("Sending a message but expecting no reply...");
      // Send directly via client if needed, or use controller
      await controller.client.sendText(controller.peer, "Henlo Fren");
    },
  );

  if (noReplyResponse.count === 0) {
    console.log("Success! No response received as expected.");
  }
}

await main();
