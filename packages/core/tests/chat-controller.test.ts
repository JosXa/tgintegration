import { test, expect, mock, describe, beforeEach } from "bun:test";
import { ChatController } from "../src/chat-controller.js";
import { Message } from "@mtcute/core";
import { AnyTelegramClient } from "../src/types.js";

describe("ChatController", () => {
  let mockClient: any;
  let controller: ChatController;
  let messageHandler: ((msg: any) => void) | undefined;

  beforeEach(() => {
    messageHandler = undefined;
    mockClient = {
      isConnected: true,
      start: mock(async () => {}),
      getFullChat: mock(async () => ({ id: 12345 })), // The resolved ID
      getFullUser: mock(async () => ({ id: 12345 })), // The resolved ID
      sendText: mock(async () => {}),
      deleteHistory: mock(async () => {}),
      onNewMessage: {
          add: mock((handler: any) => {
              messageHandler = handler;
          }),
          remove: mock((handler: any) => {
              if (messageHandler === handler) {
                  messageHandler = undefined;
              }
          })
      },
      getCallbackAnswer: mock(async () => ({}))
    };
    controller = new ChatController(mockClient as AnyTelegramClient, "bot_username");
  });

  test("collect captures messages sent during action", async () => {
    await controller.initialize();

    const promise = controller.collect({ minMessages: 1, maxWait: 1000 }, async () => {
        // Simulate a message arriving shortly after action starts
        setTimeout(() => {
            if (messageHandler) {
                messageHandler({
                    chat: { id: 12345 },
                    text: "Hello",
                    date: Date.now() / 1000
                });
            }
        }, 10);
    });

    const response = await promise;
    expect(response.count).toBe(1);
    expect(response.messages[0].text).toBe("Hello");
  });

  test("collect throws on timeout if throwOnTimeout is true", async () => {
    await controller.initialize();

    const promise = controller.collect({ 
        minMessages: 1, 
        maxWait: 100, 
        throwOnTimeout: true 
    }, async () => {
        // Do nothing, so we timeout
    });

    expect(promise).rejects.toThrow("Expected at least 1 messages");
  });

  test("pingBot sends commands", async () => {
    await controller.initialize();
    
    // Mock collect since pingBot calls it
    const collectSpy = mock(async (opts, action) => {
        await action();
        return { count: 1, messages: [] } as any;
    });
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
});
