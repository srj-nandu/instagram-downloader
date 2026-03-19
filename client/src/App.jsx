import { useState } from "react";
import { downloadPostMedia } from "./lib/api.js";

function SocialIcon({ kind }) {
  if (kind === "instagram") {
    return (
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <rect x="5.4" y="5.4" width="13.2" height="13.2" rx="4.2" fill="none" stroke="#fff" strokeWidth="1.9" />
        <circle cx="12" cy="12" r="3.05" fill="none" stroke="#fff" strokeWidth="1.9" />
        <circle cx="16.4" cy="7.8" r="1.15" fill="#fff" />
      </svg>
    );
  }

  if (kind === "github") {
    return (
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path
          d="M12 2.5a9.5 9.5 0 0 0-3 18.52c.48.09.65-.2.65-.46v-1.62c-2.63.57-3.19-1.11-3.19-1.11-.43-1.08-1.05-1.37-1.05-1.37-.86-.59.07-.58.07-.58.95.07 1.45.97 1.45.97.84 1.45 2.21 1.03 2.75.79.09-.61.33-1.03.6-1.26-2.1-.24-4.3-1.04-4.3-4.64 0-1.02.36-1.85.96-2.51-.1-.23-.42-1.2.09-2.49 0 0 .78-.25 2.56.96a8.9 8.9 0 0 1 4.66 0c1.78-1.21 2.56-.96 2.56-.96.51 1.29.19 2.26.09 2.49.6.66.96 1.49.96 2.51 0 3.61-2.2 4.39-4.31 4.63.34.29.64.85.64 1.71v2.54c0 .26.17.55.66.46A9.5 9.5 0 0 0 12 2.5Z"
          fill="currentColor"
        />
      </svg>
    );
  }

  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M4.75 18.5V7.25l3.8 2.92V18.5H4.75Z" fill="#4285F4" />
      <path d="M15.45 18.5V10.17l3.8-2.92V18.5h-3.8Z" fill="#34A853" />
      <path d="M4.75 7.35V6.7c0-1.22.98-2.2 2.2-2.2h.78L12 7.7l4.27-3.2h.78c1.22 0 2.2.98 2.2 2.2v.65L12 12.82 4.75 7.35Z" fill="#EA4335" />
      <path d="M15.6 10.3 19.25 7.55v-.2c0-1.27-1.46-1.99-2.46-1.2L12 9.9 7.21 6.15c-1-.79-2.46-.07-2.46 1.2v.2l3.65 2.75L12 7.55l3.6 2.75Z" fill="#FBBC05" opacity=".95" />
    </svg>
  );
}

function ResultPanel({ result }) {
  if (!result) {
    return (
      <div className="result-empty">
        Run a download request to get direct media links here.
      </div>
    );
  }

  return (
    <section className="result-panel">
      <div className="result-header">
        <div>
          <p className="eyebrow">Media Links</p>
          <h3>{result.message}</h3>
        </div>
        <p className="result-folder">{result.source}</p>
      </div>

      <div className="file-grid">
        {result.files.map((file) => (
          <article className="file-card" key={file.directUrl}>
            <p className="file-type">{file.mediaType}</p>
            <h4>{file.name}</h4>
            <a
              className="file-link"
              href={file.directUrl}
              target="_blank"
              rel="noreferrer"
            >
              Open media
            </a>
          </article>
        ))}
      </div>
    </section>
  );
}

export default function App() {
  const [postUrl, setPostUrl] = useState("");
  const [postResult, setPostResult] = useState(null);
  const [postError, setPostError] = useState("");
  const [loadingPost, setLoadingPost] = useState(false);

  async function handlePostSubmit(event) {
    event.preventDefault();
    setLoadingPost(true);
    setPostError("");

    try {
      const data = await downloadPostMedia(postUrl);
      setPostResult(data);
    } catch (error) {
      setPostError(error.message);
    } finally {
      setLoadingPost(false);
    }
  }

  return (
    <main className="app-shell">
      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">Instagram Downloader</p>
          <h1>Get post images and videos from one panel.</h1>
          <p className="intro">
            Paste a public Instagram post, reel, or TV URL and get direct media
            links without saving files on the server.
          </p>
        </div>

        <aside className="hero-note">
          <p className="note-label">Downloader</p>
          <p>Ready for deployment</p>
          <p className="note-label">Supported</p>
          <p>Posts, reels, TV posts</p>
          <p className="note-label">Creator</p>
          <div className="social-list">
            <a
              className="social-link instagram-link"
              href="https://www.instagram.com/_e_n_e_m_y__/"
              target="_blank"
              rel="noreferrer"
            >
              <span className="social-icon instagram-icon">
                <SocialIcon kind="instagram" />
              </span>
              <span>@_e_n_e_m_y__</span>
            </a>
            <a
              className="social-link github-link"
              href="https://github.com/srj-nandu"
              target="_blank"
              rel="noreferrer"
            >
              <span className="social-icon github-icon">
                <SocialIcon kind="github" />
              </span>
              <span>srj-nandu</span>
            </a>
            <a className="social-link mail-link" href="mailto:srj.nandu@gmail.com">
              <span className="social-icon mail-icon">
                <SocialIcon kind="mail" />
              </span>
              <span>srj.nandu@gmail.com</span>
            </a>
          </div>
        </aside>
      </section>

      <section className="workspace single-panel">
        <article className="panel">
          <div className="panel-heading">
            <p className="eyebrow">Posts</p>
            <h2>Post and image downloader</h2>
          </div>

          <form onSubmit={handlePostSubmit} className="form-stack">
            <label htmlFor="postUrl">Instagram post URL</label>
            <input
              id="postUrl"
              name="postUrl"
              type="url"
              placeholder="https://www.instagram.com/p/SHORTCODE/"
              value={postUrl}
              onChange={(event) => setPostUrl(event.target.value)}
              required
            />

            <button type="submit" disabled={loadingPost}>
              {loadingPost ? "Fetching..." : "Get Media Links"}
            </button>
          </form>

          <p className="helper-text">
            This version is easier to deploy because it does not store downloaded files on the server.
          </p>

          {postError ? <p className="error-text">{postError}</p> : null}
          <ResultPanel result={postResult} />
        </article>
      </section>
    </main>
  );
}
