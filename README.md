# llm_code_navigator

LLM Code Navigator

## prerequisite

Docker and docker compose.

### Docker engine

https://docs.docker.com/engine/install/ubuntu/

### Docker Compose

https://docs.docker.jp/compose/install.html

## start

This command runs "Getting Started" section in backend and frontend README.md.

```bash
cd llm_code_navigator
docker compose up
```

## backend

[backend/README.md](backend/README.md)

## frontend

[frontend/README.md](frontend/README.md)

## end or restart

```bash
cd llm_code_navigator
docker compose down
docker compose up
```

## CI/CD Pipeline

The CI/CD pipeline is defined in the `.github/workflows/ci.yml` file. It includes the following steps:

- Checkout code
- Set up Python
- Install dependencies
- Run tests
- Run Docker Compose CI service
- Build Docker image for backend
- Set up Node.js
- Install frontend dependencies
- Run frontend tests
- Build frontend Docker image
- Run frontend linting

## Docker Setup

The Docker setup is defined in the `docker-compose.yml` and `backend/Dockerfile` files.

### Docker Compose

The `docker-compose.yml` file defines the services for the backend and frontend. It includes the following services:

- `backend`: The backend service, which runs the Python backend.
- `frontend`: The frontend service, which runs the development server for the frontend.
- `ci`: The CI service, which runs the tests for the backend.

### Backend Dockerfile

The `backend/Dockerfile` file defines the Docker image for the backend. It includes the following steps:

- Use the `python:3.10` base image.
- Set the working directory to `/app/backend`.
- Copy the `requirements.txt` file and install the dependencies.
- Copy the rest of the backend files.
- Set the default command to run the backend application.
