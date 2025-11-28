import { beforeEach, describe, expect, mock, test } from "bun:test";
import type { Message } from "@mtcute/core";
import type { AnyTelegramClient } from "@tgintegration/core";
import { ChatController } from "../src/chat-controller.js";

describe("ChatController", () => {
  let mockClient: AnyTelegramClient;
  let controller: ChatController;
  let messageHandler: ((msg: Message) => void) | undefined;
  let editHandler: ((msg: Message) => void) | undefined;

  beforeEach(() => {
    messageHandler = undefined;
    editHandler = undefined;
    mockClient = {
      isConnected: true,
      start: mock(async () => {}),
      getFullChat: mock(async () => ({ id: 12345 })), // The resolved ID
      getFullUser: mock(async () => ({ id: 12345 })), // The resolved ID
      sendText: mock(async () => {}),
      deleteHistory: mock(async () => {}),
      onNewMessage: {
        add: mock((handler: (msg: Message) => void) => {
          messageHandler = handler;
        }),
        remove: mock((handler: (msg: Message) => void) => {
          if (messageHandler === handler) {
            messageHandler = undefined;
          }
        }),
      },
      onEditMessage: {
        add: mock((handler: (msg: Message) => void) => {
          editHandler = handler;
        }),
        remove: mock((handler: (msg: Message) => void) => {
          if (editHandler === handler) {
            editHandler = undefined;
          }
        }),
      },
      getCallbackAnswer: mock(async () => ({})),
    } as unknown as AnyTelegramClient;
    controller = new ChatController(mockClient, "bot_username");
  });

  test("collect captures messages sent during action", async () => {
    await controller.initialize();

    const promise = controller.collect(
      { minMessages: 1, maxWait: 1000 },
      async () => {
        // Simulate a message arriving shortly after action starts
        setTimeout(() => {
          if (messageHandler) {
            messageHandler({
              chat: { id: 12345 },
              text: "Hello",
              date: new Date(),
            } as Message);
          }
        }, 10);
      },
    );

    const response = await promise;
    expect(response.count).toBe(1);
    expect(response.messages[0].text).toBe("Hello");
  });

  test("collect throws on timeout if throwOnTimeout is true", async () => {
    await controller.initialize();

    const promise = controller.collect(
      {
        minMessages: 1,
        maxWait: 100,
        throwOnTimeout: true,
      },
      async () => {
        // Do nothing, so we timeout
      },
    );

    expect(promise).rejects.toThrow("Expected at least 1 messages");
  });

  test("pingBot sends commands", async () => {
    await controller.initialize();

    // Mock collect since pingBot calls it
    const collectSpy = mock(
      async (_opts: unknown, action: () => Promise<void>) => {
        await action();
        return { count: 1, messages: [] } as unknown as Awaited<
          ReturnType<typeof controller.collect>
        >;
      },
    );
    controller.collect = collectSpy;

    await controller.pingBot({ messages: ["/start", "hello"], maxWait: 100 });

    expect(collectSpy).toHaveBeenCalled();
    expect(mockClient.sendText).toHaveBeenCalledTimes(2);
    expect(mockClient.sendText).toHaveBeenCalledWith("bot_username", "/start");
    expect(mockClient.sendText).toHaveBeenCalledWith("bot_username", "hello");
  });

  test("clearChat calls deleteHistory", async () => {
    await controller.clearChat();
    expect(mockClient.deleteHistory).toHaveBeenCalledWith("bot_username");
  });

  test("collect captures edited messages", async () => {
    await controller.initialize();

    const promise = controller.collect(
      { minMessages: 1, maxWait: 1000 },
      async () => {
        // Simulate an edited message arriving shortly after action starts
        setTimeout(() => {
          if (editHandler) {
            editHandler({
              chat: { id: 12345 },
              text: "Edited Hello",
              date: new Date(),
            } as Message);
          }
        }, 10);
      },
    );

    const response = await promise;
    expect(response.count).toBe(1);
    expect(response.messages[0].text).toBe("Edited Hello");
  });
});
