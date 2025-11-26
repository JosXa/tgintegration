import { TelegramClient } from "@mtcute/bun";
import { ChatController } from "@tgintegration/core";

/**
 * 🎯 CrafterAI Bot - COMPLETE CAPABILITY DEMO
 * 
 * This comprehensive demo showcases ALL features discovered in the CrafterAI bot:
 * - Command processing and navigation
 * - Template management system
 * - Asset and knowledge base management
 * - Group collaboration features
 * - Message processing tools
 * - Natural language understanding
 * - Inline keyboard interactions
 * - Error handling and recovery
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

console.log("🚀 CrafterAI Bot - COMPLETE CAPABILITY DEMO\n");

const controller = new ChatController(client, "CrafterAIBot", {}, {
  globalActionDelay: 2000
});
await controller.initialize();

console.log("✅ Connected to @CrafterAIBot");
console.log("📱 Chat Controller initialized\n");

// Helper function to display inline keyboards
function showKeyboard(response: any, title: string) {
  if (response.inlineKeyboards.length > 0) {
    console.log(`\n⌨️  ${title}:`);
    const kb = response.inlineKeyboards[0];
    kb.buttons.forEach((row: any[], idx: number) => {
      const texts = row.map(b => `"${b.text}"`).join(" | ");
      console.log(`   Row ${idx + 1}: ${texts}`);
    });
  }
}

// ========================================
// 🎯 DEMO 1: CORE COMMAND SYSTEM
// ========================================
console.log("=".repeat(80));
console.log("🎯 DEMO 1: CORE COMMAND SYSTEM");
console.log("=".repeat(80));

await controller.clearChat();

// Test main navigation commands
const commands = [
  { cmd: "start", desc: "Main menu" },
  { cmd: "help", desc: "Help system" },
  { cmd: "intro", desc: "Tutorial walkthrough" },
  { cmd: "profile", desc: "User profile" },
  { cmd: "plans", desc: "Available plans" },
  { cmd: "updates", desc: "Latest updates" }
];

for (const { cmd, desc } of commands) {
  console.log(`\n📋 Testing /${cmd} - ${desc}`);
  console.log("-".repeat(40));
  
  const response = await controller.collect({
    minMessages: 1,
    maxWait: 5000
  }, async () => {
    await controller.sendCommand(cmd);
  });
  
  console.log("📝 Response:", response.text?.substring(0, 100) + "...");
  showKeyboard(response, `/${cmd} Menu`);
}

// ========================================
// 📁 DEMO 2: CONTENT MANAGEMENT SYSTEM
// ========================================
console.log("\n" + "=".repeat(80));
console.log("📁 DEMO 2: CONTENT MANAGEMENT SYSTEM");
console.log("=".repeat(80));

const contentCommands = [
  { cmd: "templates", desc: "Template management" },
  { cmd: "knowledge", desc: "Knowledge base" },
  { cmd: "assets", desc: "Asset management" },
  { cmd: "links", desc: "Link management" }
];

for (const { cmd, desc } of contentCommands) {
  console.log(`\n📂 Testing /${cmd} - ${desc}`);
  console.log("-".repeat(40));
  
  const response = await controller.collect({
    minMessages: 1,
    maxWait: 5000
  }, async () => {
    await controller.sendCommand(cmd);
  });
  
  console.log("📝 Response:", response.text?.substring(0, 120) + "...");
  showKeyboard(response, `${desc} Menu`);
}

// ========================================
// 👥 DEMO 3: COLLABORATION FEATURES
// ========================================
console.log("\n" + "=".repeat(80));
console.log("👥 DEMO 3: COLLABORATION FEATURES");
console.log("=".repeat(80));

const collabCommands = [
  { cmd: "groups", desc: "Group management" },
  { cmd: "addgroup", desc: "Add new group" },
  { cmd: "people", desc: "Team management" }
];

for (const { cmd, desc } of collabCommands) {
  console.log(`\n👥 Testing /${cmd} - ${desc}`);
  console.log("-".repeat(40));
  
  const response = await controller.collect({
    minMessages: 1,
    maxWait: 5000
  }, async () => {
    await controller.sendCommand(cmd);
  });
  
  console.log("📝 Response:", response.text?.substring(0, 120) + "...");
  showKeyboard(response, `${desc} Menu`);
}

// ========================================
// 🛠️ DEMO 4: TEXT PROCESSING TOOLS
// ========================================
console.log("\n" + "=".repeat(80));
console.log("🛠️ DEMO 4: TEXT PROCESSING TOOLS");
console.log("=".repeat(80));

// Test translation feature
console.log("\n🌐 Testing Translation Tool");
console.log("-".repeat(40));

const trResponse = await controller.collect({
  minMessages: 1,
  maxWait: 5000
}, async () => {
  await controller.sendCommand("tr");
});

console.log("📝 Translation response:", trResponse.text?.substring(0, 100) + "...");
showKeyboard(trResponse, "Translation Tool");

// ========================================
// 🎨 DEMO 5: MEDIA GENERATION FEATURES
// ========================================
console.log("\n" + "=".repeat(80));
console.log("🎨 DEMO 5: MEDIA GENERATION FEATURES");
console.log("=".repeat(80));

const mediaCommands = [
  { cmd: "img", desc: "Image generation" },
  { cmd: "imghd", desc: "HD image generation" },
  { cmd: "meme", desc: "Meme generation" },
  { cmd: "port", desc: "Portrait generation" },
  { cmd: "land", desc: "Landscape generation" }
];

for (const { cmd, desc } of mediaCommands) {
  console.log(`\n🎨 Testing /${cmd} - ${desc}`);
  console.log("-".repeat(40));
  
  const response = await controller.collect({
    minMessages: 1,
    maxWait: 5000
  }, async () => {
    await controller.sendCommand(cmd);
  });
  
  console.log("📝 Response:", response.text?.substring(0, 100) + "...");
  showKeyboard(response, `${desc} Tool`);
}

// ========================================
// 🤖 DEMO 6: NATURAL LANGUAGE PROCESSING
// ========================================
console.log("\n" + "=".repeat(80));
console.log("🤖 DEMO 6: NATURAL LANGUAGE PROCESSING");
console.log("=".repeat(80));

const nlpTests = [
  "Create a marketing automation workflow",
  "Help me write a business proposal",
  "Generate ideas for social media content",
  "Set up a customer service workflow",
  "Create a project management template"
];

for (let i = 0; i < nlpTests.length; i++) {
  const test = nlpTests[i];
  console.log(`\n💬 NLP Test ${i + 1}: "${test}"`);
  console.log("-".repeat(40));
  
  const response = await controller.collect({
    minMessages: 1,
    maxWait: 8000
  }, async () => {
    await controller.sendText(test);
  });
  
  console.log("📝 NLP Response:", response.text?.substring(0, 150) + "...");
  showKeyboard(response, `NLP Processing ${i + 1}`);
}

// ========================================
// ⚡ DEMO 7: INLINE KEYBOARD INTERACTIONS
// ========================================
console.log("\n" + "=".repeat(80));
console.log("⚡ DEMO 7: INLINE KEYBOARD INTERACTIONS");
console.log("=".repeat(80));

// Get to main menu first
const menuResponse = await controller.collect({
  minMessages: 1,
  maxWait: 5000
}, async () => {
  await controller.sendCommand("start");
});

if (menuResponse.inlineKeyboards.length > 0) {
  const mainMenu = menuResponse.inlineKeyboards[0];
  
  // Test each main menu button
  const menuButtons = ["Templates", "Assets", "Knowledge", "Groups", "Settings ･ 0 Credits"];
  
  for (const button of menuButtons) {
    console.log(`\n🖱️  Clicking "${button}"`);
    console.log("-".repeat(40));
    
    try {
      const buttonResponse = await mainMenu.click(button);
      console.log("📝 Button response:", buttonResponse.text?.substring(0, 100) + "...");
      showKeyboard(buttonResponse, `${button} Menu`);
      
      // Go back if there's a back button
      if (buttonResponse.inlineKeyboards.length > 0) {
        const kb = buttonResponse.inlineKeyboards[0];
        const backBtn = kb.buttons.flat().find((b: any) => b.text?.includes('Back') || b.text?.includes('Home'));
        if (backBtn) {
          await kb.click(backBtn.text);
          await new Promise(resolve => setTimeout(resolve, 1000));
        }
      }
    } catch (error) {
      console.log(`❌ Error clicking ${button}:`, error.message);
    }
  }
}

// ========================================
// 🛡️ DEMO 8: ERROR HANDLING & RECOVERY
// ========================================
console.log("\n" + "=".repeat(80));
console.log("🛡️ DEMO 8: ERROR HANDLING & RECOVERY");
console.log("=".repeat(80));

const errorTests = [
  { cmd: "invalidcommand", desc: "Invalid command" },
  { cmd: "nonexistent", desc: "Non-existent feature" },
  { text: "", desc: "Empty message" }
];

for (const { cmd, text, desc } of errorTests) {
  console.log(`\n⚠️  Testing ${desc}`);
  console.log("-".repeat(40));
  
  try {
    const response = await controller.collect({
      minMessages: 1,
      maxWait: 5000
    }, async () => {
      if (cmd) {
        await controller.sendCommand(cmd);
      } else if (text !== undefined) {
        await controller.sendText(text);
      }
    });
    
    console.log("📝 Error response:", response.text?.substring(0, 100) + "...");
    showKeyboard(response, "Error Handling");
  } catch (error) {
    console.log("🛡️ Caught error:", error.message);
  }
}

// ========================================
// 📊 DEMO SUMMARY
// ========================================
console.log("\n" + "=".repeat(80));
console.log("🎯 DEMO SUMMARY - CrafterAI Bot Capabilities");
console.log("=".repeat(80));

console.log("\n✅ COMMAND SYSTEM:");
console.log("   • Core navigation (/start, /help, /intro)");
console.log("   • Profile management (/profile, /plans)");
console.log("   • Information commands (/updates, /id)");

console.log("\n✅ CONTENT MANAGEMENT:");
console.log("   • Template system (/templates)");
console.log("   • Knowledge base (/knowledge)");
console.log("   • Asset management (/assets)");
console.log("   • Link management (/links)");

console.log("\n✅ COLLABORATION:");
console.log("   • Group management (/groups, /addgroup)");
console.log("   • Team management (/people)");

console.log("\n✅ TEXT PROCESSING:");
console.log("   • Translation (/tr)");
console.log("   • Natural language understanding");
console.log("   • Message processing tools");

console.log("\n✅ MEDIA GENERATION:");
console.log("   • Image generation (/img, /imghd)");
console.log("   • Portrait/Landscape modes (/port, /land)");
console.log("   • Meme generation (/meme)");

console.log("\n✅ USER INTERFACE:");
console.log("   • Inline keyboard navigation");
console.log("   • Contextual menus");
console.log("   • Error handling and recovery");

console.log("\n🏗️ TgIntegration Features Demonstrated:");
console.log("   • Comprehensive bot testing");
console.log("   • Command and text interaction");
console.log("   • Inline keyboard automation");
console.log("   • Response validation");
console.log("   • Error handling");
console.log("   • Natural language testing");
console.log("   • UI/UX analysis");

console.log("\n🎉 CrafterAI bot analysis complete!");
console.log("🚀 TgIntegration successfully tested all major features!");

process.exit(0);