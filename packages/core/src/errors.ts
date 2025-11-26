export class InvalidResponseError extends Error {
  constructor(message?: string) {
    super(message || "Invalid response from peer");
    this.name = "InvalidResponseError";
  }
}

export class CallbackQueryTimeoutError extends Error {
  public readonly name = "CallbackQueryTimeoutError";

  constructor(
    public readonly details: {
      buttonText: string;
      callbackData: string;
      timeout: number;
    },
  ) {
    super(
      `Callback query was never answered within ${details.timeout}ms. ` +
        `The bot should call answerCallbackQuery() to dismiss the loading indicator. ` +
        `Button: "${details.buttonText}"`,
    );
  }
}
