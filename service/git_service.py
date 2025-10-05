from model.init_project import InitProjectRequest
from dotenv import load_dotenv
import os, subprocess
from config.db import get_database

load_dotenv()

def clone_project(model: InitProjectRequest):
    BASE_DIR = os.getenv("BASE_DIR")

    #Checking directory exists
    project_path = os.path.join(BASE_DIR, model.project_name)
    if not os.path.exists(project_path):
        os.makedirs(project_path)
        
    # Cloning the repository
    subprocess.run(["git", "clone", model.github_url, project_path], check=True)
    
    return f"Project cloned to {project_path}"

def get_branch_list(project_name: str):

    # Find project in db
    db = get_database()
    collection = db["domains"]
    project = collection.find_one({"project_name": project_name})
    if not project:
        return []

    BASE_DIR = os.getenv("BASE_DIR")
    project_path = os.path.join(BASE_DIR, project_name)

    # Fetching the list of branches
    result = subprocess.run(["git", "-C", project_path, "branch", "-r"], capture_output=True, text=True, check=True)
    branches = [line.strip().replace("origin/", "") if '->' not in line.strip() else None for line in result.stdout.splitlines() if line.strip()]
    branches = [b for b in branches if b]  # Remove None values
    return branches

def pull_latest(project_name: str, branch: str = "main"):
    BASE_DIR = os.getenv("BASE_DIR")
    project_path = os.path.join(BASE_DIR, project_name)

    # Pulling the latest changes
    subprocess.run(["git", "-C", project_path, "checkout", branch], check=True)
    subprocess.run(["git", "-C", project_path, "pull", "origin", branch], check=True)
    
    return f"Pulled latest changes for {project_name} on branch {branch}"