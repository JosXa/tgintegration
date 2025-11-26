import { TelegramClient } from "@mtcute/bun";
import { ChatController, type CollectOptions } from "@tgintegration/core";

export async function createClient() {
  const apiId = parseInt(process.env.API_ID || "");
  const apiHash = process.env.API_HASH || "";
  const session = process.env.SESSION_STRING || "";

  if (!apiId || !apiHash) {
    throw new Error("Please set API_ID and API_HASH environment variables.");
  }

  // Use file storage with session import (like in test-client.ts)
  const dbPath = "./examples/session.db";
  
  const client = new TelegramClient({
    apiId,
    apiHash,
    storage: dbPath,
  });

  await client.connect();
  
  if (session) {
    await client.importSession(session, true);
  }

  return client;
}
