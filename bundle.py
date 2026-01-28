import os

# ====== CẤU HÌNH ======
CODE_OUTPUT_FILE = "project_code.txt"
TREE_OUTPUT_FILE = "project_tree.txt"

# Extension được phép xuất nội dung
ALLOWED_EXTENSIONS = {
    ".py", ".jsx", ".js", ".css", ".html",
    ".json", ".yml", ".yaml", ".md", ".txt"
}

# Thư mục loại trừ hoàn toàn
EXCLUDE_DIRS = {
    "venv",
    "node_modules",
    ".git",
    "__pycache__",
    ".pytest_cache",
    "dist",
    "build",
}

# File loại trừ
EXCLUDE_FILES = {
    ".DS_Store",
    ".gitignore",
}

# =====================


def should_exclude_file(filename: str) -> bool:
    if filename in EXCLUDE_FILES:
        return True
    if filename.startswith(".env"):
        return True
    return False


def export_project_code():
    with open(CODE_OUTPUT_FILE, "w", encoding="utf-8") as outfile:
        for root, dirs, files in os.walk("."):
            # Loại thư mục rác đúng cách
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

            for file in files:
                if should_exclude_file(file):
                    continue

                if any(file.endswith(ext) for ext in ALLOWED_EXTENSIONS):
                    full_path = os.path.join(root, file)

                    outfile.write("\n" + "=" * 30 + "\n")
                    outfile.write(f"FILE: {full_path}\n")
                    outfile.write("=" * 30 + "\n")

                    try:
                        with open(full_path, "r", encoding="utf-8", errors="ignore") as infile:
                            outfile.write(infile.read())
                    except Exception as e:
                        outfile.write(f"\n[ERROR READING FILE]: {e}\n")

    print(f"✅ Đã xuất toàn bộ code + config vào: {CODE_OUTPUT_FILE}")


def export_project_tree():
    lines = []

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        level = root.replace(".", "").count(os.sep)
        indent = "│   " * level

        folder_name = os.path.basename(root) if root != "." else os.path.abspath(".")
        lines.append(f"{indent}├── {folder_name}/")

        sub_indent = "│   " * (level + 1)
        for file in files:
            if should_exclude_file(file):
                continue
            lines.append(f"{sub_indent}├── {file}")

    with open(TREE_OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✅ Đã xuất cây thư mục (đã lọc) vào: {TREE_OUTPUT_FILE}")


def main():
    export_project_code()
    export_project_tree()
    print("\n🎉 Hoàn tất: đã tạo 2 file (CODE + TREE)")


if __name__ == "__main__":
    main()
