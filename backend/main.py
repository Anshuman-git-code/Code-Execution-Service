from fastapi import FastAPI
from pydantic import BaseModel
import docker

app = FastAPI()
docker_client = docker.from_env()

class CodeRequest(BaseModel):
    code: str

@app.post("/execute")
def execute_code(request: CodeRequest):
    try:
        # Run code inside an isolated Docker container
        container = docker_client.containers.run(
            "code-sandbox",  # Use our sandbox image
            ["python3", "-c", request.code],  # Execute code
            remove=True,  # Auto-remove container after execution
            mem_limit="200m",  # Limit memory usage
            network_disabled=True,  # No internet access
            timeout=5  # Prevent infinite loops
        )
        return {"output": container.decode("utf-8")}
    
    except docker.errors.ContainerError as e:
        return {"error": "Execution failed", "details": str(e)}
    
    except docker.errors.APIError as e:
        return {"error": "Docker error", "details": str(e)}

    except Exception as e:
        return {"error": str(e)}