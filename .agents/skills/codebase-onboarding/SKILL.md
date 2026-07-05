---
name: codebase-onboarding
description: Inspect and orient an unfamiliar codebase before making changes. Use when the user asks to understand a project, add a feature in an unknown repository, refactor unfamiliar code, choose an implementation path, summarize architecture, or produce a project map before editing.
---

# Codebase Onboarding

## Overview

Build a compact mental model of the repository before touching code. Prefer evidence from files, scripts, tests, and local conventions over assumptions.

## Workflow

1. Identify the project shape.
   - List top-level files and folders.
   - Find package manifests, build files, config files, entrypoints, and test directories.
   - Detect the main language, framework, package manager, and runtime commands.

2. Trace the likely execution path.
   - Read README, scripts, router/entry files, and main application modules.
   - Map data flow from user/API/UI entrypoints to business logic and persistence.
   - Note external services, environment variables, generated files, and migrations.

3. Learn local conventions.
   - Inspect naming, folder boundaries, state management, dependency injection, error handling, logging, and test style.
   - Prefer existing helpers and patterns over new abstractions.
   - Mark any uncertain areas for targeted follow-up reads.

4. Produce an orientation brief.
   - State what the app does, how it is organized, and where the requested change likely belongs.
   - Include relevant commands for install, dev server, tests, lint, and build when discoverable.
   - Name the risk areas and files that should be read before editing.

## Output

When onboarding is the main request, return:

- Architecture summary
- Key files and responsibilities
- Relevant commands
- Change recommendation
- Risks or unknowns

When onboarding precedes implementation, keep the brief short and continue into the requested work after the relevant files are understood.
