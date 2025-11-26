import { createClient } from "./utils.js";
import { ChatController } from "@tgintegration/core";

/**
 * Automation script for @CrafterAIBot
 * 
 * Demonstrates TgIntegration features:
 * - ChatController initialization with bot username
 * - Sending commands and text messages
 * - Collecting responses with expectations
 * - Working with inline keyboards
 */
async function main() {
  console.log("Automating @CrafterAIBot with TgIntegration...\n");
  
  const client = await createClient();

  // Create ChatController for the bot
  const controller = new ChatController(client, "CrafterAIBot", {}, {
    globalActionDelay: 2000 // 2s delay between actions
  });

  await controller.initialize();
  console.log("ChatController initialized for @CrafterAIBot");

  // Clear chat to start fresh
  console.log("\nClearing chat...");
  await controller.clearChat();

  // Test 1: /start command
  console.log("\n--- Test 1: /start command ---");
  const startResponse = await controller.collect({ 
    minMessages: 1, 
    maxMessages: 5,
    maxWait: 10000 
  }, async () => {
    await controller.sendCommand("start");
  });

  console.log(`Received ${startResponse.count} messages`);
  if (startResponse.messages.length > 0) {
    console.log("Welcome message:", startResponse.messages[0].text?.substring(0, 80) + "...");
  }

  // Explore inline keyboards
  if (startResponse.inlineKeyboards.length > 0) {
    const kb = startResponse.inlineKeyboards[0];
    console.log(`\nFound inline keyboard with ${kb.buttons.length} rows:`);
    
    for (let row = 0; row < kb.buttons.length; row++) {
      const buttonTexts = kb.buttons[row].map(b => `"${b.text}"`).join(", ");
      console.log(`  Row ${row + 1}: ${buttonTexts}`);
    }

    // Click first button
    if (kb.buttons[0]?.length > 0) {
      const firstButton = kb.buttons[0][0];
      console.log(`\nClicking button: "${firstButton.text}"...`);
      
      try {
        const buttonResponse = await kb.click(firstButton.text);
        console.log(`Button response: ${buttonResponse.count} messages`);
        if (buttonResponse.text) {
          console.log("Response:", buttonResponse.text.substring(0, 80) + "...");
        }
      } catch (e: any) {
        console.log("Could not click button:", e.message);
      }
    }
  }

  // Test 2: /help command
  console.log("\n--- Test 2: /help command ---");
  const helpResponse = await controller.collect({
    minMessages: 1,
    maxMessages: 3,
    maxWait: 6000
  }, async () => {
    await controller.sendCommand("help");
  });

  console.log(`Received ${helpResponse.count} messages`);
  if (helpResponse.messages.length > 0) {
    console.log("Help text:", helpResponse.messages[0].text?.substring(0, 150) + "...");
  }

  // Test 3: Text interaction
  console.log("\n--- Test 3: Text message ---");
  const textResponse = await controller.collect({
    minMessages: 1,
    maxMessages: 3,
    maxWait: 8000
  }, async () => {
    await controller.sendText("What games do you support?");
  });

  console.log(`Received ${textResponse.count} messages`);
  if (textResponse.messages.length > 0) {
    console.log("Bot reply:", textResponse.messages[0].text?.substring(0, 100) + "...");
  }

  console.log("\n--- Automation Complete ---");
  console.log("Successfully tested:");
  console.log("  - /start command with inline keyboard exploration");
  console.log("  - /help command");
  console.log("  - Text message interaction");
  
  process.exit(0);
}

await main();
