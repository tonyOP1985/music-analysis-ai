#!/usr/bin/env python3
"""
Diagnostic script to find and test Audiveris installation
"""

import subprocess
import os
from pathlib import Path

def find_audiveris():
    """Find Audiveris in the Docker container"""
    print("🔍 Searching for Audiveris installation...")
    
    # Check common locations
    common_paths = [
        "/audiveris",
        "/opt/audiveris", 
        "/usr/local/audiveris",
        "/home/audiveris",
        "/app/audiveris"
    ]
    
    print("\n📂 Checking common directories:")
    for path in common_paths:
        if Path(path).exists():
            print(f"✅ Found: {path}")
            # List contents
            try:
                contents = list(Path(path).iterdir())
                print(f"   Contents: {[str(p.name) for p in contents[:10]]}")
            except:
                print(f"   (Cannot list contents)")
        else:
            print(f"❌ Not found: {path}")
    
    # Search for JAR files
    print("\n🔍 Searching for JAR files...")
    try:
        result = subprocess.run(['find', '/', '-name', '*.jar', '-type', 'f'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            jar_files = [line for line in result.stdout.split('\n') 
                        if 'audiveris' in line.lower()]
            if jar_files:
                print("✅ Found Audiveris JAR files:")
                for jar in jar_files:
                    print(f"   {jar}")
            else:
                print("❌ No Audiveris JAR files found")
                print("All JAR files found:")
                all_jars = result.stdout.strip().split('\n')[:10]
                for jar in all_jars:
                    if jar:
                        print(f"   {jar}")
    except Exception as e:
        print(f"❌ JAR search failed: {e}")
    
    # Check system commands
    print("\n💻 Checking system commands:")
    commands = ['audiveris', 'java']
    for cmd in commands:
        try:
            result = subprocess.run(['which', cmd], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {cmd}: {result.stdout.strip()}")
                
                # Test java version
                if cmd == 'java':
                    version_result = subprocess.run(['java', '-version'], 
                                                  capture_output=True, text=True)
                    if version_result.returncode == 0:
                        version = version_result.stderr.split('\n')[0]
                        print(f"   Version: {version}")
                        
            else:
                print(f"❌ {cmd}: not found in PATH")
        except Exception as e:
            print(f"❌ {cmd}: error checking - {e}")
    
    # Check environment variables
    print("\n🌍 Environment variables:")
    env_vars = ['JAVA_HOME', 'PATH', 'AUDIVERIS_HOME']
    for var in env_vars:
        value = os.environ.get(var, 'Not set')
        print(f"   {var}: {value}")
    
    print("\n" + "="*50)

def test_audiveris():
    """Test Audiveris functionality"""
    print("🧪 Testing Audiveris...")
    
    # Try to run Audiveris help
    test_commands = [
        ['audiveris', '-help'],
        ['java', '-jar', '/audiveris/lib/audiveris.jar', '-help'],
        ['java', '-jar', '/opt/audiveris/lib/audiveris.jar', '-help'],
        ['java', '-jar', '/home/audiveris/audiveris/lib/audiveris.jar', '-help']
    ]
    
    for cmd in test_commands:
        try:
            print(f"\n🔧 Trying: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ Success!")
                print(f"Output preview: {result.stdout[:200]}...")
                return True
            else:
                print(f"❌ Failed with return code {result.returncode}")
                if result.stderr:
                    print(f"Error: {result.stderr[:200]}")
        except FileNotFoundError:
            print("❌ Command not found")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return False

if __name__ == "__main__":
    print("🐳 Audiveris Docker Container Diagnostic")
    print("="*50)
    
    find_audiveris()
    success = test_audiveris()
    
    if success:
        print("\n🎉 Audiveris appears to be working!")
    else:
        print("\n😞 Could not get Audiveris working")
        print("This information will help debug the setup.")