/** Product display name and public links shared by frontend surfaces. */

export const PRODUCT_NAME = "JMXS";
export const OFFICIAL_REPO_SLUG = "juantmontica75-ctrl/Dodaios";
export const OFFICIAL_REPO_URL = `https://github.com/${OFFICIAL_REPO_SLUG}`;
export const OFFICIAL_REPO_LABEL = `github.com/${OFFICIAL_REPO_SLUG}`;
/** The project JMXS is built on; credited wherever the app names its origins. */
export const UPSTREAM_PRODUCT_NAME = "Dodaios";
export const UPSTREAM_REPO_URL = "https://github.com/Dodaios/Dodaios";
/** The community registry: where published plugins, skills and agents live. */
export const MARKETPLACE_REPO_SLUG = "Dodaios/marketplace";
export const MARKETPLACE_REPO_URL = `https://github.com/${MARKETPLACE_REPO_SLUG}`;
/** The public storefront: the same catalogue, on the web. */
export const MARKETPLACE_WEB_URL = "https://dodaios.ai/marketplace/";

/**
 * Every name the app's own MCP tools server is registered under
 * (dodaios/core/branding.py). A coding CLI names a tool after its server
 * ("mcp__jmxs__gmail"). JMXS has no earlier names of its own.
 */
export const MCP_TOOLS_SERVER_NAMES: readonly string[] = ["jmxs"];
