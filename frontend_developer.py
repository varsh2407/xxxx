from typing import Any, Dict
from agents.base_agent import BaseAgent
from architecture import AgentRole, ApplicationSpec


class FrontendDeveloper(BaseAgent):
    """Generates complete, production-ready React TypeScript frontend code."""

    def __init__(self):
        super().__init__(AgentRole.FRONTEND_DEVELOPER)

    def get_system_prompt(self) -> str:
        return """You are a Senior Frontend Engineer specializing in React, TypeScript, and enterprise UI development.
You write clean, accessible, production-ready code.

Return a JSON where each key is a file path (relative to frontend/src/) and value is the complete file content.

REQUIRED FILES TO GENERATE:
- main.tsx: React entry point with providers
- App.tsx: Root component with routing
- vite.config.ts: Vite config with proxy to backend
- tsconfig.json: Strict TypeScript config
- index.html: HTML template
- types/index.ts: All TypeScript interfaces/types matching backend schemas
- api/client.ts: Axios instance with interceptors (auth, refresh token, error handling)
- api/[entity]Api.ts: API functions for each entity
- store/authStore.ts: Zustand auth store (access/refresh tokens)
- store/[entity]Store.ts: Zustand stores for app state
- hooks/useAuth.ts: Authentication hook
- hooks/use[Entity].ts: Data fetching hooks with React Query
- components/layout/Layout.tsx: Main layout with nav
- components/layout/Navbar.tsx: Navigation bar
- components/ui/Button.tsx: Reusable button with variants
- components/ui/Input.tsx: Reusable form input
- components/ui/Modal.tsx: Reusable modal
- components/ui/Spinner.tsx: Loading spinner
- components/ui/ErrorBoundary.tsx: Error boundary
- components/ui/Toast.tsx: Toast notifications
- pages/LoginPage.tsx: Login with form validation
- pages/RegisterPage.tsx: Registration page
- pages/DashboardPage.tsx: Main dashboard
- pages/[Entity]ListPage.tsx: List view with pagination, search, filter
- pages/[Entity]DetailPage.tsx: Detail/edit view
- pages/NotFoundPage.tsx: 404 page
- utils/formatters.ts: Date, number, currency formatters
- utils/validators.ts: Form validation helpers
- constants/index.ts: App-wide constants (NO hardcoded URLs - use import.meta.env)
- .env.example: Frontend env vars

MANDATORY FRONTEND STANDARDS:
- TypeScript strict mode (no any, no ts-ignore)
- React Query for all server state (no manual fetch in components)
- Zustand for client state (auth, UI state)
- React Hook Form + Zod for all forms
- Axios interceptor for automatic token refresh
- Error boundaries around major sections
- Loading states on every async operation
- Empty states for empty lists
- Proper 404/error pages
- Accessible: ARIA labels, keyboard navigation, focus management
- Responsive: mobile-first with Tailwind CSS
- Environment variables via import.meta.env (VITE_ prefix)
- No hardcoded API URLs - use VITE_API_BASE_URL
- Proper TypeScript types for all API responses
- Optimistic updates where appropriate
- Pagination on list views"""

    def develop(
        self,
        spec: ApplicationSpec,
        architecture: Dict[str, Any],
        backend_code: Dict[str, str]
    ) -> Dict[str, str]:
        """Generate the complete frontend codebase."""
        # Extract API info from backend for frontend alignment
        api_info = {k: v for k, v in backend_code.items() if "router" in k or "schema" in k}

        result = self.think(
            "Generate the complete, production-ready React TypeScript frontend. "
            "Every component must be fully implemented with real functionality. "
            "Match the exact API endpoints and response schemas from the backend.",
            context={
                "spec": spec.__dict__,
                "architecture": architecture,
                "api_schemas_sample": dict(list(api_info.items())[:5])  # Sample to avoid token limit
            }
        )

        if isinstance(result, dict) and "files" in result:
            return result["files"]
        elif isinstance(result, dict) and not any(k in result for k in ["error", "raw_response"]):
            return result
        return result
