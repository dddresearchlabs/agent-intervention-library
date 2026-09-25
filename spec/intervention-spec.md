# Intervention format, Milestone 1

An intervention is one YAML document containing declarative guidance for a
specific failure. The normative shape is
[`intervention.schema.json`](intervention.schema.json), using
[JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12).
The [reference entry](../interventions/python/module-not-found/intervention.yaml)
describes Python `ModuleNotFoundError`.

All top-level fields are required. Every object rejects unknown fields. Strings
intended for people must contain a non-whitespace character. Lists reject exact
duplicates. Slugs contain lowercase ASCII letters or digits, separated by single
hyphens, with at most 64 characters.

## Identity and classification

### `id`

A stable, globally namespaced identifier, at most 240 characters, with the shape
`<reverse-dns-namespace>/<domain>/<name>`. The namespace has at least two dot-separated
components, starts with a letter, and uses lowercase ASCII letters, digits,
dots, and hyphens. Domain and name use the slug syntax.

Repository-owned entries use this namespace:

```text
io.github.dddresearchlabs.agent-intervention-library/python/module-not-found
```

The namespace derives from the repository owner's GitHub identity and repository
name. Other publishers use a reverse-DNS namespace they control, such as
`org.example.library/python/module-not-found`. Namespace ownership provides the
cross-publisher uniqueness convention. Schema validation cannot prove ownership
or discover collisions in external libraries. Reviewers check ownership.

The test suite rejects duplicate IDs throughout this library, even if their
versions differ. It also checks that the ID's domain equals the `domain` field.
IDs remain stable across entry revisions and directory moves. Paths are an
organizational convention, not an identity source.

### `version`

The entry revision as a quoted string `MAJOR.MINOR.PATCH`, at most 32 characters.
Each part is a nonnegative integer without leading zeros. Prerelease and build
suffixes are excluded in Milestone 1. `"1.0.0"` is valid. `1.0`, `"01.0.0"`, and
`"1.0.0-beta"` are invalid.

This is the content version, not the schema version. Git history records format
changes during Milestone 1. A separate format version is deferred until multiple
formats must coexist.

### `domain`

A slug naming the technology or problem area, such as `python`. Its value equals
the middle segment of `id`. Domains are open vocabulary.

### `category`

A slug grouping related failure types within a domain, such as
`dependency-resolution`. Categories are open vocabulary.

## Applicability

### `triggers`

A list of 1 to 16 distinct objects describing observed failure signals. Each
object has exactly these fields:

- `kind`: `exception` for an exception name, or `message` for a literal message
  fragment. These are the only supported kinds.
- `value`: a nonblank string of at most 256 characters containing that name or
  fragment. Values are data, never regular expressions or expressions to evaluate.

Signals describe evidence for a reviewer. This format does not define automatic
selection, AND or OR composition, case handling, scoring, or precedence. Those
semantics require a later matcher design.

### `preconditions`

A list of 0 to 16 distinct, nonblank strings, each at most 1,000 characters.
Each string states an applicability condition for human review. An empty list
explicitly means no additional conditions. Preconditions are not executable
predicates and are not evaluated by the tests.

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
validates the schema itself, validates each entry, and checks domain consistency
and library-wide ID uniqueness. It uses
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
