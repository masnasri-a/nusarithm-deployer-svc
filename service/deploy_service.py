import os
import random
from config.db import get_database
import subprocess
import yaml, os

CONFIG_FILE = "/etc/cloudflared/config.yml"


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
    with open(CONFIG_FILE) as f:
        data = yaml.safe_load(f)

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

    # restart cloudflared
    subprocess.run(["systemctl", "restart", "cloudflared"])
    
def generate_subdomain(project_name: str):
    # Placeholder implementation
    db = get_database()
    collection = db["domains"]
    subdomain = collection.find_one({"project_name": project_name}).get("subdomain", "")
    port = collection.find_one({"project_name": project_name}).get("port", "")
    full_domain = f'{subdomain}.nusarithm.id'  # Replace with your actual domain logic
    subprocess.run([
        "cloudflared", "tunnel", "route", "dns", "nusadeploy", full_domain
    ])
    update_cloudflare_config(full_domain, port)
    return {"domain": 'https://'+full_domain, "port": port}
    