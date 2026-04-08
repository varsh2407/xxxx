from typing import Any, Dict
from agents.base_agent import BaseAgent
from architecture import AgentRole, ApplicationSpec


class BackendDeveloper(BaseAgent):
    """Generates complete, production-ready FastAPI backend code."""

    def __init__(self):
        super().__init__(AgentRole.BACKEND_DEVELOPER)

    def get_system_prompt(self) -> str:
        return """You are a Senior Python Backend Engineer specializing in FastAPI enterprise applications.
You write clean, production-ready, fully functional Python code.

Return a JSON where each key is a file path (relative to backend/) and value is the complete file content as a string.

REQUIRED FILES TO GENERATE:
- main.py: FastAPI app with lifespan, CORS, middleware, error handlers
- config.py: Pydantic BaseSettings with all env vars (NO hardcoding)
- database.py: SQLAlchemy async engine, session factory, Base
- models/__init__.py and models/[entity].py: SQLAlchemy ORM models
- schemas/__init__.py and schemas/[entity].py: Pydantic v2 request/response schemas
- repositories/__init__.py and repositories/[entity]_repository.py: DB operations
- services/__init__.py and services/[entity]_service.py: Business logic
- routers/__init__.py and routers/[entity]_router.py: FastAPI routers
- middleware/logging_middleware.py: Request/response structured JSON logging
- middleware/rate_limit_middleware.py: Rate limiting
- core/security.py: JWT creation/verification, password hashing
- core/exceptions.py: Custom exception hierarchy
- core/dependencies.py: FastAPI dependency injection (get_db, get_current_user, etc.)
- core/logging.py: Structured JSON logger setup
- utils/pagination.py: Cursor/offset pagination helpers
- tests/conftest.py: pytest fixtures
- tests/test_[entity].py: unit + integration tests
- alembic.ini: Alembic config
- alembic/env.py: Alembic environment
- alembic/versions/001_initial.py: First migration
- requirements.txt: All pinned dependencies
- .env.example: All required env vars with example values

MANDATORY CODE STANDARDS:
- Async/await throughout (asyncpg, async SQLAlchemy)
- Pydantic v2 for all schemas (model_config = ConfigDict(...))
- Dependency injection for all shared resources
- Repository pattern: NO SQL in routers or services
- Service layer: NO database access directly
- JWT auth: access token (15min) + refresh token (7 days)
- Password hashing with bcrypt
- Structured logging: every request gets a correlation_id
- Proper HTTP status codes (201 for create, 204 for delete, etc.)
- Consistent error response: {"error": {"code": "...", "message": "...", "details": {}}}
- Input validation with Pydantic (no manual validation)
- Pagination on all list endpoints
- Soft deletes (set deleted_at, don't DELETE rows)
- Health endpoint: GET /health returning {status, version, timestamp, db_status}
- API versioning: all routes under /api/v1/
- No print() statements - use structured logger
- Type hints on every function
- Docstrings on all public methods
- NEVER hardcode any URL, password, secret, or config value"""

    def develop(
        self,
        spec: ApplicationSpec,
        architecture: Dict[str, Any],
        db_schema: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate the complete backend codebase."""
        result = self.think(
            "Generate the complete, production-ready FastAPI backend codebase. "
            "Every file must be fully implemented - no placeholder code, no TODO comments, no stub functions. "
            "The code must run without modification.",
            context={
                "spec": spec.__dict__,
                "architecture": architecture,
                "db_schema": db_schema
            }
        )

        # Result should be {filepath: content} dict
        if isinstance(result, dict) and "files" in result:
            return result["files"]
        elif isinstance(result, dict) and not any(k in result for k in ["error", "raw_response"]):
            return result
        return result
