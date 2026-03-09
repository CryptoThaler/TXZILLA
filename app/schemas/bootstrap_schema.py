from typing import Literal

from pydantic import BaseModel


class BootstrapExecutionResponse(BaseModel):
    mode: Literal["sqlite_metadata", "postgres_sql_script"]
    schema_path: str
    statements_executed: int
    detail: str
