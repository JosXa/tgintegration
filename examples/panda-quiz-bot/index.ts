import { openai } from "@ai-sdk/openai";
import { ChatController } from "@tgintegration/core";
import { generateObject } from "ai";
import { z } from "zod";
import { createClient } from "../utils.js";

/**
 * Example automating the @PandaQuizEnBot quiz using AI.
 */
async function main() {
  const client = await createClient();
  const peer = "@PandaQuizEnBot";

  const controller = new ChatController(client, peer, {
    globalActionDelay: 1500,
  });

  await controller.initialize();

  console.log("Clearing chat to start with a blank screen...");
  await controller.clearChat();

  console.log("Sending /start and collecting response...");
  const startResponse = await controller.collect(
    {
      minMessages: 1,
    },
    async () => {
      await controller.sendCommand("start");
    },
  );

  startResponse.debug();

  console.log("Sending /play to start a quiz...");
  let quizResponse = await controller.collect(
    {
      minMessages: 1,
    },
    async () => {
      await controller.sendCommand("play");
    },
  );

  quizResponse.debug();

  let correctAnswers = 0;

  while (true) {
    // Extract the question and options
    const quizMessage = quizResponse.messages.find(
      (m) =>
        m.text.includes("?") ||
        (m.text.includes("Question for") && m.text.includes("coins")),
    );
    if (!quizMessage) {
      console.log("No quiz question found");
      process.exit(0);
    }

    console.log(`\n=== Question ${correctAnswers + 1} ===`);
    console.log("Quiz question:", quizMessage.text);

    // Use AI to answer the question
    const completion = await generateObject({
      model: openai("gpt-5-mini"),
      prompt: `You are playing a Telegram quiz game. Analyze the question and provide the correct answer. Only respond with the answer choice, A, B, C, or D (uppercase).\n\nQuestion: ${quizMessage.text}`,
      schema: z.object({
        answer: z
          .string()
          .describe(
            "The quiz answer key, i.e. 'A', 'B', 'C', or 'D' (uppercase letter)",
          ),
      }),
    });

    const aiAnswer = completion.object.answer.toUpperCase();
    console.log("AI answer:", aiAnswer);

    // Send the AI's answer
    if (aiAnswer) {
      const resultResponse = await controller.collect(
        {
          minMessages: 1,
        },
        async () => {
          await controller.sendText(aiAnswer);
        },
      );

      resultResponse.debug();

      // Check if answer was correct
      const resultMessage = resultResponse.messages[0]?.text || "";
      if (resultMessage.includes("The answer is correct")) {
        correctAnswers++;
        console.log(`✅ Correct! Total correct: ${correctAnswers}`);
      } else if (
        resultMessage.includes("once per the game, you have a second attempt")
      ) {
        console.log(
          `❌ Incorrect! Using second attempt. Total correct: ${correctAnswers}`,
        );
      } else if (
        resultMessage.includes("The answer is incorrect. Your gain is 0 coins")
      ) {
        console.log(
          `❌ Game over! No more attempts. Final correct: ${correctAnswers}`,
        );
        process.exit(0);
      } else {
        console.log(`❌ Incorrect. Total correct: ${correctAnswers}`);
      }

      // Check if game is complete
      if (
        resultMessage.includes(
          "Congratulations! You have answered the last question and won",
        )
      ) {
        console.log(
          `\n🎉 Game completed! Answered ${correctAnswers} questions correctly!`,
        );
        process.exit(0);
      }

      // Continue to next question
      quizResponse = resultResponse;
    } else {
      console.log("No AI answer generated");
      process.exit(0);
    }
  }
}

await main();
