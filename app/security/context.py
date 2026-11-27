from dataclasses import dataclass

@dataclass(frozen=True)
class ExecutionContext:
    user_id: str
    tenant_id: str
    role: str

    def __post_init__(self):
        if not self.user_id:
            raise ValueError("user_id is required")

        if not self.tenant_id:
            raise ValueError("tenant_id is required")

        if not self.role:
            raise ValueError("role is required")
