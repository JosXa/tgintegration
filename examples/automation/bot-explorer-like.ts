import {
  BotExplorer,
  ChatController,
  type ExplorationNode,
} from "@tgintegration/core";
import { createClient } from "../utils.js";

/**
 * Example using BotExplorer to autodiscover @like bot features.
 */
async function main() {
  const client = await createClient();

  const peer = "@josxatlbot";

  const controller = new ChatController(client, peer, {
    globalActionDelay: 1500, // 1.5s delay
  });

  console.log("Clearing chat...");
  await controller.clearChat();

  const explorer = new BotExplorer(controller);

  console.log("Starting exploration...");
  const result = await explorer.explore({ maxDepth: 3, maxSteps: 50 });

  console.log(`Exploration completed in ${result.steps} steps.`);

  // Traverse and log the exploration tree
  function logNode(node: ExplorationNode, indent = 0) {
    console.log(
      "  ".repeat(indent) +
        (node.path.length ? node.path[node.path.length - 1] : "Root"),
    );
    if (node.response.count > 0) {
      console.log(
        `${"  ".repeat(indent + 1)}Response: ${node.response.fullText.slice(0, 100)}...`,
      );
    }
    for (const child of node.children) {
      logNode(child, indent + 1);
    }
  }

  logNode(result.root);

  process.exit(0);
}

await main();
