---
name: Orval codegen naming collisions
description: How orval derives type names and why schema names must not collide with operationId-derived names
---

# Orval codegen naming collisions

Orval generates `<OperationId>Params` / `<OperationId>Response` type aliases
from each route's `operationId`, alongside one type per named schema. A schema
whose name matches an operation-derived name (e.g. schema `ExperimentReplay…`
vs operation `replayExperiment`) produces duplicate/ambiguous exports that
break the generated module.

**Why:** adding a replay endpoint with a similarly named report schema made the
generated client fail until the schema was renamed; nothing in the OpenAPI
spec itself was invalid.

**How to apply:** when adding a route + response schema pair, pick a schema
name that cannot collide with any `operationId` inflection (prefix domain
nouns, e.g. `Phase3ReplayReport`), then re-run codegen and typecheck before
touching handlers.
