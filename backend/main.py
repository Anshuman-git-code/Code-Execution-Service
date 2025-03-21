from fastapi import FastAPI
from pydantic import BaseModel
import docker
import threading


app = FastAPI()
docker_client = docker.from_env()

class CodeRequest(BaseModel):
    code: str

def run_container(code, result):
    """Runs the code inside a Docker container."""
    try:
        output = docker_client.containers.run(
            "code-sandbox",  # Our sandbox image
            ["python3", "-c", code],  # Execute code
            remove=True,  # Auto-remove container after execution
            mem_limit="200m",  # Limit memory usage
            network_disabled=True  # No internet access
        ).decode("utf-8")
        
        result["output"] = output  # Update result dictionary
        result["error"] = None  # Clear error
    except Exception as e:
        result["error"] = str(e)  # Catch any Docker execution errors


@app.post("/execute")
def execute_code(request: CodeRequest):
    result = {"error": "Execution timeout", "output": None}  # Default timeout response
    thread = threading.Thread(target=run_container, args=(request.code, result))
    
    thread.start()
    thread.join(timeout=5)  # Enforce timeout of 5 seconds

    if thread.is_alive():
        return result  # Return timeout error
    
    return {"output": result["output"]} if result["output"] else {"error": result["error"]}