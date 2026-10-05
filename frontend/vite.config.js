import { existsSync, readdirSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";

const root = fileURLToPath(new URL(".", import.meta.url));
const pageInputs = Object.fromEntries(
  readdirSync(root, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => [entry.name, resolve(root, entry.name, "code.html")])
    .filter(([, path]) => existsSync(path)),
);

export default defineConfig({
  plugins: [
    {
      name: "campusiq-screen-integration",
      transformIndexHtml(_html, context) {
        if (context.filename === resolve(root, "index.html")) return;
        return [
          {
            tag: "script",
            attrs: { type: "module", src: "/src/screen-integration.js" },
            injectTo: "head",
          },
        ];
      },
    },
  ],
  build: {
    rollupOptions: {
      input: {
        index: resolve(root, "index.html"),
        ...pageInputs,
      },
    },
  },
});