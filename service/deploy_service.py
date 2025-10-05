import os
import random
from config.db import get_database
import subprocess
import yaml, os

# Use a config file in the user's home directory or project directory
CONFIG_FILE = os.path.expanduser("~/.cloudflared/config.yml")
# Alternative: Use project-specific config
# CONFIG_FILE = os.path.join(os.getenv("BASE_DIR", ""), "cloudflared-config.yml")


def deploy_pm2(project_name: str):
    
    # Find project in db
    db = get_database()
    collection = db["domains"]
    project = collection.find_one({"project_name": project_name})
    
    # check port in project
    if not project or "port" not in project:
        #init port
        project["port"] = random.randint(30000, 90000)
        collection.update_one({"project_name": project_name}, {"$set": {"port": project["port"]}})
        print(f"Port not found for project {project_name}. Assigned new port {project['port']}")
    
    port = project["port"]

    
    # Get the source directory path where node_modules and package.json are located
    BASE_DIR_SOURCE = os.getenv("BASE_DIR")
    project_path_source = os.path.join(BASE_DIR_SOURCE, project_name)
    
    # Create start.js file that runs from the source directory
    start_js_content = f"""const {{ spawn }} = require('child_process');
const path = require('path');

// Change to the source directory where package.json and node_modules exist
process.chdir('{project_path_source}');

// Start Next.js using npm run start
const child = spawn('npm', ['run', 'start', '--', '--port', '{port}'], {{
    stdio: 'inherit',
    env: process.env
}});

child.on('error', (error) => {{
    console.error(`Error starting Next.js: ${{error.message}}`);
    process.exit(1);
}});

child.on('close', (code) => {{
    console.log(`Next.js process exited with code ${{code}}`);
    if (code !== 0) {{
        process.exit(code);
    }}
}});"""

    with open(os.path.join(project_path_source, "start.js"), "w") as f:
            f.write(start_js_content)
    # delete existing pm2 config if exists
    subprocess.run(["pm2", "delete", project_name], cwd=project_path_source, check=False)
    #create start script

    subprocess.run(["pm2", "start", "start.js", "--name", project_name], cwd=project_path_source, check=True)

    subprocess.run(["pm2", "save"], check=True)
    return f"Deployed {project_name} with PM2 on port {port}"
    



def update_cloudflare_config(hostname: str, port: int):
    # Ensure the config directory exists
    config_dir = os.path.dirname(CONFIG_FILE)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir, exist_ok=True)
    
    # Initialize config file if it doesn't exist
    if not os.path.exists(CONFIG_FILE):
        initial_config = {
            "tunnel": os.getenv("CLOUDFLARE_TUNNEL_ID", "your-tunnel-id"),
            "credentials-file": os.path.expanduser("~/.cloudflared/credentials.json"),
            "ingress": [
                {"service": "http_status:404"}
            ]
        }
        with open(CONFIG_FILE, "w") as f:
            yaml.safe_dump(initial_config, f)
    
    try:
        with open(CONFIG_FILE) as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        data = {"ingress": []}

    # pastikan key ingress ada
    if "ingress" not in data:
        data["ingress"] = []

    # hapus entry lama jika ada
    data["ingress"] = [
        i for i in data["ingress"]
        if not (isinstance(i, dict) and i.get("hostname") == hostname)
    ]

    # tambahkan mapping baru
    data["ingress"].insert(0, {
        "hostname": hostname,
        "service": f"http://localhost:{port}"
    })

    # tambahkan fallback terakhir
    if not any("service" in i and "http_status:404" in i["service"] for i in data["ingress"]):
        data["ingress"].append({"service": "http_status:404"})

    # simpan ulang config
    with open(CONFIG_FILE, "w") as f:
        yaml.safe_dump(data, f)

    # restart cloudflared with the custom config
    try:
        subprocess.run(["cloudflared", "tunnel", "run", "--config", CONFIG_FILE], check=False)
    except subprocess.CalledProcessError as e:
        print(f"Warning: Could not restart cloudflared: {e}")
        print(f"You may need to manually restart cloudflared with: cloudflared tunnel run --config {CONFIG_FILE}")
    
def generate_subdomain(project_name: str):
    # Placeholder implementation
    db = get_database()
    collection = db["domains"]
    project = collection.find_one({"project_name": project_name})
    
    if not project:
        return {"error": f"Project {project_name} not found"}
    
    subdomain = project.get("subdomain", "")
    port = project.get("port", "")
    
    if not subdomain or not port:
        return {"error": "Missing subdomain or port configuration"}
    
    full_domain = f'{subdomain}.nusarithm.id'  # Replace with your actual domain logic
    
    try:
        # Add DNS route
        subprocess.run([
            "cloudflared", "tunnel", "route", "dns", "nusadeploy", full_domain
        ], check=True)
        
        # Update config
        update_cloudflare_config(full_domain, port)
        
        return {"domain": 'https://'+full_domain, "port": port}
    except subprocess.CalledProcessError as e:
        return {"error": f"Failed to configure cloudflare: {e}"}
    except Exception as e:
        return {"error": f"Configuration error: {e}"}
    