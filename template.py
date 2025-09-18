import os
from pathlib import Path
import logging

# Configure logging to display informational messages
logging.basicConfig(level=logging.INFO, format='[%(asctime)s]: %(message)s:')

project_name = "saas_agent"

# List of files and directories to be created
list_of_files = [
    ".github/workflows/.gitkeep",
    f"app/__init__.py",
    f"app/main/__init__.py",
    f"app/main/routes.py",
    f"app/auth/__init__.py",
    f"app/auth/routes.py",
    f"app/agents/__init__.py",
    f"app/agents/routes.py",
    f"app/models.py",
    f"app/services.py",
    f"app/static/css/style.css",
    f"app/static/js/main.js",
    f"app/templates/base.html",
    f"app/templates/index.html",
    f"app/templates/chat.html",
    f"app/templates/login.html",
    "config.py",
    "run.py",
    "requirements.txt",
    ".gitignore",
    "README.md"
]

# Loop through the list to create the files and directories
for filepath in list_of_files:
    filepath = Path(filepath)
    filedir, filename = os.path.split(filepath)

    # Create the directory if it doesn't exist
    if filedir != "":
        os.makedirs(filedir, exist_ok=True)
        logging.info(f"Creating directory: {filedir} for the file: {filename}")

    # Create the file if it doesn't exist or is empty
    if (not os.path.exists(filepath)) or (os.path.getsize(filepath) == 0):
        with open(filepath, 'w') as f:
            pass  # Create an empty file
            logging.info(f"Creating empty file: {filepath}")
    else:
        logging.info(f"{filename} already exists")
