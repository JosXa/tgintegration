import type { Message } from "@mtcute/core";
import type { ChatController } from "./chat-controller.js";
import type { Response } from "./response.js";
import type { CollectOptions } from "./types.js";

export type ReplyKeyboardButton = {
  text: string;
};

export class ReplyKeyboard {
  constructor(
    private readonly controller: ChatController,
    private readonly message: Message,
    public readonly buttons: ReplyKeyboardButton[][],
  ) {}

  findButtonByText(pattern: string | RegExp): ReplyKeyboardButton | undefined {
    for (const row of this.buttons) {
      for (const btn of row) {
        const match =
          typeof pattern === "string"
            ? btn.text === pattern
            : pattern.test(btn.text);
        if (match) return btn;
      }
    }
    return undefined;
  }

  async click(
    textOrPattern: string | RegExp,
    options?: CollectOptions,
  ): Promise<Response> {
    const button = this.findButtonByText(textOrPattern);

    if (!button) {
      throw new Error(`Reply button not found: ${textOrPattern}`);
    }

    return this.controller.collect(options || {}, async () => {
      await this.controller.client.sendText(this.message.chat.id, button.text);
    });
  }
}
