from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import docker
import threading
from sandbox_utils import is_safe_code  # Import security checker


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
            mem_limit="100m",  # Limit memory usage
            network_disabled=True,  # No internet access
            cpu_period=100000,  # Limit CPU usage
            cpu_quota=50000  # Restrict to 50% of a single core            
        ).decode("utf-8")
        
        result["output"] = output  # Update result dictionary
        result["error"] = None  # Clear error
    except Exception as e:
        result["error"] = str(e)  # Catch any Docker execution errors


@app.post("/execute")
def execute_code(request: CodeRequest):
    """Execute user-submitted Python code in a secure sandbox."""
    
    # 🚨 Security Check: Reject unsafe code 🚨
    if not is_safe_code(request.code):
        raise HTTPException(status_code=400, detail="Unsafe code detected!")

    result = {"error": "Execution timeout", "output": None}  # Default timeout response
    thread = threading.Thread(target=run_container, args=(request.code, result))
    
    thread.start()
    thread.join(timeout=5)  # Enforce timeout of 5 seconds

    if thread.is_alive():
        return result  # Return timeout error
    
    return {"output": result["output"]} if result["output"] else {"error": result["error"]}