#!/usr/bin/env python3
"""
Setup script for Nepal Job Scraper.

Installs dependencies and prepares the environment.
"""

import subprocess
import sys
from pathlib import Path


def install_requirements():
    """Install Python requirements."""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False
    return True


def create_directories():
    """Create necessary directories."""
    print("📁 Creating directory structure...")
    
    directories = [
        "data/raw",
        "data/processed", 
        "data/exports",
        "logs",
        "scripts",
        "test",
        "config",
        "utils",
        "docs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   Created: {directory}")
    
    print("✅ Directory structure created")


def make_cli_executable():
    """Make the CLI script executable."""
    print("🔧 Setting up CLI...")
    
    cli_path = Path("scraper_cli.py")
    if cli_path.exists():
        # Make executable on Unix systems
        import stat
        current_mode = cli_path.stat().st_mode
        cli_path.chmod(current_mode | stat.S_IEXEC)
        print("✅ CLI script is now executable")
    else:
        print("⚠️  CLI script not found")


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python version OK: {sys.version}")
    return True


def setup_environment():
    """Set up the complete environment."""
    print("🚀 Setting up Nepal Job Scraper environment...\n")
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_requirements():
        return False
    
    # Make CLI executable
    make_cli_executable()
    
    print("\n🎉 Setup complete!")
    print("\n📋 Quick Start:")
    print("1. Check status:           python scraper_cli.py status")
    print("2. Create a scraper:       python scraper_cli.py create-script merojob")
    print("3. Test connectivity:      python test/sample_test.py")
    print("4. Run test scrape:        python scraper_cli.py scrape merojob --test-mode")
    print("5. View documentation:     cat docs/workflow.md")
    
    print("\n📖 For detailed workflow, see: docs/workflow.md")
    print("🔧 For configuration, see: config/settings.py")
    
    return True


if __name__ == "__main__":
    success = setup_environment()
    sys.exit(0 if success else 1) 