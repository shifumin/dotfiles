# Code Quality

## Test Rules

Tests cover public interfaces only (not private methods). Each test covers normal cases, error cases, and edge cases.

Reason: Avoid coupling to internal implementation, improve refactoring resilience.

## YARD Comments (Ruby only)

Public methods in Ruby code have YARD comments: `@param`, `@return`, `@raise`.

Reason: Enables accurate code understanding by AI and IDEs.
