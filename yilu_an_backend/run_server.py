# run_server.py
import subprocess
from app.config import settings

def start_fastapi():
    cmd = [
        "uv", "run", "uvicorn",
        "app.main:app",
        "--reload",
        "--host", settings.HOST,
        "--port", str(settings.PORT)
    ]
    subprocess.run(cmd)

if __name__ == "__main__":
    start_fastapi()