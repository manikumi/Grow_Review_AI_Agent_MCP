# Problem Statement — Grow Review AI Agent (MCP)

## Overview

Build an AI agent for the **Groww platform** ([Groww on Google Play](https://play.google.com/store/apps/details?id=com.nextbillion.groww&hl=en_IN)) that transforms raw mobile-store feedback into a **weekly pulse** your team can scan in minutes — covering what users care about, what they actually said, and what to do next.

Reviews are already public. The agent's job is to **aggregate → theme → summarize → deliver** that insight through familiar surfaces:
- 📄 **Google Docs** — the written weekly pulse
- 📧 **Gmail** — a draft email linking to or containing the pulse

---

## End-to-End Flow

| Step | Action |
|------|--------|
| 1 | Pull recent App Store / Play Store reviews for Groww (public exports only) |
| 2 | Cluster reviews into a small set of themes and distill a one-page weekly note |
| 3 | Write the note to **Google Docs** where stakeholders can read it |
| 4 | Create a **Gmail draft** to yourself (or an alias) containing or linking to the pulse |

---

## Deliverables

### Weekly One-Page Pulse must include:
- **Top themes** — what people are talking about most
- **Real user quotes** — verbatim snippets from reviews (no invented wording)
- **Three action ideas** — concrete next steps grounded in the themes

### Email Draft:
- A Gmail draft sent to yourself (or an alias) containing the weekly note or a clear pointer to it

---

## Who This Helps

| Audience | Why |
|----------|-----|
| **Product / Growth** | Prioritize fixes and improvements from real signals |
| **Support** | Align messaging with what users are actually saying |
| **Leadership** | One-page health check without drowning in raw reviews |

---

## What to Build

1. **Import reviews** from roughly the **last 8–12 weeks** (fields: rating, title, text, date — whatever the export provides).
2. **Group reviews** into **at most 5 themes** (e.g., onboarding, KYC, payments, statements, withdrawals — pick what fits).
3. **Generate a weekly one-page note** with:
   - Top 3 themes (subset of your themes as appropriate)
   - 3 user quotes
   - 3 action ideas
4. **Draft an email** with the note to yourself or an alias.

---

## Integrations — Google Docs & Gmail via MCP

> **MCP-first** integration is required.

- Use **MCP (Model Context Protocol) servers** for Google Docs and Gmail.
- Tasks such as creating/updating the pulse document and creating the draft message must go through MCP tools — **not** bespoke OAuth + REST client code.
- MCP servers expose tools the agent can call; lean on that pattern so Docs and Gmail stay consistent with course tooling and avoid duplicating auth/HTTP plumbing.

---

## Key Constraints

| Constraint | Detail |
|------------|--------|
| **Reviews** | Public review exports only — no scraping behind store logins or ToS-violating automation |
| **Themes** | Maximum **5 themes** for clustering; the written pulse highlights the **top 3** |
| **Length** | Keep the note scannable and **≤ 250 words** where applicable |
| **Privacy** | No PII — no usernames, emails, device IDs, or other identifiable reviewer data in any artifact; quotes must be anonymous / stripped as needed |
