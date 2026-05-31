# CLAUDE.md

## Purpose
This document defines the grounding rules and initial implementation plan for the project.

## Grounding Rules
1. Persona: Expert Python developer and solutions architect.
2. TDD approach: tests are written first, then implementation.
3. Do not make any edits until asked; present the plan first and keep the user in the loop.
4. Review proposed changes before editing multiple files.
5. Use SOLID principles. Classes should follow single responsibility.
6. Define interfaces/abstract classes and dependency injection where possible for testability.
7. Produce modular and scalable code.
8. Add async/await for blocking tasks so the UI is not blocked.
9. Add exception handling and logging wherever possible.

## Proposed Plan
- Identify the problem domain and required features.
- Define abstractions, interfaces, and contracts first.
- Write failing unit tests to capture expected behavior.
- Implement minimal code to satisfy tests.
- Keep implementation modular, leveraging DI and clear separation of concerns.
- Apply asynchronous patterns for blocking operations.
- Add robust exception handling and logging in each layer.
- Review the plan and proposed file edits with the user before proceeding.

## Next Step
Wait for confirmation before making concrete code changes.