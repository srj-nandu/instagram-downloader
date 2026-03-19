import { Router } from "express";
import { downloadPostMedia } from "../lib/postDownloader.js";

const router = Router();

router.post("/post", async (req, res) => {
  if (!req.body?.url) {
    return res.status(400).json({ detail: "A post URL is required." });
  }

  try {
    const data = await downloadPostMedia(req.body.url);
    return res.json(data);
  } catch (error) {
    return res.status(502).json({
      detail: error.message || "Unable to download Instagram post media."
    });
  }
});

export default router;
