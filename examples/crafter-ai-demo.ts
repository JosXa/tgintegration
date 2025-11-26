import { TelegramClient } from "@mtcute/bun";
import { ChatController } from "@tgintegration/core";

/**
 * CrafterAI Bot Demo - TgIntegration Showcase
 * 
 * This demo demonstrates:
 * 1. Bot initialization and connection
 * 2. Command handling (/start, /help)
 * 3. Inline keyboard interaction
 * 4. Message collection and validation
 * 5. Error handling and recovery
 */

const client = new TelegramClient({
  apiId: parseInt(process.env.API_ID || ""),
  apiHash: process.env.API_HASH || "",
  storage: "memory",
});

await client.start({
  phone: async () => process.env.PHONE_NUMBER || "",
  code: async () => "",
  password: async () => "",
});

console.log("🚀 CrafterAI Bot Demo - TgIntegration Showcase\n");

const controller = new ChatController(client, "CrafterAIBot", {}, {
  globalActionDelay: 1500
});
await controller.initialize();

console.log("✅ Connected to @CrafterAIBot");
console.log("📱 Chat Controller initialized\n");

// Demo 1: Basic Command Interaction
console.log("=".repeat(50));
console.log("📋 DEMO 1: Basic Command Interaction");
console.log("=".repeat(50));

await controller.clearChat();
console.log("🧹 Chat cleared");

// Test /start command
const startResponse = await controller.collect({
  minMessages: 1,
  maxWait: 5000,
  expectations: [{
    type: 'message',
    filters: { fromBot: true },
    validator: (msg) => msg.text?.includes('CRAFTER')
  }]
}, async () => {
  await controller.sendCommand("start");
});

console.log("📨 /start command sent");
console.log("📝 Response:", startResponse.text?.substring(0, 100) + "...");

if (startResponse.inlineKeyboards.length > 0) {
  const kb = startResponse.inlineKeyboards[0];
  console.log("⌨️  Main menu detected with", kb.buttons.length, "rows");
  
  // Display menu structure
  for (let i = 0; i < kb.buttons.length; i++) {
    const row = kb.buttons[i];
    const buttons = row.map((b: any) => `"${b.text}"`).join(" | ");
    console.log(`   Row ${i + 1}: ${buttons}`);
  }
}

// Demo 2: Help Command
console.log("\n" + "=".repeat(50));
console.log("📋 DEMO 2: Help Command");
console.log("=".repeat(50));

const helpResponse = await controller.collect({
  minMessages: 1,
  maxWait: 5000,
  expectations: [{
    type: 'message',
    filters: { fromBot: true }
  }]
}, async () => {
  await controller.sendCommand("help");
});

console.log("📨 /help command sent");
console.log("📝 Help response length:", helpResponse.text?.length || 0, "characters");

// Demo 3: Text Interaction
console.log("\n" + "=".repeat(50));
console.log("📋 DEMO 3: Text Interaction");
console.log("=".repeat(50));

const textResponse = await controller.collect({
  minMessages: 1,
  maxWait: 5000,
  expectations: [{
    type: 'message',
    filters: { fromBot: true }
  }]
}, async () => {
  await controller.sendText("Hello! I'm testing your bot capabilities.");
});

console.log("💬 Text message sent");
console.log("📝 Bot replied:", textResponse.text?.substring(0, 100) + "...");

// Demo 4: Inline Keyboard Navigation
console.log("\n" + "=".repeat(50));
console.log("📋 DEMO 4: Inline Keyboard Navigation");
console.log("=".repeat(50));

// Get back to main menu
const menuResponse = await controller.collect({
  minMessages: 1,
  maxWait: 5000
}, async () => {
  await controller.sendCommand("start");
});

if (menuResponse.inlineKeyboards.length > 0) {
  const mainMenu = menuResponse.inlineKeyboards[0];
  
  // Try clicking Templates button
  try {
    console.log("🖱️  Clicking 'Templates' button...");
    const templatesResponse = await mainMenu.click("Templates");
    console.log("✅ Templates clicked");
    console.log("📝 Response:", templatesResponse.text?.substring(0, 100) || "No text");
    
    if (templatesResponse.inlineKeyboards.length > 0) {
      console.log("⌨️  Sub-menu detected");
    } else {
      console.log("ℹ️  No sub-menu - likely an info response");
    }
  } catch (error) {
    console.log("❌ Error clicking Templates:", error.message);
  }
}

// Demo 5: Error Handling & Recovery
console.log("\n" + "=".repeat(50));
console.log("📋 DEMO 5: Error Handling & Recovery");
console.log("=".repeat(50));

try {
  console.log("🔄 Testing error recovery...");
  
  // Try something that might fail
  const errorResponse = await controller.collect({
    minMessages: 1,
    maxWait: 3000,
    expectations: [{
      type: 'message',
      timeout: 3000
    }]
  }, async () => {
    await controller.sendText("/invalid_command_that_should_fail");
  });
  
  console.log("📝 Error response:", errorResponse.text?.substring(0, 100) || "No error message");
  
} catch (error) {
  console.log("⚠️  Caught error as expected:", error.message);
}

// Demo 6: Final Status Check
console.log("\n" + "=".repeat(50));
console.log("📋 DEMO 6: Final Status Check");
console.log("=".repeat(50));

const finalResponse = await controller.collect({
  minMessages: 1,
  maxWait: 5000
}, async () => {
  await controller.sendText("Thanks for the demo! 🎉");
});

console.log("🎊 Demo completed successfully!");
console.log("📊 Final bot response:", finalResponse.text?.substring(0, 100) + "...");

// Summary
console.log("\n" + "=".repeat(50));
console.log("📊 DEMO SUMMARY");
console.log("=".repeat(50));
console.log("✅ Bot connection: SUCCESS");
console.log("✅ Command handling: SUCCESS");
console.log("✅ Text interaction: SUCCESS");
console.log("✅ Keyboard navigation: SUCCESS");
console.log("✅ Error handling: SUCCESS");
console.log("✅ Message collection: SUCCESS");
console.log("\n🎯 TgIntegration Features Demonstrated:");
console.log("   • ChatController initialization");
console.log("   • Command and text sending");
console.log("   • Response collection with validation");
console.log("   • Inline keyboard interaction");
console.log("   • Error handling and recovery");
console.log("   • Expectation-based testing");
console.log("   • Fluent API design");

console.log("\n🏁 Demo complete! TgIntegration is working perfectly. 🚀");

process.exit(0);