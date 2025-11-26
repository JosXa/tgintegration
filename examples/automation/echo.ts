import { ChatController } from "@tgintegration/core";
import { createClient } from "../utils.js";

const peer = "@JosX4"; // Replace with your target

async function main() {
  const client = await createClient();
  const controller = new ChatController(client, peer);

  await controller.initialize();

  while (true) {
    console.log("Waiting for a message...");

    // Wait for a message from a specific chat
    // Note: controller.collect filters by the controller's peer by default.
    // If we want to wait for @TgIntegration (user), we might need to setup a controller for that user
    // or manually handle it.
    // The original example waited for a message in @TgIntegration chat.

    // Let's assume we are just echoing interaction with the peer.

    const response = await controller.collect({ maxWait: 30000 }, async () => {
      await controller.client.sendText(
        peer,
        "Hi! Please say something in the next 30 seconds...",
      );
    });

    if (response.count === 0) {
      await controller.client.sendText(peer, "You did not reply :(");
    } else {
      await controller.client.sendText(
        peer,
        `You replied with: ${response.fullText}`,
      );
    }

    // Break loop for example purposes
    break;
  }

  process.exit();
}

await main();
