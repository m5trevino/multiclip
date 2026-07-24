---
name: auto-wire
description: Automatically wires up a Vite frontend to a backend (FastAPI, Flask, Express) based on init-wire-up blueprints. Use when you need to execute a wiring plan, add CORS, mount static files, or configure SPA catch-all routes with deterministic precision.
---

# Auto-Wire Protocol

You are the **Linker**. Your mission is to execute the "handshake" between a frontend and a backend with zero-guess accuracy. You use surgical scripts to inject middleware and configuration without breaking existing code.

## 🚀 The Play

1.  **Audit**: Read the `WIRING.md` (or `AGENTS.md`) to extract the Ground Truth:
    - Backend Port (e.g., 3099)
    - Static Directory (e.g., `app/static`)
    - API Prefix (e.g., `/v1`)
    - Frontend Directory (e.g., `ui/`)
2.  **Backend Hardening**: Use `scripts/wire_backend.py` to inject CORS, Static Mounts, and SPA Fallbacks into the entry point.
3.  **Frontend Alignment**: Use `scripts/wire_frontend.cjs` to update `vite.config.ts` with the correct `outDir`.
4.  **Client Sync**: Update API client files (e.g., `api.ts`) to use dynamic `API_BASE` logic.
5.  **Verification**: Confirm the build outputs to the correct directory and the backend is configured to serve it.

## 🛠️ Commands

- `auto-wire`: Executes the full wiring process.
- `auto-wire --backend-only`: Only patches the backend.
- `auto-wire --frontend-only`: Only patches the frontend build config.

## 📁 Reference Patterns

See [references/patterns.md](references/patterns.md) for framework-specific code snippets used by the injection scripts.
