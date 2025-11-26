import type { Message } from "@mtcute/core";
import type { tl } from "@mtcute/tl";
import { InvalidResponseError } from "./errors.js";
import { InlineResult } from "./inline-result.js";
import { InlineResultContainer } from "./inline-result-container.js";
import type { ChatControllerOptions } from "./options.js";
import { Response } from "./response.js";
import type { AnyTelegramClient, CollectOptions } from "./types.js";

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

export class ChatController {
  private _peerIdResolved?: number;
  private _lastActionTime: number = 0;
  public readonly globalActionDelay: number;

  constructor(
    public readonly client: AnyTelegramClient,
    public readonly peer: string | number,
    public readonly defaults: CollectOptions & ChatControllerOptions = {},
  ) {
    this.globalActionDelay = this.defaults.globalActionDelay ?? 800;
  }

  async initialize() {
    // We assume start() is safe to call or check if connected
    // TelegramClient (highlevel) usually doesn't expose simple isConnected
    // We can try accessing network.isConnected if available, but start() is robust.
    // For now, just call start({}) which should be idempotent or we catch error.
    try {
      await this.client.start({});
    } catch (e: unknown) {
      if (e instanceof Error && e.message?.includes("already connected")) {
        // ignore
      } else {
        // throw e;
        // actually start() might not throw if already connected, just return user.
      }
    }

    // Try to get as chat first (groups/channels), fallback to user (bots/private chats)
    try {
      const chat = await this.client.getFullChat(this.peer);
      this._peerIdResolved = chat.id;
    } catch (_e: unknown) {
      // If it's not a chat, try to get as user (for bots and private chats)
      try {
        const user = await this.client.getFullUser(this.peer);
        this._peerIdResolved = user.id;
      } catch (_e2: unknown) {
        throw new Error(`Could not resolve peer: ${this.peer}`);
      }
    }
  }

  private async ensurePreconditions() {
    if (!this._peerIdResolved) {
      await this.initialize();
    }
  }

  private async waitGlobalDelay() {
    if (this.globalActionDelay > 0 && this._lastActionTime > 0) {
      const now = Date.now();
      const elapsed = now - this._lastActionTime;
      const wait = this.globalActionDelay - elapsed;
      if (wait > 0) {
        await sleep(wait);
      }
    }
  }

  private updateLastActionTime() {
    this._lastActionTime = Date.now();
  }

  async sendCommand(command: string, args: string[] = []) {
    await this.ensurePreconditions();

    const text =
      args.length > 0 ? `/${command} ${args.join(" ")}` : `/${command}`;

    return this.client.sendText(this.peer, text);
  }

  /**
   * Sends a text message to the peer.
   */
  async sendText(text: string) {
    await this.ensurePreconditions();
    return this.client.sendText(this.peer, text);
  }

  /**
   * Clears the chat history with the peer.
   */
  async clearChat() {
    await this.ensurePreconditions();
    await this.client.deleteHistory(this.peer);
  }

  /**
   * Disconnects the underlying Telegram client.
   */
  async disconnect() {
    await this.client.disconnect();
  }

  /**
   * Pings the bot with /start (or custom messages) and waits for a response.
   */
  async pingBot(
    options: {
      messages?: string[];
      maxWait?: number;
      overridePeer?: string | number;
    } = {},
  ): Promise<Response> {
    const msgs = options.messages || ["/start"];

    return this.collect(
      {
        minMessages: 1,
        maxWait: options.maxWait,
      },
      async () => {
        for (const msg of msgs) {
          if (msg.startsWith("/")) {
            await this.sendCommand(msg.substring(1));
          } else {
            await this.client.sendText(this.peer, msg);
          }
          await sleep(1000); // Small delay between pings
        }
      },
    );
  }

  async collect(
    options: CollectOptions,
    action: () => Promise<void>,
  ): Promise<Response> {
    await this.ensurePreconditions();
    await this.waitGlobalDelay();

    const mergedOptions = { ...this.defaults, ...options } as CollectOptions & {
      minMessages?: number;
      maxMessages?: number;
      numMessages?: number;
    };
    const {
      minMessages: minMessagesOpt,
      maxMessages: maxMessagesOpt,
      numMessages,
      maxWait = 10000,
      waitConsecutive = undefined,
      throwOnTimeout = false,
      validators,
    } = mergedOptions;

    // Normalize numMessages to min/max if provided
    const minMessages =
      numMessages !== undefined ? numMessages : (minMessagesOpt ?? 1);
    const maxMessages =
      numMessages !== undefined ? numMessages : maxMessagesOpt;

    const messages: Message[] = [];
    let lastMessageTime = 0;

    const handler = (msg: Message) => {
      if (msg.chat.id === this._peerIdResolved) {
        messages.push(msg);
        lastMessageTime = Date.now();
      }
    };

    this.client.onNewMessage.add(handler);

    try {
      await action();

      const startTime = Date.now();

      while (true) {
        const now = Date.now();
        const elapsed = now - startTime;

        if (elapsed > maxWait) break;

        const count = messages.length;

        // Check maxMessages
        if (maxMessages !== undefined && count > maxMessages) break;

        // Check minMessages and validators
        const enoughCount = count >= minMessages;
        let passedValidators = true;
        if (validators) {
          passedValidators = validators(messages);
        }

        if (enoughCount && passedValidators) {
          if (waitConsecutive) {
            const silenceDuration = now - lastMessageTime;
            if (silenceDuration >= waitConsecutive) break;
          } else {
            break;
          }
        }

        await sleep(100);
      }
    } finally {
      this.client.onNewMessage.remove(handler);
      this.updateLastActionTime();
    }

    const count = messages.length;

    if (throwOnTimeout) {
      if (count < minMessages) {
        throw new InvalidResponseError(
          `Expected at least ${minMessages} messages, got ${count}`,
        );
      }
      if (maxMessages !== undefined && count > maxMessages) {
        throw new InvalidResponseError(
          `Expected at most ${maxMessages} messages, got ${count}`,
        );
      }
      if (validators && !validators(messages)) {
        throw new InvalidResponseError("Validators failed");
      }
    }

    return new Response(this, messages);
  }

  /**
   * Query a bot for inline results (user-side inline query).
   *
   * @param query - The search query text
   * @param options - Optional parameters for the inline query
   * @returns Container with inline results
   *
   * @example
   * ```typescript
   * const results = await controller.queryInline("cats", { limit: 50 });
   * const catGifs = results.findResults({ typePattern: /gif/ });
   * await catGifs[0].send();
   * ```
   */
  async inlineQuery(
    query: string,
    options: {
      latitude?: number;
      longitude?: number;
      limit?: number;
      offset?: string;
      paginationDelay?: number;
    } = {},
  ): Promise<InlineResultContainer> {
    await this.ensurePreconditions();

    const {
      latitude,
      longitude,
      limit = 100,
      offset = "",
      paginationDelay = 3000,
    } = options;

    if (limit <= 0) {
      throw new Error("limit must be greater than 0");
    }

    // Use raw TL method: messages.getInlineBotResults
    const botUser = await this.client.resolveUser(this.peer);
    const firstBatch = (await this.client.call({
      _: "messages.getInlineBotResults",
      bot: botUser,
      peer: await this.client.resolvePeer("me"),
      query,
      offset,
      geoPoint:
        latitude !== undefined && longitude !== undefined
          ? {
              _: "inputGeoPoint",
              lat: latitude,
              long: longitude,
            }
          : undefined,
    })) as tl.messages.RawBotResults;

    const allResults: InlineResult[] = [];
    let currentOffset = offset;
    let currentBatch = firstBatch;

    // Paginate through results if needed
    while (allResults.length < limit) {
      for (const result of currentBatch.results) {
        if (result._ === "botInlineResult") {
          allResults.push(new InlineResult(this, result, currentBatch.queryId));
        }
        if (allResults.length >= limit) break;
      }

      // Check if there are more results
      if (
        !currentBatch.nextOffset ||
        currentBatch.nextOffset === currentOffset
      ) {
        break;
      }

      // Wait before next pagination request to avoid flood wait
      await sleep(paginationDelay);

      currentOffset = currentBatch.nextOffset;
      currentBatch = (await this.client.call({
        _: "messages.getInlineBotResults",
        bot: botUser,
        peer: await this.client.resolvePeer("me"),
        query,
        offset: currentOffset,
        geoPoint:
          latitude !== undefined && longitude !== undefined
            ? {
                _: "inputGeoPoint",
                lat: latitude,
                long: longitude,
              }
            : undefined,
      })) as tl.messages.RawBotResults;
    }

    return new InlineResultContainer(
      this,
      query,
      allResults,
      currentBatch.gallery || false,
      currentBatch.switchPm,
      currentBatch.nextOffset,
    );
  }

  /**
   * Get the list of commands available for this bot.
   */
  async getBotCommands(): Promise<string[]> {
    await this.ensurePreconditions();

    try {
      const commands = await this.client.call({
        _: "bots.getBotCommands",
        bot: await this.client.resolveUser(this.peer),
        scope: { _: "botCommandScopeDefault" },
        langCode: "",
      });
      return commands.map((c: any) => c.command);
    } catch {
      return [];
    }
  }
}
