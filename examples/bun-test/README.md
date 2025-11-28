# TgIntegration Bun Test Example

A simple test suite demonstrating how to use TgIntegration with Bun's native test runner.

This example automates the [@like](https://t.me/like) bot - sending messages and interacting with inline keyboards.

## Running Tests

```bash
bun test
```

## Environment Variables

You'll need to set the following environment variables:

- `API_ID` - Your Telegram API ID
- `API_HASH` - Your Telegram API hash
- `SESSION_STRING` - Your exported Telegram session string
