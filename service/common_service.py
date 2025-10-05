from dotenv import load_dotenv
import os, subprocess, logging, shutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def build_nextjs_app(project_name: str, branch: str) -> str:
    # Placeholder implementation
    BASE_DIR_CLONE = os.getenv("BASE_DIR")
    project_path = os.path.join(BASE_DIR_CLONE, project_name)
    
    # Building the Next.js app
    logger.info(f"Building Next.js app for project {project_name} on branch {branch}")
    # Run npm install first
    subprocess.run(["npm", "install"], cwd=project_path, check=True)
    logger.info(f"Running npm build for project {project_name} on branch {branch}")
    # Then run npm build (without invalid --output-path argument)
    subprocess.run(["npm", "run", "build"], cwd=project_path, check=True)
    return f"Built Next.js app for project {project_name} on branch {branch}"


def set_environment_variables(project_name: str, env_vars: dict) -> str:
    BASE_DIR = os.getenv("BASE_DIR")
    project_path = os.path.join(BASE_DIR, project_name)
    env_file_path = os.path.join(project_path, ".env")
    
    with open(env_file_path, "w") as env_file:
        for key, value in env_vars.items():
            env_file.write(f"{key}={value}\n")

    return f"Set environment variables for project {project_name} in {env_file_path}"

def get_environment_variables(project_name: str) -> dict:
    BASE_DIR = os.getenv("BASE_DIR")
    project_path = os.path.join(BASE_DIR, project_name)
    env_file_path = os.path.join(project_path, ".env")

    env_vars = {}
    if os.path.exists(env_file_path):
        with open(env_file_path, "r") as env_file:
            for line in env_file:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value

    return env_vars