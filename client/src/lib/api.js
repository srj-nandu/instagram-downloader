export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(path, options = {}) {
  let response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {})
      },
      ...options
    });
  } catch {
    throw new Error(
      `Could not reach the API at ${API_BASE_URL}. Make sure the server is running.`
    );
  }

  const text = await response.text();
  let payload = {};

  if (text) {
    try {
      payload = JSON.parse(text);
    } catch {
      payload = { message: text };
    }
  }

  if (!response.ok) {
    throw new Error(payload.detail || payload.message || "Request failed");
  }

  return payload;
}

export function downloadPostMedia(url) {
  return request("/api/downloader/post", {
    method: "POST",
    body: JSON.stringify({ url })
  });
}

export function resolveDownloadUrl(publicPath) {
  return `${API_BASE_URL}${publicPath}`;
}
