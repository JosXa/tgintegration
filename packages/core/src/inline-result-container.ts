import type { Message } from "@mtcute/core";
import type { tl } from "@mtcute/tl";
import type { ChatController } from "./chat-controller.js";
import type { InlineResult } from "./inline-result.js";

export class InlineResultContainer {
  constructor(
    private readonly controller: ChatController,
    public readonly query: string,
    public readonly results: InlineResult[],
    public readonly isGallery: boolean,
    private readonly switchPm?: tl.RawInlineBotSwitchPM,
    public readonly nextOffset?: string,
  ) {}

  /**
   * Filter results by various patterns.
   *
   * @param options - Filter options using regular expressions
   * @returns Filtered array of inline results
   *
   * @example
   * ```typescript
   * const results = await controller.queryInline("cats");
   * const catGifs = results.findResults({ typePattern: /gif/i });
   * const exactMatch = results.findResults({ titlePattern: /^Exact Title$/i });
   * ```
   */
  findResults(options: {
    titlePattern?: RegExp;
    descriptionPattern?: RegExp;
    typePattern?: RegExp;
    urlPattern?: RegExp;
  }): InlineResult[] {
    let filtered = this.results;

    if (options.titlePattern) {
      filtered = filtered.filter(
        (r) => r.title && options.titlePattern?.test(r.title),
      );
    }

    if (options.descriptionPattern) {
      filtered = filtered.filter(
        (r) => r.description && options.descriptionPattern?.test(r.description),
      );
    }

    if (options.typePattern) {
      filtered = filtered.filter((r) => options.typePattern?.test(r.type));
    }

    if (options.urlPattern) {
      filtered = filtered.filter(
        (r) => r.url && options.urlPattern?.test(r.url),
      );
    }

    return filtered;
  }

  /**
   * Whether the bot offers to switch to PM (private message).
   */
  get canSwitchPm(): boolean {
    return !!this.switchPm;
  }

  /**
   * Switch to PM with the bot using the provided start parameter.
   *
   * @returns The sent /start message
   * @throws Error if the inline query does not support switching to PM
   */
  async switchToPm(): Promise<Message> {
    if (!this.canSwitchPm || !this.switchPm) {
      throw new Error("This inline query does not allow switching to PM.");
    }

    const text = `/start ${this.switchPm.startParam || ""}`.trim();
    return this.controller.client.sendText(this.controller.peer, text);
  }

  /**
   * Total number of results in this container.
   */
  get count(): number {
    return this.results.length;
  }

  /**
   * Whether the container has no results.
   */
  get isEmpty(): boolean {
    return this.results.length === 0;
  }

  toString(): string {
    return `InlineResultContainer(query="${this.query}", count=${this.count}, gallery=${this.isGallery})`;
  }
}
