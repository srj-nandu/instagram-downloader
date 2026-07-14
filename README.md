# Instagram Image Downloader

This repository is split into two services:

- `client/` - React frontend powered by Vite
- `server/` - Node.js API powered by Express
- `story-service/` - optional FastAPI service for authenticated story downloads

## What the MVP supports

- Public Instagram post URLs for image and video download
- Direct media links returned to the frontend

## Environment

### Client

Copy `client/.env.example` to `client/.env` if you want a custom API URL.

### Server

Copy `server/.env.example` to `server/.env`.

## Root shortcuts

From the repo root you can now use:

```bash
npm run setup
npm run dev
```

`npm run setup` will:

- install `client/` dependencies
- install `server/` dependencies
- create missing `.env` files from `.env.example`

The root `npm run dev` command starts:

- Vite in `client/`
- Express in `server/`

## Windows bootstrap files

If you prefer direct shell scripts:

- `.\setup.ps1`
- `.\dev.ps1`
- `setup.bat`
- `dev.bat`

### Server

```bash
cd server
npm install
npm run dev
```

Deploy note:

- A root `render.yaml` is included for Git-based Render deployment of the
  Vite static site, Express API, and optional FastAPI story service.
- The FastAPI service runs behind Gunicorn with Uvicorn workers via
  `story-service/gunicorn.conf.py`.
- To enable story downloads, add `INSTAGRAM_USERNAME` and `INSTAGRAM_PASSWORD`
  to the `instagram-story-service` environment in Render.
- For persistent story sessions across deploys, attach a Render disk and point
  `INSTAGRAM_SESSION_FILE` and `DOWNLOADS_DIR` at that disk mount path.

### Client

```bash
cd client
npm install
npm run dev
```

## API summary

- `POST /api/downloader/post`
