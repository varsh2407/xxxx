from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


class AgentRole(Enum):
    REQUIREMENTS_ANALYST = "requirements_analyst"
    ARCHITECT = "architect"
    BACKEND_DEVELOPER = "backend_developer"
    FRONTEND_DEVELOPER = "frontend_developer"
    DATABASE_DESIGNER = "database_designer"
    DEVOPS_ENGINEER = "devops_engineer"
    SECURITY_AUDITOR = "security_auditor"
    QA_ENGINEER = "qa_engineer"


@dataclass
class ApplicationSpec:
    app_name: str
    description: str
    app_type: str  # e.g., "REST API + React SPA", "CLI Tool", "Microservice"
    features: List[str] = field(default_factory=list)
    tech_stack: Dict[str, str] = field(default_factory=dict)
    non_functional_requirements: Dict[str, Any] = field(default_factory=dict)
    api_endpoints: List[Dict[str, Any]] = field(default_factory=list)
    entities: List[Dict[str, Any]] = field(default_factory=list)
    external_integrations: List[str] = field(default_factory=list)
    environment_variables: List[Dict[str, str]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "ApplicationSpec":
        return cls(
            app_name=data.get("app_name", "MyApp"),
            description=data.get("description", ""),
            app_type=data.get("app_type", "REST API + React SPA"),
            features=data.get("features", []),
            tech_stack=data.get("tech_stack", {}),
            non_functional_requirements=data.get("non_functional_requirements", {}),
            api_endpoints=data.get("api_endpoints", []),
            entities=data.get("entities", []),
            external_integrations=data.get("external_integrations", []),
            environment_variables=data.get("environment_variables", []),
        )


@dataclass
class BuildState:
    prompt: str
    spec: Optional[ApplicationSpec] = None
    architecture: Optional[Dict[str, Any]] = None
    db_schema: Optional[Dict[str, Any]] = None
    backend_code: Optional[Dict[str, str]] = None
    frontend_code: Optional[Dict[str, str]] = None
    devops_config: Optional[Dict[str, str]] = None
    security_report: Optional[Dict[str, Any]] = None
    test_suite: Optional[Dict[str, str]] = None
    documentation: Optional[Dict[str, str]] = None
    status: str = "started"
    errors: List[str] = field(default_factory=list)
    output_directory: str = ""
    github_repo: Optional[Dict[str, str]] = None
