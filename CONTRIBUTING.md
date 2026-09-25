# Contribute an intervention

Milestone 1 defines the intervention format and validates contributor data.
Read the [field reference](spec/intervention-spec.md) before adding an entry.

## Add an entry

1. Copy `interventions/python/module-not-found/intervention.yaml` into a new
   `interventions/<domain>/<name>/intervention.yaml` directory.
2. Choose a stable, human-readable ID in a namespace you control. Entries owned
   by this repository use `io.github.dddresearchlabs.agent-intervention-library`.
   Follow it with `/<domain>/<name>`. Never reuse another entry's ID.
3. Describe the observed failure in `triggers` and the applicability conditions
   in `preconditions`. Keep both declarative.
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

Keep the ID when revising the same intervention. Increment `version`: use a patch
for wording corrections, a minor version for compatible additions, and a major
version for a changed purpose or applicability contract. For a different failure
or remedy, create a new ID. Keep one current file per ID, even across versions.
Git history preserves earlier revisions.

When changing the format, update the schema, field reference, example, and tests
together. Add a regression case for each new rule. Unknown fields fail validation.

## Review the submission

- Verify namespace ownership and search the library for duplicate IDs.
- Check that the guidance is accurate, scoped to its preconditions, and concise.
- Check that the proposed token budget is realistic. Automated validation checks
  its numeric bounds, not the payload's token count.
- Check that success criteria describe observable results. Passing schema tests
  does not prove that a remedy works or mark it as vetted.
- Run the tests and include their result in the submission.

The validation suite only parses data and checks the schema and library rules.
It does not execute entry content, import contributor modules, install suggested
packages, run payload commands, or evaluate success criteria. It does not provide
a sandbox for changes to Python tests themselves. Review test and dependency
changes as code before running them.

Keep runtime execution, matching, Jev logic, APIs, embeddings, vector search, and
agent integration outside this milestone.
