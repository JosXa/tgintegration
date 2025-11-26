import {
  Message,
} from "@mtcute/core";
import type { CollectOptions } from "./types.js";
import type { ChatController } from "./chat-controller.js";
import type { Response } from "./response.js";

export type InlineKeyboardButton = {
  text: string;
  callbackData?: string;
  url?: string;
  // other fields...
};

export class InlineKeyboard {
  constructor(
    private readonly controller: ChatController,
    private readonly message: Message,
    public readonly buttons: InlineKeyboardButton[][]
  ) {}

  /**
   * Find a button by text pattern or index.
   */
  findButton(
    predicate: (btn: InlineKeyboardButton) => boolean
  ): InlineKeyboardButton | undefined {
    for (const row of this.buttons) {
      for (const btn of row) {
        if (predicate(btn)) return btn;
      }
    }
    return undefined;
  }

  findButtonByText(pattern: string | RegExp): InlineKeyboardButton | undefined {
    return this.findButton((btn) => {
      if (typeof pattern === "string") {
        return btn.text === pattern;
      }
      return pattern.test(btn.text);
    });
  }

  /**
   * Clicks an inline button and waits for the resulting response.
   * This automatically initiates a `collect` session.
   */
  async click(
    query: string | RegExp | number, // Text, Regex, or Index (if number)
    options?: CollectOptions
  ): Promise<Response> {
    let button: InlineKeyboardButton | undefined;

    if (typeof query === "number") {
      // Flatten and find by index
      const flat = this.buttons.flat();
      button = flat[query];
    } else {
      button = this.findButtonByText(query);
    }

    if (!button) {
      throw new Error(`Button not found for query: ${query}`);
    }

    if (!button.callbackData) {
       if (button.url) {
           throw new Error(`Cannot click URL button: ${button.url}`);
       }
       throw new Error("Button is not clickable (no callback data)");
    }

    const callbackData = button.callbackData;

    return this.controller.collect(options || {}, async () => {
        // Perform the click
        await this.controller.client.getCallbackAnswer({
            chatId: this.message.chat.id,
            message: this.message.id,
            data: callbackData,
        });
    });
  }
}
