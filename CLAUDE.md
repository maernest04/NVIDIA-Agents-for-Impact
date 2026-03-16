# CLAUDE.md

## Project Overview

**WatchEmGo** is a server monitoring system using a heartbeat/dead-man's-switch pattern. Registered servers must ping WatchEmGo within a configurable interval. If a server goes silent, the system sends alert notifications.

- **Domain:** doggo.ink
- **Go version:** 1.23 (uses Go 1.22+ `http.ServeMux` pattern matching)
- **Routing:** Go 1.22+ enhanced `http.ServeMux` with `r.PathValue()` — no manual string parsing
- **Auth:** OAuth via `goth`/`gothic` (Google, GitHub, Discord)
- **Encryption:** AES-256-GCM tokens via `encrypt` package
- **Deployment:** Docker containers on 3 VMs via GitHub Actions matrix strategy

## Project Structure

```
backend_go/
├── main.go                  # Route registration (Go 1.22+ ServeMux), http.Server with timeouts,
│                            #   OAuth callback with user upsert, auth handlers
├── auth/
│   ├── auth.go              # OAuth setup (Google, GitHub, Discord). Requires SESSION_SECRET env var.
│   ├── auth_test.go         # Provider registration + session option tests
│   ├── middleware.go         # RequireUser middleware, SessionUser type, UserFromContext/ContextWithUser
│   └── middleware_test.go    # Middleware unit tests (6 tests)
├── handlers/
│   ├── servers.go           # Server CRUD + key rotation handlers (ServerHandler struct, Querier interface)
│   ├── servers_test.go      # Handler unit tests (mock Querier)
│   ├── heartbeat.go         # Heartbeat endpoint (HeartbeatHandler struct, HeartbeatQuerier interface, recovery alerts)
│   ├── heartbeat_test.go    # Heartbeat handler unit tests (mock HeartbeatQuerier, recovery alert tests)
│   ├── timers.go            # Per-monitor stale timers (StaleTimerManager, TimerQuerier interface, down alerts)
│   ├── timers_test.go       # Timer manager unit tests (fire, reset, cancel, retry, concurrency, alerts)
│   ├── discord.go           # Discord channel picker (DiscordHandler, DiscordQuerier interface, token storage/refresh, user guild filtering, per-user cache)
│   ├── discord_test.go      # Discord handler unit tests (mock Discord API, token refresh, cache isolation, intersection, StoreTokens)
│   ├── slack.go             # Slack OAuth install, callback, multi-workspace management, channel listing (SlackHandler, SlackQuerier)
│   ├── slack_test.go        # Slack handler unit tests (install, callback, workspaces, channels, uninstall)
│   └── testmain_test.go     # TestMain — initializes encrypt for handler tests
├── db/
│   ├── pool.go              # pgxpool.Pool connection helper
│   ├── migrate.go           # Embedded migrations via golang-migrate (runs on app startup)
│   ├── migrations/
│   │   ├── 000001_init_schema.{up,down}.sql
│   │   ├── 000002_add_monitor_status_check.{up,down}.sql
│   │   ├── 000003_add_notify_email.{up,down}.sql
│   │   ├── 000004_add_monitor_limit.{up,down}.sql
│   │   ├── 000005_add_discord_notifications.{up,down}.sql
│   │   ├── 000006_add_provider_tokens.{up,down}.sql
│   │   ├── 000007_add_slack_notifications.{up,down}.sql
│   │   └── 000008_multi_workspace_slack.{up,down}.sql
│   ├── sqlc/
│   │   ├── db.go            # Generated DBTX interface + Queries struct
│   │   ├── models.go        # Generated model types (User, Monitor, UserProvider, SlackInstallation)
│   │   ├── users.sql.go     # Generated user queries
│   │   ├── user_providers.sql.go  # Generated provider queries
│   │   ├── monitors.sql.go  # Generated monitor queries
│   │   ├── slack_installations.sql.go  # Generated slack installation queries
│   │   └── queries_test.go  # System tests (requires running Postgres)
│   └── sqlc.yaml            # sqlc codegen config
├── notify/
│   ├── notify.go            # Alerter interface (SendDownAlert, SendRecoveryAlert)
│   ├── smtp.go              # SMTPAlerter — sends email alerts via net/smtp with PlainAuth
│   ├── smtp_test.go         # SMTP alerter unit tests
│   ├── discord.go           # DiscordAlerter (DM/channel alerts), DiscordClient (guild/channel listing with cache, user guild listing, token refresh), snowflake validation
│   ├── discord_test.go      # Discord alerter + client unit tests (httptest, cache, filtering, user guilds, token refresh, snowflake validation)
│   ├── slack.go             # SlackAlerter (channel alerts with per-workspace bot tokens), SlackClient (channel listing), SlackHTTP (shared HTTP plumbing)
│   ├── slack_test.go        # Slack alerter + client unit tests (httptest, encryption, channel ID validation)
│   ├── service.go           # NotificationService — dispatches alerts to all configured channels (email + Discord + Slack)
│   ├── service_test.go      # NotificationService unit tests (flag combinations, nil safety, error isolation)
│   └── testmain_test.go     # TestMain — initializes encrypt for notify tests
├── encrypt/
│   ├── encrypt.go           # AES-256-GCM encrypt/decrypt with TTL + DecryptNoTTL for OAuth tokens. Requires ENCRYPT_KEY or SESSION_SECRET.
│   └── encrypt_test.go      # Encrypt/decrypt round-trip, expiry, tampering, no-TTL tests
├── static/
│   ├── index.html           # Frontend HTML (login, dashboard, search input, sort dropdown, monitor usage pill, add/edit/delete/rotate-confirm/rotate modals, notification channel checkboxes, Discord server/channel picker, Slack channel picker)
│   ├── app.js               # Frontend logic (auth, server CRUD, kebab menu, edit/rotate/delete flows, pagination, sort with localStorage persistence, search with debounce, keyboard shortcuts, channel selector, monitor usage indicator, Discord guild/channel dropdown picker, Slack cascading workspace→channel picker with OAuth install flow)
│   └── style.css            # Dark theme styles (includes .search-input, .sort-select, .monitor-usage, .channel-group/.channel-option, .discord-picker/.discord-select, .slack-picker/.slack-select/.slack-install-btn for channel dropdowns)
├── Dockerfile               # Multi-stage Go build (stripped binary) → Alpine runtime
├── go.mod / go.sum
├── .golangci.yml            # golangci-lint config (revive only, mirrors revive.toml rules)
├── revive.toml              # Linter config (used locally; CI uses golangci-lint)
└── .env                     # Local env vars (not committed)

nginx/
├── Dockerfile               # Nginx Alpine with custom config
└── nginx.conf               # SSL termination, reverse proxy to watchemgo:8080

.github/workflows/
├── deploy.yml               # CI/CD: lint, test, build Docker images, deploy via canary → remaining
└── utilities.yml            # Reusable deploy-to-VM workflow (called by deploy.yml)

docs/
└── api-design.md            # API specification for heartbeat monitoring service
```

## Build & Test Commands

```bash
# Run locally (from backend_go/)
go run .

# Run tests (auth + encrypt + handlers — no Postgres needed)
SESSION_SECRET=test go test -v -race ./...

# Run sqlc system tests (requires Postgres on localhost:5432)
docker compose up -d postgres
DATABASE_URL="postgres://watchemgo:localdev@localhost:5432/watchemgo?sslmode=disable" \
  SESSION_SECRET=test go test -v -race ./db/sqlc/

# Lint (install once: go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest)
~/go/bin/golangci-lint run ./...

# Docker compose (local)
docker compose up --build
```

## Key Architecture Decisions

- **Secrets are required:** `SESSION_SECRET` must be set or the app crashes on startup. No hardcoded fallbacks.
- **Request immutability:** `withProvider()` in main.go clones the request before injecting the `provider` query param for gothic. Never mutate `r.URL` directly.
- **Route pattern:** Auth routes are `/auth/{provider}`, `/auth/{provider}/callback`, `/auth/{provider}/logout`, `/auth/verify`. All provider-specific routes nest under `/auth/{provider}/`.
- **Auth middleware:** `auth.RequireUser` wraps all `/api/` handlers. It reads the `watchemgo_user` session cookie, parses `SessionUser` from the stored JSON, and injects it into the request context via `context.WithValue`. Downstream handlers retrieve it with `auth.UserFromContext(ctx)`. `auth.ContextWithUser` is exported for testing only.
- **User upsert on OAuth callback:** `callbackHandler` is a factory function taking `*pgxpool.Pool` and `*handlers.DiscordHandler`. On callback, it calls `FindUserByProvider` — if no rows, it creates the user and links the provider in a single transaction (`CreateUser` + `LinkProvider`). For Discord logins, it also stores the OAuth access/refresh tokens (encrypted) via `DiscordHandler.StoreTokens` for the channel picker guild filtering. The session stores the **DB UUID** as `user_id`, not the OAuth provider's ID.
- **Handler struct pattern:** `handlers.ServerHandler` holds a `Querier` interface (subset of `*sqlc.Queries`) and an optional `TxBeginner` (`Pool` field, satisfied by `*pgxpool.Pool`) for transactional creates. `handlers.HeartbeatHandler` holds a `HeartbeatQuerier` interface (`RecordHeartbeat`, `GetUserNotificationInfo`) and an optional `*notify.NotificationService` (nil-safe) for recovery alerts. Both handlers hold an optional `*StaleTimerManager` (nil-safe). `handlers.StaleTimerManager` holds a `TimerQuerier` interface (`UpdateMonitorStatus`, `GetActiveMonitorsWithPing`, `GetMonitorByID`, `GetUserNotificationInfo`) and an optional `*notify.NotificationService` (nil-safe) for down alerts. `handlers.DiscordHandler` holds an optional `*notify.DiscordClient` (nil-safe), a `DiscordQuerier` interface (`GetDiscordTokens`, `UpdateProviderTokens`), and OAuth client credentials (`ClientID`, `ClientSecret`) for token refresh. It maintains a per-user guild cache (30s TTL) and filters the channel picker to guilds where both the bot and user are members. This enables unit testing with mocks — no database or third-party mock library needed. Tests inject `auth.SessionUser` via `auth.ContextWithUser` and set path params via `r.SetPathValue()`.
- **Heartbeat endpoint:** `GET/POST /api/heartbeat` — unauthenticated, API key passed via `Authorization: Bearer <uuid>` header (not in URL path — keeps keys out of access logs, proxy logs, and referrer headers). Returns 404 for unknown keys, 500 for DB errors.
- **Per-monitor stale timers:** `StaleTimerManager` in `handlers/timers.go` replaces the old global polling loop. Each active monitor gets a `time.AfterFunc` timer set to fire at `last_ping_at + interval_sec * (grace_period + 1)`. The first interval is the normal heartbeat window; `grace_period` is the number of *additional* missed intervals tolerated. Timers are scheduled/reset on heartbeat (`Ping`), rescheduled on update (`Update`), and cancelled on delete (`Delete`). On startup, `LoadExisting` queries `GetActiveMonitorsWithPing` and hydrates timers for all active monitors — already-stale ones fire immediately. On timer expiry, `UpdateMonitorStatus` marks the monitor `"down"` with the TOCTOU race guard (`LastPingAt`). If the DB call fails, the timer retries up to 3 times with 30s backoff; a heartbeat arriving between retries cancels the retry.
- **Graceful shutdown:** On SIGINT/SIGTERM, `timerMgr.StopAll()` cancels all per-monitor timers, prevents new ones from being scheduled, and blocks (via `sync.WaitGroup`) until all in-flight timer callbacks complete — ensuring no goroutines are mid-DB-call when the pool closes. Then `srv.Shutdown()` drains HTTP requests, then `pool.Close()` closes the DB connection.
- **API key one-time view:** `api_key` is only returned on Create (full `sqlc.Monitor`) and Rotate (explicit `api_key` field). List, Get, and Update return `monitorResponse` which deliberately omits `api_key`. Defense in depth — even if the frontend is compromised, the API won't leak keys on read operations.
- **Sort and search options:** `GET /api/servers` supports `?sort=` with values: `created` (default, newest first), `name` (A-Z), `status` (down first). Invalid values silently default to `created`. Supports `?search=` for case-insensitive substring matching on monitor name via SQL `ILIKE` (empty string returns all; trimmed of whitespace). Implemented as 3 separate sqlc queries (`ListMonitorsByUserIDByCreated`, `ListMonitorsByUserIDByName`, `ListMonitorsByUserIDByStatus`) dispatched by `listMonitors()` in the handler. Each sort includes `created_at DESC` as a tiebreaker. The response also includes `monitor_count` (total monitors owned, unfiltered) and `monitor_limit` (null = unlimited) via the read-only `GetMonitorUsage` query. The frontend persists the user's sort preference in `localStorage` and restores it on page load. Search is session-only (not persisted) with 300ms debounce.
- **CI/CD:** Pipeline: `build` (lint + test) → `build-images` (app + nginx in parallel via matrix) → `deploy-canary` → `deploy-remaining` (matrix over team members). All GitHub Actions are SHA-pinned for supply chain security. Docker builds use GHA layer cache (`cache-from: type=gha`). Images are tagged `:latest` + `:sha-<commit>` for rollback. A `concurrency` group prevents overlapping deploys. Secrets accessed dynamically via `secrets[format('{0}_VM_IP', matrix.env)]`.
- **Migrations:** Schema is managed by embedded SQL migrations (`golang-migrate`), applied automatically on app startup via `db.RunMigrations()`. No manual `init.sql` needed on deploy — the legacy SCP + `psql` step has been removed from the deploy workflow. Note: prod originally used a manual `init.sql`, so 000001 is idempotent (`IF NOT EXISTS`) and 000002+ carry incremental changes.
- **Query-level ownership:** User-facing mutating queries (`UpdateMonitor`, `DeleteMonitor`, `RotateAPIKey`) include `AND user_id = $N` in the WHERE clause. This enforces ownership at the data layer as defense in depth — even a handler bug can't allow cross-user mutation. `DeleteMonitor` uses `:execresult` so handlers can check `RowsAffected()` to distinguish "not found" from "deleted." `UpdateMonitorStatus` is intentionally unscoped — it's called by the per-monitor stale timer (a system action, not a user action). It includes a TOCTOU race guard (`AND (last_ping_at IS NULL OR last_ping_at <= $3)`) to prevent a stale check from overwriting a heartbeat that arrived between the staleness query and the status update.
- **Multi-channel notifications:** The `notify` package provides `NotificationService` which dispatches alerts to all configured channels. `SMTPAlerter` sends email via `net/smtp` with `PlainAuth`. `DiscordAlerter` sends Discord messages via the Bot API — supports DMs (via user ID from `user_providers`) and channel messages (via `discord_channel_id` on monitors). Channel messages include `@here` pings; DMs do not. `SlackAlerter` sends Slack messages via `chat.postMessage` — receives the encrypted per-workspace bot token per-call (looked up via `slack_installations` using `monitors.slack_workspace_id`), decrypts it via `encrypt.DecryptNoTTL`, and posts to the configured `slack_channel_id`. All three are nil-safe — if the respective env vars are not set, the alerter is nil and that channel is silently skipped. The `NotificationService` is injected into both `StaleTimerManager` (down alerts) and `HeartbeatHandler` (recovery alerts). Alerts are best-effort: errors are logged but not retried. Per-monitor opt-in is controlled by `notify_email` (default true), `notify_discord` (default false), and `notify_slack` (default false) boolean columns. The frontend sends `notify_channels: ["email", "discord", "slack"]` in the JSON payload. `GetUserNotificationInfo` (replaces `GetUserEmailByMonitorID`) joins users + monitors + user_providers + slack_installations (via `monitors.slack_workspace_id`) to fetch all notification context in one query.
- **Discord bot integration:** Reuses the existing Discord OAuth application as a bot. `DiscordAlerter` (in `notify/discord.go`) shares HTTP plumbing with `DiscordClient` via an embedded `DiscordHTTP` struct (DRY). `DiscordClient` provides `ListGuildChannels(ctx)` for the channel picker — fetches guilds via `GET /users/@me/guilds`, then fetches channels per guild in parallel (semaphore-capped at 5 goroutines), filters to text (type 0) and announcement (type 5) channels. Bot guild/channel results are cached in-memory with 60s TTL. `DiscordHTTP.SetBaseURL()` allows tests to point at httptest servers without mutating package globals. `GET /api/discord/channels` (authenticated) returns only guilds where both the bot AND the authenticated user are members. User guild lists are fetched via `DiscordClient.ListUserGuilds` (Bearer auth with the user's stored OAuth token) and cached per-user with 30s TTL. If the user's token is expired (401), `DiscordHandler` attempts an automatic refresh via `DiscordHTTP.RefreshToken` using Discord's OAuth2 token endpoint; refreshed tokens are persisted back to the DB (non-fatal on failure). If refresh also fails, returns 403 `discord_reauth_required`. Discord OAuth scope `guilds` is required in addition to `identify` and `email`. Snowflake IDs are validated as numeric-only before interpolation into API URL paths. `GET /api/config` (unauthenticated) exposes `DISCORD_CLIENT_ID` for the frontend invite button. The frontend renders cascading server/channel `<select>` dropdowns when the Discord checkbox is enabled; falls back to an "Add Bot to Server" invite link if the bot isn't in any servers.
- **Discord OAuth token storage:** Discord OAuth tokens are encrypted (AES-256-GCM via `encrypt.Encrypt`) and stored in `user_providers.access_token`/`refresh_token` (migration 000006). Tokens are written on OAuth callback via `DiscordHandler.StoreTokens` and refreshed automatically when expired. `encrypt.DecryptNoTTL` decrypts tokens without enforcing TTL since their lifecycle is managed externally by Discord's token expiry.
- **Slack bot integration:** Unlike Discord (single global bot token), Slack provides a **per-workspace bot token** during OAuth v2 installation. Each user can install the bot to **multiple** workspaces via `GET /api/slack/install` → Slack OAuth → `GET /api/slack/callback`. Bot tokens are encrypted (AES-256-GCM) and stored in the `slack_installations` table (one row per user per workspace, keyed by `(user_id, team_id)`). Monitors reference a specific workspace via `slack_workspace_id`. `SlackAlerter` (in `notify/slack.go`) shares HTTP plumbing via an embedded `SlackHTTP` struct (mirrors `DiscordHTTP` pattern). `SlackClient` provides `ListChannels(ctx, botToken)` for the channel picker — calls `conversations.list?types=public_channel,private_channel&exclude_archived=true`. `SlackHTTP.SetBaseURL()` allows tests to point at httptest servers. `GET /api/slack/workspaces` (authenticated) returns installed workspaces. `GET /api/slack/channels?workspace_id=T...` (authenticated) returns channels for a specific workspace. `DELETE /api/slack/workspaces/{workspace_id}` removes a workspace installation. The frontend renders cascading workspace→channel `<select>` dropdowns (mirroring Discord's server→channel pattern). Slack channel IDs are validated with regex `^[A-Z0-9]{9,15}$`. Workspace IDs are validated with regex `^[A-Z0-9]{1,20}$`. Slack always returns HTTP 200 — the response body must be parsed for `{"ok": false, "error": "..."}`. `GET /api/config` (unauthenticated) also exposes `slack_client_id` for the frontend. Configured via `SLACK_CLIENT_ID`, `SLACK_CLIENT_SECRET`, `SLACK_CALLBACK_URL` env vars.
- **Recovery alerts via CTE:** `RecordHeartbeat` uses a CTE to capture `previous_status` before the UPDATE, returning it alongside the updated row. The heartbeat handler checks `previous_status == "down"` to trigger recovery alerts without a separate query.
- **Per-user monitor limit:** The `users.monitor_limit` column (nullable `INTEGER`, default 5 for new users) caps how many monitors a user can create. Existing users have `NULL` (unlimited — grandfathered). The `Create` handler wraps the limit check and INSERT in a single transaction via `ServerHandler.Pool` (`TxBeginner` interface, satisfied by `*pgxpool.Pool`). `CheckMonitorLimit` uses `FOR UPDATE OF u` to lock the user row, serializing concurrent creates and preventing TOCTOU races. The shared `createMonitor` helper works with any `Querier` (real `*sqlc.Queries` or a mock). When `Pool` is nil (unit tests), the handler falls back to non-transactional mode using `h.Queries` directly. If `monitor_limit` is NULL, the check is skipped. If the count meets or exceeds the limit, returns 403 "monitor limit reached". The `List` handler also calls `GetMonitorUsage` (a read-only variant without `FOR UPDATE`) to include `monitor_count` and `monitor_limit` in the response. The frontend displays a usage pill (`3 / 5 monitors`) with color-coded states (green → yellow at 80% → red at limit) and disables the "+ Add Service" button when the limit is reached.
- **Path filters:** CI only runs when `backend_go/**`, `nginx/**`, or the workflow file itself changes.

## Environment Variables

Required:
- `SESSION_SECRET` — used for session cookies and as fallback encryption key
- `POSTGRES_PASSWORD` — used by Docker Compose to configure Postgres and build `DATABASE_URL` automatically

Optional:
- `PORT` — defaults to 8080
- `ENCRYPT_KEY` — separate encryption key (falls back to SESSION_SECRET)
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_CALLBACK_URL`
- `GH_CLIENT_ID`, `GH_CLIENT_SECRET`, `GH_CALLBACK_URL`
- `DISCORD_CLIENT_ID`, `DISCORD_CLIENT_SECRET`, `DISCORD_CALLBACK_URL`
- `DISCORD_BOT_TOKEN` — Discord bot token (same application as OAuth). Discord alerts + channel picker disabled if not set.
- `SLACK_CLIENT_ID`, `SLACK_CLIENT_SECRET`, `SLACK_CALLBACK_URL` — Slack app credentials for OAuth v2 bot installation. Slack alerts + channel picker disabled if `SLACK_CLIENT_ID` is not set.
- `SMTP_HOST` — SMTP server hostname (e.g., `smtp.gmail.com`). Email alerts disabled if not set.
- `SMTP_PORT` — SMTP server port (e.g., `587`)
- `SMTP_USER` — SMTP username
- `SMTP_PASS` — SMTP password (e.g., Gmail app password)
- `SMTP_FROM` — sender email address

---

## Engineering Preferences

These preferences apply to ALL code changes, reviews, and recommendations.

### Verification Steps

After every code change, run these before considering the task complete:
1. `SESSION_SECRET=test go test -v -race ./...`
2. `~/go/bin/golangci-lint run ./...`
3. `DATABASE_URL="postgres://watchemgo:localdev@localhost:5432/watchemgo?sslmode=disable" SESSION_SECRET=test go test -v -race ./db/sqlc/` (requires `docker compose up -d postgres`)
4. Update `CLAUDE.md` and `docs/api-design.md` if the change affects schema, API behavior, architecture decisions, or project structure.

### Core Values

- **DRY is important** — flag repetition aggressively.
- **Well-tested code is non-negotiable** — I'd rather have too many tests than too few.
- **"Engineered enough"** — not under-engineered (fragile, hacky) and not over-engineered (premature abstraction, unnecessary complexity).
- **Handle more edge cases, not fewer** — thoughtfulness > speed.
- **Bias toward explicit over clever.**

### Review Process

Before making code changes, review the plan thoroughly. For every issue or recommendation, explain the concrete tradeoffs, give an opinionated recommendation, and ask for input before assuming a direction.

**Before starting any task, ask:**

1. **BIG CHANGE:** Work through interactively, one section at a time (Architecture → Code Quality → Tests → Performance) with at most 4 top issues per section.
2. **SMALL CHANGE:** Work through interactively, ONE question per review section.

**For each stage of review:**

1. **Architecture review** — system design, component boundaries, dependency graph, coupling, data flow, bottlenecks, scaling, single points of failure, security architecture (auth, data access, API boundaries).
2. **Code quality review** — code organization, module structure, DRY violations (be aggressive), error handling patterns, missing edge cases (call out explicitly), technical debt hotspots, over/under-engineering.
3. **Test review** — coverage gaps (unit, system, e2e), test quality, assertion strength, missing edge case coverage, untested failure modes and error paths.
4. **Performance review** — N+1 queries, database access patterns, memory usage, caching opportunities, slow or high-complexity code paths.

**For every specific issue found:**

- Describe the problem concretely, with file and line references.
- Present 2-3 options, including "do nothing" where reasonable.
- For each option: implementation effort, risk, impact on other code, maintenance burden.
- Give a recommended option and why, mapped to the engineering preferences above.
- NUMBER issues and give LETTERS for options. Recommended option is always listed first.
- Ask whether I agree or want a different direction before proceeding.

**Workflow rules:**

- Do not assume priorities on timeline or scale.
- After each section, pause and ask for feedback before moving on.


The following list are mistakes that have been made by Claude, and should be read so it won't be repeated
- Do not use any sleep function in the CI
- Always quote `-e` values in `docker run` commands (e.g., `-e "VAR=${{ secrets.VAR }}"`) — unquoted values break when secrets contain spaces or shell metacharacters
- PostgreSQL CTE subqueries referenced in `RETURNING` clauses of DML statements return NULL — the CTE result is not accessible from RETURNING. Use `UPDATE ... FROM (subquery) ... RETURNING` instead to capture pre-update column values (e.g., `previous_status`). The `FROM` subquery's columns are directly available in RETURNING as real column references.
