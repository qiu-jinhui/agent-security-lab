from app.security.context import ExecutionContext

class ResourceAuthorizationEngine:

    def __init__(self, access_control: dict):

        self.access_control = access_control

    def authorize(
        self,
        context: ExecutionContext | None,
        resource_id: str
    ) -> bool: 

        if context is None:
            return False

        key = (
            context.tenant_id,
            context.user_id
        )

        allowd_resources = self.access_control.get(key)

        if allowd_resources is None:
            return False

        return resource_id in allowd_resources