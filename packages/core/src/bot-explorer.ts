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

    // Initial ping with /start and /help
    const initialResponse = await this.controller.pingBot({
      messages: ["/start", "/help"],
    });

    // Get bot commands
    const botCommands = await this.controller.getBotCommands();

    const root: ExplorationNode = {
      path: [],
      response: initialResponse,
      depth: 0,
      children: [],
      explored: false,
    };

    const stack: ExplorationNode[] = [root];
    let steps = 0;
    const visitedActions = new Set<string>();

    while (stack.length > 0 && steps < maxSteps) {
      const current = stack[stack.length - 1];
      stack.pop();
      if (current.explored || current.depth >= maxDepth) continue;
      current.explored = true;

      const actions = this.extractActions(
        current.response,
        botCommands,
        visitedActions,
      );

      for (const action of actions) {
        if (steps >= maxSteps) break;

        const newResponse = await this.performAction(action);
        const newNode: ExplorationNode = {
          path: [...current.path, action.description],
          response: newResponse,
          depth: current.depth + 1,
          children: [],
          explored: false,
        };
        current.children.push(newNode);
        stack.push(newNode);
        steps++;
      }
    }

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
      if (botCommands.includes(cmd) && !visited.has(desc)) {
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
        return this.controller.collect({ minMessages: 0 }, async () => {
          await (action.keyboard as InlineKeyboard).click(action.buttonIndex!);
        });
      case "reply_click":
        return (action.keyboard as ReplyKeyboard).click(action.buttonText!);
      case "command":
        return this.controller.collect({ minMessages: 0 }, async () => {
          await this.controller.sendCommand(action.command!);
        });
    }
  }
}
