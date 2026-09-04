import os
from pathlib import Path

# Các thư mục cần loại bỏ khi quét
IGNORE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    ".vscode",
    ".idea",
    ".pytest_cache",
}

# Các file không cần đưa vào sơ đồ
IGNORE_FILES = {
    ".DS_Store",
    "Thumbs.db",
    ".env",
    "*.pyc",
    "codebase-map.md",  # Không tự lồng chính nó
}

def build_tree(dir_path: Path, prefix: str = "") -> list:
    lines = []
    try:
        entries = sorted(
            [e for e in dir_path.iterdir() if e.name not in IGNORE_DIRS and not e.name.endswith(".pyc")],
            key=lambda s: (not s.is_dir(), s.name.lower())
        )
    except PermissionError:
        return lines

    for index, entry in enumerate(entries):
        is_last = (index == len(entries) - 1)
        connector = "└── " if is_last else "├── "
        sub_prefix = "    " if is_last else "│   "

        if entry.is_dir():
            lines.append(f"{prefix}{connector}{entry.name}/")
            lines.extend(build_tree(entry, prefix + sub_prefix))
        else:
            if entry.name not in IGNORE_FILES:
                lines.append(f"{prefix}{connector}{entry.name}")
    return lines

def update_codebase_map():
    # Thư mục gốc là thư mục cha của scripts/
    root_dir = Path(__file__).resolve().parent.parent
    output_file = root_dir / "codebase-map.md"

    tree_lines = [f"{root_dir.name}/"]
    tree_lines.extend(build_tree(root_dir))

    content = (
        "# CODEBASE MAP\n\n"
        "> Tự động sinh bởi script `scripts/update_map.py`.\n\n"
        "```text\n"
        + "\n".join(tree_lines)
        + "\n```\n"
    )

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[OK] Đã cập nhật cấu trúc toàn bộ dự án vào: {output_file.name}")

if __name__ == "__main__":
    update_codebase_map()