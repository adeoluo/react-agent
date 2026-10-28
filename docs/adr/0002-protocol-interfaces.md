# ADR-0002: Structural Protocol interfaces for tools and models

- **Status:** Accepted
- **Date:** 2026-01-01

## Context

The agent needs to call tools and a language model. We could require tools and models to
inherit from base classes, or we could type them structurally.

## Decision

Define `Tool` and `LanguageModel` as `typing.Protocol` classes. Any object exposing the
right attributes and methods satisfies the interface, with no inheritance required.

## Alternatives considered

- **Abstract base classes.** Familiar, but force every integration to import and subclass
  our types, which is friction for wrapping an existing SDK object or a one-off function.
- **Duck typing with no annotations.** Flexible but unchecked; mistakes surface at runtime.

## Consequences

- A deterministic scripted model (for tests and the offline demo) and a frontier API
  adapter are interchangeable; the control loop never changes.
- `FunctionTool` adapts a plain `str -> str` function in one line.
- Static type checking still verifies conformance because `Protocol` is checkable.
