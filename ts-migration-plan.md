# TypeScript Migration Plan

## Project Vision & Requirements
**TgIntegration** is a dual-purpose library for **Integration Testing** and **Automation** of Telegram interactions. It treats Telegram chats like web pages, allowing developers to script interactions ("Do X, expect Y") in a robust, runner-agnostic way (Bun, Node, Deno). It effectively acts as "Playwright for Telegram".

### Key Requirements
1.  **Stack Migration**: Rewrite from Python (Pyrogram) to **TypeScript (Strict Mode)** using **mtcute** as the Telegram client.
2.  **Monorepo Structure**:
    *   Root: `tgintegration` (Bun workspace)
    *   `packages/core`: Main library logic (`@tgintegration/core`).
    *   `packages/bun`, `packages/node`, `packages/deno`: Platform-specific entry points (`@tgintegration/*`).
3.  **API Architecture**:
    *   **Action-Wrapper Pattern**: The primary API `collect(options, action)` ensures event listeners are attached *before* actions occur, eliminating race conditions.
    *   **Page Object Model**: `ChatController` wraps an *existing* `mtcute` client instance, scoping interactions to a specific chat/peer without hiding the underlying client.
    *   **Runner Agnostic**: The library must not rely on runner-specific plugins (like Vitest environments). It uses standard Promises and Errors for control flow, compatible with Bun Test, Node Test Runner, and Deno Test.
4.  **Tooling**:
    *   **Runtime**: Bun.
    *   **Linting/Formatting**: Biome.
    *   **Documentation**: VitePress.
    *   **CI/CD**: GitHub Actions for testing and publishing to JSR & NPM.

## Overview
**Note**: The legacy Python codebase has been moved to the `archive/` directory. Please refer to it for logic porting and historical context.

This document outlines the plan to rewrite `tgintegration` from Python (Pyrogram) to TypeScript (mtcute), utilizing a modern stack including Bun, Biome, VitePress, and GitHub Actions.

## Target Stack
- **Language:** TypeScript (Strict Mode)
- **Runtime:** Bun
- **Architecture:** Monorepo (Workspaces)
- **Telegram Client:** [mtcute](https://github.com/mtcute/mtcute)
- **Testing:** `bun test`
- **Linter/Formatter:** Biome
- **Documentation:** VitePress
- **Package Management:** ESM only
- **Registry:** JSR (primary), NPM (via bun publish)

## Phase 1: Project Initialization
- [ ] **Initialize Bun Monorepo**: 
    - Run `bun init`.
    - Configure `package.json` workspaces: `["packages/*"]`.
- [ ] **Configure Tools**:
    - **TypeScript**: Root `tsconfig.json` (base config) + Package-level configs.
    - **Biome**: Root `biome.json`.
- [ ] **Directory Structure**:
    ```
    ├── package.json       # Root workspace config
    ├── bun.lockb
    ├── tsconfig.json      # Base TS config
    ├── biome.json         # Lint/Format config
    ├── packages/
    │   ├── core/          # Main library logic (platform agnostic)
    │   ├── bun/           # Bun entry point & adapters
    │   ├── node/          # Node.js entry point & adapters
    │   └── deno/          # Deno entry point & adapters
    ├── docs/              # VitePress docs
    └── examples/          # Examples
    ```

## Phase 2: Core Library Migration (`packages/core`)
- [ ] **Setup Package**: Create `packages/core/package.json` (name: `@tgintegration/core`).
- [ ] **Install Dependencies**: `mtcute` (core).
- [ ] **Port `ChatController`**:
    - **Architecture**: "Page Object" pattern.
        - Class `ChatController` wraps an *existing* `mtcute.TelegramClient` instance (passed in constructor).
        - Scoped to a specific chat (peer).
    - Implement `initialize`, `ensurePreconditions`.
    - Port `send_command` and `ping_bot`.
- [ ] **Port `MessageRecorder`**:
    - Implement message capture logic using `mtcute` updates.
    - Handle concurrency using `bun`'s async primitives or standard `Promise` logic.
- [ ] **Port `collect` (Core Logic)**:
    - **API Design**: Adopt the "Action-Wrapper" pattern: `collect(options, action)`.
        - Starts recording updates.
        - Awaits the `action` callback.
        - Waits for `expectations` (count, timeout, etc.) to be met.
        - Returns `Promise<Response>`.
    - This serves as the safe primitive for both testing and internal automation helpers.
- [ ] **Port Containers (Automation Layer)**:
    - `Response`: Wrapper for captured messages with rich accessors.
    - `InlineKeyboard` / `ReplyKeyboard`: 
        - Implement `.click()` methods that *internally use `collect`*.
        - This provides the fluent "Playwright-like" automation API (e.g., `await keyboard.click("Next")` returns the next Response).
    - Ensure strict typing for all Telegram objects.
- [ ] **Port `Expectation`**:
    - Logic for `min_messages`, `max_messages`.

## Phase 3: Runtime Packages
- [ ] **`packages/bun`**:
    - Package name: `@tgintegration/bun`
    - Export `core`.
    - Implement Bun-specific test runner integration if needed.
- [ ] **`packages/node`**:
    - Package name: `@tgintegration/node`
    - Export `core`.
    - Ensure Node.js compatibility (ESM).
- [ ] **`packages/deno`**:
    - Package name: `@tgintegration/deno`
    - Export `core`.
    - Configure for JSR publishing.

## Phase 4: Testing Infrastructure
- [ ] **Setup Test Environment**:
    - Create `setup.ts` for global test configuration.
    - Implement a `createTestController` helper (fixture-like).
- [ ] **Migrate Tests**:
    - Port `tests/integration/test_basic.py` to `packages/core/tests/basic.test.ts`.
    - Verify `collect` works as expected with `bun test`.

## Phase 5: Documentation (VitePress)
- [ ] **Initialize VitePress**: Setup in `docs/`.
- [ ] **Migrate Content**:
    - Convert `mkdocs.yml` navigation to `.vitepress/config.mts`.
    - Convert Markdown files from `docs/` to VitePress format.
    - Rewrite code blocks in documentation to TypeScript.
- [ ] **API Documentation**:
    - Investigate tools for generating API docs from TS comments (e.g., TypeDoc) or write manual API references if preferred.

## Phase 5: Examples & CI/CD
- [ ] **Migrate Examples**:
    - Rewrite `examples/` scripts to TypeScript using the new library (consuming `packages/core`).
- [ ] **GitHub Actions**:
    - Create `test.yml` to run `bun test` and `biome check` across workspaces.
    - Create `publish.yml` to publish to JSR/NPM on release.

## Key Implementation Details
- **Async Context Managers**: TypeScript doesn't have direct equivalent to Python's `async with`.
    - *Solution*: Use the callback pattern or `try/finally` blocks, or a helper function like `await controller.collect(options, async (controller) => { ... })`.
- **Transient Handlers**: `mtcute` allows dynamic handler registration. We will need to ensure handlers are strictly removed after collection to prevent memory leaks or unexpected behavior.

## Next Steps
1. Initialize the repository structure.
2. Begin implementation of `BotController` and `collect`.
