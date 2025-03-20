from fastapi import FastAPI
from pydantic import BaseModel
import subprocess

app = FastAPI()

class CodeRequest(BaseModel):
    code: str

@app.post("/execute")
def execute_code(request: CodeRequest):
    try:
        # Run the submitted code in a sandboxed process
        result = subprocess.run(
            ["python3", "-c", request.code],
            capture_output=True,
            text=True,
            timeout=5  # Prevent infinite loops
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except subprocess.TimeoutExpired:
        return {"error": "Execution timed out"}