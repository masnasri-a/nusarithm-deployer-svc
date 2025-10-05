from pydantic import BaseModel, Field

class EnvModel(BaseModel):
    key: str = Field(..., description="The environment variable key")
    value: str = Field(..., description="The environment variable value")