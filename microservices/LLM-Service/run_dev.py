import os
import sys
from pathlib import Path

# Add src to path for development
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

if __name__ == "__main__":
    # Set environment variables
    os.environ.setdefault("OPENAI_API_KEY", "test-key-for-development")
    os.environ.setdefault("DEBUG", "true")
    
    # Import and run
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8004,
        reload=True,
        log_level="info"
    )
