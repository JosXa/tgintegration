import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { TelegramClient } from "@mtcute/bun";
import * as dotenv from "dotenv";

// Load .env from project root
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectRoot = resolve(__dirname, "..");

dotenv.config({ path: resolve(projectRoot, ".env") });

export async function createClient() {
  const apiId = process.env.API_ID;
  const apiHash = process.env.API_HASH;
  const phone = process.env.PHONE_NUMBER;
  const session = process.env.SESSION_STRING;

  if (!apiId || !apiHash) {
    throw new Error("Please set API_ID and API_HASH environment variables.");
  }

  if (!phone && !session) {
    throw new Error(
      "Please set either PHONE_NUMBER or SESSION_STRING environment variable.",
    );
  }

  // Use file storage with session import (like in test-client.ts)
  const dbPath = resolve(projectRoot, "examples", "session.db");

  const client = new TelegramClient({
    apiId: parseInt(apiId, 10),
    apiHash,
    storage: dbPath,
  });

  if (session) {
    await client.importSession(session, true);
  }

  await client.start({ phone });

  if (!session) {
    const sessionString = await client.exportSession();
    console.log(
      `Please add your session string to .env:\n\nSESSION_STRING=${sessionString}\n`,
    );
  }

  return client;
}
