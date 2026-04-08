import os
import json
import logging
import traceback
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import asdict

from architecture import ApplicationSpec, BuildState
from github_publisher import GitHubPublisher
from agents.requirements_analyst import RequirementsAnalyst
from agents.architect import SystemArchitect
from agents.database_designer import DatabaseDesigner
from agents.backend_developer import BackendDeveloper
from agents.frontend_developer import FrontendDeveloper
from agents.devops_engineer import DevOpsEngineer
from agents.security_auditor import SecurityAuditor
from agents.qa_engineer import QAEngineer

logger = logging.getLogger(__name__)


class VibeCodingOrchestrator:
    """
    Master orchestrator that coordinates all AI agents to build
    a complete enterprise application from a single vibe prompt.
    """

    def __init__(self):
        self.agents = {
            "requirements": RequirementsAnalyst(),
            "architect": SystemArchitect(),
            "database": DatabaseDesigner(),
            "backend": BackendDeveloper(),
            "frontend": FrontendDeveloper(),
            "devops": DevOpsEngineer(),
            "security": SecurityAuditor(),
            "qa": QAEngineer(),
        }

    def build_from_vibe(
        self,
        vibe_prompt: str,
        output_dir: str = "./generated_app",
        skip_phases: list = None,
        publish_to_github: bool = False,
        github_private: bool = False,
    ) -> BuildState:
        """
        Main entry point: transform a vibe prompt into a complete enterprise application.

        Args:
            vibe_prompt: Natural language description of the desired application
            output_dir: Directory to write generated files
            skip_phases: List of phases to skip (e.g., ["security", "qa"] for faster builds)
            publish_to_github: If True, push generated code to a new GitHub repo
            github_private: If True, create the GitHub repo as private

        Returns:
            BuildState with all generated artifacts and metadata
        """
        skip_phases = skip_phases or []
        state = BuildState(prompt=vibe_prompt, output_directory=output_dir)
        state.github_repo = None

        self._print_banner(vibe_prompt)

        # ── Phase 1: Requirements Analysis ──────────────────────────────────
        state = self._run_phase(
            phase_name="Requirements Analysis",
            phase_num=1,
            total=7,
            state=state,
            runner=lambda: self._phase_requirements(state, vibe_prompt),
            skip=False
        )
        if state.status == "failed": return state

        # ── Phase 2: Architecture Design ─────────────────────────────────────
        state = self._run_phase(
            phase_name="Architecture Design",
            phase_num=2,
            total=7,
            state=state,
            runner=lambda: self._phase_architecture(state),
            skip=False
        )
        if state.status == "failed": return state

        # ── Phase 3: Database Design ──────────────────────────────────────────
        state = self._run_phase(
            phase_name="Database Design",
            phase_num=3,
            total=7,
            state=state,
            runner=lambda: self._phase_database(state),
            skip=False
        )
        if state.status == "failed": return state

        # ── Phase 4: Backend Development ─────────────────────────────────────
        state = self._run_phase(
            phase_name="Backend Development",
            phase_num=4,
            total=7,
            state=state,
            runner=lambda: self._phase_backend(state),
            skip=False
        )
        if state.status == "failed": return state

        # ── Phase 5: Frontend Development ────────────────────────────────────
        state = self._run_phase(
            phase_name="Frontend Development",
            phase_num=5,
            total=7,
            state=state,
            runner=lambda: self._phase_frontend(state),
            skip="frontend" in skip_phases
        )

        # ── Phase 6: DevOps Configuration ────────────────────────────────────
        state = self._run_phase(
            phase_name="DevOps Configuration",
            phase_num=6,
            total=7,
            state=state,
            runner=lambda: self._phase_devops(state),
            skip="devops" in skip_phases
        )

        # ── Phase 7: Security Audit + QA ─────────────────────────────────────
        state = self._run_phase(
            phase_name="Security Audit & QA",
            phase_num=7,
            total=7,
            state=state,
            runner=lambda: self._phase_security_and_qa(state),
            skip="security" in skip_phases and "qa" in skip_phases
        )

        # ── Write all files to disk ───────────────────────────────────────────
        self._write_all_files(state)

        # ── Generate README ───────────────────────────────────────────────────
        self._write_readme(state)

        # ── Save build manifest ───────────────────────────────────────────────
        self._write_manifest(state)

        # ── Publish to GitHub ─────────────────────────────────────────────────
        if publish_to_github:
            state = self._run_phase(
                phase_name="Publishing to GitHub",
                phase_num=8,
                total=8,
                state=state,
                runner=lambda: self._phase_github(state, github_private),
                skip=False
            )

        state.status = "complete"
        self._print_completion(state)
        return state

    # ─────────────────────────────────────────────────────────────────────────
    # Phase Runners
    # ─────────────────────────────────────────────────────────────────────────

    def _phase_requirements(self, state: BuildState, vibe_prompt: str) -> None:
        spec = self.agents["requirements"].analyze(vibe_prompt)
        state.spec = spec
        print(f"   ✓ App: {spec.app_name}")
        print(f"   ✓ Type: {spec.app_type}")
        print(f"   ✓ Features: {len(spec.features)} features identified")
        print(f"   ✓ Entities: {len(spec.entities)} data entities")
        print(f"   ✓ Endpoints: {len(spec.api_endpoints)} API endpoints")

    def _phase_architecture(self, state: BuildState) -> None:
        arch = self.agents["architect"].design(state.spec)
        state.architecture = arch
        pattern = arch.get("pattern", "N/A")
        layers = len(arch.get("layers", []))
        print(f"   ✓ Pattern: {pattern}")
        print(f"   ✓ Layers: {layers} architectural layers")

    def _phase_database(self, state: BuildState) -> None:
        db = self.agents["database"].design(state.spec, state.architecture)
        state.db_schema = db
        tables = len(db.get("tables", []))
        print(f"   ✓ Tables: {tables} database tables")

    def _phase_backend(self, state: BuildState) -> None:
        backend = self.agents["backend"].develop(
            state.spec, state.architecture, state.db_schema
        )
        state.backend_code = backend if isinstance(backend, dict) else {}
        files = len(state.backend_code)
        print(f"   ✓ Generated: {files} backend files")

    def _phase_frontend(self, state: BuildState) -> None:
        frontend = self.agents["frontend"].develop(
            state.spec, state.architecture, state.backend_code or {}
        )
        state.frontend_code = frontend if isinstance(frontend, dict) else {}
        files = len(state.frontend_code)
        print(f"   ✓ Generated: {files} frontend files")

    def _phase_devops(self, state: BuildState) -> None:
        devops = self.agents["devops"].configure(state.spec, state.architecture)
        state.devops_config = devops if isinstance(devops, dict) else {}
        files = len(state.devops_config)
        print(f"   ✓ Generated: {files} DevOps config files")

    def _phase_github(self, state: BuildState, private: bool) -> None:
        publisher = GitHubPublisher()
        result = publisher.publish(
            app_name=state.spec.app_name,
            output_dir=state.output_directory,
            description=state.spec.description,
            private=private,
        )
        state.github_repo = result
        # Append GitHub URL to build manifest
        manifest_path = Path(state.output_directory) / "build_manifest.json"
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text())
            manifest["github"] = result
            manifest_path.write_text(json.dumps(manifest, indent=2))
        # Security audit
        security = self.agents["security"].audit(
            state.spec, state.backend_code or {}, state.architecture
        )
        state.security_report = security
        score = security.get("security_score", "N/A")
        critical = len(security.get("critical_issues", []))
        print(f"   ✓ Security score: {score}/100")
        if critical > 0:
            print(f"   ⚠  Critical issues found: {critical} (see security_report.json)")

        # QA test generation
        tests = self.agents["qa"].generate_tests(
            state.spec, state.backend_code or {}, state.db_schema or {}
        )
        state.test_suite = tests if isinstance(tests, dict) else {}
        test_files = len(state.test_suite)
        print(f"   ✓ Test files: {test_files} test files generated")

    # ─────────────────────────────────────────────────────────────────────────
    # File Writers
    # ─────────────────────────────────────────────────────────────────────────

    def _write_all_files(self, state: BuildState) -> None:
        print("\n📁 Writing files to disk...")
        base = Path(state.output_directory)

        file_groups = [
            ("backend", state.backend_code or {}, "backend"),
            ("frontend", state.frontend_code or {}, "frontend"),
            ("devops", state.devops_config or {}, ""),  # devops files go at root
            ("tests", state.test_suite or {}, ""),
        ]

        total_files = 0
        for group_name, files, prefix in file_groups:
            for filepath, content in files.items():
                if not filepath or not content:
                    continue
                full_path = base / prefix / filepath if prefix else base / filepath
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(str(content), encoding="utf-8")
                total_files += 1

        # Write database files
        if state.db_schema:
            db_dir = base / "database"
            db_dir.mkdir(parents=True, exist_ok=True)

            schema_sql = state.db_schema.get("schema_sql", "")
            if schema_sql:
                (db_dir / "schema.sql").write_text(str(schema_sql))
                total_files += 1

            migration_sql = state.db_schema.get("migration_sql", "")
            if migration_sql:
                migrations_dir = db_dir / "migrations"
                migrations_dir.mkdir(exist_ok=True)
                (migrations_dir / "001_initial.sql").write_text(str(migration_sql))
                total_files += 1

            seed_sql = state.db_schema.get("seed_sql", "")
            if seed_sql:
                seeds_dir = db_dir / "seeds"
                seeds_dir.mkdir(exist_ok=True)
                (seeds_dir / "initial_data.sql").write_text(str(seed_sql))
                total_files += 1

        print(f"   ✓ {total_files} files written to {state.output_directory}")

    def _write_readme(self, state: BuildState) -> None:
        spec = state.spec
        base = Path(state.output_directory)

        env_vars = "\n".join(
            f"  {v.get('name', '')}={v.get('example', '')!r}  # {v.get('description', '')}"
            for v in (spec.environment_variables or [])
        )

        readme = f"""# {spec.app_name}

{spec.description}

## 🏗 Architecture

**Type:** {spec.app_type}
**Pattern:** {(state.architecture or {}).get('pattern', 'Layered MVC')}

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+
- Python 3.11+
- PostgreSQL 15+

### 1. Clone and Configure

```bash
# Copy environment variables
cp .env.example .env

# Edit .env with your actual values
nano .env
```

### 2. Environment Variables

```env
{env_vars or "# See .env.example for required variables"}
```

### 3. Start with Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# Run database migrations
./scripts/migrate.sh

# Seed initial data
./scripts/seed.sh
```

### 4. Development Setup (Without Docker)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 📋 Features

{chr(10).join(f'- {f}' for f in (spec.features or []))}

## 🔌 API Endpoints

| Method | Path | Description | Auth |
|--------|------|-------------|------|
{chr(10).join(f"| {e.get('method','GET')} | {e.get('path','/')} | {e.get('description','')} | {'✓' if e.get('auth_required') else '✗'} |" for e in (spec.api_endpoints or [])[:20])}

**Full API docs:** http://localhost:8000/docs (Swagger UI)

## 🧪 Running Tests

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=. --cov-report=html

# Frontend tests
cd frontend
npm test

# E2E tests
cd frontend
npx cypress run
```

## 🐳 Production Deployment

```bash
# Build and start production stack
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Check health
./scripts/healthcheck.sh
```

## 🔒 Security

- JWT authentication (15-min access tokens, 7-day refresh tokens)
- bcrypt password hashing
- Rate limiting on public endpoints
- Input validation via Pydantic
- Security headers via Nginx
- Soft deletes (data is never permanently deleted)

## 📊 Tech Stack

| Layer | Technology |
|-------|-----------|
{chr(10).join(f"| {k.title()} | {v} |" for k, v in (spec.tech_stack or {}).items())}

---
*Generated by VibeCoding AI — {spec.app_name} v1.0.0*
"""
        (base / "README.md").write_text(readme, encoding="utf-8")
        print("   ✓ README.md generated")

    def _write_manifest(self, state: BuildState) -> None:
        base = Path(state.output_directory)
        manifest = {
            "app_name": state.spec.app_name if state.spec else "unknown",
            "prompt": state.prompt[:200],
            "status": state.status,
            "files_generated": {
                "backend": len(state.backend_code or {}),
                "frontend": len(state.frontend_code or {}),
                "devops": len(state.devops_config or {}),
                "tests": len(state.test_suite or {}),
            },
            "security_score": (state.security_report or {}).get("security_score", "N/A"),
            "errors": state.errors,
        }
        (base / "build_manifest.json").write_text(
            json.dumps(manifest, indent=2, default=str), encoding="utf-8"
        )

        # Write full security report
        if state.security_report:
            (base / "security_report.json").write_text(
                json.dumps(state.security_report, indent=2, default=str), encoding="utf-8"
            )

    # ─────────────────────────────────────────────────────────────────────────
    # Utilities
    # ─────────────────────────────────────────────────────────────────────────

    def _run_phase(
        self,
        phase_name: str,
        phase_num: int,
        total: int,
        state: BuildState,
        runner,
        skip: bool = False
    ) -> BuildState:
        if skip:
            print(f"\n⏭  Phase {phase_num}/{total}: {phase_name} [SKIPPED]")
            return state

        print(f"\n{'='*60}")
        print(f"🔄 Phase {phase_num}/{total}: {phase_name}")
        print(f"{'='*60}")

        try:
            runner()
            print(f"✅ Phase {phase_num} complete.")
        except Exception as e:
            error_msg = f"Phase {phase_num} ({phase_name}) failed: {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            state.errors.append(error_msg)
            print(f"❌ {error_msg}")

            # Critical phases fail the build; optional phases are warned
            if phase_num <= 4:
                state.status = "failed"

        return state

    def _print_banner(self, prompt: str) -> None:
        print("\n" + "="*60)
        print("🚀 VibeCoding — Enterprise Application Generator")
        print("="*60)
        print(f"📝 Prompt: {prompt[:80]}{'...' if len(prompt) > 80 else ''}")
        print("="*60)

    def _print_completion(self, state: BuildState) -> None:
        print("\n" + "="*60)
        print("🎉 Application Build Complete!")
        print("="*60)
        print(f"📁 Output: {state.output_directory}")
        print(f"🔧 Backend files: {len(state.backend_code or {})}")
        print(f"🎨 Frontend files: {len(state.frontend_code or {})}")
        print(f"🐳 DevOps files: {len(state.devops_config or {})}")
        print(f"🧪 Test files: {len(state.test_suite or {})}")
        print(f"🔒 Security score: {(state.security_report or {}).get('security_score', 'N/A')}/100")
        if state.errors:
            print(f"⚠  Warnings: {len(state.errors)} non-critical issues (see build_manifest.json)")
        if getattr(state, "github_repo", None):
            print(f"🐙 GitHub: {state.github_repo['repo_url']}")
        print(f"\n📖 Next steps:")
        if getattr(state, "github_repo", None):
            print(f"   1. git clone {state.github_repo['clone_url']}")
        else:
            print(f"   1. cd {state.output_directory}")
        print(f"   2. cp .env.example .env && nano .env")
        print(f"   3. docker-compose up -d")
        print(f"   4. ./scripts/migrate.sh")
        print(f"   5. Open http://localhost:3000")
        print("="*60 + "\n")
