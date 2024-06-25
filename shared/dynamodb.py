from boto3.dynamodb.types import TypeDeserializer, TypeSerializer


def dynamo_to_python(dynamodb_object: dict) -> dict:
    deserializer = TypeDeserializer()

    res = dict()
    for k, v in dynamodb_object.items():
        dynamodb_type = list(v.keys())[0]
        if dynamodb_type == 'N':
            res[k] = int(deserializer.deserialize(v))
        else:
            res[k] = deserializer.deserialize(v)

    return res


def python_to_dynamo(python_object: dict) -> dict:
    serializer = TypeSerializer()
    return {
        k: serializer.serialize(v)
        for k, v in python_object.items()
    }
