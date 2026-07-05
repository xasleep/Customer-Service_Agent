---
name: feature-builder
description: Implement a user-requested feature end to end in an existing codebase. Use when the user asks to add, change, or complete functionality, build a UI/workflow, wire backend behavior, update tests, or turn a vague product request into working code.
---

# Feature Builder

## Overview

Turn a feature request into a small, verified implementation. Keep changes scoped to the existing architecture and make the result easy to review.

## Workflow

1. Clarify through code first.
   - Read the existing entrypoints, related components, state, routes, APIs, schemas, and tests.
   - Infer reasonable defaults when the user has not specified implementation details.
   - Ask a question only when multiple choices would create materially different products or risky behavior.

2. Plan the smallest coherent slice.
   - Identify files to change and tests to add or update.
   - Prefer local patterns, existing helpers, and current design language.
   - Avoid unrelated refactors and dependency additions unless clearly needed.

3. Implement the feature.
   - Update data models, APIs, UI, state, and copy as required by the feature.
   - Handle loading, empty, error, disabled, and success states where user-facing.
   - Keep text concise and avoid explanatory in-app tutorial copy unless the product already uses it.

4. Verify.
   - Run the most focused relevant tests or checks first.
   - For frontend work, run or inspect the app when feasible and check responsive states.
   - If verification cannot run, state the blocker and the exact command attempted.

## Done Criteria

- The requested behavior works through the intended user or API path.
- Edge states are handled at the same quality level as nearby code.
- Tests or checks cover the highest-risk path.
- The final response names changed files, verification, and any residual risk.
