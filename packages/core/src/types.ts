import type { Message } from "@mtcute/core";
import type { TelegramClient } from "@mtcute/core/client.js";

export type AnyTelegramClient = Pick<
  TelegramClient,
  | "start"
  | "sendText"
  | "deleteHistory"
  | "onNewMessage"
  | "onEditMessage"
  | "getFullChat"
  | "getFullUser"
  | "getCallbackAnswer"
  | "disconnect"
  | "call"
  | "resolvePeer"
  | "resolveUser"
>;

export interface TimeoutSettings {
  maxWait?: number;
  waitConsecutive?: number;
  throwOnTimeout?: boolean;
}

interface ExpectationBase {
  validators?: (messages: Message[]) => boolean;
}

export type Expectation = ExpectationBase &
  ({ minMessages?: number; maxMessages?: number } | { numMessages: number });

export type CollectOptions = TimeoutSettings &
  ExpectationBase &
  (
    | {
        minMessages?: number;
        maxMessages?: number;
      }
    | { numMessages?: number }
  );

export interface ClickOptions {
  /**
   * Maximum time in milliseconds to wait for the bot to answer the callback query.
   * If the bot doesn't call `answerCallbackQuery` within this time, an error is thrown.
   * @default 10000
   */
  maxWait?: number;

  /**
   * If true, don't throw an error when the callback query is not answered.
   *
   * Some bots neglect to call `answerCallbackQuery()`, leaving users with a
   * loading spinner until Telegram times out. This is poor UX and generally
   * indicates a bug in the bot. By default, tgintegration treats this as an
   * error to help you catch such issues during testing.
   *
   * Set to `true` if you're testing a bot known to have this behavior and
   * want to proceed regardless.
   *
   * @default false
   */
  allowUnanswered?: boolean;
}
