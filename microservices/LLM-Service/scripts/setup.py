#!/usr/bin/env python3
"""
Setup script for LLM Service
Handles environment setup, dependency installation, and service configuration
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_command(command, check=True, cwd=None):
    """Run a shell command"""
    print(f"Running: {command}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=check, 
            cwd=cwd,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        if check:
            sys.exit(1)
        return e

def setup_environment():
    """Setup Python environment and install dependencies"""
    print("Setting up Python environment...")
    
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    
    # Install dependencies
    requirements_file = project_root / "requirements.txt"
    if requirements_file.exists():
        run_command(f"pip install -r {requirements_file}")
    else:
        print("requirements.txt not found, installing basic dependencies...")
        run_command("pip install fastapi uvicorn openai aiohttp python-dotenv pydantic")
    
    print("Environment setup complete!")

def setup_env_file():
    """Setup environment variables file"""
    print("Setting up environment file...")
    
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"
    
    if not env_file.exists() and env_example.exists():
        # Copy .env.example to .env
        import shutil
        shutil.copy(env_example, env_file)
        print(f"Created .env file from .env.example")
        print("Please edit .env file to add your OpenAI API key")
    elif env_file.exists():
        print(".env file already exists")
    else:
        # Create a basic .env file
        env_content = """# LLM Service Environment Variables
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.3
OPENAI_MAX_TOKENS=2000
SERVICE_PORT=8004
DEBUG=false
LOG_LEVEL=INFO
ENABLE_CACHING=true
CACHE_TTL_SECONDS=3600
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("Created basic .env file")
        print("Please edit .env file to add your OpenAI API key")

def create_directories():
    """Create necessary directories"""
    print("Creating directories...")
    
    project_root = Path(__file__).parent.parent
    directories = [
        project_root / "logs",
        project_root / "data",
        project_root / "cache"
    ]
    
    for directory in directories:
        directory.mkdir(exist_ok=True)
        print(f"Created directory: {directory}")

def run_tests():
    """Run the test suite"""
    print("Running tests...")
    
    project_root = Path(__file__).parent.parent
    test_directory = project_root / "tests"
    
    if test_directory.exists():
        run_command("python -m pytest tests/ -v", cwd=project_root)
    else:
        print("No tests directory found")

def start_service(dev=False):
    """Start the LLM service"""
    print("Starting LLM Service...")
    
    project_root = Path(__file__).parent.parent
    
    if dev:
        # Development mode with auto-reload
        run_command(
            "python -m uvicorn src.main:app --host 0.0.0.0 --port 8004 --reload",
            cwd=project_root,
            check=False
        )
    else:
        # Production mode
        run_command(
            "python -m uvicorn src.main:app --host 0.0.0.0 --port 8004",
            cwd=project_root,
            check=False
        )

def build_docker():
    """Build Docker image"""
    print("Building Docker image...")
    
    project_root = Path(__file__).parent.parent
    run_command("docker build -t llm-service .", cwd=project_root)

def run_docker():
    """Run Docker container"""
    print("Running Docker container...")
    
    run_command(
        "docker run -d -p 8004:8004 --name llm-service-container llm-service",
        check=False
    )

def run_benchmark():
    """Run performance benchmark"""
    print("Running performance benchmark...")
    
    project_root = Path(__file__).parent.parent
    benchmark_script = project_root / "tests" / "benchmark.py"
    
    if benchmark_script.exists():
        run_command(f"python {benchmark_script}", cwd=project_root)
    else:
        print("Benchmark script not found")

def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(description="LLM Service Setup Script")
    parser.add_argument("command", choices=[
        "setup", "test", "start", "start-dev", "docker-build", 
        "docker-run", "benchmark", "all"
    ], help="Command to execute")
    
    args = parser.parse_args()
    
    if args.command == "setup" or args.command == "all":
        setup_environment()
        setup_env_file()
        create_directories()
        
    if args.command == "test" or args.command == "all":
        run_tests()
        
    if args.command == "start":
        start_service(dev=False)
        
    if args.command == "start-dev":
        start_service(dev=True)
        
    if args.command == "docker-build":
        build_docker()
        
    if args.command == "docker-run":
        run_docker()
        
    if args.command == "benchmark":
        run_benchmark()
    
    print("Setup complete!")

if __name__ == "__main__":
    main()
