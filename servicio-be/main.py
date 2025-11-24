import base64
import functions_framework
import json

from google.cloud import firestore
from cloudevents.http import CloudEvent


db = firestore.Client() # Using '(default)' Cloud Firestore DB

def validate_product(product: dict, schema: dict):
    """
    Validates a single product against the provided schema.
    Raises ValueError if validation fails.
    """
    schema_fields = schema.get("fields", {})

    for field_name, rules in schema_fields.items():
        # Check for required fields
        if rules.get("required") and field_name not in product:
            raise ValueError(f"Missing required field '{field_name}' in product: {product.get('nombre', 'N/A')}")

        # If field is present, validate its type
        if field_name in product:
            product_value = product[field_name]
            expected_type = rules.get("type")

            type_map = {
                "string": str,
                "float": float,
                "boolean": bool,
                "array": list
            }

            if expected_type in type_map and not isinstance(product_value, type_map[expected_type]):
                raise ValueError(f"Invalid type for field '{field_name}'. Expected {expected_type}, got {type(product_value).__name__} in product: {product.get('nombre', 'N/A')}")

            # If field is an array, validate its elements
            if expected_type == "array" and "elements" in rules:
                element_type_str = rules["elements"].get("type")
                if element_type_str:
                    element_type = type_map.get(element_type_str)
                    if not all(isinstance(elem, element_type) for elem in product_value): # type: ignore
                        raise ValueError(f"Invalid element type in array '{field_name}'. All elements should be {element_type_str}.")


@functions_framework.cloud_event
def subscribe(cloud_event: CloudEvent) -> None:
    msg_data = cloud_event.data["message"]["data"]

    data = json.loads(base64.b64decode(msg_data).decode())

    schema = data.get("_schema", {})
    products = data.get("productos", [])

    if not schema or not products:
        raise ValueError("JSON data must contain '_schema' and 'productos' fields.")

    products = data.get("productos", [])

    for product in products:
        validate_product(product, schema)

        # 'nombre' field as document ID
        product_name = product.get("nombre")
        doc_ref = db.collection("productos").document(product_name)
        doc_ref.set(product)
        
        print(f"Document '{product_name}' created in 'productos' collection.")

    print('successful')
