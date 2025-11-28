# Introduction

{{tgi}} is a Python library that helps you test your [bots](https://core.telegram.org/bots) and automate
routine tasks on [Telegram Messenger](https://telegram.org). It does so by logging in as a user or interacting in your
name using the popular [Pyrogram](https://github.com/pyrogram/pyrogram) library and
[mtproto](https://core.telegram.org/mtproto).

### See it in action

<video style="width: 100%;" controls>
  <source src="assets/screencast-botlistbot-tests.mp4" type="video/mp4">
Your browser does not support the video tag.
</video>

<!--
> "Why tests, my bot runs fine?!"

*Hint: It doesn't.*
-->

### The Testing Pyramid

When writing software, it is almost always a good idea to have a number of tests for your code (this varies by the
complexity of your project). What kinds of tests should be written typically follows the so-called ["testing
pyramid"](https://martinfowler.com/bliki/TestPyramid.html).

<img align="left" src="assets/testing-pyramid.png" alt="The Testing Pyramid" />

This guideline recommends to have a test suite consisting of a **large base of unit tests**, a fair **number of
integration tests**, and only **very few end-to-end (E2E) or manual tests**. In this classification, {{tgi}} lies in
 the center and should be seen as a supplement to unit tests that cover the core logic of your bot.

By their nature, integration tests are slower since they interact with multiple systems over the network instead of
everything happening on the same machine. The same is true for {{tgi}}, which reaches out to the Telegram servers to
automate an interaction between two conversation partners.
