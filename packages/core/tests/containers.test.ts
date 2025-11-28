import { beforeEach, describe, expect, mock, test } from "bun:test";
import type { Message } from "@mtcute/core";
import type { TelegramClient } from "@mtcute/core/client.js";
import { ChatController } from "../src/chat-controller.js";
import { InlineKeyboard } from "../src/inline-keyboard.js";
import { ReplyKeyboard } from "../src/reply-keyboard.js";
import { Response } from "../src/response.js";

describe("Containers", () => {
  let mockClient: TelegramClient;
  let controller: ChatController;

  beforeEach(() => {
    mockClient = {
      isConnected: true,
      start: mock(async () => {}),
      resolvePeer: mock(async () => ({
        _: "inputPeerUser",
        userId: 123,
        accessHash: "0",
      })),
      getChat: mock(async () => ({ id: 12345 })),
      sendText: mock(async () => {}),
      getCallbackAnswer: mock(async () => {}),
      onNewMessage: {
        add: mock(() => {}),
        remove: mock(() => {}),
      },
    } as unknown as TelegramClient;
    controller = new ChatController(mockClient, "bot");
    // Manually set peerIdResolved to skip initialize
    Object.defineProperty(controller, "_peerIdResolved", {
      value: 12345,
      writable: true,
      enumerable: true,
      configurable: true,
    });
  });

  describe("InlineKeyboard", () => {
    test("parses buttons from message markup", () => {
      const msg = {
        chat: { id: 12345 },
        id: 100,
        text: "Menu",
        markup: {
          type: "inline",
          buttons: [
            [
              { text: "Button 1", data: "btn1" },
              { text: "Button 2", data: "btn2" },
            ],
            [{ text: "Link", url: "https://example.com" }],
          ],
        },
      } as unknown as Message;

      const response = new Response(controller, [msg]);
      const kb = response.inlineKeyboards[0];

      expect(kb).toBeInstanceOf(InlineKeyboard);
      expect(kb.buttons.length).toBe(2);
      expect(kb.buttons[0][0].text).toBe("Button 1");
      expect(kb.buttons[0][0].callbackData).toBe("btn1");
      expect(kb.buttons[1][0].url).toBe("https://example.com");
    });

    test("click() finds button and calls getCallbackAnswer", async () => {
      const msg = {
        chat: { id: 12345 },
        id: 100,
        markup: {
          type: "inline",
          buttons: [[{ text: "Click Me", data: "click_payload" }]],
        },
      } as unknown as Message;

      const kb = new InlineKeyboard(controller, msg, [
        [{ text: "Click Me", callbackData: "click_payload" }],
      ]);

      await kb.click("Click Me");

      expect(mockClient.getCallbackAnswer).toHaveBeenCalledWith({
        chatId: 12345,
        message: 100,
        data: "click_payload",
        timeout: 10100, // maxWait (10000) + 100
      });
    });
  });

  describe("ReplyKeyboard", () => {
    test("parses buttons from message markup", () => {
      const msg = {
        chat: { id: 12345 },
        id: 200,
        markup: {
          type: "reply",
          buttons: [[{ text: "Yes" }, { text: "No" }]],
        },
      } as unknown as Message;

      const response = new Response(controller, [msg]);
      const kb = response.replyKeyboard;

      expect(kb).toBeInstanceOf(ReplyKeyboard);
      expect(kb?.buttons[0][0].text).toBe("Yes");
    });

    test("click() sends text message", async () => {
      const msg = {
        chat: { id: 12345 },
        id: 200,
      } as unknown as Message;

      const kb = new ReplyKeyboard(controller, msg, [[{ text: "Option A" }]]);

      const collectSpy = mock(async (_opts, action) => {
        await action();
        return new Response(controller, []);
      });
      controller.collect = collectSpy;

      await kb.click("Option A");

      expect(collectSpy).toHaveBeenCalled();
      expect(mockClient.sendText).toHaveBeenCalledWith(12345, "Option A");
    });
  });
});
