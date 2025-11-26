import { Message } from "@mtcute/core";
import type { ChatController } from "./chat-controller.js";
import { InlineKeyboard, type InlineKeyboardButton } from "./inline-keyboard.js";
import { ReplyKeyboard, type ReplyKeyboardButton } from "./reply-keyboard.js";

export class Response {
  constructor(
    private readonly controller: ChatController,
    public readonly messages: Message[]
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

  get text(): string | undefined {
    return this.first?.text;
  }

  getText(): string {
    return this.messages.map((m) => m.text).join("\n");
  }

  get inlineKeyboards(): InlineKeyboard[] {
    return this.messages
      .filter((m) => m.markup && 'type' in m.markup && m.markup.type === "inline")
      .map((m) => {
        const markup = m.markup as any; 
        
        const buttons = markup.buttons.map((row: any[]) => 
             row.map((btn: any) => ({
                 text: btn.text,
                 callbackData: btn.data ? Buffer.from(btn.data).toString('utf8') : undefined,
                 url: btn.url
             }))
        );

        return new InlineKeyboard(this.controller, m, buttons);
      });
  }

  get replyKeyboard(): ReplyKeyboard | undefined {
    for (let i = this.messages.length - 1; i >= 0; i--) {
      const m = this.messages[i];
      if (m.markup && 'type' in m.markup && m.markup.type === "reply") {
          const markup = m.markup as any;
          const buttons = markup.buttons.map((row: any[]) =>
                row.map((btn: any) => ({
                    text: btn.text
                }))
          );
          return new ReplyKeyboard(this.controller, m, buttons);
      }
    }
    return undefined;
  }

  debug(): void {
    console.log(`Response with ${this.count} message(s):`);
    for (let i = 0; i < this.messages.length; i++) {
      const msg = this.messages[i];
      const senderName = msg.sender && 'firstName' in msg.sender ? msg.sender.firstName || msg.sender.username : 'Unknown';
      console.log(`  [${i}] ${senderName}: ${msg.text || '[no text]'}`);
      if (msg.media) {
        console.log(`      Media: ${msg.media.type}`);
      }
      if (msg.markup) {
        const processedMarkup = JSON.parse(JSON.stringify(msg.markup, (key, value) => {
          if (value && typeof value === 'object' && 'data' in value && value.data && typeof value.data === 'object') {
            // If data is a Buffer-like object, convert to string
            if (Buffer.isBuffer(value.data)) {
              return { ...value, data: value.data.toString('utf8') };
            }
            // If data is an object with numeric keys (serialized Buffer), reconstruct string
            if (Object.keys(value.data).every(k => /^\d+$/.test(k))) {
              const bytes = Object.values(value.data) as number[];
              return { ...value, data: Buffer.from(bytes).toString('utf8') };
            }
          }
          return value;
        }));
        console.log(`      Markup: ${JSON.stringify(processedMarkup, null, 2)}`);
      }
    }
  }
}
