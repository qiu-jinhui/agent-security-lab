class ArgumentValidationError(Exception):
    pass


class ToolArgumentValidator:

    def validate(
        self,
        tool_name: str,
        arguments: dict,
        schemas: dict
    ):

        if not isinstance(arguments, dict):
            raise ArgumentValidationError(
                "Arguments must be a JSON object"
            )

        schema = schemas.get(tool_name)

        if schema is None:
            raise ArgumentValidationError(
                "No argument schema registered for tool"
            )

        properties = schema.get("properties", {})
        required = schema.get("required", [])

        additional_allowed = schema.get(
            "additionalProperties",
            False
        )

        # Required fields
        for field in required:

            if field not in arguments:
                raise ArgumentValidationError(
                    f"Missing required argument: {field}"
                )

        # Unknown fields
        if not additional_allowed:

            unknown = set(arguments) - set(properties)

            if unknown:
                raise ArgumentValidationError(
                    f"Unexpected arguments: {sorted(unknown)}"
                )

        # Type validation
        type_mapping = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "object": dict,
            "array": list
        }

        for field, value in arguments.items():

            if field not in properties:
                continue

            expected_type = properties[field].get("type")

            python_type = type_mapping.get(expected_type)

            if python_type is None:
                raise ArgumentValidationError(
                    f"Unsupported schema type: {expected_type}"
                )

            # bool is a subclass of int in Python.
            if expected_type == "integer":
                valid = type(value) is int
            elif expected_type == "number":
                valid = type(value) in (int, float)
            else:
                valid = isinstance(value, python_type)

            if not valid:
                raise ArgumentValidationError(
                    f"Invalid type for argument: {field}"
                )

            if isinstance(value, str) and not value.strip():
                raise ArgumentValidationError(
                    f"Empty argument: {field}"
                )

        return True
