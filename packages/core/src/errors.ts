export class InvalidResponseError extends Error {
  constructor(message?: string) {
    super(message || "Invalid response from peer");
    this.name = "InvalidResponseError";
  }
}
