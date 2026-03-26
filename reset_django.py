import os
import sys
import subprocess
import shutil
import time
import gc

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_DIR = os.path.join(BASE_DIR, "env")
PYTHON = "python"
USERNAME = "<your-username-here>"  # Replace with your desired username
PASSWORD = "<your-password-here>"  # Replace with your desired password
EMAIL = "<your-email-here>"      # Replace with your desired email


def run(cmd):
    print(f"\n👉 {cmd}")
    result = subprocess.run(
        cmd,
        shell=True,
        text=True,
        capture_output=True
    )

    if result.stdout:
        print(result.stdout)

    if result.returncode != 0:
        print("❌ COMMAND FAILED")
        print("STDERR:")
        print(result.stderr)
        sys.exit(1)



def remove_env():
    if os.path.exists(ENV_DIR):
        print("🔥 Removing env folder...")
        shutil.rmtree(ENV_DIR)


def remove_db():
    db = os.path.join(BASE_DIR, "db.sqlite3")
    if os.path.exists(db):
        print("🗑 Removing db.sqlite3...")
        gc.collect()
        time.sleep(1)
        try:
            os.remove(db)
        except PermissionError:
            print("❌ Close programs using db.sqlite3")
            sys.exit(1)


def remove_migrations():
    print("🧹 Removing migrations...")
    for root, dirs, files in os.walk(BASE_DIR):
        if root.endswith("migrations"):
            for f in files:
                if f != "__init__.py" and f.endswith(".py"):
                    os.remove(os.path.join(root, f))


def create_env():
    print("🐍 Creating virtual environment...")
    run(f"{PYTHON} -m venv env")


def install_requirements():
    pip = os.path.join(ENV_DIR, "Scripts", "pip")
    req = os.path.join(BASE_DIR, "requirements.txt")

    if os.path.exists(req):
        print("📦 Installing from requirements.txt...")
        run(f"{pip} install -r requirements.txt")
    else:
        print("📦 Installing Django + widget-tweaks...")
        run(f"{pip} install django django-widget-tweaks")


def migrate():
    python = os.path.join(ENV_DIR, "Scripts", "python")
    run(f"{python} manage.py makemigrations")
    run(f"{python} manage.py migrate")


def create_superuser():
    python = os.path.join(ENV_DIR, "Scripts", "python")
    print("👤 Creating superuser...")
    cmd = (
        f"{python} manage.py shell -c "
        "\"from django.contrib.auth import get_user_model;"
        "User=get_user_model();"
        "User.objects.filter(username={USERNAME}).exists() or "
        "User.objects.create_superuser('{USERNAME}','{EMAIL}','{PASSWORD}')\""
    )
    run(cmd)


if __name__ == "__main__":
    remove_env()
    remove_db()
    remove_migrations()

    create_env()
    install_requirements()
    migrate()
    create_superuser()

    print("\n✅ FULL DJANGO RESET COMPLETED SUCCESSFULLY")
