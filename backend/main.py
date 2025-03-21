from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import docker
import threading
import time
from sandbox_utils import is_safe_code  # Import security checker

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust to match your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)

docker_client = docker.from_env()

class CodeRequest(BaseModel):
    code: str

def run_container(code, result):
    """Runs the code inside a Docker container and ensures cleanup."""
    container = None  # Track the running container
    try:
        container = docker_client.containers.run(
            "code-sandbox",  # Sandbox image
            ["python3", "-c", code],  # Execute code
            detach=True,  # Run in background to allow monitoring
            mem_limit="100m",  # Limit memory usage
            network_disabled=True,  # No internet access
            cpu_period=100000,  # Limit CPU usage
            cpu_quota=50000  # Restrict to 50% of a single core            
        )
        
        # Wait up to 5 seconds for completion
        start_time = time.time()
        while time.time() - start_time < 5:
            container.reload()
            if container.status in ["exited", "dead"]:
                break  # Stop if the container has finished execution
            time.sleep(0.5)  # Check status every 500ms

        # Fetch logs before removing container
        logs = container.logs().decode("utf-8") if container else ""

        # Check final status
        if container.status not in ["exited", "dead"]:
            result["error"] = "Execution timeout"
        else:
            result["output"] = logs.strip()

    except docker.errors.ContainerError as e:
        result["error"] = f"Execution Error: {str(e)}"
    except docker.errors.APIError as e:
        result["error"] = f"Docker API Error: {str(e)}"
    except docker.errors.NotFound:
        result["error"] = "Container not found."
    finally:
        # Ensure container cleanup
        if container:
            try:
                container.stop(timeout=1)  # Force-stop running container
                container.remove(force=True)  # Force remove container
            except docker.errors.APIError:
                pass  # Ignore errors in cleanup

@app.post("/execute")
def execute_code(request: CodeRequest):
    """Execute user-submitted Python code in a secure sandbox."""
    
    # 🚨 Security Check: Reject unsafe code 🚨
    if not is_safe_code(request.code):
        raise HTTPException(status_code=400, detail="Unsafe code detected!")

    result = {"error": "Execution timeout", "output": None}  # Default timeout response
    thread = threading.Thread(target=run_container, args=(request.code, result))
    
    thread.start()
    thread.join(timeout=6)  # Give 6 seconds max (1s buffer)

    if thread.is_alive():
        return result  # Return timeout error
    
    return {"output": result["output"]} if result["output"] else {"error": result["error"]}