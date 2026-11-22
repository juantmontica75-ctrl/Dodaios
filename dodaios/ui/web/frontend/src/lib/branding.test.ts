import { describe, expect, it } from "vitest";

import {
  MARKETPLACE_REPO_SLUG,
  MARKETPLACE_REPO_URL,
  MCP_TOOLS_SERVER_NAMES,
  OFFICIAL_REPO_LABEL,
  OFFICIAL_REPO_SLUG,
  OFFICIAL_REPO_URL,
  PRODUCT_NAME,
  UPSTREAM_PRODUCT_NAME,
  UPSTREAM_REPO_URL,
} from "@/lib/branding";

describe("branding", () => {
  it("shows the product display name", () => {
    expect(PRODUCT_NAME).toBe("JMXS");
  });

  it("links to the JMXS repository", () => {
    expect(OFFICIAL_REPO_SLUG).toBe("juantmontica75-ctrl/Dodaios");
    expect(OFFICIAL_REPO_URL).toBe("https://github.com/juantmontica75-ctrl/Dodaios");
    expect(OFFICIAL_REPO_LABEL).toBe("github.com/juantmontica75-ctrl/Dodaios");
  });

  it("credits the upstream project", () => {
    expect(UPSTREAM_PRODUCT_NAME).toBe("Dodaios");
    expect(UPSTREAM_REPO_URL).toBe("https://github.com/Dodaios/Dodaios");
  });

  it("links to the community registry", () => {
    expect(MARKETPLACE_REPO_SLUG).toBe("Dodaios/marketplace");
    expect(MARKETPLACE_REPO_URL).toBe("https://github.com/Dodaios/marketplace");
  });

  it("names the MCP tools server under JMXS only", () => {
    expect(MCP_TOOLS_SERVER_NAMES).toEqual(["jmxs"]);
  });
});
