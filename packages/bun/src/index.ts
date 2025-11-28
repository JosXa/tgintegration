export * from "@tgintegration/core";

import { TelegramClient } from "@mtcute/bun";

export function createBot(options: {
  apiId: number;
  apiHash: string;
  phone: string;
}) {
  const client = new TelegramClient(options);
  return {
    client,
    async start() {
      await client.start();
    },
    async stop() {
      await client.disconnect();
    },
    async getChat(username: string) {
      return await client.resolvePeer(username);
    },
  };
}
