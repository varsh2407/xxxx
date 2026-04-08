from typing import Any, Dict
from agents.base_agent import BaseAgent
from architecture import AgentRole, ApplicationSpec


class QAEngineer(BaseAgent):
    """Generates comprehensive test suites for the application."""

    def __init__(self):
        super().__init__(AgentRole.QA_ENGINEER)

    def get_system_prompt(self) -> str:
        return """You are a Senior QA Engineer specializing in automated testing for enterprise Python/React applications.

Return a JSON where each key is a test file path and value is complete, runnable test code.

REQUIRED TEST FILES:
- backend/tests/conftest.py: pytest fixtures (async db, test client, test user, auth headers)
- backend/tests/unit/test_services.py: Unit tests for all service methods (mock repositories)
- backend/tests/unit/test_schemas.py: Pydantic schema validation tests
- backend/tests/integration/test_[entity]_routes.py: Full API integration tests
- backend/tests/integration/test_auth.py: Auth flow tests (login, refresh, logout)
- backend/tests/integration/test_health.py: Health endpoint tests
- frontend/src/__tests__/components/[Component].test.tsx: React Testing Library tests
- frontend/src/__tests__/hooks/useAuth.test.ts: Hook tests
- frontend/src/__tests__/api/client.test.ts: API client tests
- frontend/cypress/e2e/auth.cy.ts: Cypress E2E auth tests
- frontend/cypress/e2e/[feature].cy.ts: Cypress E2E feature tests

TEST STANDARDS:
- pytest-asyncio for async backend tests
- httpx.AsyncClient for API tests (not TestClient)
- Factory pattern for test data creation
- Isolated tests: each test creates and cleans up its own data
- Test all happy paths AND edge cases AND error cases
- Test authentication and authorization on every protected endpoint
- Test input validation (invalid data, boundary values, missing fields)
- Test pagination (empty, single page, multiple pages)
- Test soft delete (deleted items don't appear in lists)
- 80%+ coverage target
- No test interdependencies (order-independent)
- Descriptive test names: test_[action]_[condition]_[expected_result]"""

    def generate_tests(
        self,
        spec: ApplicationSpec,
        backend_code: Dict[str, str],
        db_schema: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate comprehensive test suite."""
        result = self.think(
            "Generate a comprehensive, runnable test suite for this application.",
            context={
                "spec": spec.__dict__,
                "db_schema": db_schema,
                "backend_files": list(backend_code.keys())  # Just file names to save tokens
            }
        )

        if isinstance(result, dict) and "files" in result:
            return result["files"]
        elif isinstance(result, dict) and not any(k in result for k in ["error", "raw_response"]):
            return result
        return result
