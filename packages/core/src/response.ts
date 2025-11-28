import type { Message } from "@mtcute/core";
import type { tl } from "@mtcute/tl";
import type { ChatController } from "./chat-controller.js";
import { InlineKeyboard } from "./inline-keyboard.js";
import { ReplyKeyboard } from "./reply-keyboard.js";

export class Response {
  constructor(
    private readonly controller: ChatController,
    public readonly messages: Message[],
  ) {}

  get first(): Message | undefined {
    return this.messages[0];
  }

  get last(): Message | undefined {
    return this.messages[this.messages.length - 1];
  }

  get count(): number {
    return this.messages.length;
  }

  get fullText(): string {
    return this.messages.map((m) => m.text).join("\n");
  }

  get inlineKeyboards(): InlineKeyboard[] {
    return this.messages
      .filter(
        (m) => m.markup && "type" in m.markup && m.markup.type === "inline",
      )
      .map((m) => {
        const markup = m.markup as unknown as tl.TypeReplyMarkup;

        if (!("buttons" in markup)) {
          return new InlineKeyboard(this.controller, m, []);
        }

        const buttons = (markup.buttons as tl.TypeKeyboardButton[][]).map(
          (row: tl.TypeKeyboardButton[]) =>
            row.map((btn: tl.TypeKeyboardButton) => ({
              text: "text" in btn ? btn.text : "",
              callbackData:
                "data" in btn && btn.data
                  ? Buffer.from(btn.data).toString("utf8")
                  : undefined,
              url: "url" in btn ? btn.url : undefined,
            })),
        );

        return new InlineKeyboard(this.controller, m, buttons);
      });
  }

  get replyKeyboard(): ReplyKeyboard | undefined {
    for (let i = this.messages.length - 1; i >= 0; i--) {
      const m = this.messages[i];
      if (m.markup && "type" in m.markup && m.markup.type === "reply") {
        const markup = m.markup as unknown as tl.TypeReplyMarkup;

        if (!("buttons" in markup)) {
          continue;
        }

        const buttons = (markup.buttons as tl.TypeKeyboardButton[][]).map(
          (row: tl.TypeKeyboardButton[]) =>
            row.map((btn: tl.TypeKeyboardButton) => ({
              text: "text" in btn ? btn.text : "",
            })),
        );
        return new ReplyKeyboard(this.controller, m, buttons);
      }
    }
    return undefined;
  }

  /**
   * Extract command names from the response text (e.g., /start, /help).
   */
  get commands(): string[] {
    const commands = new Set<string>();
    const regex = /\/(\w+)/g;
    let match = regex.exec(this.fullText);
    while (match !== null) {
      commands.add(match[1]);
      match = regex.exec(this.fullText);
    }
    return Array.from(commands);
  }

  debug(): void {
    console.log(
      this.count > 0
        ? `Response with ${this.count} message(s):`
        : "Empty Response.",
    );
    for (let i = 0; i < this.messages.length; i++) {
      const msg = this.messages[i];
      const senderName =
        msg.sender && "firstName" in msg.sender
          ? msg.sender.firstName || msg.sender.username
          : "Unknown";
      console.log(`[${i}] ${senderName}:\n${msg.text || "[no text]"}`);
      if (msg.media) {
        console.log(`Media: ${msg.media.type}`);
      }
      if (msg.markup) {
        const processedMarkup = JSON.parse(
          JSON.stringify(msg.markup, (_key, value) => {
            if (
              value &&
              typeof value === "object" &&
              "data" in value &&
              value.data &&
              typeof value.data === "object"
            ) {
              // If data is a Buffer-like object, convert to string
              if (Buffer.isBuffer(value.data)) {
                return { ...value, data: value.data.toString("utf8") };
              }
              // If data is an object with numeric keys (serialized Buffer), reconstruct string
              if (Object.keys(value.data).every((k) => /^\d+$/.test(k))) {
                const bytes = Object.values(value.data) as number[];
                return { ...value, data: Buffer.from(bytes).toString("utf8") };
              }
            }
            return value;
          }),
        );
        console.log(`Markup: ${JSON.stringify(processedMarkup, null, 2)}`);
      }
    }
  }
}
