"""
Setup script for Forget Me Not Backend
"""

import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"  Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("✗ Python 3.8 or higher is required")
        print(f"  Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✓ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_system_dependencies():
    """Install system dependencies based on the platform."""
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        print("Installing system dependencies for macOS...")
        # Check if Homebrew is installed
        if not run_command("which brew", "Checking for Homebrew"):
            print("Please install Homebrew first: https://brew.sh/")
            return False
        
        # Install cmake (required for dlib)
        run_command("brew install cmake", "Installing cmake")
        
    elif system == "linux":
        print("Installing system dependencies for Linux...")
        # Install cmake and build tools
        run_command("sudo apt-get update", "Updating package list")
        run_command("sudo apt-get install -y cmake build-essential", "Installing cmake and build tools")
        
    elif system == "windows":
        print("Installing system dependencies for Windows...")
        print("Please install Visual Studio Build Tools manually:")
        print("https://visualstudio.microsoft.com/visual-cpp-build-tools/")
        
    return True

def check_conda_environment():
    """Check if conda environment 'forget' exists and is activated."""
    print("Checking conda environment 'forget'...")
    
    # Check if we're in the correct conda environment
    conda_env = os.environ.get('CONDA_DEFAULT_ENV')
    if conda_env == 'forget':
        print("✓ Conda environment 'forget' is already activated")
        return True
    elif conda_env:
        print(f"⚠️  Currently in conda environment '{conda_env}', not 'forget'")
        print("Please activate the 'forget' environment first:")
        print("  conda activate forget")
        return False
    else:
        print("⚠️  No conda environment detected")
        print("Please create and activate the 'forget' environment first:")
        print("  conda create -n forget python=3.9")
        print("  conda activate forget")
        return False

def install_python_dependencies():
    """Install Python dependencies using pip in conda environment."""
    print("Installing Python dependencies in conda environment 'forget'...")
    
    if not run_command("pip install --upgrade pip", "Upgrading pip"):
        return False
    
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        return False
    
    return True

def create_directories():
    """Create necessary directories."""
    directories = ["uploads", "logs", "backups"]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✓ Created directory: {directory}")
        else:
            print(f"✓ Directory already exists: {directory}")
    
    return True

def create_env_file():
    """Create .env file from template."""
    env_file = ".env"
    env_example = ".env.example"
    
    if os.path.exists(env_file):
        print(f"✓ {env_file} already exists")
        return True
    
    if os.path.exists(env_example):
        # Copy example to .env
        with open(env_example, 'r') as src, open(env_file, 'w') as dst:
            dst.write(src.read())
        print(f"✓ Created {env_file} from {env_example}")
        print(f"  Please edit {env_file} and add your API keys")
    else:
        # Create basic .env file
        env_content = """# Forget Me Not Backend Configuration

# Llama API Configuration (Optional - will use fallback if not provided)
LLAMA_API_KEY=your_llama_api_key_here
LLAMA_API_URL=https://api.llama-api.com/chat/completions

# Server Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=True

# Face Recognition Configuration
FACE_CONFIDENCE_THRESHOLD=0.6

# Database Configuration
DATABASE_FILE=person_database.json

# Upload Configuration
MAX_FILE_SIZE_MB=16
UPLOAD_FOLDER=uploads
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"✓ Created basic {env_file}")
        print(f"  Please edit {env_file} and add your API keys")
    
    return True

def main():
    """Main setup function."""
    print("🚀 Setting up Forget Me Not Backend...")
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install system dependencies
    if not install_system_dependencies():
        print("⚠️  System dependencies installation had issues, but continuing...")
    
    # Check conda environment
    if not check_conda_environment():
        return False
    
    # Install Python dependencies
    if not install_python_dependencies():
        return False
    
    # Create directories
    if not create_directories():
        return False
    
    # Create .env file
    if not create_env_file():
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file and add your Llama API key (optional)")
    print("2. Make sure you're in the 'forget' conda environment:")
    print("   conda activate forget")
    print("3. Run the server:")
    print("   python api.py")
    print("\n4. Find your computer's IP address and share it with the Unity developer")
    print("   The server will be accessible at: http://YOUR_IP:5000")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
