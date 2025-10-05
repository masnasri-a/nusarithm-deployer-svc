from config.db import get_database
from model.init_project import InitProjectRequest, InitProjectResponse


def init_project(model: InitProjectRequest) -> InitProjectResponse:
    db = get_database()
    collection = db["domains"]
    # checking if subdomain or github_url already exists
    existing_entry = collection.find_one({
        "$or": [
            {"subdomain": model.subdomain},
            {"github_url": model.github_url}
        ]
    })
    if existing_entry:
        return InitProjectResponse(message="Subdomain or GitHub URL already exists", status_code=400)

    # Proceed with initialization
    if collection.insert_one(model.model_dump()):
        # Call git service to clone the project
        from service import git_service
        git_service.clone_project(model)
    
    
    return InitProjectResponse(message="Initialization successful", status_code=200)

