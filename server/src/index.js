import "dotenv/config";
import cors from "cors";
import express from "express";
import path from "node:path";
import { fileURLToPath } from "node:url";
import downloaderRouter from "./routes/downloader.js";

const app = express();
const port = Number(process.env.PORT || 8000);
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const serverRoot = path.resolve(__dirname, "..");
const downloadsDir = path.resolve(
  serverRoot,
  process.env.DOWNLOADS_DIR || "../downloads"
);

app.use(cors());
app.use(express.json());
app.use("/downloads", express.static(downloadsDir));
app.use("/api/downloader", downloaderRouter);

app.get("/health", (_req, res) => {
  res.json({
    service: "server",
    status: "ok"
  });
});

app.get("/api", (_req, res) => {
  res.json({
    message: "Instagram downloader API is running",
    downloadsRoute: "/downloads"
  });
});

app.listen(port, () => {
  console.log(`Server listening on http://localhost:${port}`);
});
