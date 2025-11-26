import type {
  Message,
  InputPeerLike,
  InputText,
  FullChat,
  FullUser,
  User,
  InputMessageId
} from "@mtcute/core";
import type { tl } from "@mtcute/tl";

export interface AnyTelegramClient {
  start(params?: any): Promise<User>;

  getFullChat(chatId: InputPeerLike): Promise<FullChat>;
  getFullUser(userId: InputPeerLike): Promise<FullUser>;
  sendText(chatId: InputPeerLike, text: InputText, params?: any): Promise<Message>;
  deleteHistory(chat: InputPeerLike, params?: {
    mode?: 'delete' | 'clear' | 'revoke';
    maxId?: number;
  }): Promise<void>;

  readonly onNewMessage: {
    add: (handler: (msg: Message) => void) => void;
    remove: (handler: (msg: Message) => void) => void;
  };

  getCallbackAnswer(params: InputMessageId & {
    data: string | Uint8Array;
    timeout?: number;
    fireAndForget?: boolean;
    game?: boolean;
    password?: string;
  }): Promise<tl.messages.TypeBotCallbackAnswer>;
}

export interface TimeoutSettings {
  maxWait?: number;
  waitConsecutive?: number;
  throwOnTimeout?: boolean;
}

export interface Expectation {
  minMessages?: number;
  maxMessages?: number;
  validators?: (messages: Message[]) => boolean;
}

export interface CollectOptions extends TimeoutSettings, Expectation {
  // merged options
}
