#!/usr/bin/env python3
"""
Test Runner Script - Run all tests in the organized test structure
"""
import os
import subprocess
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def run_tests(test_category: str = "all", verbose: bool = True):
    """
    Run tests for specified category or all tests
    
    Args:
        test_category: 'unit', 'integration', 'functional', 'e2e', 'performance', or 'all'
        verbose: Whether to run with verbose output
    """
    test_dir = project_root / "tests"
    
    if test_category == "all":
        cmd = ["python", "-m", "pytest", str(test_dir)]
    else:
        category_dir = test_dir / test_category
        if not category_dir.exists():
            print(f"Error: Test category '{test_category}' directory does not exist")
            return False
        cmd = ["python", "-m", "pytest", str(category_dir)]
    
    if verbose:
        cmd.extend(["-v", "--tb=short"])
    
    # Add coverage if available
    cmd.extend(["--cov=microservices", "--cov-report=html", "--cov-report=term"])
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, cwd=project_root, check=True)
        print(f"\n✅ Tests completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return False

def main():
    """Main entry point for the test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run organized tests")
    parser.add_argument(
        "category", 
        nargs="?", 
        default="all",
        choices=["unit", "integration", "functional", "e2e", "performance", "all"],
        help="Test category to run (default: all)"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Run tests quietly"
    )
    
    args = parser.parse_args()
    
    print(f"🧪 Running {args.category} tests...")
    print(f"📁 Test directory: {project_root / 'tests'}")
    print("-" * 50)
    
    success = run_tests(args.category, verbose=not args.quiet)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
