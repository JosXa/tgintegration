# tgintegration

An integration test and automation library for [Telegram Bots](https://core.telegram.org/bots) based on [mtcute](https://github.com/mtcute/mtcute). Written in TypeScript.
<br />**Test your bot in realtime scenarios!**

**Are you a user of tgintegration?** I'm actively looking for feedback and ways to improve the library, come and let me know in the [official group](https://t.me/tgintegration)!

[![JSR](https://jsr.io/badges/@tgintegration/core)](https://jsr.io/@tgintegration/core)
[![NPM](https://img.shields.io/npm/v/@tgintegration/core)](https://www.npmjs.com/package/@tgintegration/core)
![GitHub top language](https://img.shields.io/github/languages/top/josxa/tgintegration)
[![GitHub Workflow Status (branch)](https://img.shields.io/github/actions/workflow/status/josxa/tgintegration/ci.yml?branch=main)](https://github.com/JosXa/tgintegration/actions/workflows/ci.yml)

[Features](#features) • [Prerequisites](#prerequisites) • [Installation](#installation) • [**Quick Start Guide**](#quick-start-guide) • [Test Frameworks](#integrating-with-test-frameworks)

- 📖 [Documentation](https://josxa.github.io/tgintegration/)
- 👥 [Telegram Chat](https://t.me/tgintegration)
- 📄 Free software: [MIT License](https://tldrlegal.com/license/mit-license)

## Features

<!-- ▶️ [**See it in action!** 🎬](https://josxa.github.io/tgintegration/#see-it-in-action) (coming soon) -->

- 👤 Log into a Telegram user account and interact with bots or other users
- ✅ Write **realtime integration tests** to ensure that your bot works as expected! ▶️ [Bun Test examples](https://github.com/JosXa/tgintegration/tree/master/examples/bun-test)
- ⚡️ **Automate any interaction** on Telegram! ~~▶️ [Automatically play @IdleTownBot](https://github.com/JosXa/tgintegration/blob/master/examples/automation/like-bot.ts)~~ | [More examples](https://github.com/JosXa/tgintegration/tree/master/examples/automation)
- 🛡 Fully typed
- 🚀 **Runtime agnostic** - Works with Bun, Node.js, and Deno
- 📦 **ES modules** only - Modern ESM JavaScript ecosystem
- 🧪 Built with high test coverage and modern tooling

## Prerequisites

- A [Telegram API key](https://docs.mtcute.dev/getting-started/setup#api-keys).
- A [signed in mtcute Telegram Client](https://mtcute.dev/guide/intro/sign-in.html#signing-in-1)
- **Node.js 18+**, **Bun 1.0+**, or **Deno 1.40+**
- **TypeScript 5.0+** (recommended)

## Installation

### Bun

```bash
bun add @tgintegration/core @tgintegration/bun
```

### Node.js

```bash
npm add @tgintegration/core @tgintegration/node
```

### Deno

```bash
deno add jsr:@tgintegration/core
```

### JSR (Universal)

```bash
npx jsr add @tgintegration/core
```

## Quick Start Guide

_You can [follow along by running the example](https://github.com/JosXa/tgintegration/blob/master/examples/readme-example.ts) ([README](https://github.com/JosXa/tgintegration/blob/master/examples/README.md))_

### Setup

Suppose we want to write integration tests for [@BotListBot](https://t.me/BotListBot) by sending it a couple of
messages and checking that it responds the way it should.

After [configuring an mtcute **user client**](https://docs.mtcute.dev/getting-started/setup),
let's start by creating a `ChatController`:

```typescript
import { ChatController } from "@tgintegration/core";
import { TelegramClient } from "@mtcute/bun";

const client = new TelegramClient({
  apiId: 12345, // Your API ID
  apiHash: "abc123", // Your API hash
  storage: "session.db",
});

const controller = new ChatController(client, "@BotListBot", {
  maxWait: 8000, // Maximum timeout for responses (optional)
  globalActionDelay: 2500, // Delay between actions for observation (optional)
});

await controller.initialize();
await controller.clearChat(); // Start with a blank screen (⚠️)
```

Now, let's send `/start` to the bot and wait until exactly three messages have been received by using the `collect` method with a callback:

```typescript
const response = await controller.collect(
  {
    numMessages: 3,
    maxWait: 8000,
  },
  async () => {
    await controller.sendCommand("start");
  }
);

console.log(`Received ${response.count} messages`);
console.log("First message is a sticker:", response.messages[0].media?.type === "sticker");
```

The result should look like this:

![image](https://raw.githubusercontent.com/JosXa/tgintegration/master/docs/assets/start_botlistbot.png)

Examining the buttons in the response...

```typescript
// Get the inline keyboard and examine its buttons
const inlineKeyboard = response.inlineKeyboards[0];
console.log("Three buttons in the first row:", inlineKeyboard.buttons[0].length === 3);
```

We can also press the inline keyboard buttons, for example based on a regular expression:

```typescript
const examples = await inlineKeyboard.click(/.*Examples/);
```

As the bot edits the message, `.click()` automatically listens for "message edited" updates and returns
the new state as another `Response`.

![image](https://raw.githubusercontent.com/JosXa/tgintegration/master/docs/assets/examples_botlistbot.png)

```typescript
console.log("Found examples text:", examples.fullText.includes("Examples for contributing to the BotList"));
```

### Error handling

So what happens when we send an invalid query or the peer fails to respond?

The following instruction will raise an `InvalidResponseError` after `maxWait` seconds.
This is because we passed `throwOnTimeout: true` in the collect options.

```typescript
import { InvalidResponseError } from "@tgintegration/core";

try {
  await controller.collect(
    {
      maxWait: 8000,
      throwOnTimeout: true,
    },
    async () => {
      await controller.sendCommand("ayylmao");
    }
  );
} catch (e) {
  if (e instanceof InvalidResponseError) {
    console.log("Expected timeout occurred");
  }
}
```

Let's explicitly set `throwOnTimeout` to `false` so that no exception occurs:

```typescript
const noReplyResponse = await controller.collect(
  {
    maxWait: 3000,
    throwOnTimeout: false,
  },
  async () => {
    await controller.client.sendText(controller.peer, "Henlo Fren");
  }
);

if (noReplyResponse.isEmpty) {
  console.log("No response received as expected");
}
```

## Integrating with Test Frameworks

### Bun Test (Recommended)

Bun Test is the recommended test framework for use with **tgintegration**. You can
[browse through several examples](https://github.com/JosXa/tgintegration/tree/master/examples/bun-test)
and **tgintegration** also uses Bun Test for its own test suite.

```typescript
import { test, expect } from "bun:test";
import { ChatController } from "@tgintegration/core";

test("bot should respond to /start", async () => {
  const controller = new ChatController(client, "@MyBot");
  await controller.initialize();

  const response = await controller.collect(
    { minMessages: 1 },
    async () => await controller.sendCommand("start")
  );

  expect(response.count).toBeGreaterThan(0);
});
```

### Node.js Test Runner

**tgintegration** is runner-agnostic and works perfectly with Node.js's built-in test runner:

```typescript
import { test } from "node:test";
import { strict as assert } from "node:assert";
import { ChatController } from "@tgintegration/core";

test("bot should respond to /start", async () => {
  const controller = new ChatController(client, "@MyBot");
  await controller.initialize();

  const response = await controller.collect(
    { minMessages: 1 },
    async () => await controller.sendCommand("start")
  );

  assert(response.count > 0);
});
```

### Deno Test

Deno users can enjoy the same seamless experience:

```typescript
import { test } from "deno:test";
import { assertEquals } from "std/assert";
import { ChatController } from "@tgintegration/core";

test("bot should respond to /start", async () => {
  const controller = new ChatController(client, "@MyBot");
  await controller.initialize();

  const response = await controller.collect(
    { minMessages: 1 },
    async () => await controller.sendCommand("start")
  );

  assertEquals(response.count > 0, true);
});
```

## Architecture

**tgintegration** follows a monorepo structure with platform-specific packages:

- `@tgintegration/core` - Main library logic (platform agnostic)
- `@tgintegration/bun` - Bun-specific optimizations and entry point
- `@tgintegration/node` - Node.js compatibility layer
- `@tgintegration/deno` - Deno compatibility and JSR publishing