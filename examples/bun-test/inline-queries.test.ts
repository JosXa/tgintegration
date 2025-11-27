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
    const results = await controller.inlineQuery("cats", {
      limit: 5,
      paginationDelay: 10000,
    });

    expect(results.count).toBeGreaterThan(0);
    expect(results.query).toBe("cats");
    expect(results.isEmpty).toBe(false);
  });

  test("should filter results by type pattern", async () => {
    const results = await controller.inlineQuery("dogs", {
      limit: 5,
      paginationDelay: 10000,
    });
    const gifs = results.findResults({
      typePattern: /gif/i,
    });

    // @gif bot should return GIF results
    expect(gifs.length).toBeGreaterThan(0);
  });

  test("should respect limit parameter", async () => {
    const results = await controller.inlineQuery("funny", {
      limit: 3,
      paginationDelay: 10000,
    });

    expect(results.count).toBeLessThanOrEqual(3);
  });

  // Skip the more complex tests that might hit rate limits
  test.skip("should have proper result properties", async () => {
    // This test is skipped to avoid rate limiting issues
  });

  test.skip("should handle empty query results", async () => {
    // This test is skipped to avoid rate limiting issues
  });

  test.skip("should expose gallery property", async () => {
    // This test is skipped to avoid rate limiting issues
  });

  test.skip("should expose switch PM properties", async () => {
    // This test is skipped to avoid rate limiting issues
  });
});
