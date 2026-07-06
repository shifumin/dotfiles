# Code Quality

## Test Rules

Tests cover public interfaces only (not private methods). Each public interface's test suite covers normal cases, error cases, and edge cases.

Reason: Avoid coupling to internal implementation, improve refactoring resilience.

## YARD Comments (Ruby only)

Public methods you add or modify have YARD comments: `@param`, `@return`, `@raise`. Do not retrofit YARD onto untouched methods.

Reason: Enables accurate code understanding by AI and IDEs.
