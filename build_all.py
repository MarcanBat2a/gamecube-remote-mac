#!/usr/bin/env python3
"""
macOS build script for NSO GameCube Controller Pairing App
"""

import os
import sys
import subprocess
import platform
import shutil

def run_command(cmd, shell=True):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, shell=shell, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def build_executable():
    """Build executable for macOS"""
    print(f"Building for {platform.system()} ({platform.machine()})")

    output_dir = "dist/macos"
    script_name = "./platform/macos/build.sh"

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Check if build script exists
    if os.path.exists(script_name):
        print(f"Running platform-specific build script: {script_name}")
        os.chmod(script_name, 0o755)
        return run_command(script_name)
    else:
        # Fallback to direct PyInstaller build
        print("Platform-specific script not found, using direct PyInstaller build...")
        return build_with_pyinstaller(output_dir)

def build_with_pyinstaller(output_dir):
    """Build using PyInstaller directly"""

    print("Building with PyInstaller...")
    cmd = [
        "python", "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "NSO-GameCube-Controller-Pairing-App",
        "--distpath", output_dir,
        "--paths", "src",
        "src/gc_controller/__main__.py"
    ]
    cmd = " ".join(cmd)

    return run_command(cmd)

def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")

    # Check Python version
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required")
        return False

    # Check if PyInstaller is available
    try:
        import PyInstaller
        print(f"PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("Installing PyInstaller...")
        if not run_command("pip install pyinstaller"):
            print("Failed to install PyInstaller")
            return False

    # Check main dependencies
    required_packages = ["tkinter", "threading", "json"]
    optional_packages = ["hid", "usb"]

    for package in required_packages:
        try:
            __import__(package)
            print(f"  {package}")
        except ImportError:
            print(f"  {package} - Required dependency missing")
            return False

    for package in optional_packages:
        try:
            __import__(package)
            print(f"  {package}")
        except ImportError:
            print(f"  {package} - Optional dependency missing (some features may not work)")

    return True

def main():
    """Main build function"""
    print("NSO GameCube Controller Pairing App - Build Script")
    print("=" * 50)

    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Check dependencies
    if not check_dependencies():
        print("Dependency check failed. Please install required packages.")
        return 1

    # Build executable
    if build_executable():
        print("\n" + "=" * 50)
        print("Build completed successfully!")

        output_dir = "dist/macos"

        if os.path.exists(output_dir):
            print(f"Executable location: {os.path.abspath(output_dir)}")
            files = os.listdir(output_dir)
            print(f"Files created: {files}")

        print("\nNext steps:")
        print("1. Test the executable on a clean system")
        print("2. Check that all features work correctly")
        print("3. Grant USB permissions if needed")

        return 0
    else:
        print("\nBuild failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
