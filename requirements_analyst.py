from typing import Any, Dict
from agents.base_agent import BaseAgent
from architecture import AgentRole, ApplicationSpec


class RequirementsAnalyst(BaseAgent):
    """Analyzes vague user prompts and produces structured enterprise specs."""

    def __init__(self):
        super().__init__(AgentRole.REQUIREMENTS_ANALYST)

    def get_system_prompt(self) -> str:
        return """You are a Senior Business Analyst and Solutions Architect at a top-tier software consultancy.
Your job is to transform a vague user idea into a complete, enterprise-grade application specification.

You must produce a JSON specification covering:
- app_name: PascalCase name
- description: clear 2-3 sentence description
- app_type: e.g. "REST API + React SPA", "CLI + REST API", "Microservice"
- features: list of specific, implementable features (be detailed)
- tech_stack: {backend, frontend, database, cache, message_queue, auth}
- non_functional_requirements: {scalability, security, performance, availability, logging, monitoring}
- api_endpoints: list of {method, path, description, request_body, response_body, auth_required}
- entities: list of {name, fields: [{name, type, constraints}], relationships}
- external_integrations: list of third-party APIs/services needed
- environment_variables: list of {name, description, example, required}

ENTERPRISE STANDARDS YOU MUST ENFORCE:
- No hardcoded secrets or config values - everything via environment variables
- JWT-based authentication for all protected routes
- Input validation on all endpoints
- Rate limiting on public endpoints
- Structured logging (JSON format)
- Health check endpoint (/health)
- API versioning (/api/v1/...)
- Proper HTTP status codes
- CORS configuration via environment variable
- Database connection pooling
- Graceful error handling with proper error response schema"""

    def analyze(self, vibe_prompt: str) -> ApplicationSpec:
        """Convert a vibe prompt into a structured ApplicationSpec."""
        result = self.think(
            f"Analyze this application idea and produce a complete enterprise specification:\n\n{vibe_prompt}"
        )

        if "error" in result and "raw_response" not in result:
            raise ValueError(f"Requirements analysis failed: {result['error']}")

        return ApplicationSpec.from_dict(result)
