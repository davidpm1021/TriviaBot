#!/usr/bin/env python3
"""
Test script to verify configuration and basic imports
"""
import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_environment():
    """Test environment variables"""
    print("🔧 Testing Environment Configuration...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    discord_token = os.getenv("DISCORD_TOKEN")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if discord_token:
        print(f"✅ Discord Token: {discord_token[:20]}...")
    else:
        print("❌ Discord Token: Missing")
    
    if openai_key:
        print(f"✅ OpenAI Key: {openai_key[:20]}...")
    else:
        print("❌ OpenAI Key: Missing")
    
    print()

def test_imports():
    """Test if all modules can be imported"""
    print("📦 Testing Module Imports...")
    
    try:
        import discord
        print("✅ discord.py imported successfully")
    except ImportError as e:
        print(f"❌ discord.py: {e}")
    
    try:
        import openai
        print("✅ openai imported successfully")
    except ImportError as e:
        print(f"❌ openai: {e}")
    
    try:
        from config.settings import settings
        print("✅ settings imported successfully")
    except ImportError as e:
        print(f"❌ settings: {e}")
    
    print()

def test_project_structure():
    """Test project structure"""
    print("📁 Testing Project Structure...")
    
    required_files = [
        "main.py",
        ".env",
        "requirements.txt",
        "config/settings.py",
        "src/bot/bot.py",
        "src/trivia/generator.py",
        "src/personality/personas.py"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
    
    print()

if __name__ == "__main__":
    print("🎯 TriviaBot Configuration Test\n")
    
    try:
        test_project_structure()
        test_environment()
        test_imports()
        
        print("🎉 Basic configuration test complete!")
        print("\n📋 Next Steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run the bot: python main.py")
        print("3. In Discord, use: !sync (to sync slash commands)")
        print("4. Start playing: /trivia")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)