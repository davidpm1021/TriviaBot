#!/usr/bin/env python3
"""
Dependency installer for environments without pip
"""
import subprocess
import sys
import os

def install_pip():
    """Try to install pip"""
    print("🔧 Installing pip...")
    try:
        # Try downloading get-pip.py
        import urllib.request
        url = "https://bootstrap.pypa.io/get-pip.py"
        urllib.request.urlretrieve(url, "get-pip.py")
        
        # Run get-pip.py
        result = subprocess.run([sys.executable, "get-pip.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ pip installed successfully!")
            return True
        else:
            print(f"❌ Failed to install pip: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Could not install pip: {e}")
        return False

def install_package(package):
    """Install a single package"""
    try:
        print(f"📦 Installing {package}...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", package], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {package} installed successfully!")
            return True
        else:
            print(f"❌ Failed to install {package}: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error installing {package}: {e}")
        return False

def main():
    print("🚀 TriviaBot Dependency Installer\n")
    
    # Required packages
    packages = [
        "discord.py>=2.3.0",
        "openai>=1.0.0", 
        "python-dotenv>=1.0.0",
        "sqlalchemy>=2.0.0",
        "alembic>=1.12.0",
        "aiofiles>=23.0.0",
        "pydantic>=2.0.0",
        "python-dateutil>=2.8.0"
    ]
    
    # Check if pip is available
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      capture_output=True, check=True)
        print("✅ pip is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ pip not found, attempting to install...")
        if not install_pip():
            print("\n❌ Could not install pip automatically.")
            print("\n📋 Manual installation required:")
            print("1. Install pip: curl https://bootstrap.pypa.io/get-pip.py | python3")
            print("2. Or use system package manager: sudo apt install python3-pip")
            print("3. Then run: pip install -r requirements.txt")
            return False
    
    # Install packages
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print(f"\n📊 Installation Summary:")
    print(f"✅ Successfully installed: {success_count}/{len(packages)} packages")
    
    if success_count == len(packages):
        print("\n🎉 All dependencies installed! You can now run:")
        print("python3 main.py")
    else:
        print(f"\n⚠️  Some packages failed to install. Try manual installation:")
        print("pip install -r requirements.txt")
    
    # Clean up
    if os.path.exists("get-pip.py"):
        os.remove("get-pip.py")

if __name__ == "__main__":
    main()