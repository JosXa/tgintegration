# Panda Quiz Bot

An example bot that automates playing the @PandaQuizEnBot quiz using AI.

## Features

- Connects to @PandaQuizEnBot on Telegram
- Sends `/start` and `/quiz` commands to begin the quiz
- Uses GPT-4o-mini to analyze quiz questions and provide answers
- Structured output using Zod schemas for reliable answer extraction

## Setup

1. Install dependencies:
   ```bash
   bun install
   ```

2. Set up environment variables in your `.env` file:
   ```
   API_ID=your_telegram_api_id
   API_HASH=your_telegram_api_hash
   PHONE_NUMBER=your_phone_number
   SESSION_STRING=your_session_string
   OPENAI_API_KEY=your_openai_api_key
   ```

## Usage

Run the bot:
```bash
bun run start
```

Or run in development mode with hot reload:
```bash
bun run dev
```

## How it works

1. Initializes a Telegram client using the shared utils
2. Creates a ChatController for @PandaQuizEnBot
3. Clears the chat and sends `/start` to explore the bot
4. Sends `/quiz` to start a quiz question
5. Extracts the question from the bot's response
6. Uses AI to analyze the question and generate an answer
7. Sends the answer back to the bot
8. Collects and displays the result

## Dependencies

- `@tgintegration/core` - Core Telegram integration functionality
- `@ai-sdk/openai` - OpenAI provider for Vercel AI SDK
- `ai` - Vercel AI SDK for structured generation
- `zod` - Schema validation for structured outputs