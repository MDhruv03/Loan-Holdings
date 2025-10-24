"""
Verification script to check project setup
"""
import sys
from pathlib import Path

print("🔍 Verifying Loan Tracker Setup...\n")

# Check Python version
print(f"✓ Python version: {sys.version.split()[0]}")

# Check directory structure
project_root = Path(__file__).parent
checks = {
    "app directory": project_root / "app",
    "app/models": project_root / "app" / "models",
    "app/routers": project_root / "app" / "routers",
    "app/services": project_root / "app" / "services",
    "templates": project_root / "templates",
    "templates/borrowers": project_root / "templates" / "borrowers",
    "templates/holdings": project_root / "templates" / "holdings",
    "static": project_root / "static",
    "static/style.css": project_root / "static" / "style.css",
    "requirements.txt": project_root / "requirements.txt",
}

all_good = True
for name, path in checks.items():
    if path.exists():
        print(f"✓ {name}")
    else:
        print(f"✗ {name} - MISSING")
        all_good = False

# Check key files
key_files = [
    "app/main.py",
    "app/config.py",
    "app/database.py",
    "app/models/borrower.py",
    "app/models/holder.py",
    "app/routers/auth.py",
    "app/routers/borrowers.py",
    "app/routers/holdings.py",
    "templates/login.html",
    "templates/base.html",
]

print("\n📄 Key Files:")
for file in key_files:
    filepath = project_root / file
    if filepath.exists():
        print(f"✓ {file}")
    else:
        print(f"✗ {file} - MISSING")
        all_good = False

# Try importing modules
print("\n📦 Checking Dependencies:")
try:
    import fastapi
    print(f"✓ fastapi {fastapi.__version__}")
except ImportError:
    print("✗ fastapi - NOT INSTALLED")
    all_good = False

try:
    import uvicorn
    print(f"✓ uvicorn")
except ImportError:
    print("✗ uvicorn - NOT INSTALLED")
    all_good = False

try:
    import sqlmodel
    print(f"✓ sqlmodel")
except ImportError:
    print("✗ sqlmodel - NOT INSTALLED")
    all_good = False

try:
    import jinja2
    print(f"✓ jinja2 {jinja2.__version__}")
except ImportError:
    print("✗ jinja2 - NOT INSTALLED")
    all_good = False

print("\n" + "="*60)
if all_good:
    print("✅ All checks passed! Ready to run.")
    print("\nTo start the application:")
    print("  python -m app.main")
    print("  OR")
    print("  python run.py")
    print("\nThen open: http://localhost:8000")
    print("Login: admin / admin123")
else:
    print("⚠️  Some checks failed. Please install dependencies:")
    print("  pip install -r requirements.txt")

print("="*60)
