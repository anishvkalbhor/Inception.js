"""
Pre-flight check before starting the system
Ensures all dependencies are installed and configured
"""
import sys
import subprocess
import os
from pathlib import Path

def check_command(cmd, name):
    """Check if a command exists"""
    try:
        subprocess.run(cmd, capture_output=True, check=True, shell=True)
        print(f"✅ {name} is installed")
        return True
    except:
        print(f"❌ {name} is NOT installed")
        return False

def check_ollama_models():
    """Check if required Ollama models are downloaded"""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout
        
        has_llm = "qwen2.5:3b" in output
        has_embed = "bge-m3" in output
        
        if has_llm:
            print("✅ Ollama LLM model (qwen2.5:3b) is downloaded")
        else:
            print("❌ Ollama LLM model (qwen2.5:3b) NOT downloaded")
            print("   Run: ollama pull qwen2.5:3b")
        
        if has_embed:
            print("✅ Ollama embedding model (bge-m3) is downloaded")
        else:
            print("❌ Ollama embedding model (bge-m3) NOT downloaded")
            print("   Run: ollama pull bge-m3")
        
        return has_llm and has_embed
    except:
        print("❌ Cannot check Ollama models (Ollama not running?)")
        return False

def check_docker_images():
    """Check if required Docker images are pulled"""
    try:
        result = subprocess.run(
            ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"],
            capture_output=True,
            text=True,
            check=True
        )
        images = result.stdout
        
        required = [
            "mongo:7.0",
            "milvusdb/milvus:v2.4.6",
            "quay.io/coreos/etcd:v3.5.5",
            "minio/minio:latest"
        ]
        
        all_present = True
        for img in required:
            if img in images:
                print(f"✅ Docker image {img}")
            else:
                print(f"❌ Docker image {img} NOT pulled")
                all_present = False
        
        return all_present
    except:
        print("❌ Cannot check Docker images")
        return False

def main():
    print("=" * 60)
    print("VICTOR OFFLINE SYSTEM - PRE-FLIGHT CHECK")
    print("=" * 60)
    print()
    
    all_ok = True
    
    # Check Python
    print("[System Requirements]")
    all_ok &= check_command("python --version", "Python")
    all_ok &= check_command("node --version", "Node.js")
    all_ok &= check_command("npm --version", "NPM")
    all_ok &= check_command("docker --version", "Docker")
    all_ok &= check_command("docker-compose --version", "Docker Compose")
    all_ok &= check_command("ollama --version", "Ollama")
    
    print()
    print("[Ollama Models]")
    all_ok &= check_ollama_models()
    
    print()
    print("[Docker Images]")
    all_ok &= check_docker_images()
    
    print()
    print("=" * 60)
    if all_ok:
        print("🎉 ALL CHECKS PASSED!")
        print("✅ System is ready for OFFLINE operation")
        print()
        print("To start the system, run: start-offline.bat")
    else:
        print("⚠️  SOME CHECKS FAILED")
        print("Please install missing dependencies first")
    print("=" * 60)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())