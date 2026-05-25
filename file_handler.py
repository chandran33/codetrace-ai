import os
import zipfile
import shutil

SUPPORTED_EXTENSIONS = [
    ".py", ".js", ".jsx", ".ts", ".tsx",
    ".java", ".c", ".cpp", ".html", ".css", ".json", ".md"
]

IGNORE_FOLDERS = [
    "node_modules", ".git", "dist", "build",
    "__pycache__", ".venv", "venv"
]


def extract_zip(zip_path, extract_to):
    if os.path.exists(extract_to):
        shutil.rmtree(extract_to)

    os.makedirs(extract_to, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)


def is_supported_file(filename):
    return any(filename.endswith(ext) for ext in SUPPORTED_EXTENSIONS)


def read_project_files(project_path):
    files_data = []

    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_FOLDERS]

        for file in files:
            if is_supported_file(file):
                file_path = os.path.join(root, file)

                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    files_data.append({
                        "name": file,
                        "path": file_path,
                        "content": content
                    })

                except Exception:
                    pass

    return files_data


def create_code_summary(files_data, max_chars=12000):
    summary = ""

    for file in files_data:
        summary += f"\n\n--- FILE: {file['name']} ---\n"
        summary += file["content"][:2000]

        if len(summary) > max_chars:
            break

    return summary[:max_chars]


def get_readme_content(files_data):
    for file in files_data:
        if file["name"].lower() == "readme.md":
            return file["content"]

    return "README file not found."