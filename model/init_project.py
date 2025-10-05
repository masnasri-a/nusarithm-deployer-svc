from pydantic import BaseModel

class InitProjectRequest(BaseModel):
    project_name: str
    github_url: str
    subdomain: str
    description: str = None
    
class InitProjectResponse(BaseModel):
    message: str
    status_code: int = 200
    