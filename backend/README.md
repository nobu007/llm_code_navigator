## Getting Started

First, run the python backend.

```bash
cd llm_code_navigator/backend
python -m app.main
```

Open [http://localhost:9000](http://localhost:9000) with your browser to see the result.

```
{"detail":"Not Found"}
```

## Detailed Usage Instructions

### Running the Backend

To run the backend, use the following command:

```bash
cd llm_code_navigator/backend
python -m app.main
```

### API Endpoints

The backend provides the following API endpoints:

- `GET /api/files_info`: Retrieves information about the files.
- `GET /api/file_content/{full_path}`: Retrieves the content of a specific file.

### Configuration Options

The backend can be configured using environment variables. The following options are available:

- `PROJECT_NAME`: The name of the project.
- `BACKEND_DIR`: The directory where the backend files are located.
- `ALLOWED_ORIGINS`: A list of allowed origins for CORS.
- `LOG_LEVEL`: The log level for the application.

### Testing Setup

To run the tests for the backend, use the following command:

```bash
cd llm_code_navigator/backend
python -m unittest discover -s backend/tests
```

The tests are located in the `backend/tests` directory and cover various aspects of the backend services.
