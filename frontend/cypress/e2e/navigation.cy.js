/// <reference types="cypress" />

describe("Odin app", () => {
  beforeEach(() => {
    cy.visit("/");
  });

  describe("loads the home page", () => {
    it("from url", () => {
      cy.visit("/");

      cy.contains("Welcome to the Overall Data Import Navigator").should(
        "exist"
      );
      cy.url().should("include", "/");
    });

    it("by navbar click", () => {
      cy.visit("/database"); // go to other page in order to come back
      cy.get(".nav-links").contains("Home").click();

      cy.contains("Welcome to the Overall Data Import Navigator").should(
        "exist"
      );
      cy.url().should("include", "/");
    });
  });

  describe("loads the database page", () => {
    it("from url", () => {
      cy.visit("/database");

      cy.get("span.title").contains("PNO").should("exist");
      cy.url().should("include", "/database");
    });

    it("by navbar click", () => {
      cy.get(".nav-links").contains("Database").click();

      cy.get("span.title").contains("PNO").should("exist");
      cy.url().should("include", "/database");
    });
  });

  describe("loads the export page", () => {
    it("from url", () => {
      cy.visit("/documents");

      cy.get("span.title").contains("Specifications").should("exist");
      cy.url().should("include", "/documents");
    });

    it("by navbar click", () => {
      cy.get(".nav-links").contains("Export").click();

      cy.get("span.title").contains("Specifications").should("exist");
      cy.url().should("include", "/documents");
    });
  });
});
