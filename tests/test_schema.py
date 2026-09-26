"""Validate contributor data without executing payloads, triggers, or checks."""

import copy
import json
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "spec/intervention.schema.json").read_text(encoding="utf-8"))
VALIDATOR = Draft202012Validator(SCHEMA)
REFERENCE = ROOT / "interventions/python/module-not-found/intervention.yaml"


class InterventionLoader(yaml.SafeLoader):
    """Safe YAML with explicit fields: no aliases, merge keys, or duplicates."""

    def compose_node(self, parent, index):
        if self.check_event(yaml.AliasEvent):
            raise ValueError("YAML aliases are not allowed")
        return super().compose_node(parent, index)

    def construct_mapping(self, node, deep=False):
        keys = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, str):
                raise ValueError("Mapping keys must be strings")
            if key in keys:
                raise ValueError(f"Duplicate YAML key: {key}")
            keys.add(key)
        return super().construct_mapping(node, deep=deep)


def discover_interventions(directory):
    paths = sorted(directory.rglob("intervention.yaml"))
    if not paths:
        raise ValueError(f"No intervention.yaml files found under {directory}")
    return paths


def load_intervention(path):
    try:
        with path.open(encoding="utf-8") as stream:
            document = yaml.load(stream, Loader=InterventionLoader)
        # Reject YAML-only values such as dates, sets, and non-finite numbers.
        json.dumps(document, allow_nan=False)
        return document
    except (yaml.YAMLError, ValueError, TypeError) as error:
        raise ValueError(f"{path}: {error}") from error


def validate_intervention(path):
    document = load_intervention(path)
    errors = list(VALIDATOR.iter_errors(document))
    if errors:
        messages = [f"{error.json_path}: {error.message}" for error in errors]
        raise ValueError(f"{path}:\n" + "\n".join(messages))
    return document


def validate_unique_implementations(entries):
    seen = {}
    for path, document in entries:
        # One current entry per implementation, even across content/contract revisions.
        implementation = document["implementation"]
        identity = (
            implementation["provider"],
            document["primitive"]["id"],
            implementation["language"],
        )
        if identity in seen:
            raise ValueError(f"Duplicate implementation {identity}: {seen[identity]} and {path}")
        seen[identity] = path


def test_schema_is_valid_draft_2020_12():
    assert SCHEMA["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    Draft202012Validator.check_schema(SCHEMA)


@pytest.mark.parametrize(
    "path",
    discover_interventions(ROOT / "interventions"),
    ids=lambda path: str(path.relative_to(ROOT)),
)
def test_intervention_matches_schema(path):
    validate_intervention(path)


def test_library_implementation_identities_are_unique():
    paths = discover_interventions(ROOT / "interventions")
    validate_unique_implementations((path, validate_intervention(path)) for path in paths)


@pytest.fixture
def reference():
    return load_intervention(REFERENCE)


@pytest.mark.parametrize("field", SCHEMA["required"])
def test_missing_required_fields_are_rejected(reference, field):
    del reference[field]
    assert not VALIDATOR.is_valid(reference)


@pytest.mark.parametrize(
    "path,value",
    [
        (("schema_version",), "1.1"),
        (("schema_version",), 1.0),
        (("schema_version",), ""),
        (("primitive", "id"), "module-not-found"),
        (("primitive", "id"), "dependency/import/missing-module"),
        (("primitive", "id"), "Dependency.import.missing-module"),
        (("primitive", "id"), "dependency..missing-module"),
        (("primitive", "id"), "dependency.import.missing_module"),
        (("primitive", "id"), "dependency.import.missing-module."),
        (("primitive", "id"), "dependency.import.missing-module\n"),
        (("primitive", "domain"), "Dependency"),
        (("primitive", "category"), "import resolution"),
        (("implementation", "language"), "Python"),
        (("implementation", "language"), ""),
        (("implementation", "provider"), "publisher"),
        (("implementation", "provider"), "https://example.org"),
        (("implementation", "provider"), "org.example/python"),
        (("implementation", "provider"), "org..example"),
        (("implementation", "provider"), "Org.example"),
        (("implementation", "provider"), "org.example_library"),
        (("implementation", "provider"), "org.example\n"),
        (("triggers",), []),
        (("triggers", 0, "kind"), "regex"),
        (("triggers", 0, "value"), "   "),
        (("preconditions",), "Python is running"),
        (("preconditions",), ["same", "same"]),
        (("intervention", "type"), "script"),
        (("intervention", "token_budget"), 0),
        (("intervention", "token_budget"), 4097),
        (("intervention", "token_budget"), True),
        (("intervention", "token_budget"), 12.5),
        (("intervention", "token_budget"), "256"),
        (("intervention", "payload"), " \n\t"),
        (("intervention", "payload"), {"command": "echo unwanted"}),
        (("validation", "success_criteria"), []),
        (("metadata", "authors"), []),
        (("metadata", "title"), ""),
        (("metadata", "tags"), ["python", "python"]),
    ],
)
def test_malformed_values_are_rejected(reference, path, value):
    target = reference
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    assert not VALIDATOR.is_valid(reference)


@pytest.mark.parametrize(
    "path", [("primitive", "contract_version"), ("implementation", "version")]
)
@pytest.mark.parametrize(
    "value", ["01.0.0", "1.0", 1.0, "1.0.0-beta", "1.0.0+build", "1.0.0\n", "-1.0.0", True]
)
def test_malformed_versions_are_rejected(reference, path, value):
    reference[path[0]][path[1]] = value
    assert not VALIDATOR.is_valid(reference)


@pytest.mark.parametrize("field", ["id", "version", "domain", "category"])
def test_legacy_top_level_identity_fields_are_rejected(reference, field):
    reference[field] = "legacy"
    assert not VALIDATOR.is_valid(reference)


@pytest.mark.parametrize(
    "path",
    [(), ("primitive",), ("implementation",), ("triggers", 0), ("intervention",), ("validation",), ("metadata",)],
)
def test_unknown_fields_are_rejected(reference, path):
    target = reference
    for key in path:
        target = target[key]
    target["execute"] = "untrusted contributor text"
    assert not VALIDATOR.is_valid(reference)


@pytest.mark.parametrize(
    "path,fields",
    [
        (("primitive",), ("id", "contract_version", "domain", "category")),
        (("implementation",), ("language", "version", "provider")),
        (("triggers", 0), ("kind", "value")),
        (("intervention",), ("type", "token_budget", "payload")),
        (("validation",), ("success_criteria",)),
        (("metadata",), ("title", "summary", "authors")),
    ],
)
def test_nested_required_fields_are_rejected(reference, path, fields):
    for field in fields:
        document = copy.deepcopy(reference)
        target = document
        for key in path:
            target = target[key]
        del target[field]
        assert not VALIDATOR.is_valid(document), field


@pytest.mark.parametrize(
    "source",
    [
        "id: first\nid: second\n",
        "intervention:\n  payload: first\n  payload: second\n",
        "value: &value text\ncopy: *value\n",
        "<<: {id: merged}\n",
        "!!python/object/apply:builtins.eval ['1 + 1']",
        "1: non-string key\n",
        "date: 2026-09-24\n",
        "budget: .inf\n",
        "id: first\n---\nid: second\n",
    ],
)
def test_unsafe_or_ambiguous_yaml_is_rejected(tmp_path, source):
    path = tmp_path / "intervention.yaml"
    path.write_text(source, encoding="utf-8")
    with pytest.raises(ValueError, match="intervention.yaml"):
        load_intervention(path)


@pytest.mark.parametrize("revision", [None, "implementation", "primitive"])
def test_duplicate_implementations_are_rejected_even_at_different_versions(reference, revision):
    revised = copy.deepcopy(reference)
    if revision is not None:
        field = "version" if revision == "implementation" else "contract_version"
        revised[revision][field] = "2.0.0"
    with pytest.raises(ValueError, match="Duplicate implementation.*first.yaml and second.yaml"):
        validate_unique_implementations([("first.yaml", reference), ("second.yaml", revised)])


@pytest.mark.parametrize(
    "section,field,value",
    [
        ("implementation", "language", "javascript"),
        ("implementation", "provider", "org.example.library"),
        ("primitive", "id", "dependency.import.circular-import"),
    ],
)
def test_distinct_implementation_identities_can_coexist(tmp_path, reference, section, field, value):
    other = copy.deepcopy(reference)
    other[section][field] = value
    entries = []
    for name, document in [("first.yaml", reference), ("second.yaml", other)]:
        path = tmp_path / name
        path.write_text(yaml.safe_dump(document), encoding="utf-8")
        entries.append((path, validate_intervention(path)))
    validate_unique_implementations(entries)


def test_discovery_includes_arbitrarily_nested_entries(tmp_path):
    paths = [tmp_path / "intervention.yaml", tmp_path / "a/b/c/intervention.yaml"]
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
    (tmp_path / "unrelated.yaml").touch()
    assert discover_interventions(tmp_path) == sorted(paths)


def test_empty_library_is_rejected(tmp_path):
    with pytest.raises(ValueError, match="No intervention.yaml"):
        discover_interventions(tmp_path)


@pytest.mark.parametrize("language", ["python", "javascript", "rust", "agnostic"])
def test_identity_does_not_depend_on_language_classification_or_path(tmp_path, reference, language):
    reference["primitive"]["domain"] = "module-loading"
    reference["implementation"]["language"] = language
    reference["implementation"]["version"] = "1.2.3"
    path = tmp_path / "unrelated-directory" / "intervention.yaml"
    path.parent.mkdir()
    path.write_text(yaml.safe_dump(reference), encoding="utf-8")
    document = validate_intervention(path)
    assert document["primitive"]["id"] == "dependency.import.missing-module"
    assert document["primitive"]["contract_version"] == "1.0.0"
    assert document["implementation"]["version"] == "1.2.3"


def test_minimal_optional_fields_and_inert_payload(tmp_path, reference):
    reference["preconditions"] = []
    reference["metadata"].pop("tags")
    reference["intervention"]["payload"] = "{{expression}} $(command) is inert text."
    path = tmp_path / "intervention.yaml"
    path.write_text(yaml.safe_dump(reference), encoding="utf-8")
    assert validate_intervention(path) == reference


def test_invalid_entry_reports_file_and_field(tmp_path, reference):
    reference["intervention"]["token_budget"] = -1
    path = tmp_path / "intervention.yaml"
    path.write_text(yaml.safe_dump(reference), encoding="utf-8")
    with pytest.raises(ValueError, match=r"intervention.yaml:\n\$\.intervention\.token_budget"):
        validate_intervention(path)
