# Examples

This directory contains examples for `tgintegration`.

## Available Examples

- **`readme-example.ts`** - Basic usage example from the main README
- **`playground.ts`** - Experimental testing ground
- **`crafter-ai-demo.ts`** - Comprehensive showcase demonstrating all major features
- **`crafter-ai-bot.ts`** - Real-world automation script for @CrafterAIBot
- **`crafter-ai-complete-demo.ts`** - Complete capability analysis of @CrafterAIBot (ALL features)
- **`crafter-ai-interesting-workflow.ts`** - Most interesting workflow: Natural language processing with interactive buttons

## Prerequisites

1.  **Environment Variables**: Create a `.env` file in the root of the project (or export them) with your Telegram API credentials:
    ```env
    API_ID=123456
    API_HASH=your_api_hash
    SESSION_STRING=your_session_string
    ```
    You can obtain `API_ID` and `API_HASH` from [my.telegram.org](https://my.telegram.org).
    The `SESSION_STRING` can be generated using `scripts/create_session_strings.py` (legacy) or any mtcute session string generator.

2.  **Install Dependencies**:
    ```bash
    bun install
    ```

## Running Examples

Run the examples using `bun`:

```bash
# Run the README example
bun examples/readme-example.ts

# Run the playground example
bun examples/playground.ts

# Run the CrafterAI Bot demo (comprehensive showcase)
bun examples/crafter-ai-demo.ts

# Run the CrafterAI automation script
bun examples/crafter-ai-bot.ts

# Run the complete CrafterAI capability analysis
bun examples/crafter-ai-complete-demo.ts

# Run the most interesting workflow demo (NLP + buttons)
bun examples/crafter-ai-interesting-workflow.ts
```
