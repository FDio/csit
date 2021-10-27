
import json
import jsonschema

def test(instance_path, schema_path):
    with open(instance_path, u"rt") as fin:
        instance = json.load(fin)
    with open(schema_path, u"rt") as fin:
        schema = json.load(fin)
    resolver = jsonschema.RefResolver.from_schema(schema)
    jsonschema.validate(instance, schema, resolver=resolver)

test(u"devicetest.example.json", u"../test_case_info.schema.json")
