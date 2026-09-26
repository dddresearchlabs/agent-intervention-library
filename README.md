# agent-intervention-library

A library of structured, token-efficient guidance for recurring failures and
workflow states encountered by AI agents and developers. Interventions are
declarative data with inert text payloads, not executable plugins. Guidance can
confirm that an intentional state needs no change.

This is the language-neutral bootstrap/prototype Intervention Library, not the
Agent Intervention runtime/engine. The format separates conceptual primitive IDs
and contract versions from provider, implementation language, and implementation
version. Python is the first reference implementation, not a repository restriction.

Milestone 1A established the [intervention format](spec/intervention-spec.md),
[JSON Schema](spec/intervention.schema.json), and validation suite. Milestone 1B
Part 1 adds an initial seed collection:

- **Python:** module not found (the reference guidance), circular import,
  and dependency version conflict.
- **JavaScript/Node:** module or package not found, and package export not defined.
- **Git:** merge conflict and detached HEAD, including intentional inspection.

Browse [the entries](interventions/) or read [the contributor guide](CONTRIBUTING.md)
for authoring and test setup. With development requirements installed, validate
the library with `python -m pytest -q`.

Schema validation checks structure and library invariants. It does not establish
that guidance is correct or empirically vetted. Success criteria describe intended
observable outcomes; token budgets are authoring targets, not runtime enforcement.
Inert guidance still needs review for accuracy and safety before someone follows it.
This milestone defines no runtime execution, automatic matching, or scoring.
Further library expansion is paused pending work on the separate Agent Intervention
runtime repository. Future language-specific libraries and a canonical specification
repository may be split out later.
