import subprocess
import re
from pathlib import Path
from datetime import datetime

# Định vị thư mục gốc dự án
root_dir = Path(__file__).resolve().parent.parent
output_file = root_dir / "CHANGELOG.md"

# Bản đồ phân loại Conventional Commits
COMMIT_CATEGORIES = {
    "feat": "✨ Tính năng mới (Features)",
    "fix": "🐛 Sửa lỗi (Bug Fixes)",
    "refactor": "♻️ Tái cấu trúc mã nguồn (Refactoring)",
    "docs": "📝 Tài liệu (Documentation)",
    "perf": "⚡ Tối ưu hiệu năng (Performance)",
    "test": "🧪 Kiểm thử (Tests)",
    "chore": "🔧 Cấu hình & Bảo trì (Chores)",
}

def get_git_commits():
    """Lấy danh sách commit từ git log với định dạng: hash|ngày|tác giả|tiêu đề"""
    cmd = ["git", "log", "--pretty=format:%h|%ad|%an|%s", "--date=short"]
    try:
        result = subprocess.run(
            cmd,
            cwd=root_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True
        )
        return result.stdout.strip().split("\n")
    except subprocess.CalledProcessError as e:
        print(f"[LỖI] Không thể đọc git log: {e}")
        return []
    except FileNotFoundError:
        print("[LỖI] Không tìm thấy lệnh git trong môi trường hệ thống.")
        return []

def parse_commit_message(msg: str):
    """Phân tích loại commit dựa trên tiền tố (conventional commits)"""
    pattern = r"^(\w+)(?:\((.*?)\))?:\s*(.*)$"
    match = re.match(pattern, msg.strip())
    if match:
        c_type = match.group(1).lower()
        scope = match.group(2)
        subject = match.group(3)
        return c_type, scope, subject
    return "other", None, msg.strip()

def generate_changelog():
    commit_lines = [c for c in get_git_commits() if c.strip()]
    if not commit_lines:
        print("[CẢNH BÁO] Chưa có commit nào trong repository để tạo changelog.")
        return

    # Nhóm commit theo ngày (Date)
    commits_by_date = {}
    total_commits = len(commit_lines)

    for line in commit_lines:
        parts = line.split("|", 3)
        if len(parts) < 4:
            continue
        commit_hash, commit_date, author, subject = parts
        c_type, scope, clean_msg = parse_commit_message(subject)

        if commit_date not in commits_by_date:
            commits_by_date[commit_date] = {}

        category_key = c_type if c_type in COMMIT_CATEGORIES else "other"
        if category_key not in commits_by_date[commit_date]:
            commits_by_date[commit_date][category_key] = []

        commits_by_date[commit_date][category_key].append({
            "hash": commit_hash,
            "scope": scope,
            "msg": clean_msg,
            "author": author
        })

    # Xây dựng nội dung Markdown
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# NHẬT KÝ THAY ĐỔI (CHANGELOG)\n",
        "> Tự động sinh bởi script `scripts/generate_changelog.py` từ lịch sử Git.",
        f"> Cập nhật lần cuối: `{now_str}`",
        f"> Tổng số bản ghi commits: `{total_commits}`\n",
        "---"
    ]

    for date_str, categories in commits_by_date.items():
        lines.append(f"\n## 📅 Ngày {date_str}\n")
        
        # Sắp xếp các danh mục quen thuộc lên trước
        sorted_cats = sorted(
            categories.keys(),
            key=lambda k: list(COMMIT_CATEGORIES.keys()).index(k) if k in COMMIT_CATEGORIES else 999
        )

        for cat in sorted_cats:
            cat_title = COMMIT_CATEGORIES.get(cat, "📌 Thay đổi khác (Other Changes)")
            lines.append(f"### {cat_title}")
            for c in categories[cat]:
                scope_prefix = f"**[{c['scope']}]** " if c['scope'] else ""
                lines.append(f"- {scope_prefix}{c['msg']} (`{c['hash']}` bởi *{c['author']}*)")
            lines.append("")

    lines.append("---\n*Nhật ký được trích xuất trực tiếp từ Git log của dự án.*")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"[OK] Đã quét thành công {total_commits} commits.")
    print(f"[OK] Đã xuất nhật ký vào file: {output_file.name}")

if __name__ == "__main__":
    generate_changelog()