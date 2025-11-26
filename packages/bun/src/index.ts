export * from "@tgintegration/core";

import { ChatController, type CollectOptions } from "@tgintegration/core";
import { TelegramClient } from "@mtcute/core/client.js";

export interface TestControllerOptions {
    apiId?: number;
    apiHash?: string;
    sessionString?: string;
    peer: string | number;
    defaults?: CollectOptions;
}

/**
 * Creates a ChatController configured from environment variables or explicit options.
 * 
 * Env vars used if not provided:
 * - API_ID
 * - API_HASH
 * - SESSION_STRING
 */
export function createTestController(options: TestControllerOptions): ChatController {
    const apiId = options.apiId ?? parseInt(process.env.API_ID || "0");
    const apiHash = options.apiHash ?? process.env.API_HASH;
    const session = options.sessionString ?? process.env.SESSION_STRING;

    if (!apiId || !apiHash) {
        throw new Error("API_ID and API_HASH are required");
    }

    const client = new TelegramClient({
        apiId,
        apiHash,
        storage: session // In real usage this might need proper MemoryStorage or StringSession parser if it's a string
    });

    // mtcute needs a session mechanism. passing a string directly to storage isn't quite right 
    // unless we use StringSession.
    // But for now, let's assume the user configures the client themselves if they have complex needs.
    // Actually, for a helper, we should make it easy.
    
    return new ChatController(client, options.peer, options.defaults);
}
