import base64
import json
from jsonschema import validate, ValidationError

schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "content": {"type": "string"}
    },
    "required": ["content"]
}

def is_base64(s):
    try:
        decoded_str = base64.b64decode(s)
        encoded_str = base64.b64encode(decoded_str).decode()
        return encoded_str == s
    except BaseException:
        return False

def check_payload(payload):
    try:
        payload = json.loads(payload.decode("utf-8"))
    except Exception as err:
        return False
    try:
        validate(instance=payload, schema=schema)
        # print("Payload is valid")
        return True
    except ValidationError as e:
        # print("Payload is invalid:", e.message)
        return False
