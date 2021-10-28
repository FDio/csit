
import json
import jsonschema

# Manual test to explore which schemas are accepted.
schema = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "results": {
            "type": "object",
            # For some reason, type can be extracted, but additionalProperties cannot.
            "oneOf": [
                {
                    "$ref": "#/$defs/foo"
                },
                {
                    "$ref": "#/$defs/bar"
                }
            ]
        }
    },
    "required": [
        "results"
    ],
    "$defs": {
        "foo": {
            "additionalProperties": False,
            "properties": {
                "baz": {
                    "type": "object"
                }
            },
            "required": [ "baz" ]
        },
        "bar": {
            "additionalProperties": False,
            "properties": {
                "baa": {
                    "type": "object"
                }
            },
            "required": [ "baa" ]
        }
    }
}
jsonschema.validate({"results": {"baa": {}}}, schema)
jsonschema.validate({"results": {"baz": {}}}, schema)

# The main purpose is to test CSIT UTI model.

def test(instance_path, schema_path):
    with open(instance_path, u"rt") as fin:
        instance = json.load(fin)
    with open(schema_path, u"rt") as fin:
        schema = json.load(fin)
    jsonschema.validate(instance, schema)

test(u"devicetest.example.json", u"../test_case_info.schema.json")
