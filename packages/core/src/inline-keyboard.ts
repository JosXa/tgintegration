import type { Message } from "@mtcute/core";
import type { tl } from "@mtcute/tl";
import type { ChatController } from "./chat-controller.js";
import { CallbackQueryTimeoutError } from "./errors.js";
import type { ClickOptions } from "./types.js";

export type InlineKeyboardButton = {
  text: string;
  callbackData?: string;
  url?: string;
};

export interface ClickResult {
  /** The callback answer from the bot, if any */
  answer: tl.messages.TypeBotCallbackAnswer | null;
  /** Whether the callback query was answered */
  answered: boolean;
}

export class InlineKeyboard {
  constructor(
    private readonly controller: ChatController,
    private readonly message: Message,
    public readonly buttons: InlineKeyboardButton[][],
  ) {}

  /**
   * Find a button by text pattern or index.
   */
  findButton(
    predicate: (btn: InlineKeyboardButton) => boolean,
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
   * Clicks an inline callback button and waits for the bot to answer.
   *
   * This method ONLY handles the callback query interaction. If you expect
   * the bot to send additional messages after clicking, wrap this call in
   * `controller.collect()`:
   *
   * @example
   * ```ts
   * // Button click that triggers new messages
   * const response = await controller.collect({ minMessages: 1 }, async () => {
   *   await keyboard.click("Show Details");
   * });
   * ```
   *
   * @example
   * ```ts
   * // Simple button click (e.g., toggle, acknowledge)
   * const result = await keyboard.click("Confirm");
   * if (result.answer?.message) {
   *   console.log("Toast:", result.answer.message);
   * }
   * ```
   *
   * @throws {CallbackQueryTimeoutError} If the bot doesn't answer within maxWait
   *         and `allowUnanswered` is false
   * @throws {Error} If button is not found or is not a callback button
   */
  async click(
    query: string | RegExp | number,
    options: ClickOptions = {},
  ): Promise<ClickResult> {
    const { maxWait = 10000, allowUnanswered = false } = options;

    const button = this.resolveButton(query);

    if (!button.callbackData) {
      if (button.url) {
        throw new Error(
          `Button "${button.text}" is a URL button (${button.url}). ` +
            `URL buttons open links and cannot be "clicked" via the API.`,
        );
      }
      // TODO: Handle other button types (switchInline, switchInlineCurrent, etc.)
      throw new Error(
        `Button "${button.text}" is not a callback button. ` +
          `Only buttons with callback_data can be clicked.`,
      );
    }

    const callbackData = button.callbackData;

    try {
      const answer = await this.controller.client.getCallbackAnswer({
        chatId: this.message.chat.id,
        message: this.message.id,
        data: callbackData,
        timeout: maxWait + 100, // Slightly more than our wait to avoid premature timeout
      });

      return { answer, answered: true };
    } catch (error) {
      if (this.isTimeoutError(error)) {
        if (allowUnanswered) {
          return { answer: null, answered: false };
        }
        throw new CallbackQueryTimeoutError({
          buttonText: button.text,
          callbackData,
          timeout: maxWait,
        });
      }
      throw error;
    }
  }

  private resolveButton(query: string | RegExp | number): InlineKeyboardButton {
    let button: InlineKeyboardButton | undefined;

    if (typeof query === "number") {
      const flat = this.buttons.flat();
      button = flat[query];
    } else {
      button = this.findButtonByText(query);
    }

    if (!button) {
      throw new Error(`Button not found for query: ${query}`);
    }

    return button;
  }

  private isTimeoutError(error: unknown): boolean {
    // Check for mtcute timeout error - may need adjustment based on actual error type
    if (error instanceof Error) {
      const isTimeoutMessage = error.message.includes("timeout");
      const isTimeoutName = error.name === "TimeoutError";
      const hasTimeoutCode =
        typeof error === "object" &&
        error !== null &&
        "code" in error &&
        error.code === "TIMEOUT";
      return isTimeoutMessage || isTimeoutName || hasTimeoutCode;
    }
    return false;
  }
}
