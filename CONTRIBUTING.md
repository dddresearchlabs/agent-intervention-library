# Contribute an intervention

Milestone 1 defines the intervention format and validates contributor data.
Read the [field reference](spec/intervention-spec.md) before adding an entry.

## Add an entry

1. Copy `interventions/python/module-not-found/intervention.yaml` into a new
   `interventions/<context>/<name>/intervention.yaml` directory. Paths organize
   entries; they do not define identity or constrain implementation language.
2. Set `schema_version: "1.0"`. Choose a conceptual `primitive.id`, such as
   `dependency.import.missing-module`, with its contract version, domain, and
   category. Reuse the primitive ID for another language's implementation of
   the same problem. Set `implementation.language`, `implementation.version`,
   and a provider identifier you control. This repository's provider is
   `io.github.dddresearchlabs.agent-intervention-library`. Start new contracts and
   implementations at `"1.0.0"`. Use `agnostic` for language-independent guidance.
3. Describe the observed diagnostic or state signals in `triggers` and the
   applicability conditions in `preconditions`. Keep both declarative.
4. Write focused text in `intervention.payload`. Describe actions for a reader.
   Do not add scripts, executable hooks, template logic, or contributor plugins.
5. Describe observable outcomes in `validation.success_criteria`. These are
   human review criteria, not code that the test suite runs.
6. Fill in the title, summary, and author attribution. Add tags if useful.
7. Run the validation suite from the repository root.

Use Python 3.9 or newer and a virtual environment:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
```

Do not commit the virtual environment, pytest cache, or Python bytecode.
Use `.venv\Scripts\python.exe` instead of `.venv/bin/python` on Windows.

Every file named exactly `intervention.yaml` under `interventions/` is discovered
recursively. You do not need to register new paths. A missing or empty library
fails validation. Failures identify the file and, for schema errors, the field.

## Revise an entry

Keep `primitive.id` when revising an implementation of the same conceptual
problem. Increment `implementation.version`: use a patch for wording corrections
or compatible fixes, a minor version for compatible additions, and a major version
for incompatible implementation changes. Change `primitive.contract_version` only
when the shared conceptual contract changes, using the same version conventions.
A Python wording fix need not change the contract or JavaScript implementation.
For a different solved problem, create a new primitive ID.

Keep one current file per `(implementation.provider, primitive.id,
implementation.language)`, regardless of either version. Different languages or
providers may implement the same primitive. Git history preserves revisions.

When changing the format, update the schema, field reference, example, and tests
together. Add a regression case for each new rule. Unknown fields fail validation.

## Review the submission

- Verify provider ownership and search for duplicate implementation identities.
  Review reused primitive IDs for the same conceptual problem and contract;
  schema validation does not prove equivalence. Do not classify a primitive as
  Python merely because its current implementation uses Python.
- Review trigger fragments in their original tool output and language. Prefer
  characteristic fragments over broad words or redundant overlapping fragments.
  State the tool context in preconditions; do not imply coverage of all versions
  or locales, or infer matching rules from the list of signals.
- Check a plausible lookalike that needs different guidance. Preconditions must
  identify the evidence needed to distinguish it. For a diagnostic entry, the
  payload must establish the cause before recommending a change. A generic
  import failure or resolver warning is insufficient evidence of a specific cause.
- Check that the guidance is accurate, scoped to its preconditions, and concise.
- Review the advice itself for unsafe actions, speculative package names,
  unverified code, and loss of local work. Inert text can still contain harmful
  instructions for a reader. Passing schema validation is not a safety review.
- Check that the proposed token budget is realistic. Automated validation checks
  its numeric bounds, not the payload's token count.
- Check that success criteria describe observable results. Passing schema tests
  does not prove that a remedy works or mark it as vetted. For conditional paths,
  state which outcome applies; intentional states need not be changed. Reporting
  a blocked diagnosis is not evidence that the original failure was resolved.
- Distinguish structural test results, source checks, and actual reproduction of
  the remedy in the submission. Describe only verification that was performed,
  with its environment and limits; do not label untested guidance as vetted.
- Run the tests and include their result in the submission.

The validation suite only parses data and checks the schema and library rules.
It does not execute entry content, import contributor modules, install suggested
packages, run payload commands, or evaluate success criteria. It does not provide
a sandbox for changes to Python tests themselves. Review test and dependency
changes as code before running them.

Keep runtime execution, matching, Jev logic, APIs, embeddings, vector search, and
agent integration outside this milestone.
