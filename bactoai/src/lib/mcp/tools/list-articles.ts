import { defineTool } from "@lovable.dev/mcp-js";
import { z } from "zod";
import { posts } from "@/content/posts";

export default defineTool({
  name: "list_articles",
  title: "List articles",
  description:
    "List BactoAI blog and resource articles (title, excerpt, category, date, reading time), optionally filtered by category.",
  inputSchema: {
    category: z
      .enum(["Research", "Clinical", "Public Health", "Product"])
      .optional()
      .describe("Filter articles by category."),
  },
  annotations: { readOnlyHint: true, idempotentHint: true, openWorldHint: false },
  handler: ({ category }) => {
    const items = (category ? posts.filter((p) => p.category === category) : posts).map(
      ({ slug, title, excerpt, category: cat, date, readTime }) => ({
        slug,
        title,
        excerpt,
        category: cat,
        date,
        readTime,
      }),
    );
    return {
      content: [{ type: "text", text: JSON.stringify(items, null, 2) }],
      structuredContent: { count: items.length, articles: items },
    };
  },
});
