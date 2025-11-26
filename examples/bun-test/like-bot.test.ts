import { afterAll, beforeAll, describe, expect, test } from "bun:test";
import { ChatController } from "@tgintegration/core";
import { createClient } from "../utils.js";

describe("@like bot", () => {
  let controller: ChatController;

  beforeAll(async () => {
    controller = new ChatController(await createClient(), "@like");

    await controller.initialize();

    // Clear chat to start fresh
    await controller.clearChat();
  });

  afterAll(() => {
    controller.disconnect();
  });

  test("create a poll and interact with keyboard", async () => {
    // Send /start command and expect a response
    const startResponse = await controller.collect(
      {
        numMessages: 1,
      },
      async () => {
        await controller.sendCommand("start");
      },
    );

    expect(startResponse.messages.length).toEqual(1);
    expect(startResponse.fullText).toContain(
      "Let's create a message with emoji like-buttons.",
    );

    // Send poll title and options, expect multiple messages
    const titleResponse = await controller.collect(
      { numMessages: 3 },
      async () => {
        await controller.sendText("This is an awesome poll");
        await controller.sendText("👍🫰👎");
      },
    );

    expect(titleResponse.messages.length).toEqual(3);

    // Verify inline keyboards are present
    expect(titleResponse.inlineKeyboards.length).toBeGreaterThan(0);

    await titleResponse.inlineKeyboards[0].click("👍");
    await titleResponse.inlineKeyboards[0].click("👎");
  });
});
