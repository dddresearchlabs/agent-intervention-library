# Intervention format, Milestone 1

An intervention is one YAML document containing declarative guidance for a
specific failure or workflow state that needs interpretation. Guidance may
confirm that an intentional state should be preserved, as with detached HEAD
inspection. A trigger does not imply that an error occurred or a change is needed.
The normative shape is
[`intervention.schema.json`](intervention.schema.json), using
[JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12).
The [reference entry](../interventions/python/module-not-found/intervention.yaml)
describes Python `ModuleNotFoundError`.

This is a language-neutral bootstrap/prototype Intervention Library, not the
Agent Intervention runtime/engine. Python supplied the first reference
implementation to pressure-test the format; it is not a repository-wide language
restriction. Future language-specific libraries may enforce their own language
rule. A canonical `intervention-spec` repository may be split out later. No such
repository split or runtime integration is implemented here.

All top-level fields are required. Every object rejects unknown fields. Strings
intended for people must contain a non-whitespace character. Lists reject exact
duplicates. Slugs contain lowercase ASCII letters or digits, separated by single
hyphens, with at most 64 characters.

## Identity and classification

### `schema_version`

The required quoted string `"1.0"` identifies this declarative format. Other
values, including numeric `1.0`, are rejected. This is independent of both
content versions below. The previous unversioned format is no longer accepted;
there is no compatibility loader or migration machinery.

### `primitive`

The conceptual solved problem, independent of its implementation language or
publisher. This object has exactly four required fields:

- `id`: a stable, dot-separated problem identifier, at most 240 characters, such
  as `dependency.import.missing-module`. It has at least two components. Each
  component starts with a lowercase ASCII letter and contains lowercase letters,
  digits, or single internal hyphens. Do not add a language merely because one
  implementation uses it. Python and JavaScript share this missing-module ID.
- `contract_version`: the revision of the conceptual problem's applicability and
  intended outcome, using the version syntax below. This is a declaration, not
  proof of stability, compatibility, or empirical validation.
- `domain`: an open-vocabulary slug for the conceptual area, such as `dependency`
  or `version-control`, rather than the implementation language.
- `category`: an open-vocabulary slug grouping related concepts, such as
  `import-resolution`, `version-resolution`, or `repository-state`.

Classification is explicit. Validation does not derive domain or category from
ID components, language, or paths, or require equality between them. Reviewers
check conceptual consistency. Shared primitive IDs do not imply shared trigger
syntax or identical implementation guidance. Cross-repository registration and
contract-equivalence checks are outside this milestone.

### `implementation`

The provider's guidance for a primitive in a particular language context. This
object has exactly three required fields:

- `language`: an open-vocabulary slug, such as `python`, `javascript`, or `rust`.
  The value `agnostic` denotes guidance independent of a programming language,
  as in the Git entries. It defines no runtime wildcard or fallback behavior.
- `version`: the revision of this implementation's guidance and applicability,
  using the version syntax below.
- `provider`: a reverse-DNS publisher identifier, at most 240 characters, such
  as `io.github.dddresearchlabs.agent-intervention-library`. It contains at least
  two dot-separated lowercase ASCII alphanumeric components with single internal
  hyphens; the first component starts with a letter. It contains no path or URL.
  Reviewers check ownership. Schema validation cannot verify ownership or trust.

Implementation identity is the tuple `(implementation.provider, primitive.id,
implementation.language)`. The library permits the same primitive ID across
languages and providers. It rejects duplicate implementation identities, even
when contract or implementation versions differ: keep one current file per tuple.
Git history preserves earlier revisions. This is a local uniqueness rule, not a
registry, resolver, or cross-repository collision guarantee.

Filesystem paths are not canonical identity. The reference can remain at
`interventions/python/module-not-found/intervention.yaml`; the `git` directories
can contain `agnostic` implementations. Discovery remains recursive.

### Contract and implementation versions

Both versions are quoted `MAJOR.MINOR.PATCH` strings, at most 32 characters. Each
part is a nonnegative integer without leading zeros. Prerelease and build suffixes
are excluded. `"1.0.0"` is valid; `1.0`, `"01.0.0"`, and `"1.0.0-beta"` are not.

A primitive's contract can remain `"1.0.0"` while its Python implementation advances
to `"1.2.3"`. Wording corrections and implementation-specific fixes change the
implementation version, not automatically the conceptual contract. Change the
contract version when the shared conceptual applicability or intended outcome
changes. A different solved problem needs a different primitive ID. Neither
version changes merely because a file moves; schema changes use `schema_version`.

## Applicability

### `triggers`

A list of 1 to 16 distinct objects describing observed diagnostic or state signals.
Each object has exactly these fields:

- `kind`: `exception` for an exception name, or `message` for a literal message
  fragment. These are the only supported kinds.
- `value`: a nonblank string of at most 256 characters containing that name or
  fragment. Values are data, never regular expressions or expressions to evaluate.

Signals describe evidence for a reviewer. This format does not define automatic
selection, AND or OR composition, case handling, scoring, or precedence. Those
semantics require a later matcher design.

Literal fragments are examples of observable evidence, not an exhaustive catalog
of tool versions, locales, or output formats. A fragment does not establish the
cause or applicability on its own. Similar or overlapping signals do not express
stronger evidence, precedence, or a relationship between entries. Exact object
uniqueness in the schema does not establish semantic independence of signals.

### `preconditions`

A list of 0 to 16 distinct, nonblank strings, each at most 1,000 characters.
Each string states an applicability condition for human review. An empty list
explicitly means no additional conditions. Preconditions are not executable
predicates and are not evaluated by the tests.

Conditions distinguish when diagnosis is useful from when a remedy is justified.
For example, a partial-initialization message can justify investigating an import
cycle; changing dependency structure requires confirming the cycle and loaded
module paths. A dependency resolver warning alone does not establish conflicting
version requirements. Preconditions describe the needed context and evidence;
the payload explains how to verify the cause before changing anything.

## Guidance

### `intervention.type`

The literal string `guidance`. Milestone 1 supports a single text payload type.
New types require a deliberate schema change.

### `intervention.token_budget`

An integer from 1 through 4,096 representing the declared target ceiling for the
payload's token count. It excludes the other fields. The range is a provisional
Milestone 1 authoring constraint. It does not reserve tokens or enforce truncation.

No tokenizer or agent model is selected. Tests validate the value's type and
range only. They do not verify that the payload fits the declared budget.

### `intervention.payload`

A nonblank string of at most 16,000 characters containing plain text or Markdown
guidance. Multiline YAML block scalars are supported. Guidance may describe steps
for a reader, but no payload content is executed, interpolated, imported, or
treated as a template. There are no script paths, callbacks, or execution hooks.

## Outcome description

### `validation.success_criteria`

A list of 1 to 16 distinct, nonblank strings, each at most 1,000 characters,
describing observable outcomes after a person applies the guidance. This is the
only field within `validation`.

These criteria describe intended success. They are not test commands, executable
assertions, or evidence that the entry has been vetted. The pytest suite checks
their structure, not whether a Python environment has been repaired.

When guidance offers different paths, criteria state the observable outcome for
the applicable path in ordinary language. Intentional detached inspection can
succeed without attaching HEAD to a branch. Ruling out a suspected cause or
reporting insufficient evidence does not claim that an unresolved failure has
been repaired. These distinctions add no executable branching or validation.

## Metadata

### `metadata.title`

A required, nonblank display title of at most 120 characters.

### `metadata.summary`

A required, nonblank description of the entry's purpose, at most 1,000 characters.

### `metadata.authors`

A required list of 1 to 16 distinct, nonblank author or organization names, each
at most 120 characters. These provide attribution, not verified identity.

### `metadata.tags`

An optional list of up to 20 distinct slugs for browsing. An omitted or empty list
means no tags. Tags have no matching behavior.

## Validation boundary

Files contain a single UTF-8 YAML document that can be represented as JSON.
The loader extends `yaml.SafeLoader` and rejects duplicate mapping keys,
non-string keys, aliases, merge keys, unsafe tags, multiple documents, YAML-only
values such as timestamps and sets, and non-finite numbers. Quote values that
YAML would otherwise parse as booleans or dates when a string is intended.

The suite discovers every `intervention.yaml` recursively under `interventions/`,
validates the schema itself, validates each entry, and checks library-wide
implementation identity uniqueness. It uses
[`Draft202012Validator`](https://python-jsonschema.readthedocs.io/en/stable/api/jsonschema/validators/)
with local schema references. It does not fetch schemas or entry-supplied URLs.
Negative tests exercise malformed entries and rejected YAML constructs.

## Design limits

Structured executable conditions would require an expression language and a
runtime. Plain text conditions and outcome criteria keep this milestone focused
on authoring and validation. Fixed nested objects catch misspelled fields without
introducing extension mechanisms. Domain, category, and tags remain open so new
problem areas do not need a schema release.

Length and list limits are provisional authoring limits, not a complete resource
sandbox. A schema-valid entry may still contain incorrect or harmful advice.
Human review remains necessary. No runtime, matcher, Jev logic, API, embeddings,
vector search, or agent integration is included.
