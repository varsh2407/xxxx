from typing import Any, Dict
from agents.base_agent import BaseAgent
from architecture import AgentRole, ApplicationSpec


class DatabaseDesigner(BaseAgent):
    """Designs complete database schemas with migrations and seed data."""

    def __init__(self):
        super().__init__(AgentRole.DATABASE_DESIGNER)

    def get_system_prompt(self) -> str:
        return """You are a Principal Database Architect specializing in PostgreSQL and enterprise data modeling.

Your database design JSON must include:
- schema_sql: complete CREATE TABLE statements with all constraints
- migration_sql: Alembic-compatible migration SQL
- seed_sql: realistic seed data for development
- indexes: list of {table, columns, reason, sql}
- tables: list of {name, description, estimated_rows}
- relationships: list of {from_table, to_table, type, foreign_key}
- enum_types: any PostgreSQL enum types needed

MANDATORY DATABASE STANDARDS:
- UUID primary keys (gen_random_uuid()) not serial integers
- created_at TIMESTAMPTZ DEFAULT NOW() on every table
- updated_at TIMESTAMPTZ DEFAULT NOW() on every table  
- Soft deletes: deleted_at TIMESTAMPTZ NULL (not hard deletes)
- Row-level security considerations (add RLS comments)
- Proper foreign key constraints with ON DELETE behavior
- Check constraints for data integrity
- Indexes on all foreign keys
- Composite indexes for common query patterns
- No nullable columns without explicit business reason (comment why)
- All text fields have appropriate length constraints
- ENUM types for status fields (not strings)
- Audit trail: include an audit_logs table
- Proper schema comments (COMMENT ON TABLE/COLUMN)"""

    def design(self, spec: ApplicationSpec, architecture: Dict[str, Any]) -> Dict[str, Any]:
        """Design the complete database schema."""
        result = self.think(
            "Design a complete, production-ready PostgreSQL database schema.",
            context={
                "spec": spec.__dict__,
                "architecture": architecture
            }
        )
        return result
