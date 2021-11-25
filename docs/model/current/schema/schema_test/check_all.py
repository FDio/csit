
import json
import jsonschema

fmt_checker = jsonschema.FormatChecker()
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
jsonschema.validate({"results": {"baa": {}}}, schema, format_checker=fmt_checker)
jsonschema.validate({"results": {"baz": {}}}, schema, format_checker=fmt_checker)

schema = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "results": {
            "type": "object",
            # For some reason, type can be extracted, but additionalProperties cannot.
            "oneOf": [
                {
                    "additionalProperties": False,
                    "properties": {
                        "foo": {
                            "type": "object"
                        },
                        "typename": {
                            "type": "string",
                            "const": "foo"
                        }
                    }
                },
                {
                    "additionalProperties": False,
                    "properties": {
                        "bar": {
                            "type": "object"
                        },
                        "typename": {
                            "type": "string",
                            "const": "bar"
                        }
                    }
                },
                {
                    "additionalProperties": False,
                    "properties": {}
                }
            ]
        }
    },
    "required": [
        "results"
    ]
}
print(u"foofoo")
jsonschema.validate({"results": {"foo": {}, "typename": "foo"}}, schema, format_checker=fmt_checker)
print(u"barbar")
jsonschema.validate({"results": {"bar": {}, "typename": "bar"}}, schema, format_checker=fmt_checker)
print(u"empty")
jsonschema.validate({"results": {}}, schema, format_checker=fmt_checker)
print(u"foobar")
jsonschema.validate({"results": {"foo": {}, "typename": "bar"}}, schema, format_checker=fmt_checker)

schema = {
    "type": "object",
    "properties": {
        "datetime": {
            "type": "string",
            "format": "date-time"
        }
    }
}
jsonschema.validate({"datetime": "2021-11-03T15:55:28.374645Z"}, schema, format_checker=fmt_checker)
#jsonschema.validate({"datetime": "foobar"}, schema, format_checker=fmt_checker)

schema = {
    "type": "object",
    "properties": {
        "version": {
            "type": "string",
            "const": "0.2.0"
        }
    }
}
jsonschema.validate({"version": "0.2.0"}, schema, format_checker=fmt_checker)
#jsonschema.validate({"version": "0.2.1"}, schema, format_checker=fmt_checker)

# The main purpose is to test CSIT UTI model.

def test(instance_path, schema_path):
    with open(instance_path, u"rt") as fin:
        instance = json.load(fin)
    with open(schema_path, u"rt") as fin:
        schema = json.load(fin)
    jsonschema.validate(instance, schema)

test(u"devicetest.example.json", u"../test_case.info.schema.json")
