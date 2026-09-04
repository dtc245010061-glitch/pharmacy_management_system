import os
import sys
from pathlib import Path
from datetime import datetime

# 1. Định vị thư mục gốc và thư mục backend
root_dir = Path(__file__).resolve().parent.parent
backend_dir = root_dir / "backend"

# Thêm backend vào sys.path để import được module app lúc runtime
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Tải biến môi trường từ backend/.env nếu có
try:
    from dotenv import load_dotenv
    load_dotenv(backend_dir / ".env")
except ImportError:
    pass

# 2. Import FastAPI app
try:
    from app.main import app  # type: ignore
    from fastapi.routing import APIRoute
except Exception as e:
    print(f"[LỖI] Không thể nạp ứng dụng FastAPI từ app.main: {e}")
    print("Gợi ý: Hãy kích hoạt môi trường ảo (virtualenv) trước khi chạy script:")
    print("   .venv\\Scripts\\activate  (trên Windows)")
    print("   source .venv/bin/activate (trên Linux/macOS)")
    sys.exit(1)

def get_all_dependencies(dependant):
    """Lấy đệ quy toàn bộ danh sách dependency gắn trên route."""
    deps = list(dependant.dependencies)
    for d in list(deps):
        deps.extend(get_all_dependencies(d))
    return deps

def extract_rbac(route: APIRoute) -> str:
    """Trích xuất danh sách vai trò được phép từ dependency require_roles."""
    roles = []
    is_auth_required = False
    all_deps = [route.dependant] + get_all_dependencies(route.dependant)

    for dep in all_deps:
        callable_obj = getattr(dep, "call", None)
        if not callable_obj:
            continue

        # 1. Kiểm tra thuộc tính gắn trực tiếp (nếu có)
        if hasattr(callable_obj, "allowed_roles"):
            for r in callable_obj.allowed_roles:
                roles.append(r.value if hasattr(r, "value") else str(r))

        # 2. Quét biến closure của hàm checker (nơi lưu danh sách roles truyền vào require_roles)
        if hasattr(callable_obj, "__closure__") and callable_obj.__closure__:
            for cell in callable_obj.__closure__:
                try:
                    val = cell.cell_contents
                    if isinstance(val, (list, tuple, set)):
                        for item in val:
                            if hasattr(item, "value"):
                                roles.append(str(item.value))
                            elif isinstance(item, str) and item in ["manager", "pharmacist", "cashier", "admin"]:
                                roles.append(item)
                except Exception:
                    pass

        # 3. Kiểm tra xem có dependency xác thực danh tính hay không
        func_name = getattr(callable_obj, "__name__", "")
        if "current_user" in func_name or "auth" in func_name.lower():
            is_auth_required = True

    unique_roles = []
    for r in roles:
        if r not in unique_roles:
            unique_roles.append(r)

    if unique_roles:
        return ", ".join(f"`{r}`" for r in unique_roles)
    if is_auth_required:
        return "Đã đăng nhập (Tất cả vai trò)"
    return "Công khai (Public)"

def generate_api_map():
    output_file = root_dir / "API-MAP.md"
    grouped_routes = {}
    total_endpoints = 0
    protected_endpoints = 0

    for route in app.routes:
        if isinstance(route, APIRoute):
            if route.path in ["/docs", "/redoc", "/openapi.json"]:
                continue

            total_endpoints += 1
            methods = [m for m in route.methods if m not in {"HEAD", "OPTIONS"}]
            method_str = ", ".join(methods)
            
            tag = route.tags[0] if route.tags else "General"
            
            summary = route.summary or ""
            if not summary and route.endpoint.__doc__:
                summary = route.endpoint.__doc__.strip().split("\n")[0]
            if not summary:
                summary = route.name.replace("_", " ").capitalize()

            roles_str = extract_rbac(route)
            if "Công khai" not in roles_str:
                protected_endpoints += 1

            if tag not in grouped_routes:
                grouped_routes[tag] = []

            grouped_routes[tag].append({
                "method": method_str,
                "path": route.path,
                "summary": summary,
                "roles": roles_str
            })

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# BẢN ĐỒ API & PHÂN QUYỀN (API MAP & RBAC)\n",
        f"> Tự động sinh bởi script `scripts/generate_api_map.py`.",
        f"> Thời gian cập nhật: `{now_str}`\n",
        "## 📊 Thống kê tổng quan",
        f"- **Tổng số API Endpoints:** `{total_endpoints}`",
        f"- **Endpoints được bảo vệ bởi RBAC / Auth:** `{protected_endpoints}`",
        f"- **Endpoints công khai (Public):** `{total_endpoints - protected_endpoints}`\n",
        "---"
    ]

    for tag, routes in grouped_routes.items():
        lines.append(f"\n### 📌 Phân hệ: {tag}")
        lines.append("| Phương thức | Đường dẫn API | Chức năng / Mô tả | Phân quyền truy cập |")
        lines.append("| :--- | :--- | :--- | :--- |")
        for r in routes:
            method_badge = f"`{r['method']}`"
            lines.append(f"| {method_badge} | `{r['path']}` | {r['summary']} | {r['roles']} |")

    lines.append("\n---\n*Tài liệu tự động đồng bộ từ cấu hình router thực tế của Backend.*")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"[OK] Đã quét thành công {total_endpoints} API endpoints.")
    print(f"[OK] Đã xuất bản đồ API vào file: {output_file.name}")

if __name__ == "__main__":
    generate_api_map()