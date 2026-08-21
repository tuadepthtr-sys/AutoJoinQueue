import hashlib
import json
import os
import sys
import subprocess
import urllib.request
import urllib.error

KEYS_FILE = "keys.json"

try:
    import winreg
except ImportError:
    winreg = None

class HWIDManager:
    @staticmethod
    def get_raw_hardware_info():
        info_parts = []

        if sys.platform == "win32" and winreg:
            # 1. MachineGuid from Windows Registry (64-bit view)
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography", 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
                guid, _ = winreg.QueryValueEx(key, "MachineGuid")
                winreg.CloseKey(key)
                if guid:
                    info_parts.append(f"GUID:{guid}")
            except Exception:
                pass

            # 2. System BIOS / BaseBoard info from Windows Registry
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\BIOS", 0, winreg.KEY_READ)
                date, _ = winreg.QueryValueEx(key, "BIOSReleaseDate")
                vendor, _ = winreg.QueryValueEx(key, "SystemManufacturer")
                winreg.CloseKey(key)
                info_parts.append(f"BIOS:{vendor}|{date}")
            except Exception:
                pass

            # 3. CPU info from Windows Registry
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0", 0, winreg.KEY_READ)
                proc_id, _ = winreg.QueryValueEx(key, "Identifier")
                winreg.CloseKey(key)
                info_parts.append(f"CPU:{proc_id}")
            except Exception:
                pass
        elif sys.platform == "darwin":
            # macOS Hardware Identification
            try:
                cmd = "ioreg -rd1 -c IOPlatformExpertDevice | grep -E 'IOPlatformUUID|IOPlatformSerialNumber'"
                out = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode('utf-8')
                for line in out.strip().splitlines():
                    if "IOPlatformUUID" in line:
                        uuid_val = line.split("=")[-1].strip().strip('"')
                        info_parts.append(f"UUID:{uuid_val}")
                    elif "IOPlatformSerialNumber" in line:
                        serial_val = line.split("=")[-1].strip().strip('"')
                        info_parts.append(f"SERIAL:{serial_val}")
            except Exception:
                pass

            if not info_parts:
                try:
                    import uuid
                    info_parts.append(f"MAC_NODE:{uuid.getnode()}")
                except Exception:
                    pass

        if not info_parts:
            host_name = os.environ.get('COMPUTERNAME') or os.environ.get('HOSTNAME') or 'UNKNOWN'
            info_parts.append(f"HOST:{host_name}")

        raw_str = "|".join(info_parts)
        return raw_str

    @classmethod
    def generate_hwid(cls):
        raw_info = cls.get_raw_hardware_info()
        sha = hashlib.sha256(raw_info.encode('utf-8')).hexdigest().upper()
        formatted = "-".join([sha[i:i+4] for i in range(0, 32, 4)])
        return formatted

    @classmethod
    def get_keys_file_paths(cls):
        import sys
        candidate_paths = []
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        candidate_paths.append(os.path.join(base_dir, KEYS_FILE))
        candidate_paths.append(os.path.join(os.path.dirname(base_dir), KEYS_FILE))
        candidate_paths.append(os.path.join(os.getcwd(), KEYS_FILE))

        # Remove duplicates while preserving order
        unique_paths = []
        for p in candidate_paths:
            if p not in unique_paths:
                unique_paths.append(p)
        return unique_paths

    @classmethod
    def load_keys_data(cls, keys_url=""):
        combined_keys = {}

        # 1. Load local keys.json first
        for path in cls.get_keys_file_paths():
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        ldata = json.load(f)
                        if isinstance(ldata, dict) and "valid_keys" in ldata:
                            combined_keys.update(ldata["valid_keys"])
                except Exception:
                    pass

        # 2. Fetch remote keys if URL is provided
        if keys_url and keys_url.startswith("http"):
            try:
                import time
                import base64
                url_with_cb = f"{keys_url}{'&' if '?' in keys_url else '?'}t={int(time.time())}"
                req = urllib.request.Request(
                    url_with_cb,
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Accept': 'application/json'}
                )
                with urllib.request.urlopen(req, timeout=5) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    if isinstance(data, dict) and "content" in data and "encoding" in data:
                        raw_bytes = base64.b64decode(data["content"].encode('utf-8'))
                        data = json.loads(raw_bytes.decode('utf-8'))
                    if isinstance(data, dict) and "valid_keys" in data:
                        combined_keys.update(data["valid_keys"])
            except Exception as e:
                print(f"[HWID] Error fetching remote keys: {e}")

        return {"valid_keys": combined_keys}

    @classmethod
    def save_keys_data(cls, data):
        paths = cls.get_keys_file_paths()
        success = False
        for path in paths:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                success = True
            except Exception as e:
                print(f"[HWID] Error saving keys to {path}: {e}")
        return success

    @classmethod
    def activate_key(cls, license_key, config_mgr):
        current_hwid = cls.generate_hwid()
        key_str = license_key.strip().upper()
        if not key_str:
            return {"success": False, "message": "Vui lòng nhập mã Key!"}

        hwid_settings = config_mgr.config.get("hwid_settings", {})
        keys_url = hwid_settings.get("keys_url", "").strip() or hwid_settings.get("whitelist_url", "").strip()

        # Try remote activation if URL is configured
        if keys_url and keys_url.startswith("http"):
            try:
                activate_url = keys_url.replace("/api/verify", "/api/activate").replace("/keys.json", "/api/activate")
                if not activate_url.endswith("/api/activate"):
                    activate_url = keys_url
                
                payload = json.dumps({"license_key": key_str, "hwid": current_hwid}).encode('utf-8')
                req = urllib.request.Request(
                    activate_url,
                    data=payload,
                    headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
                )
                with urllib.request.urlopen(req, timeout=5) as resp:
                    res_data = json.loads(resp.read().decode('utf-8'))
                    if res_data.get("success"):
                        config_mgr.config["license_key"] = key_str
                        config_mgr.save_config(config_mgr.config)
                        return res_data
            except Exception as e:
                print(f"[HWID] Remote activation failed, falling back to local check: {e}")

        # Local fallback activation logic
        keys_data = cls.load_keys_data(keys_url)
        valid_keys = keys_data.get("valid_keys", {})

        if key_str not in valid_keys:
            return {"success": False, "message": "Mã License Key không tồn tại hoặc không hợp lệ!"}

        key_info = valid_keys[key_str]
        bound_hwid = key_info.get("hwid", "").strip()

        if bound_hwid and bound_hwid != current_hwid:
            return {"success": False, "message": "Mã Key này đã được kích hoạt trên một máy tính khác!"}

        # Bind Key to current HWID
        key_info["hwid"] = current_hwid
        key_info["used"] = True
        valid_keys[key_str] = key_info
        cls.save_keys_data({"valid_keys": valid_keys})

        # Save active key to config
        config_mgr.config["license_key"] = key_str
        config_mgr.save_config(config_mgr.config)

        return {
            "success": True,
            "message": f"Kích hoạt thành công License Key: {key_str}!"
        }

    @classmethod
    def verify_hwid(cls, config):
        current_hwid = cls.generate_hwid()
        
        hwid_settings = config.get("hwid_settings", {})
        enabled = hwid_settings.get("enabled", True)
        
        if not enabled:
            return {
                "authorized": True,
                "hwid": current_hwid,
                "message": "HWID verification is disabled."
            }

        whitelist_url = hwid_settings.get("whitelist_url", "").strip()
        keys_url = hwid_settings.get("keys_url", "").strip() or whitelist_url
        local_whitelist = hwid_settings.get("allowed_hwids", [])

        # 1. Check direct HWID whitelist
        if current_hwid in local_whitelist or "*" in local_whitelist:
            return {
                "authorized": True,
                "hwid": current_hwid,
                "message": "HWID authorized locally."
            }

        # 2. Check saved license_key in config
        active_key = config.get("license_key", "").strip().upper()
        if active_key:
            keys_data = cls.load_keys_data(keys_url)
            valid_keys = keys_data.get("valid_keys", {})
            if active_key in valid_keys:
                bound_hwid = valid_keys[active_key].get("hwid", "").strip()
                if bound_hwid == current_hwid:
                    return {
                        "authorized": True,
                        "hwid": current_hwid,
                        "message": f"License Key '{active_key}' active."
                    }

        # 3. Check remote whitelist URL if configured
        if whitelist_url and whitelist_url.startswith("http"):
            try:
                req = urllib.request.Request(
                    whitelist_url,
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                )
                with urllib.request.urlopen(req, timeout=5) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    allowed = []
                    if isinstance(data, list):
                        allowed = data
                    elif isinstance(data, dict):
                        allowed = data.get("whitelisted_hwids", [])
                        if isinstance(allowed, dict):
                            allowed = list(allowed.keys())

                    if current_hwid in allowed or "*" in allowed:
                        return {
                            "authorized": True,
                            "hwid": current_hwid,
                            "message": "HWID authorized via online whitelist."
                        }
            except Exception as e:
                print(f"[HWID] Error fetching remote whitelist: {e}")

        # If not authorized
        return {
            "authorized": False,
            "hwid": current_hwid,
            "message": "Mã phần cứng (HWID) hoặc License Key chưa được kích hoạt!"
        }

if __name__ == "__main__":
    hwid = HWIDManager.generate_hwid()
    print(f"Generated HWID: {hwid}")
