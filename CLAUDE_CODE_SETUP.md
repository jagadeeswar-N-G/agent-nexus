# 🚀 Claude Code Setup + Maximize Your Pro Plan
## Tailored for AgentNexus Development

---

## PART 1: Install Claude Code (5 minutes)

### Requirements
- Node.js 18+ installed
- Active Claude Pro subscription (you have this ✅)
- macOS, Linux, Windows (WSL recommended), or Git Bash

### Installation

```bash
# Install Claude Code
npm install -g @anthropic-ai/claude-code
# ⚠️  Do NOT use sudo — it causes permission issues

# Verify it worked
claude --version

# Log in with your Claude Pro credentials
claude
# On first run it will prompt you to authenticate
# → Log in with your claude.ai account (same email/password as Pro)
```

### Windows Users

```bash
# Option A: WSL2 (strongly recommended — full feature support)
wsl --install
# Then run the npm install above inside WSL

# Option B: Git Bash (native Windows, limited features)
# Install Git for Windows first, then run npm install above
```

### Verify your Pro plan is connected

```bash
# Inside Claude Code session, check auth
/status
# Should show: Subscription: Pro
# If it shows API key instead → run /login and re-authenticate with claude.ai
```

---

## PART 2: Configure Claude Code for AgentNexus

### Step 1: Create your CLAUDE.md (the most important file)

This file tells Claude Code everything about your project. Put it in the root of `agent-nexus/`:

```bash
cd agent-nexus
touch CLAUDE.md
```

Paste this content into CLAUDE.md:

```markdown
# AgentNexus — Claude Code Instructions

## What this project is
Professional agent collaboration SaaS platform.
Backend: FastAPI + Python 3.11 + SQLAlchemy + PostgreSQL + Redis + Qdrant
Frontend: Next.js 14 + TypeScript + Tailwind CSS + shadcn/ui
Auth: Ed25519 cryptographic keypair authentication
Infrastructure: Docker Compose (local), deployable to Railway/Vercel/K8s

## Commands to use
- Install (frontend): `cd frontend && pnpm install`
- Install (backend): `cd backend && pip install -r requirements.txt`
- Dev servers: `pnpm dev` (runs both via concurrently)
- Frontend only: `cd frontend && pnpm dev`
- Backend only: `cd backend && uvicorn app.main:app --reload`
- Tests (frontend): `cd frontend && pnpm test`
- Tests (backend): `cd backend && pytest`
- Lint (frontend): `cd frontend && pnpm lint`
- Lint (backend): `cd backend && ruff check .`
- Typecheck (frontend): `cd frontend && pnpm type-check`
- Docker up: `docker-compose up -d`
- DB migrate: `cd backend && alembic upgrade head`

## Architecture rules
- Frontend pages live in: frontend/src/app/ (App Router)
- React components live in: frontend/src/components/
- API endpoints live in: backend/app/api/v1/endpoints/
- DB models live in: backend/app/models/
- Pydantic schemas live in: backend/app/schemas/
- Business logic lives in: backend/app/services/

## Coding conventions
- Python: type hints always, async/await for all DB/HTTP, docstrings on public functions
- TypeScript: strict mode, no `any`, functional components only, hooks for state
- React: Tailwind for all styling, shadcn/ui components preferred, no inline styles
- Tests: pytest for backend, React Testing Library for frontend
- Commits: Conventional Commits (feat:, fix:, docs:, etc.)
- Imports: absolute imports in both frontend and backend

## Do NOT touch
- backend/venv/ — virtual environment
- frontend/node_modules/ — dependencies
- frontend/.next/ — build cache
- Any .env files — environment config (edit manually)

## When adding new API endpoints
1. Create schema in backend/app/schemas/
2. Add model if needed in backend/app/models/
3. Create endpoint in backend/app/api/v1/endpoints/
4. Register in backend/app/api/v1/__init__.py
5. Add corresponding frontend API client in frontend/src/lib/api/

## Safety rules for this codebase
- Never commit secrets or .env files
- All new DB columns need migrations (alembic revision --autogenerate)
- Rate limiting must be added to all public endpoints
- Agent messages must go through the safety orchestrator
```

### Step 2: Open Claude Code in your project

```bash
cd agent-nexus
claude
```

---

## PART 3: Essential Claude Code Commands

### Navigation
```bash
# Start in your project folder
claude

# Open a specific file for context
# (just reference it in your message)
"Look at backend/app/models/agent.py and..."

# Give Claude a mission
"Here's what I want to build today: [describe feature]"
```

### Power Commands (inside Claude Code session)
```bash
/help          # See all commands
/status        # Check your plan and usage
/clear         # Clear conversation context
/cost          # See token usage for session
/review        # Review changes before applying

# Plan Mode — ALWAYS use for large changes
/plan          # Enter plan mode (Claude thinks, doesn't touch files)
# Review the plan, then say "looks good, proceed"
```

### Best Workflow for AgentNexus Features

```bash
# 1. Start with Plan Mode for any feature > 2 files
"[Plan mode] I want to add the reputation scoring system.
 It should update scores after each collaboration ends,
 decay over time, and be visible on agent profiles."

# 2. Review the plan Claude proposes

# 3. Approve and let it execute
"Plan looks good, go ahead"

# 4. Run tests after
"Now run the backend tests and fix any failures"
```

---

## PART 4: Maximize Your Pro Plan

### Key Facts About Pro + Claude Code

- ✅ **Included in your $20/mo Pro plan** — no extra cost
- ⚡ **Usage is shared** — chat.claude.ai + Claude Code draw from the same pool
- 🔄 **Resets every 5 hours** — you get fresh capacity each window
- 🤖 **Models available**: Sonnet 4.5 (default, fast) and Opus 4 (smarter, uses more)

### Smart Usage Strategy

#### Use Sonnet (default) for:
- Routine coding tasks (add a field, fix a bug)
- Linting / formatting fixes
- Writing boilerplate
- Explaining code
- Small component changes

#### Switch to Opus for:
- Complex architecture decisions
- Designing the matching algorithm
- Debugging tricky async issues
- Writing the safety orchestrator logic
- Anything requiring deep reasoning

```bash
# Switch model inside session
/model claude-opus-4-20250514
# Switch back
/model claude-sonnet-4-5-20250929
```

### The CLAUDE.md Advantage

A well-written CLAUDE.md (already set up above) means:
- Claude never asks "what framework are you using?"
- Claude never uses wrong test commands
- Claude never touches files it shouldn't
- **You save 20-30% tokens per session** — more features per plan window

### Context Management Tips

```bash
# ✅ Start fresh for new features (saves context)
/clear

# ✅ Be specific — vague prompts waste tokens
# Bad:  "fix the matching"
# Good: "The /api/v1/matching/search endpoint returns 500 when
#        required_skills is an empty array. Fix the validation
#        in backend/app/schemas/agent.py and add a test."

# ✅ Batch related tasks
# "Do these 3 things in one go:
#  1. Add the reputation field to AgentResponse schema
#  2. Update the GET /agents/{id} endpoint to include it
#  3. Add a test for the new field"

# ✅ Use Plan Mode for multi-file features — it's more token-efficient
#    than iterating on mistakes
```

### When You Hit Usage Limits

You'll see a warning message. Options:
1. **Wait** — resets every 5 hours (often the best choice)
2. **Enable Extra Usage** — Pro charges standard API rates after limit
3. **Upgrade to Max** — if you consistently hit limits ($100-200/mo)

For AgentNexus development, **Pro is plenty** if you use Plan Mode and focused prompts.

---

## PART 5: Recommended Daily Workflow for AgentNexus

### Morning Session (full fresh context)
Use Opus for architectural and complex work:

```bash
cd agent-nexus
claude
# In session:
"[Plan mode] Today I want to build the matching engine service.
 Review backend/app/services/ and backend/app/schemas/agent.py,
 then plan the full implementation of the vector-based
 compatibility scoring in backend/app/services/matching/"
```

### Afternoon Session (another fresh window)
Use Sonnet for execution tasks:

```bash
claude
"The matching service plan from CLAUDE.md is approved.
 Now implement the speed_collab mode:
 1. New endpoint POST /api/v1/collaborations/speed
 2. 5-minute timer with Celery task
 3. Auto-score on completion
 4. Tests for all three"
```

### Quick Fix Sessions
Tight, specific prompts:

```bash
claude
"backend/app/api/v1/endpoints/agents.py line 87:
 The pagination is returning total_pages as 0 when
 there are results. Fix it and add a unit test."
```

---

## PART 6: AgentNexus-Specific Power Prompts

Copy these into Claude Code to build key features fast:

### Build the Matching Service
```
[Plan mode] Build the vector-based matching service for AgentNexus.
File: backend/app/services/matching/engine.py

Requirements:
- Accept MatchSearchParams (from existing schemas)
- Embed agent bios + skills using sentence-transformers
- Store/query embeddings in Qdrant (QDRANT_URL from config)
- Return top-K candidates with CompatibilityScore breakdown
- Score = weighted: 40% skill match + 30% style match + 30% goal alignment
- Cache results in Redis for 5 minutes
- Async throughout
- Full pytest coverage
```

### Build the Safety Orchestrator
```
[Plan mode] Build the conversation safety orchestrator.
File: backend/app/services/orchestrator/safety.py

Requirements:
- Wrap all collaboration messages before storage
- Check for: prompt injection patterns, secret leakage,
  manipulation attempts, excessive tool requests
- Flag suspicious messages (set is_flagged=True on Message model)
- Rate limit: 30 messages/min per agent per collaboration
- Log all flags with reason to audit table
- Never block messages silently — always return a reason code
- Async, testable, no external AI calls (rule-based + regex)
```

### Build the Frontend Agent Card
```
Build a polished AgentCard component for AgentNexus.
File: frontend/src/components/agent/AgentCard.tsx

Requirements:
- Shows: avatar, name, tagline, top 3 skills, reputation score,
  online indicator, compatibility score (if provided as prop)
- Compatibility breakdown: skill match, style match, goal alignment
  shown as colored progress bars
- "Connect" button with loading state
- "Speed Collab" button (secondary action)
- Dark mode support via Tailwind
- Skeleton loading state
- Use shadcn/ui Card, Badge, Button, Progress components
- Fully typed with TypeScript interfaces
```

### Build the Real-time Collaboration Chat
```
[Plan mode] Build the collaboration chat system.

Backend: backend/app/api/websocket/collaboration.py
Frontend: frontend/src/components/collaboration/ChatRoom.tsx

Requirements:
- WebSocket connection per collaboration session
- Messages go through safety orchestrator before broadcast
- Show typing indicators
- Support message types: text, code (with syntax highlight), proposal
- Proposals have accept/reject buttons
- Rate limit enforcement (30 msg/min)
- Reconnect on disconnect
- Both agents see the same real-time state
```

---

## PART 7: VS Code + Claude Code Integration

```bash
# Install the VS Code extension
# Open VS Code → Extensions → search "Claude Code"
# Install "Claude Code" by Anthropic

# Now you can:
# - Right-click any file → "Ask Claude"
# - Use Cmd+Esc (Mac) or Ctrl+Esc (Windows) to open Claude panel
# - Claude sees your current file automatically
```

### Cursor/Windsurf Users
Claude Code has native extensions for both — install from their extension marketplaces.

---

## PART 8: Quick Reference Card

| Task | Command |
|------|---------|
| Start Claude Code | `cd agent-nexus && claude` |
| Check plan status | `/status` |
| Plan mode (no file changes) | `/plan` |
| Clear context | `/clear` |
| Switch to Opus | `/model claude-opus-4-20250514` |
| Switch to Sonnet | `/model claude-sonnet-4-5-20250929` |
| Review pending changes | `/review` |
| Check token usage | `/cost` |
| Exit | `/exit` or Ctrl+C |

---

## Troubleshooting

**"Authenticating with API key instead of Pro"**
```bash
# Check for conflicting env var
echo $ANTHROPIC_API_KEY
# If it prints a key, remove it from your shell config
unset ANTHROPIC_API_KEY
# Then re-login
claude /logout
claude /login
```

**"Permission denied on npm install"**
```bash
# Fix npm global permissions (don't use sudo)
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
export PATH=~/.npm-global/bin:$PATH
# Add above line to ~/.bashrc or ~/.zshrc
npm install -g @anthropic-ai/claude-code
```

**"Claude Code not finding my project files"**
```bash
# Always start Claude Code from your project root
cd agent-nexus   # ← important!
claude
```

**"Usage limit reached too fast"**
- Switch to Sonnet (faster, uses fewer tokens)
- Use `/clear` between unrelated tasks
- Use Plan Mode — it's more token-efficient than trial-and-error
- Keep prompts specific and focused

---

## You're Ready! 🎉

**Your setup:**
- ✅ Claude Pro (you're subscribed)
- ✅ Claude Code installed (`npm install -g @anthropic-ai/claude-code`)
- ✅ CLAUDE.md configured for AgentNexus
- ✅ Prompts ready for every major feature
- ✅ VS Code integration available

**First thing to build:**
```bash
cd agent-nexus
claude
# Paste this:
"[Plan mode] I want to set up the matching service first.
 Review the existing schemas in backend/app/schemas/agent.py
 and plan the full implementation of the MatchingEngine class
 in backend/app/services/matching/"
```

Go build AgentNexus! 🤖🚀
