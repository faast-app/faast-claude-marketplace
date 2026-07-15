# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

This is the **FAAST Claude Code plugin marketplace** — a distribution repo, not an application. There is no build, lint, or test step. The "code" is Markdown agent/command definitions and JSON manifests that Claude Code installs and loads at runtime. Validation is structural: manifests must match Claude Code's plugin/marketplace schemas, and agent/command Markdown must carry correct YAML frontmatter.

Users consume it via:
```bash
claude plugin marketplace add faast-app/faast-claude-marketplace
claude plugin install <plugin-name>@faast-marketplace
claude plugin marketplace update faast-marketplace   # after changes are pushed to main
```

## Repository structure

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json) — the marketplace manifest. Every plugin must be registered here with a `source` pointing at `./plugins/<name>`. **Adding a plugin folder is not enough — it must also be listed here.**
- [plugins/](plugins/) — one folder per distributable plugin. Each has `.claude-plugin/plugin.json` plus some combination of `agents/`, `commands/`, `templates/`, `README.md`.
- `.claude/` (untracked) — this repo's own local agent/command setup. Not part of what gets distributed.

## The two plugins

### senior-backend-architect
Single agent + single `/architect` command. A self-contained expert that runs a fixed 4-phase flow (Understand → Analyze → Recommend → optionally Implement) for backend review/debugging/design across .NET, Python, Java, Node.js, etc. No coordination machinery — it's a one-shot consultant.

### dev-team
A **team of 15 role-agents** covering the full SDLC that collaborate to build/operate real projects (mono-repo or multi-repo). This is the substantial plugin; understand its model before editing it.

**Agents** (`plugins/dev-team/agents/*.md`): `setup`, `product-owner`, `architect`, `ui-designer`, `lead`, `backend`, `frontend`, `dba`, `qa` (QA Lead), `qa-frontend`, `qa-backend`, `release-manager`, `infra`, `cybersec`, `tech-writer`. Each is a Markdown file with frontmatter (`name`, `description`, `model`, `tools`). The `description` is what Claude Code uses to decide when to auto-delegate, so it matters functionally. The `model` field is deliberately tiered to optimize token cost: `haiku` for setup/tech-writer, `sonnet` for everyone else (architect included — it defaults to sonnet, upgradeable per project via `team.models.architect: "opus"` in `.coordination/config.json`, which the lead/flows pass as a model override when invoking). Keep that discipline when adding agents, and never use `fable`.

**Commands** (`plugins/dev-team/commands/*.md`): 22 slash commands. `/start` is the universal entry point (detects context, routes the user — simplicity is a core design goal). Others: `/new-project`, `/onboard`, `/setup`, `/refine`, `/assign-task`, `/inbox`, `/handoff`, `/sync`, `/test-plan`, `/e2e`, `/review-pr`, `/git-check`, `/security-audit`, `/db-health`, `/deploy-check`, `/document`, `/status`, `/pase` (environment release requests via release-manager), `/team-metrics` (per-agent productivity + token usage, for the Lead), `/wiki` (init/ingest/lint/query of the project wiki, run by tech-writer), `/team-office` (live 2D virtual-office dashboard). Frontmatter `description` + `argument-hint`; body is the procedure, with `$ARGUMENTS` interpolated. Commands orchestrate; agents do the work.

**Templates** (`plugins/dev-team/templates/`): scaffolding the `/new-project` flow copies when creating repos — `dotnet-microservice`, `nodejs-microservice`, `react-spa`, `react-microfrontend`, gateway variants (`gateway-yarp`, `gateway-ocelot`, `gateway-traefik`), and `project-umbrella`. Filenames/contents use `{{ServiceName}}` placeholders. `templates/pase/` holds the release-request docx template (`Plantilla_Solicitud_Pase_Devs.docx`) that release-manager fills.

## Core model of dev-team (the non-obvious part)

These conventions are enforced by the agent prompts themselves — preserve them when editing:

- **`.coordination/config.json` is the source of truth** every agent reads first: `topology` (`"mono"` | `"multi"`) and `tracker.provider` (`"github"` | `"azure"`). Created by `/new-project` or `/onboard`.
- **Two topologies.** `multi`: umbrella folder `~/projects/{name}/` with one git repo per service plus `.coordination/`. `mono`: a single repo where agents are scoped to folders (`src/services/*`, `src/frontend/`) and `.coordination/` sits at the repo root (secrets like `dba-access.json` gitignored). Onboarded projects never get their topology migrated unless the user asks.
- **Two trackers.** The PO creates HUs as GitHub Issues/Projects (via `gh`) or Azure DevOps PBIs (via `az boards`); `/sync` translates both directions. `.coordination/backlog.md` is the local mirror.
- **HUs are business-language only** (the PO's golden rule); technical "how" lives in the Lead's task handoffs, never in the HU.
- **QA is a merge gate — and a team.** Devs hand off to QA on completion; `qa` (QA Lead) splits acceptance criteria between `qa-frontend` (UI, Playwright MCP `browser_*` tools) and `qa-backend` (API contract testing), which can run in parallel, then consolidates one APROBADA/RECHAZADA verdict plus the automated Playwright suite (criterion→test traceability). The Lead cannot merge without it. QA **never debugs**: it only reproduces, documents and reports (blockers immediately), always with visual evidence (screenshots/short clips in `.coordination/evidence/`, attached to the tracker item). cybersec is a second gate for auth/sensitive changes.
- **release-manager is the gate for environment releases** (certificación, puente, demo CL/PE/CO, preprod CO/PE, client production): it audits the DBA's pase scripts against the global format rule and can reject them back to the DBA, consolidates `Scripts.zip`, fills the request doc from `templates/pase/` and delivers the pase folder (PDF + Word copy, `Release v{X.Y.Z} {fecha} - {Proyecto}/` naming).
- **DBA pase scripts follow a global format rule** defined in `dba.md`: numbered files grouped by operation type (`1_createTable.sql` … `7_update.sql`), fully idempotent (insert-only data with `WHERE NOT EXISTS` guards, no `ON DUPLICATE KEY UPDATE`), DB-agnostic (no schema-qualified names), external-catalog FKs resolved by natural key, UTF-8 with accents intact. DB comparisons (`dba`) are strictly read-only.
- **The setup agent runs first** in both entry flows — it validates/installs prerequisites (git, Docker, gh/az, DB CLI clients, Playwright) with one user confirmation, and stores state in `.coordination/setup-status.json`.
- **Handoffs are the only inter-agent channel.** Markdown files in `.coordination/handoffs/` (named `{from}-to-{to}-{timestamp}.md`), read via `/inbox`.
- **The project wiki compounds knowledge (Karpathy LLM Wiki pattern).** `.coordination/wiki/` is an Obsidian-compatible vault of `[[wikilink]]`-connected pages (servicios/, hus/, bugs/, decisiones/, pases/, agentes/; schema in `templates/coordination-wiki/CLAUDE.md`). Only tech-writer writes to it (ingest/query/lint via `/wiki`); every other agent reads the wiki FIRST instead of re-reading archived handoffs — that's the token optimization. Raw sources (handoffs, evidence) stay immutable; the wiki cites them.
- **Only the lead delegates to subagents.** All other agents (qa included) carry `disallowedTools: Agent` in frontmatter, and a `PreToolUse` hook (`hooks/block-nested-delegation.py`) denies Agent/Task calls made from inside dev-team subagents — this prevents token waste like backend spawning nested backends. `lead` may spawn any team agent, including multiple parallel instances of the same role on distinct tasks/branches, but never another `lead`. Anyone may spawn `Explore` (cheap read-only search). Main-session delegation is untouched; QA parallelism is orchestrated by the lead from qa's handoff split.
- **Agent activity is logged automatically via plugin hooks.** `hooks/hooks.json` fires `SubagentStart`/`SubagentStop` → `hooks/log-activity.py`, which appends `task_start`/`task_end` JSONL lines to `.coordination/metrics/activity.jsonl` (walks up from the agent's cwd to find `.coordination`; silently no-ops otherwise; never fails outward). Agents manually log only what hooks can't see: `handoff_sent`, `blocked`, `evidence_added`, etc. This feeds `/team-metrics` and `/team-office` (a dependency-free Node SSE server + canvas office in `templates/team-office/`).
- **One agent = one branch = one task.** Branches are `{type}/{ID}-{agent}-{desc}`, cut from `develop`. **Only the Lead merges** (to `develop`, then `main`).
- **cybersec never commits code** — it only audits and reports findings via handoff; the relevant agent implements the fix.
- **dba uses one permanent central repo** (`dba-scripts/`) spanning all projects. Microservice architecture is **database-per-service** (polyglot persistence allowed; single DB acceptable in small mono-repo projects).
- **The architect chooses topology and stack per service** — it does not assume everything is .NET or multi-repo.

Two entry flows: `/new-project` (setup → architect designs from a requirements doc → user approves → repos scaffolded from templates → PO creates the HU backlog in the tracker) and `/onboard` (setup → detect repos/topology/stack → pull tickets from GitHub or Azure DevOps into the backlog). `/start` wraps both for users who don't know the commands.

## Conventions when editing

- After changing any plugin, bump nothing automatically — but the change only reaches users after a push to `main` and a `marketplace update`.
- Keep agent/command `description` fields accurate; they drive Claude Code's routing, not just docs.
- The codebase prose is primarily in **Spanish** (agent identities, command procedures, READMEs). Match the language of the file you're editing.
- When adding a plugin: create `plugins/<name>/.claude-plugin/plugin.json`, add agents/commands, then register it in `.claude-plugin/marketplace.json` with `source: "./plugins/<name>"`.
