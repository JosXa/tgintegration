import type { ChatController } from "./chat-controller.js";
import type { InlineKeyboard } from "./inline-keyboard.js";
import type { ReplyKeyboard } from "./reply-keyboard.js";
import type { Response } from "./response.js";

export interface ExplorationNode {
  path: string[];
  response: Response;
  depth: number;
  children: ExplorationNode[];
  explored: boolean;
}

export interface ExplorationResult {
  root: ExplorationNode;
  steps: number;
}

interface Action {
  type: "inline_click" | "reply_click" | "command";
  description: string;
  buttonIndex?: number;
  keyboard?: InlineKeyboard | ReplyKeyboard;
  buttonText?: string;
  command?: string;
}

export class BotExplorer {
  constructor(private controller: ChatController) {}

  async explore(
    options: { maxDepth?: number; maxSteps?: number } = {},
  ): Promise<ExplorationResult> {
    const { maxDepth = 5, maxSteps = 100 } = options;

    console.log(
      `[EXPLORER] Starting exploration with maxDepth=${maxDepth}, maxSteps=${maxSteps}`,
    );

    // Initial ping with /start and /help
    console.log(`[EXPLORER] Sending initial messages: /start, /help`);
    const initialResponse = await this.controller.pingBot({
      messages: ["/start", "/help"],
    });
    console.log(
      `[EXPLORER] Initial response: ${initialResponse.count} messages`,
    );

    // Get bot commands
    const botCommands = await this.controller.getBotCommands();
    console.log(
      `[EXPLORER] Retrieved ${botCommands.length} bot commands: ${botCommands.join(", ")}`,
    );

    // If no interactive elements, send a sample message to trigger bot response
    let currentResponse = initialResponse;
    if (
      initialResponse.inlineKeyboards.length === 0 &&
      !initialResponse.replyKeyboard &&
      initialResponse.commands.length === 0
    ) {
      console.log(
        `[EXPLORER] No interactive elements found, sending sample message to trigger bot`,
      );
      currentResponse = await this.controller.collect(
        { minMessages: 1 },
        async () => {
          await this.controller.sendText("This is an awesome poll");
          await this.controller.sendText("👍🫰👎");
        },
      );
      console.log(
        `[EXPLORER] Sample message response: ${currentResponse.count} messages`,
      );
    }

    const root: ExplorationNode = {
      path: [],
      response: currentResponse,
      depth: 0,
      children: [],
      explored: false,
    };

    const queue: ExplorationNode[] = [root];
    let steps = 0;
    const visitedActions = new Set<string>();

    console.log(`[EXPLORER] Beginning BFS exploration`);

    while (queue.length > 0 && steps < maxSteps) {
      const current = queue.shift()!;
      if (current.explored || current.depth >= maxDepth) {
        if (current.explored)
          console.log(
            `[EXPLORER] Skipping already explored node at depth ${current.depth}`,
          );
        if (current.depth >= maxDepth)
          console.log(`[EXPLORER] Skipping node at max depth ${maxDepth}`);
        continue;
      }
      current.explored = true;
      console.log(
        `[EXPLORER] Exploring node at depth ${current.depth}, path: ${current.path.join(" -> ") || "Root"}`,
      );

      const actions = this.extractActions(
        current.response,
        botCommands,
        visitedActions,
      );
      console.log(`[EXPLORER] Found ${actions.length} actions to explore`);

      for (const action of actions) {
        if (steps >= maxSteps) {
          console.log(
            `[EXPLORER] Reached max steps limit (${maxSteps}), stopping`,
          );
          break;
        }

        console.log(`[EXPLORER] Performing action: ${action.description}`);
        const newResponse = await this.performAction(action);
        console.log(
          `[EXPLORER] Action response: ${newResponse.count} messages`,
        );

        const newNode: ExplorationNode = {
          path: [...current.path, action.description],
          response: newResponse,
          depth: current.depth + 1,
          children: [],
          explored: false,
        };
        current.children.push(newNode);
        if (action.type === "inline_click" || action.type === "reply_click") {
          queue.unshift(newNode); // Prioritize interactive actions
        } else {
          queue.push(newNode);
        }
        steps++;
        console.log(`[EXPLORER] Added new node, total steps: ${steps}`);
      }
    }

    let stopReason = "";
    if (queue.length === 0) {
      stopReason = "All reachable nodes explored";
    } else if (steps >= maxSteps) {
      stopReason = `Reached maximum steps limit (${maxSteps})`;
    } else {
      stopReason = "Unknown reason";
    }
    console.log(
      `[EXPLORER] Exploration completed: ${steps} steps taken. Stop reason: ${stopReason}`,
    );
    return { root, steps };
  }

  private extractActions(
    response: Response,
    botCommands: string[],
    visited: Set<string>,
  ): Action[] {
    const actions: Action[] = [];

    // Inline buttons (highest priority)
    for (const kb of response.inlineKeyboards) {
      kb.buttons.flat().forEach((btn, i) => {
        const desc = `Click inline: ${btn.text}`;
        if (btn.callbackData && !visited.has(desc)) {
          visited.add(desc);
          actions.push({
            type: "inline_click",
            buttonIndex: i,
            keyboard: kb,
            description: desc,
          });
        }
      });
    }

    // Reply keyboard buttons
    const replyKb = response.replyKeyboard;
    if (replyKb) {
      replyKb.buttons.flat().forEach((btn) => {
        const desc = `Click reply: ${btn.text}`;
        if (!visited.has(desc)) {
          visited.add(desc);
          actions.push({
            type: "reply_click",
            buttonText: btn.text,
            keyboard: replyKb,
            description: desc,
          });
        }
      });
    }

    // Commands from response text
    for (const cmd of response.commands) {
      const desc = `Send command: /${cmd}`;
      if (!visited.has(desc)) {
        visited.add(desc);
        actions.push({
          type: "command",
          command: cmd,
          description: desc,
        });
      }
    }

    // Known bot commands not in text
    for (const cmd of botCommands) {
      const desc = `Send command: /${cmd}`;
      if (!visited.has(desc)) {
        visited.add(desc);
        actions.push({
          type: "command",
          command: cmd,
          description: desc,
        });
      }
    }

    return actions;
  }

  private async performAction(action: Action): Promise<Response> {
    switch (action.type) {
      case "inline_click":
        return this.controller.collect(
          { minMessages: 0, maxMessages: 3, maxWait: 2500 },
          async () => {
            await (action.keyboard as InlineKeyboard).click(
              action.buttonIndex as number,
            );
          },
        );
      case "reply_click":
        return (action.keyboard as ReplyKeyboard).click(
          action.buttonText as string,
          { maxMessages: 3, maxWait: 2500 },
        );
      case "command":
        return this.controller.collect(
          { minMessages: 0, maxMessages: 3, maxWait: 2500 },
          async () => {
            await this.controller.sendCommand(action.command as string);
          },
        );
    }
  }
}
