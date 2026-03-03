# 🧠 Synaptic — In-Depth Implementation Guide

This document provides a high-level and granular look at the technical architecture, security protocols, and persistence layers of the **Synaptic Learning Tracker**.

---

## 🏗️ Technical Architecture

Synaptic is built on a **Service-Repository Pattern** to decouple business logic from data access, ensuring the codebase is testable and maintainable.

### 📐 Layer Breakdown
1.  **📊 Models (SQLAlchemy)**: Database schema definitions using SQLAlchemy 2.0. 
2.  **📦 Repositories (CRUD)**: Pure database interactions. The `BaseRepository` provides generic operations and integrates with our sync notification system.
3.  **⚙️ Services (Logic)**: Orchestrates complex operations (e.g., progress calculation across categories, multi-entity updates).
4.  **🛤️ Routers (FastAPI)**: HTTP endpoints that validate incoming models (Pydantic) and return standardized JSON envelopes.

---

## 🛡️ Security & Authentication

We transitioned from simple names to a full-fledged **JWT (JSON Web Token)** security layer.

### 🔐 Implementation Details
- **Password Protection**: Passwords are never stored in plain text. We use `passlib` with the `bcrypt` hashing algorithm.
- **JWT Lifetime**: Tokens are set to expire after **30 days** to balance security and user convenience.
- **Statelessness**: The server doesn't "remember" you; it validates the `Authorization: Bearer <token>` header on every sensitive request.
- **Frontend Marriage**: The UI stores the token in `localStorage`, automatically injecting it into all `fetch()` calls via a global `apiFetch` wrapper.

---

## ☁️ Google Drive Persistence Layer

To solve the "In-Memory Data Loss" problem of SQLite, we implemented a sophisticated background synchronization service.

### 🔄 The Dual Auth System
Synaptic supports two ways to connect to Google Drive:
1.  **OAuth2 (Primary)**: Best for personal `@gmail.com` accounts. It creates a `token.json` that acts as YOU, using your personal storage quota.
2.  **Service Account (Backup)**: Used for server-to-server communication in organizational Google Workspace environments.

### ⚡ Optimization: Modification Tracking
We don't want to waste API calls or CPU cycles. We implemented a **"Lazy Sync"** pattern:
- **Global Counter**: A variable `_HAS_CHANGES` monitors the system.
- **Hooked Repository**: Every time `create()`, `update()`, or `delete()` is called in the `BaseRepository`, it triggers `mark_modified()`.
- **Intelligent Loop**: The background thread wakes up every 5 minutes (default), checks the flag, and only uploads files if actual changes were detected.

---

## 🌈 Domain Features

### 🎨 Dynamic Categories & Auto-Coloring
- **Unlimited Categories**: Users aren't restricted to "Math" or "Code." Any category name works.
- **Deterministic Coloring**: A specific algorithm generates a stable HSL color based on the category name string, ensuring "Backend" is always the same blue across all sessions.
- **Category Progress**: Aggregates all underlying topics to give a real-time percentage of mastery for that specific domain.

### 📅 Metadata & Progress Cascading
- **Automatic Timestamps**: `created_at` and `updated_at` are managed at the model level.
- **Topic Completion**: Marking a SubTopic as complete automatically triggers a recalculation of the parent Topic's progress.

---

## 🐳 Deployment & Operations

### 📦 Containerization
The app is fully Dockerized using a multi-stage `Dockerfile` and `docker-compose.yml`.
- **Runtime Injection**: Secrets are **not** baked into the image. We use `--env-file .env` at runtime to inject sensitive keys (GDrive JSON, JWT secrets).
- **Static UI**: Nginx serves the Glassmorphism frontend and proxies API requests to the Python backend.

### 📝 Observability (Logging)
- **Terminal**: Real-time streaming logs.
- **File Logging**: All events are persisted to **`app.log`** in the root directory. This allows for post-mortem debugging and audit trails of the sync service.

---
*Last Updated: 2026-03-03*
