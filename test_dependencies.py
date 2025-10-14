import sys

packages = [
    ("fastapi", "Web Framework"),
    ("uvicorn", "ASGI Server"),
    ("requests", "HTTP Client"),
    ("dotenv", "Environment Variables"),
    ("pydantic", "Data Validation"),
    ("multipart", "File Upload Handler"),
    ("aiofiles", "Async File Operations"),
    ("google.generativeai", "Google Gemini API"),
    ("httpx", "Async HTTP Client"),
]

print("🔍 Testing Dependencies...\n")

all_ok = True
for package, description in packages:
    try:
        __import__(package)
        print(f"✅ {package} ({description}) - OK")
    except ImportError:
        print(f"❌ {package} ({description}) - FAILED")
        all_ok = False

if all_ok:
    print("\n🎉 All dependencies installed successfully!")
else:
    print("\n⚠️ Some packages failed. Run: pip install -r requirements.txt")
