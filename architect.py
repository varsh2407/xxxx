from typing import Any, Dict
from agents.base_agent import BaseAgent
from architecture import AgentRole, ApplicationSpec


class SystemArchitect(BaseAgent):
    """Designs the complete system architecture."""

    def __init__(self):
        super().__init__(AgentRole.ARCHITECT)

    def get_system_prompt(self) -> str:
        return """You are a Principal Software Architect with 20+ years experience designing scalable systems.
You design production-ready architectures following industry best practices.

Your architecture JSON must include:
- pattern: architecture pattern (e.g., "Layered MVC", "Clean Architecture", "Hexagonal")
- layers: list of {name, responsibility, components}
- directory_structure: the complete file/folder tree as a dict
- design_patterns: list of patterns used (Repository, Factory, Strategy, etc.)
- api_design: {versioning, authentication, rate_limiting, caching_strategy, error_handling}
- security_architecture: {auth_flow, token_strategy, data_encryption, input_sanitization}
- scalability: {horizontal_scaling, caching, async_processing, database_strategy}
- observability: {logging_strategy, metrics, health_checks, tracing}
- backend_structure: detailed explanation of backend folder structure
- frontend_structure: detailed explanation of frontend folder structure

ARCHITECTURAL PRINCIPLES:
- Separation of concerns at every layer
- Dependency injection (no tight coupling)
- Repository pattern for all data access
- Service layer for business logic
- Schema validation at API boundaries (Pydantic)
- Environment-based configuration (no hardcoding)
- Structured JSON logging with correlation IDs
- Circuit breaker for external service calls
- Proper exception hierarchy"""

    def design(self, spec: ApplicationSpec) -> Dict[str, Any]:
        """Design the complete system architecture."""
        import json
        result = self.think(
            "Design the complete enterprise architecture for this application specification.",
            context={"spec": spec.__dict__}
        )
        return result
