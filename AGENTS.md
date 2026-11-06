# AGENTS.md

This file provides guidance to AI coding agents when working with code in this repository.

## Overview

치직 (Chzzk Discord bot): sends Discord notifications when Chzzk (Naver streaming) channels go live. Backend is Python 3.12 AWS Lambdas deployed with Serverless Framework v4 (`ap-northeast-2`, stage `prodV2`, AWS profile `chzzk`); single DynamoDB table `chzzk-bot-db`. Frontend is a Next.js dashboard in `frontend/` served from S3 + CloudFront at chzzk.junah.dev. Comments, log messages, and user-facing strings are mostly Korean.

## Commands

Backend (repo root, Python managed by `uv`):

```bash
uv sync                      # install deps (incl. dev group: ruff, pytest, boto3, pynacl)
sh scripts/format.sh         # ruff check --fix + ruff format
serverless login             # once per machine; v4 needs a login for the `junah` org
serverless deploy            # deploy all lambdas/infra (needs .env and the `chzzk` AWS profile)
serverless deploy function -f live_check   # redeploy a single function
```

Tests (pytest, `pytest-mock`, `pytest-cov`):

```bash
uv run pytest                                            # all tests
uv run pytest lambdas/tests/shared/test_utils.py         # one file
uv run pytest --cov=lambdas --cov-report=term-missing    # with coverage (add --cov-report=html for htmlcov/)
```

- Tests live in `lambdas/tests/`, mirroring the `lambdas/` layout (`lambdas/shared/utils.py` → `lambdas/tests/shared/test_utils.py`). No `__init__.py` in test dirs; `--import-mode=importlib` keeps same-named test files apart. `serverless.yml` excludes `lambdas/tests/**` from the deploy package.
- `lambdas/tests/conftest.py` overwrites AWS/Discord env vars with fake values before any module is imported (several modules create boto3 clients or read tokens at import time) and blocks real socket connections. Every external call (Discord, Chzzk, AWS) must be mocked: `responses` for `requests`, `moto` for DynamoDB (replace the module-level `dynamodb`/`table` objects created inside `mock_aws()`).
- Use `monkeypatch` for env vars and plain attribute/dict swaps, and `mocker` (pytest-mock) for patching, spies, and call assertions; avoid importing `unittest.mock` directly.
- Code whose I/O is meant to be swapped in tests calls it through the module (`from cron.live_check import adapters` → `adapters.get_follows(...)`), never `from ... import get_follows`, which copies the name so patches on the module don't apply. `cron/live_check` is the example: `logic.py` (no I/O), `adapters.py` (DynamoDB/Chzzk/Discord), and the flow in `__init__.py`; its tests swap every adapter for an in-memory `Fake`.
- Pin current behavior; if it looks like a bug, note it and fix it in a separate commit. There is no coverage threshold.
- `tzdata` is a dev dependency because Windows has no system time zone data for `zoneinfo`.
- CI: `.github/workflows/backend-test.yml` runs `ruff check lambdas`, `ruff format --check lambdas`, and the full pytest suite with coverage on PRs and pushes to `main` that touch `lambdas/**`, `pyproject.toml`, or `uv.lock`.

Frontend (`frontend/`, pnpm):

```bash
pnpm install
pnpm dev      # local dev at :3000 (uses .env.development; API points at prod api.chzzk.junah.dev)
pnpm build    # static export to frontend/out
pnpm lint          # ESLint (eslint-config-next); lint only
pnpm format        # Biome formatter (formatter only; linter/assist disabled in biome.json)
pnpm format:check
```

Frontend deploys automatically via `.github/workflows/frontend-deploy.yml` on push to `main` touching `frontend/**` (build → `aws s3 sync out` → CloudFront invalidation).

## Backend architecture

- **Import root is `lambdas/`.** `PYTHONPATH` is `lambdas` locally (devcontainer) and `/var/task/lambdas` in Lambda, so code imports `from shared import ...`. Each function is a package `lambdas/<trigger>/<group>/<name>/__init__.py` exposing `handler`, and is wired up in `serverless.yml` as `handler: lambdas/<trigger>/.../<name>.handler`. When moving/adding a function, keep the `serverless.yml` handler path in sync with the directory.
- **Directories by trigger type:** `api/` (API Gateway REST endpoints for the dashboard, under api.chzzk.junah.dev), `bot/` (Discord interaction webhooks: `event_handler` for the main bot, `admin_event_handler` for the admin bot; both verify Ed25519 signatures with PyNaCl), `cron/` (EventBridge schedules), `admin/` (manually invoked).
- **`shared.middleware(logger, admin_check=...)`** wraps every handler: logs the event, converts `shared.exceptions.BaseException` subclasses into HTTP responses (`to_dict()`), turns other exceptions into 500, and adds CORS/JSON headers. With `admin_check=True` it reads the Discord OAuth token from the `Authorization` header and `guild_id` from path params or JSON body, and verifies the user is a guild admin via `shared.discord.utils.is_admin`, which never raises and returns an `AdminCheckResult` (429 → `RateLimitError`, timeout/connection error/5xx → 502 `DiscordApiUnavailableError`, otherwise 403 `UserNotAdminError`). Raise exceptions from `shared.exceptions` rather than building error responses by hand.
- **Discord API is pinned to v10.** Build every Discord REST URL from `shared.discord.utils.DISCORD_API_BASE_URL` (`https://discord.com/api/v10`); never use unversioned `https://discord.com/api/...` paths, which answer in the deprecated v6 format. In v10, `permissions` on guild objects is a decimal string (`int(guild["permissions"])` before bit checks; see `shared.discord.PartialGuild`). User-supplied webhook URLs (`https://discord.com/api/webhooks/...`) are the exception and are used as given.
- **DynamoDB** is a single table `chzzk-bot-db` (see schema below).
- **Live detection works by following, not polling each channel.** There are 7 Naver accounts (index 0–6). `post_notification` assigns a channel to account `int(chzzk_id, 16) % 7` (probing forward if full) and makes that account follow the channel. `cron/live_check` runs every 5 minutes per account: one EventBridge Scheduler schedule per index (`live_check_for_N`, `schedule` events with `method: scheduler` on the `live_check` function in `serverless.yml`), each passing `{"index": N}` as the event, which the handler reads directly. It fetches the account's following list, finds `openLive` channels, and dispatches notifications via `shared.notification_dispatcher` (Discord bot message or custom webhook for subscribed guilds). Adding an account means adding a DynamoDB `NAVER#<n>` item, a new `live_check_for_<n>` schedule event with `input: {index: <n>}`, and updating the `% 7` modulus.
- Operational errors/reports are posted to internal Discord channels using `ADMIN_DISCORD_TOKEN`; channel IDs live in `serverless.yml` `provider.environment`. Secrets come from `.env`, which v4 loads automatically for `${env:...}`; it does not add variables to functions, so a new secret must also be listed under `provider.environment`.
- **Packaging (`serverless.yml`):** `package.patterns` is a whitelist (`!**`, then `lambdas/**`, minus `lambdas/tests/**`), so new top-level files and tests are never deployed. Runtime deps in `pyproject.toml` `dependencies` are bundled by v4's built-in Python requirements support (`custom.pythonRequirements`, via `uv.lock`; the dev group is excluded). PyNaCl is the exception: it ships as the prebuilt Lambda layer `custom.layers.pynacl` (python3.12/x86_64) attached only to `event_handler` and `admin_event_handler`, and is in the dev group for local use only. A function that newly imports `nacl` needs that layer too. `shared.discord.bot` (signature verification, `reply`, `PONG`, shared by both bot handlers) imports `nacl`, so import it by its full path and never re-export it from `shared.discord` or `shared`.
- **IAM:** extra permissions go in `provider.iam.role.statements`. In plain strings use Serverless variables (`${aws:region}`, `${aws:accountId}`); CloudFormation pseudo parameters like `${AWS::AccountId}` only work inside `!Sub`/`Fn::Sub`.

## DynamoDB schema (`chzzk-bot-db`)

The table is not managed by `serverless.yml` (its definition there is commented out), so this is the only schema reference. Single-table design with `PK`/`SK` strings, a `type` attribute on every item, and GSI `GSI-GuildID-v2` (hash `guild_id`, range `PK`, projection `ALL`) used to list a guild's items (filter on `type = NOTI` for its notifications). A second, sparse GSI `GSI-Type-ExpiresAt` (hash `type`, range `expires_at`, projection `ALL`) only holds items that have `expires_at`, which today means SUBSCRIPTION items; `cron/subscription_expiry` queries it for expired subscriptions. Don't add `expires_at` to other item types without accounting for this index. Code mixes the low-level client (`{"S": ...}` typed values) and the `Table` resource (plain values); `shared.dynamo_to_python` converts client items.

| `PK` | `SK` | `type` | Purpose |
| --- | --- | --- | --- |
| `GUILD#<guild_id>` | `GUILD#<guild_id>` | `GUILD` | Guild slot counter |
| `GUILD#<guild_id>` | `SUB#CURRENT` | `SUBSCRIPTION` | Current monthly subscription |
| `GUILD#<guild_id>` | `ORDER#<YYYYMMDDHHMMSS>#<short_uuid>` | `ORDER` | Purchase history |
| `CHZZK#<chzzk_id>` | `CHZZK#<chzzk_id>` | `CHZZK` | Registered Chzzk channel |
| `CHZZK#<chzzk_id>` | `NOTI#<discord_channel_id>` | `NOTI` | One notification (Chzzk channel → Discord channel) |
| `NAVER#ACCOUNTS` | `NAVER#<index>` | `NAVER` | Naver account used for following |

Attributes:

- **GUILD**: `guild_id`, `current_count` (notifications registered; must be kept in sync whenever a NOTI item is created or deleted), `max_limit` (slots; default 5 when the item is missing, raised by purchases, 250 for subscribers).
- **SUBSCRIPTION**: `guild_id`, `plan_type` (e.g. `MONTHLY_SUB_2000`), `status` (`ACTIVE` | `EXPIRED` | `SUSPENDED`), `purchased_at`, `expires_at` (ISO 8601 UTC), `amount`, `auto_renew`, `buyer_discord_id`. Active means `status == ACTIVE` and `expires_at` > now (`shared.notification_dispatcher.is_guild_subscription_active`). Renewing while active extends from the current `expires_at`. Purchasing slots while subscribed is refused. `cron/subscription_expiry` runs daily: it sets `status = EXPIRED`, restores the GUILD `max_limit` to the `slot_info.previous_slot` of the guild's latest subscription ORDER whose `previous_slot` isn't 250 (renewals record 250; guilds that joined before paid plans got 15 slots, so 5 is not a safe default and the cron skips and alerts when no such ORDER exists), and clears `is_subscription_active` on its NOTI items.
- **ORDER**: `guild_id`, `product_type`, `amount`, `payment_status`, `purchased_at`, `buyer_discord_id`, `slot_info` map (`previous_slot`, `final_slot`). Created by the admin bot (`bot/admin_event_handler`).
- **CHZZK**: `channelId`, `channelName`, `channelImageUrl` (camelCase, copied from the Chzzk API), `index` (Naver account that follows it), `lastLiveId` / `lastLiveTitle`. `live_check` sends notifications only when the current `liveId` differs from `lastLiveId`, then updates it, so a channel is notified once per broadcast.
- **NOTI**: `guild_id`, `channel_id`, `channel_name` (Discord), `chzzk_id`, `chzzk_name`, `chzzk_image_url`, `custom_message`, `disable_notification` / `disable_embed` / `disable_button` / `disable_tag` (bools; `disable_tag` hides the stream tags embed field, missing means shown), optional `webhook_url` / `embed_color` / `is_subscription_active` (subscriber features), and delivery state written by `live_check`: `last_noti_at`, `last_noti_status` (`SUCCESS` | failure), `noti_fail_count` (reset to 0 on success). `index` is always written as `-1` here; the real account index lives on the CHZZK item.
- **NAVER**: `NID_AUT`, `NID_SES` (session cookies used by `live_check`/`post_notification`, refreshed by `cron/naver_session_renew`) plus account credentials/personal info (`id`, `password`, `name`, `birth`, `phone`). These are live secrets: never log, print, or copy their values into code, docs, or commits.

## Frontend architecture

- Next.js App Router with `output: "export"` (fully static, `trailingSlash: true`); no server components that need runtime/API routes. A CloudFront function rewrites extensionless paths to `/index.html`.
- Route groups: `(marketing)` (landing, pricing, docs, policies), `(auth)` (Discord OAuth login/callback/logout), `dashboard` (guild/notification management).
- API calls go through the axios client in `lib/api-client.ts` (`NEXT_PUBLIC_API_URL`) with TanStack Query; UI is Tailwind v4 + shadcn/Radix components in `components/ui`.

## Commit convention

Commit subjects are `<gitmoji> <English summary>`: one emoji (the Unicode character, not `:code:`), a space, then an imperative, capitalized summary with no trailing period. PRs are squash-merged, so GitHub appends the PR number: `🐛 Fix some imports after lambdas restructure (#1)`. Don't invent a `(#N)` for a direct commit. Older history has some Korean subjects; write new ones in English.

Gitmoji as used in this repo:

| Emoji | Use for | Example from history |
| --- | --- | --- |
| ✨ | New feature, endpoint, or Lambda | `✨ Add lambda handler that send weekly report (#35)` |
| 🐛 | Bug fix | `🐛 Use the correct Discord API base URL (#20)` |
| 🚑️ | Urgent hotfix to production | `🚑️ 관리자 권한 체크 추가` |
| ♻️ | Refactor without behavior change | `♻️ Wrap notification delete and count update in a transaction` |
| ⚡️ | Performance improvement | `⚡️Switch from query to scan for cleanup orphan chzzk channels` |
| 🧱 | AWS infrastructure in `serverless.yml` (resources, log retention, S3/CloudFront) | `🧱 Secures S3 bucket and configures CloudFront` |
| 🔒 | Security and IAM permissions | `🔒 Restrict DynamoDB IAM permissions to necessary actions` |
| 🗃️ | DynamoDB schema or index changes | `🗃️ Switch to GSI-GuildID-v2 for full projection` |
| 🔧 | Dev tooling config (devcontainer, scripts, uv) | `🔧 Update format script to use uv and new lambdas layout` |
| 🔨 | Add development scripts | `🔨 Add format script` |
| 👷 | CI/CD (GitHub Actions) | `👷 Removes push trigger for frontend deployment` |
| 🔊 | Add or improve logs | `🔊 Add timestamp to discord log payload` |
| 💬 | User-facing text and messages | `💬 Enhance user-facing error messages for notification registration` |
| 📝 | Docs (README, docs pages, blog posts) | `📝 Expand troubleshooting docs with new error cases` |
| ✅ | Add or update tests | `✅ Add tests for shared utils` |
| 🎨 | Formatting only (ruff, eslint) | `🎨 Ruff format` |
| 🚚 | Move or rename files, directories, or routes | `🚚 Restructure lambdas by trigger type (api, cron, bot, admin)` |
| 🔥 | Remove code, files, or dependencies | `🔥 Remove pydantic dependencies` |
| ⬆️ | Upgrade dependencies (Dependabot uses this too) | `⬆️ Bump requests from 2.32.5 to 2.34.2` |
| ➕ | Add a dependency | `➕ user_agent 모듈 의존성 추가` |
| 🙈 | `.gitignore` | `🙈 Update .gitignore` |
| ⏪️ | Revert | `⏪️ Revert v2 changes and restore to v1` |
| 🔖 | Release / version tag | `🔖 Release version 2.0.0` |

Pick the emoji by the main intent of the change. For infra, use 🧱 for resources, 🔒 for permissions, and 🔧 for local tooling.
