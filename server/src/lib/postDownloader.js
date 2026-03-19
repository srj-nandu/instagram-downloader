import { instagramGetUrl } from "instagram-url-direct";

function extractShortcode(url) {
  const match = url.match(/instagram\.com\/(?:p|reel|reels|tv)\/([^/?#]+)/i);
  return match?.[1] || "media";
}

function extensionFromUrl(url, mediaType) {
  try {
    const pathname = new URL(url).pathname;
    const ext = pathname.split(".").pop();
    if (ext) {
      return `.${ext.toLowerCase()}`;
    }
  } catch {
    return mediaType === "video" ? ".mp4" : ".jpg";
  }

  return mediaType === "video" ? ".mp4" : ".jpg";
}

export async function downloadPostMedia(url) {
  const data = await instagramGetUrl(url);
  const shortcode = extractShortcode(url);
  const owner = data.post_info?.owner_username || "instagram";

  const files = data.media_details.map((item, index) => {
    const extension = extensionFromUrl(item.url, item.type);
    const filename = `${owner}-${shortcode}-${String(index + 1).padStart(2, "0")}${extension}`;

    return {
      name: filename,
      mediaType: item.type,
      directUrl: item.url,
      thumbnailUrl: item.thumbnail || item.url
    };
  });

  return {
    kind: "post",
    source: `${owner}/${shortcode}`,
    message: `Found ${files.length} media file(s) from the Instagram post.`,
    files
  };
}
