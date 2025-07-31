#!/usr/bin/env python3
"""
Quick setup script for Reddit Content Analyzer
"""

import os
import sys
import subprocess

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print("✅ Python version check passed")

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        sys.exit(1)

def setup_env_file():
    """Create .env file from template if it doesn't exist"""
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            try:
                with open('.env.example', 'r') as src:
                    with open('.env', 'w') as dst:
                        dst.write(src.read())
                print("✅ Created .env file from template")
                print("⚠️  Please edit .env file with your API credentials before running the app")
            except Exception as e:
                print(f"❌ Failed to create .env file: {e}")
        else:
            print("❌ .env.example file not found")
    else:
        print("✅ .env file already exists")

def main():
    """Main setup function"""
    print("🚀 Setting up Reddit Content Analyzer...")
    print()
    
    check_python_version()
    install_dependencies()
    setup_env_file()
    
    print()
    print("🎉 Setup completed!")
    print()
    print("Next steps:")
    print("1. Edit .env file with your Reddit and OpenAI API credentials")
    print("2. Run: python web_app.py")
    print("3. Open http://localhost:5000 in your browser")
    print()
    print("For detailed instructions, see README_REDDIT_ANALYZER.md")

if __name__ == "__main__":
    main()