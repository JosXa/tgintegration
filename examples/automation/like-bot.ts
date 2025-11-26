import { ChatController } from "@tgintegration/core";
import { createClient } from "../utils.js";

/**
 * Example automating the @like bot.
 */
async function main() {
  const client = await createClient();

  const peer = "@like";

  const controller = new ChatController(client, peer, {
    globalActionDelay: 1000, // 1s delay to follow along
  });

  await controller.initialize();

  console.log("Clearing chat to start with a blank screen...");
  await controller.clearChat();

  console.log("Sending /start and collecting response...");
  const _startResponse = await controller.collect(
    {
      minMessages: 1,
    },
    async () => {
      await controller.sendCommand("start");
    },
  );

  const titleResponse = await controller.collect(
    { minMessages: 3 },
    async () => {
      await controller.sendText("This is an awesome poll");
      await controller.sendText("👍🫰👎");
    },
  );

  titleResponse.debug();

  await titleResponse.inlineKeyboards[0].click("👍");
  await titleResponse.inlineKeyboards[0].click("👎");

  process.exit(0);
}

await main();
