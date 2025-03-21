import ast

# List of dangerous built-ins
UNSAFE_MODULES = {"os", "subprocess", "sys", "shutil"}
UNSAFE_FUNCTIONS = {"exec", "eval", "compile", "__import__", "open", "os", "subprocess"}

def is_safe_code(code: str) -> bool:
    """Check if the code contains unsafe functions."""
    try:
        tree = ast.parse(code)  # Parse the code into AST
        for node in ast.walk(tree):  # Walk through all nodes
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in UNSAFE_MODULES:
                        return False  # Block importing unsafe modules

            if isinstance(node, ast.ImportFrom):
                if node.module in UNSAFE_MODULES:
                    return False  # Block `from os import system`

            if isinstance(node, ast.Call):  # Function calls
                if isinstance(node.func, ast.Name) and node.func.id in UNSAFE_FUNCTIONS:
                    return False
            if isinstance(node, ast.Attribute):
                if node.attr in UNSAFE_FUNCTIONS or node.attr in UNSAFE_MODULES:
                    return False
        return True
    except Exception:
        return False  # If parsing fails, reject the code