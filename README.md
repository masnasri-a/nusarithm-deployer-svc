# Deployer App Backend

A FastAPI-based backend service for deploying and managing Next.js applications with automatic Git integration, build processes, and PM2 deployment.

## Features

- **Git Integration**: Clone repositories, manage branches, and pull latest changes
- **Automatic Building**: Build Next.js applications with dependency management
- **PM2 Deployment**: Deploy applications using PM2 process manager with automatic port assignment
- **Environment Management**: Set and manage environment variables for projects
- **MongoDB Integration**: Store project configurations and deployment data
- **Subdomain Generation**: Automatic subdomain generation for deployed applications

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **MongoDB**: Database for storing project and deployment configurations
- **PM2**: Process manager for Node.js applications
- **Python**: Backend programming language
- **Git**: Version control integration

## Installation

### Prerequisites

- Python 3.8+
- Node.js and npm
- PM2 (`npm install -g pm2`)
- MongoDB
- Git

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd deployer-app/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the root directory:
   ```env
   # MongoDB Configuration
   MONGODB_URL=mongodb://localhost:27017
   DATABASE_NAME=deployer_app
   
   # Project Directories
   BASE_DIR=/path/to/clone/directory
   BASE_DIR_BUILD=/path/to/build/directory
   
   # Optional: Add other environment variables as needed
   ```

5. **Start the application**
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- **Interactive API docs**: `http://localhost:8000/docs`
- **ReDoc documentation**: `http://localhost:8000/redoc`

## API Endpoints

### Project Management

- **POST `/init`** - Initialize a new project
  - Body: `{ "repo_url": "string", "branch": "string", "project_name": "string" }`
  - Response: Project initialization status

- **GET `/list_branches?project_name=<name>`** - List all branches for a project
  - Response: Array of branch names

- **POST `/pull_latest?project_name=<name>&branch=<branch>`** - Pull latest changes
  - Response: Pull operation status

### Build and Deployment

- **POST `/build_nextjs_app?project_name=<name>&branch=<branch>`** - Build Next.js application
  - Response: Build operation status

- **POST `/deploy_pm2?project_name=<name>`** - Deploy application using PM2
  - Response: Deployment status with assigned port

- **GET `/generate_subdomain?project_name=<name>`** - Generate subdomain for project
  - Response: Generated subdomain

### Environment Variables

- **POST `/set_env_vars?project_name=<name>`** - Set environment variables
  - Body: `[{ "key": "string", "value": "string" }]`
  - Response: Operation status

- **GET `/get_env_vars?project_name=<name>`** - Get environment variables
  - Response: Key-value pairs of environment variables

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── .env                   # Environment configuration
├── config/
│   └── db.py             # MongoDB connection configuration
├── model/
│   ├── env_model.py      # Environment variable models
│   └── init_project.py   # Project initialization models
└── service/
    ├── common_service.py # Common utilities (build, env vars)
    ├── git_service.py    # Git operations
    ├── init_project.py   # Project initialization logic
    └── deploy_service.py # PM2 deployment logic
```

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `MONGODB_URL` | MongoDB connection string | Yes | - |
| `DATABASE_NAME` | Database name | Yes | - |
| `BASE_DIR` | Directory for cloned repositories | Yes | - |
| `BASE_DIR_BUILD` | Directory for build outputs | Yes | - |

### MongoDB Collections

The application uses the following collections:
- **domains**: Stores project configurations, ports, and deployment data

## Usage Example

1. **Initialize a project**
   ```bash
   curl -X POST "http://localhost:8000/init" \
     -H "Content-Type: application/json" \
     -d '{
       "repo_url": "https://github.com/user/nextjs-app.git",
       "branch": "main",
       "project_name": "my-app"
     }'
   ```

2. **Build the application**
   ```bash
   curl -X POST "http://localhost:8000/build_nextjs_app?project_name=my-app&branch=main"
   ```

3. **Deploy with PM2**
   ```bash
   curl -X POST "http://localhost:8000/deploy_pm2?project_name=my-app"
   ```

## Development

### Running in Development Mode

```bash
python main.py
```

The server will start with auto-reload enabled on `http://localhost:8000`

### Logging

The application uses Python's built-in logging module. Logs are output to the console with INFO level by default.

## Troubleshooting

### Common Issues

1. **"Invalid project directory" error**
   - Ensure the project has been built before deployment
   - Check that `BASE_DIR` and `BASE_DIR_BUILD` are correctly configured

2. **"Command not found: next"**
   - Ensure Node.js and npm are installed
   - Make sure dependencies are installed (`npm install`)

3. **MongoDB connection issues**
   - Verify MongoDB is running
   - Check `MONGODB_URL` in `.env` file

4. **PM2 deployment failures**
   - Ensure PM2 is installed globally: `npm install -g pm2`
   - Check that the project has been built successfully

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add your license information here]

## Support

For issues and questions, please create an issue in the repository or contact the development team.