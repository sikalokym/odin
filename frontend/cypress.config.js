const { defineConfig } = require("cypress");

const baseUrl = process.env.BASE_URL || "http://localhost:8080";

module.exports = defineConfig({
  e2e: {
    baseUrl,
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
  },
});
