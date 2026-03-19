import axios from "axios";
import { instagramGetUrl } from "instagram-url-direct";
import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const serverRoot = path.resolve(__dirname, "..", "..");
const downloadsDir = path.resolve(
  serverRoot,
  process.env.DOWNLOADS_DIR || "../downloads"
);

function makeFolderName(ownerUsername = "instagram", postUrl = "") {
  const shortcode = extractShortcode(postUrl);
  const stamp = new Date().toISOString().replace(/[:.]/g, "-");
  return `post-${ownerUsername}-${shortcode}-${stamp}`;
}

function extractShortcode(url) {
  const match = url.match(/instagram\.com\/(?:p|reel|reels|tv)\/([^/?#]+)/i);
  return match?.[1] || "media";
}

function extensionFromUrl(url, mediaType) {
  try {
    const pathname = new URL(url).pathname;
    const ext = path.extname(pathname);
    if (ext) {
      return ext;
    }
  } catch {
    return mediaType === "video" ? ".mp4" : ".jpg";
  }

  return mediaType === "video" ? ".mp4" : ".jpg";
}

export async function downloadPostMedia(url) {
  const data = await instagramGetUrl(url);
  const folder = makeFolderName(data.post_info?.owner_username, url);
  const targetDir = path.join(downloadsDir, folder);

  await mkdir(targetDir, { recursive: true });

  const files = await Promise.all(
    data.media_details.map(async (item, index) => {
      const extension = extensionFromUrl(item.url, item.type);
      const filename = `${String(index + 1).padStart(2, "0")}${extension}`;
      const outputPath = path.join(targetDir, filename);
      const response = await axios.get(item.url, {
        responseType: "arraybuffer"
      });

      await writeFile(outputPath, response.data);

      return {
        name: filename,
        mediaType: item.type,
        publicPath: `/downloads/${folder}/${filename}`,
        sizeBytes: Buffer.byteLength(response.data)
      };
    })
  );

  return {
    kind: "post",
    folder,
    message: `Downloaded ${files.length} file(s) from the Instagram post.`,
    files
  };
}
