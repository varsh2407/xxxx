from typing import Any, Dict
from agents.base_agent import BaseAgent
from architecture import AgentRole, ApplicationSpec


class SecurityAuditor(BaseAgent):
    """Audits generated code for security vulnerabilities and generates fixes."""

    def __init__(self):
        super().__init__(AgentRole.SECURITY_AUDITOR)

    def get_system_prompt(self) -> str:
        return """You are a Senior Application Security Engineer (AppSec) specializing in OWASP Top 10.
You review code for security vulnerabilities and provide actionable fixes.

Your audit JSON must include:
- owasp_checklist: {category: {status, findings, recommendations}} for all OWASP Top 10
- critical_issues: list of {file, issue, severity, cwe_id, fix}
- high_issues: list of {file, issue, severity, cwe_id, fix}
- medium_issues: list of {file, issue, severity, cwe_id, fix}
- security_score: 0-100 score with justification
- code_fixes: {filepath: fixed_code_snippet} for critical issues
- security_headers: complete list of required HTTP security headers
- recommendations: prioritized list of security improvements
- compliance_notes: GDPR, SOC2, PCI-DSS considerations if applicable

CHECK FOR:
- SQL injection (use parameterized queries/ORM only)
- XSS (output encoding, CSP headers)
- CSRF (token validation)
- Authentication flaws (JWT validation, token expiry)
- Authorization flaws (check every endpoint)
- Sensitive data exposure (no secrets in logs/responses)
- Security misconfiguration (CORS, debug mode, error messages)
- Insecure dependencies (flag known vulnerable versions)
- Broken access control
- Cryptographic failures (weak algorithms, improper key storage)"""

    def audit(
        self,
        spec: ApplicationSpec,
        backend_code: Dict[str, str],
        architecture: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform security audit on the generated code."""
        # Sample the most security-sensitive files
        sensitive_files = {
            k: v for k, v in backend_code.items()
            if any(keyword in k for keyword in ["security", "auth", "router", "main", "config", "middleware"])
        }

        result = self.think(
            "Perform a comprehensive security audit on this enterprise application.",
            context={
                "spec": spec.__dict__,
                "architecture": architecture,
                "sensitive_code_files": dict(list(sensitive_files.items())[:8])
            }
        )
        return result
