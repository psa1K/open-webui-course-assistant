# AGENTS.md — Team Collaboration Conventions

This repository is the collaboration repo for the course project *Course-Specific AI Assistant* (assigned by Li Zhengdan & Zhu Jingwen) in the Software Engineering Programming Practicum. The project is built on Open WebUI + Codex.

## Team Members

- **psa1K** (Jialiang Cai)
- **eco-NIN** (Yuzhe Guo)

## Basic Requirements

### 1. Keep Interaction Records with Agents

This project is developed with AI coding tools such as Codex / Claude / opencode. **Each member must keep their own interaction records with their agents**, to be submitted as part of the course deliverables (the assignment requires "interaction records with Codex").

- Location: `interactions/<github-username>/` directory
- Naming: each member keeps **exactly one** Markdown file in their own directory, named `interactions.md`
- Content: **each interaction** includes
  - **Time**: when the interaction happened (e.g. `2026-09-03 17:10`)
  - **Agent/Model**: the agent and model used (e.g. `opencode / DeepSeek-V4-Flash-0731`)
  - Task description and the prompt used
  - Key output from the agent (summarized as needed)
  - Decisions made (adopted/rejected) and the reasoning
  - Issues encountered and how they were resolved
- Append each interaction to `interactions.md` in chronological order; commit along with the code. Each member maintains their own record file and must not overwrite the other's.

### 2. All Commits Go Through PR-Merge Workflow

- Never push directly to `main`
- All changes are developed on feature branches: `feat/<name>` / `fix/<name>` / `docs/<name>`
- Land changes via Pull Request to `main`; confirm the diff is clean and contains no sensitive information before merging
- **PRs must be reviewed and approved by the user before merging**: an agent must not merge a PR on its own; wait for an explicit approval from the user (a member) before running the merge
- **Delete branches after merge**: immediately delete both the local and remote feature branches after a PR is merged, to avoid leftovers
- Follow Conventional Commits for commit messages: `<type>(<scope>): <subject>` (types include `feat` `fix` `docs` `refactor` `test` `chore`, etc.)
- When committing/PRing with an agent identity, sign with the agent used by that member: e.g. psa1K uses opencode, so sign as `opencode[bot]`; the other member signs with their actual agent (e.g. Codex / Claude), so human vs agent commits are distinguishable

### 3. README.md Creation & Maintenance

- Maintain the **root-level** `README.md` as the repository overview (project intro, install & deployment, usage, directory structure, test/optimization records)
- Subdirectories **may** keep their own local README when it adds value (e.g. `knowledge/README.md` as the material index, `interactions/README.md` for the log convention); create one per directory only when useful, not mechanically
- After every feature update, deployment change, or doc adjustment, update the relevant README (root and/or local) so it stays in sync with the actual repo state

### 4. Code & Documentation Conventions

- Do not introduce unused dependencies; do not add redundant comments
- Store course materials (knowledge-base source files) categorized by chapter/module
- Keep key configurations (model config, system prompts, RAG parameters) archived in the repo for testing and optimization comparisons

### 5. Reproducibility Requirements

- Any project edit/change must be reproducible by the **repo owner (other members) following the README** after a fresh clone; it must not depend on private local data (databases, secrets, caches, etc.) to run
- Changes touching dependencies, config, knowledge base, models, or tools must be accompanied by updates to `requirements.lock`, `.env.example`, `scripts/`, and the README, so that "fresh clone → `./scripts/setup.sh` → start" passes in one go
- Real secrets (e.g. API keys) always go into the local `.env` (gitignored); only commit the `.env.example` template
- Regenerate `requirements.lock` after dependency changes to keep environments consistent
