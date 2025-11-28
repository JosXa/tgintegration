import type { Message } from "@mtcute/core";
import { Long, type tl } from "@mtcute/core";
import type { ChatController } from "./chat-controller.js";

export class InlineResult {
  constructor(
    private readonly controller: ChatController,
    public readonly result: tl.RawBotInlineResult,
    private readonly queryId: Long,
  ) {}

  /**
   * Send this inline result to a chat.
   *
   * @param options - Options for sending the result
   * @returns The sent message (captured via collect)
   *
   * @example
   * ```typescript
   * const results = await controller.queryInline("cats");
   * await results.results[0].send({ chatId: "me" });
   * ```
   */
  async send(options?: {
    chatId?: string | number;
    disableNotification?: boolean;
    replyToMessageId?: number;
  }): Promise<Message> {
    const chatId = options?.chatId ?? this.controller.peer;

    // Use collect to capture the sent message
    const response = await this.controller.collect(
      {
        numMessages: 1,
        maxWait: 10000,
      },
      async () => {
        // Use raw TL method: messages.sendInlineBotResult
        await this.controller.client.call({
          _: "messages.sendInlineBotResult",
          peer: await this.controller.client.resolvePeer(chatId),
          randomId: Long.fromNumber(
            Math.floor(Math.random() * Number.MAX_SAFE_INTEGER),
          ),
          queryId: this.queryId,
          id: this.result.id,
          silent: options?.disableNotification,
          replyTo: options?.replyToMessageId
            ? {
                _: "inputReplyToMessage",
                replyToMsgId: options.replyToMessageId,
              }
            : undefined,
        });
      },
    );

    if (response.count === 0 || !response.first) {
      throw new Error("Failed to send inline result: no message received");
    }

    return response.first;
  }

  get id(): string {
    return this.result.id;
  }

  get title(): string | undefined {
    return this.result.title;
  }

  get description(): string | undefined {
    return this.result.description;
  }

  get fullText(): string {
    return `${this.title || ""}\n${this.description || ""}`.trim();
  }

  get url(): string | undefined {
    return this.result.url;
  }

  get type(): string {
    return this.result.type;
  }

  get thumb(): tl.TypeWebDocument | undefined {
    return this.result.thumb;
  }

  get content(): tl.TypeWebDocument | undefined {
    return this.result.content;
  }

  toString(): string {
    return `InlineResult(id=${this.id}, type=${this.type}, title=${this.title})`;
  }
}
