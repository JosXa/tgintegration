import { afterAll, beforeAll, describe, expect, test } from "bun:test";
import { ChatController } from "@tgintegration/core";
import { createClient } from "../utils.js";

describe("Inline Queries", () => {
  let controller: ChatController;

  beforeAll(async () => {
    // Use @gif bot for testing - it has inline query support
    controller = new ChatController(await createClient(), "@gif");
    await controller.initialize();
  });

  afterAll(() => {
    controller.disconnect();
  });

  test("should query inline results", async () => {
    const results = await controller.inlineQuery("cats");

    expect(results.count).toBeGreaterThan(0);
    expect(results.query).toBe("cats");
    expect(results.isEmpty).toBe(false);
  });

  test("should filter results by type pattern", async () => {
    const results = await controller.inlineQuery("dogs");
    const gifs = results.findResults({
      typePattern: /gif/i,
    });

    // @gif bot should return GIF results
    expect(gifs.length).toBeGreaterThan(0);
  });

  test("should respect limit parameter", async () => {
    const results = await controller.inlineQuery("funny", { limit: 5 });

    expect(results.count).toBeLessThanOrEqual(5);
  });

  test("should have proper result properties", async () => {
    const results = await controller.inlineQuery("birds");

    if (results.count > 0) {
      const firstResult = results.results[0];

      expect(firstResult.id).toBeDefined();
      expect(firstResult.type).toBeDefined();
      expect(typeof firstResult.fullText).toBe("string");
    }
  });

  test("should handle empty query results", async () => {
    // Use a query that likely returns no results
    const results = await controller.inlineQuery(
      "xyzabc123nonexistentquerystring",
    );

    // It may return 0 results or some default results depending on the bot
    expect(results.isEmpty).toBe(results.count === 0);
  });

  test("should expose gallery property", async () => {
    const results = await controller.inlineQuery("animals");

    expect(typeof results.isGallery).toBe("boolean");
  });

  test("should expose switch PM properties", async () => {
    const results = await controller.inlineQuery("nature");

    expect(typeof results.canSwitchPm).toBe("boolean");
    // Don't test switchToPm() unless we know the bot supports it
  });
});
