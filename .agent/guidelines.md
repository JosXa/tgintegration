---
alwaysApply: true
---

## Project Guidelines

### Architecture & Design

**TgIntegration** is a TypeScript library for Telegram integration testing and automation

### Technology Stack

- **Language**: TypeScript (Strict Mode only)
- **Runtime**: Bun (primary), Node.js and Deno support
- **Telegram Client**: mtcute (not Pyrogram)
- **Testing**: `bun test`
- **Linting/Formatting**: Biome
- **Package Management**: ESM only
- **Registry**: JSR, NPM
- **Targets**: Deno, NPM, Bun, NodeJS

### Implementation Guidelines

#### Core Components
- **ChatController**: Implements "Page Object" pattern, wraps mtcute client
- **collect()**: Core primitive for safe action-execution with expectation handling
- **Containers**: Response, InlineKeyboard, ReplyKeyboard with fluent automation API
- **MessageRecorder**: Handles message capture using mtcute updates

#### API Design
- Use callback pattern instead of Python's `async with`: `await controller.collect(options, async (controller) => { ... })`
- Ensure transient handlers are strictly removed after collection to prevent memory leaks
- All keyboard interactions should internally use `collect()` for safety
- Maintain strict typing for all Telegram objects

#### Testing
- Use `bun test` for all testing
- Create `createTestController` helper for test fixtures
- Port integration tests to TypeScript in `packages/core/tests/`

#### Migration Notes
- Legacy Python code is in `archive/` directory for reference
- Port logic from Python Pyrogram to TypeScript mtcute
- Convert all documentation code blocks to TypeScript
- Ensure ESM compatibility across all packages

### Development Workflow

1. **Initialize**: Use Bun workspaces with proper package.json configuration
2. **Develop**: Implement core logic in `packages/core`, platform adapters in runtime packages
3. **Test**: Use `bun test` with Biome linting
4. **Document**: Use VitePress for documentation
5. **Publish**: JSR first, then NPM via `bun publish`

### Code Quality

- **REQUIRED: Run `bun run ai:check` after concluding changes** - This command runs formatting fixes, typechecks, and tests across the entire monorepo
  - You MUST run this after concluding changes
  - You SHOULD run this intermediarily during development to catch issues early
  - The build will fail if formatting, type errors, or test failures are detected
  - Never skip this step - it ensures code quality and prevents breaking changes
- Use `bun run format` to check formatting without making changes
- Biome handles both linting and formatting with unsafe fixes enabled

### Key Constraints

- **No runner-specific plugins** - keep library framework agnostic
- **Strict TypeScript mode** only
- **ESM modules** only - no CommonJS
- **mtcute client** - do not use other Telegram libraries
- **Bun as primary runtime** - ensure compatibility but optimize for Bun