#!/usr/bin/env python3
"""
Virtual environment setup for TriviaBot
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and return success status"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False

def main():
    print("🚀 TriviaBot Virtual Environment Setup\n")
    
    venv_path = Path("venv")
    
    # Create virtual environment
    if not venv_path.exists():
        if not run_command(f"{sys.executable} -m venv venv", "Creating virtual environment"):
            print("\n❌ Could not create virtual environment")
            print("You may need to install python3-venv:")
            print("sudo apt install python3-venv")
            return False
    else:
        print("✅ Virtual environment already exists")
    
    # Determine activation script path
    if os.name == 'nt':  # Windows
        pip_path = venv_path / "Scripts" / "pip"
        python_path = venv_path / "Scripts" / "python"
        activate_script = venv_path / "Scripts" / "activate"
    else:  # Unix/Linux
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"
        activate_script = venv_path / "bin" / "activate"
    
    # Upgrade pip in virtual environment
    run_command(f"{python_path} -m pip install --upgrade pip", "Upgrading pip")
    
    # Install requirements
    if run_command(f"{pip_path} install -r requirements.txt", "Installing requirements"):
        print("\n🎉 Setup complete!")
        print("\n📋 To run the bot:")
        print("# Activate virtual environment:")
        print(f"source {activate_script}")
        print("# Run the bot:")
        print("python main.py")
        print("\n# Or run directly:")
        print(f"{python_path} main.py")
        
        # Create convenience script
        with open("run_bot.sh", "w") as f:
            f.write(f"#!/bin/bash\n")
            f.write(f"source {activate_script}\n")
            f.write(f"python main.py\n")
        
        os.chmod("run_bot.sh", 0o755)
        print("\n🚀 Convenience script created: ./run_bot.sh")
        
    else:
        print("\n❌ Failed to install requirements")
        print("Try manual installation in virtual environment:")
        print(f"source {activate_script}")
        print("pip install -r requirements.txt")

if __name__ == "__main__":
    main()