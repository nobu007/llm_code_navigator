from fastapi import APIRouter
import importlib
from pathlib import Path

api_router = APIRouter()

# endpoints ディレクトリのパスを取得
endpoints_path = Path(__file__).parent / "endpoints"

# endpoints ディレクトリ内のすべての .py ファイルをループ
for file in endpoints_path.glob("*.py"):
    if file.name != "__init__.py":
        # ファイル名からモジュール名を生成 (例: "files.py" -> "app.api.endpoints.files")
        module_name = f"app.api.endpoints.{file.stem}"

        # モジュールを動的にインポート
        module = importlib.import_module(module_name)

        # モジュール内の 'router' オブジェクトを探す
        if hasattr(module, 'router'):
            # ルーターをインクルード
            api_router.include_router(
                module.router,
                prefix=f"/{file.stem}",
                tags=[file.stem]
            )
            print(f"Included router from {module_name}")
        else:
            print(f"No router found in {module_name}")

print("All routers have been included.")