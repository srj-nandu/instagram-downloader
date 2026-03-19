import "dotenv/config";
import cors from "cors";
import express from "express";
import downloaderRouter from "./routes/downloader.js";

const app = express();
const port = Number(process.env.PORT || 8000);

app.use(cors());
app.use(express.json());
app.use("/api/downloader", downloaderRouter);

app.get("/health", (_req, res) => {
  res.json({
    service: "server",
    status: "ok"
  });
});

app.get("/api", (_req, res) => {
  res.json({
    message: "Instagram downloader service is running"
  });
});

app.listen(port, () => {
  console.log(`Server listening on http://localhost:${port}`);
});
