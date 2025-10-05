from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import logging
from fastapi.responses import JSONResponse as HttpResponse

from service import init_project, git_service, common_service
from model.init_project import InitProjectRequest, InitProjectResponse
from model.env_model import EnvModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code here
    load_dotenv()  # Load environment variables from .env file
    yield
    # Shutdown code here

app = FastAPI(lifespan=lifespan)


@app.post("/init")
def init(model: InitProjectRequest) -> InitProjectResponse:
    logger.info(f"Received init request: {model}")
    response = init_project.init_project(model)
    logger.info(f"Response: {response}")
    return HttpResponse(content={"message": response.message}, status_code=response.status_code)
    

@app.get("/list_branches")
def list_branches(project_name:str):
    branches = git_service.get_branch_list(project_name)
    return HttpResponse(content={"branches": branches}, status_code=200)

@app.post("/pull_latest")
def pull_latest(project_name: str, branch: str = "main"):
    message = git_service.pull_latest(project_name, branch)
    return HttpResponse(content={"message": message}, status_code=200)

@app.post("/build_nextjs_app")
def build_nextjs_app(project_name: str, branch: str = "main"):
    message = common_service.build_nextjs_app(project_name, branch)
    return HttpResponse(content={"message": message}, status_code=200)
    
    
@app.post("/set_env_vars")
def set_env_vars(project_name: str, env_vars: list[EnvModel]):
    env_dict = {var.key: var.value for var in env_vars}
    message = common_service.set_environment_variables(project_name, env_dict)
    return HttpResponse(content={"message": message}, status_code=200)

@app.get("/get_env_vars")
def get_env_vars(project_name: str):
    env_vars = common_service.get_environment_variables(project_name)
    return HttpResponse(content={"env_vars": env_vars}, status_code=200)

@app.post("/deploy_pm2")
def deploy_pm2(project_name: str):
    from service.deploy_service import deploy_pm2 as deploy_service_pm2
    message = deploy_service_pm2(project_name)
    return HttpResponse(content={"message": message}, status_code=200)

@app.get("/generate_subdomain")
def generate_subdomain(project_name: str):
    from service.deploy_service import generate_subdomain as deploy_service_generate_subdomain
    subdomain = deploy_service_generate_subdomain(project_name)
    return HttpResponse(content={"subdomain": subdomain}, status_code=200)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)