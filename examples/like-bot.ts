import { createClient } from "./utils.js";
import { ChatController } from "@tgintegration/core";

/**
 * Example automating the @like bot.
 */
async function main() {
  const client = await createClient();

  const peer = "@like";

  const controller = new ChatController(client, peer, {
    // Default options
  }, {
    globalActionDelay: 1000 // 1s delay to follow along
  });

  await controller.initialize();

  console.log("Clearing chat to start with a blank screen...");
  await controller.clearChat();

  console.log("Sending /start and collecting response...");
  const startResponse = await controller.collect({
    minMessages: 1
  }, async () => {
    await controller.sendCommand("start");
  });

  const titleResponse = await controller.collect({ minMessages: 3 }, async () => {
    await controller.sendText("This is an awesome poll");
    await controller.sendText("👍🫰👎");
  })


  titleResponse.debug();
  const thumbsUp = await titleResponse.inlineKeyboards[0].click("👍", { maxWait: 0 })
  const thumbsDown = await titleResponse.inlineKeyboards[0].click("👎", { maxWait: 0 })
  thumbsDown.debug();

  process.exit(0)
}

await main()