# Instagram Image Downloader

This repository is split into two services:

- `client/` - React frontend powered by Vite
- `server/` - Node.js API powered by Express

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

- A root `render.yaml` is included for Git-based Render backend deployment.

### Client

```bash
cd client
npm install
npm run dev
```

## API summary

- `POST /api/downloader/post`
