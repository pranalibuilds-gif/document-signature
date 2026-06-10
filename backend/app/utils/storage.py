import os
import shutil
from pathlib import Path
from fastapi import UploadFile
from app.core.config import settings

class StorageService:
    def __init__(self, base_path: str = settings.STORAGE_BASE_PATH):
        self.base_path = Path(base_path)
        self._ensure_dirs()

    def _ensure_dirs(self):
        (self.base_path / "original").mkdir(parents=True, exist_ok=True)
        (self.base_path / "final").mkdir(parents=True, exist_ok=True)

    async def save_file(self, file: UploadFile, stored_name: str, sub_dir: str = "original") -> str:
        dest_path = self.base_path / sub_dir / stored_name

        with dest_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return str(dest_path)

    def delete_file(self, file_path: str):
        path = Path(file_path)
        if path.exists():
            path.unlink()

    def file_exists(self, file_path: str) -> bool:
        return Path(file_path).exists()
