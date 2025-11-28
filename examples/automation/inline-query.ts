import { ChatController } from "@tgintegration/core";
import { createClient } from "../utils.js";

/**
 * Example demonstrating inline query automation.
 *
 * This example queries the @gif bot for cat GIFs and sends one to saved messages.
 */
async function main() {
  const client = await createClient();

  // @gif is a popular bot that returns GIF results for inline queries
  const controller = new ChatController(client, "@gif");
  await controller.initialize();

  console.log("Querying @gif for cat GIFs...");
  const results = await controller.inlineQuery("cats", { limit: 10 });

  console.log(`Found ${results.count} results`);
  console.log(`Gallery mode: ${results.isGallery}`);
  console.log(`Next offset: ${results.nextOffset || "none"}`);

  // Find GIF results specifically
  const gifs = results.findResults({ typePattern: /gif/i });
  console.log(`Found ${gifs.length} GIF results`);

  if (gifs.length > 0) {
    const firstGif = gifs[0];
    console.log("\nFirst GIF result:");
    console.log(`  ID: ${firstGif.id}`);
    console.log(`  Type: ${firstGif.type}`);
    console.log(`  Title: ${firstGif.title || "N/A"}`);
    console.log(`  Description: ${firstGif.description || "N/A"}`);

    console.log("\nSending first cat GIF to saved messages...");
    try {
      const sentMessage = await firstGif.send({ chatId: "me" });
      console.log(`Sent! Message ID: ${sentMessage.id}`);
    } catch (error) {
      console.error("Failed to send inline result:", error);
    }
  } else {
    console.log("No GIF results found.");
  }

  // Example: Search with limit
  console.log("\n--- Searching with limit of 5 results ---");
  const limitedResults = await controller.inlineQuery("dogs", { limit: 5 });
  console.log(`Limited search returned ${limitedResults.count} results`);

  // Example: Filter by title pattern
  console.log("\n--- Filtering by title pattern ---");
  const botListController = new ChatController(client, "@BotListBot");
  await botListController.initialize();

  const botResults = await botListController.inlineQuery("examples");
  const exampleResults = botResults.findResults({
    titlePattern: /example/i,
  });
  console.log(
    `Found ${exampleResults.length} results matching 'example' in title`,
  );

  for (const result of exampleResults) {
    console.log(`  - ${result.title}: ${result.description}`);
  }

  await client.disconnect();
  console.log("\nDone!");
}

await main();
