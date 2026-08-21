import asyncio
import os
import queue
import sys
import time
import threading
import webview

from anti_capture import AntiCaptureManager
from config_manager import ConfigManager
from discord_queue import DiscordQueueEngine
from hwid_manager import HWIDManager
from token_extractor import TokenExtractor
from tray_manager import SystemTrayManager

class Api:
    def __init__(self, config_mgr, loop):
        self.config_mgr = config_mgr
        self.loop = loop
        self.log_queue = queue.Queue()
        self.status_queue = queue.Queue()
        self.engine = DiscordQueueEngine(
            loop=self.loop,
            log_callback=self.push_log,
            status_callback=self.push_status
        )
        self.tray = None

    def set_tray(self, tray):
        self.tray = tray

    def push_log(self, text, level="info"):
        self.log_queue.put({
            "sender": "Engine",
            "message": text,
            "level": level
        })

    def push_status(self, category, state, extra=None):
        self.status_queue.put({
            "category": category,
            "state": state,
            "extra": extra or {}
        })

    def get_logs(self):
        logs = []
        while not self.log_queue.empty():
            try:
                logs.append(self.log_queue.get_nowait())
            except queue.Empty:
                break
        return logs

    def get_statuses(self):
        statuses = []
        while not self.status_queue.empty():
            try:
                statuses.append(self.status_queue.get_nowait())
            except queue.Empty:
                break
        return statuses

    def get_config(self):
        return self.config_mgr.config

    def get_hwid_info(self):
        return HWIDManager.verify_hwid(self.config_mgr.config)

    def activate_license_key(self, key):
        res = HWIDManager.activate_key(key, self.config_mgr)
        if res.get("success"):
            self.push_log(f"🔑 {res.get('message')}", "success")
        else:
            self.push_log(f"❌ {res.get('message')}", "error")
        return res

    def save_config(self, config):
        success = self.config_mgr.save_config(config)
        if success:
            anti_ss = config.get("global_settings", {}).get("anti_screenshot", True)
            AntiCaptureManager.set_protection("Discord Queue Joiner", enable=anti_ss)
            self.push_log("Cấu hình đã được lưu thành công!", "success")
        else:
            self.push_log("Lỗi khi lưu file config.json", "error")
        return success

    def toggle_anti_screenshot(self, enabled):
        success = AntiCaptureManager.set_protection("Discord Queue Joiner", enable=enabled)
        if enabled:
            self.push_log("🔒 Đã BẬT tính năng Chống Chụp / Quay Màn Hình (Anti-Screenshot)!", "success")
        else:
            self.push_log("🔓 Đã TẮT tính năng Chống Chụp / Quay Màn Hình.", "warning")
        return {"success": success}

    def validate_token(self, token):
        future = asyncio.run_coroutine_threadsafe(self.engine.validate_token(token), self.loop)
        try:
            valid, info = future.result(timeout=5)
            return {
                "valid": valid,
                "username": info.get("username", ""),
                "avatar_url": info.get("avatar_url", ""),
                "message": info.get("message", "")
            }
        except Exception as e:
            return {"valid": False, "message": f"Lỗi check token: {e}"}

    def auto_detect_token(self):
        future = asyncio.run_coroutine_threadsafe(TokenExtractor.auto_detect_valid_token(), self.loop)
        try:
            info, err = future.result(timeout=8)
            if info:
                self.push_log(f"⚡ [AUTO-DETECT] {info['message']}", "success")
                return {
                    "success": True,
                    "token": info["token"],
                    "username": info["username"],
                    "avatar_url": info["avatar_url"],
                    "message": info["message"]
                }
            else:
                self.push_log(f"⚠️ [AUTO-DETECT] {err}", "warning")
                return {"success": False, "message": err}
        except Exception as e:
            err_msg = f"Lỗi quét Token: {e}"
            self.push_log(f"❌ [AUTO-DETECT] {err_msg}", "error")
            return {"success": False, "message": err_msg}

    def test_webhook(self, webhook_url):
        if not webhook_url or not webhook_url.strip():
            return {"success": False, "message": "Vui lòng nhập Webhook URL!"}
        
        asyncio.run_coroutine_threadsafe(
            self.engine.send_webhook_alert(
                webhook_url=webhook_url.strip(),
                preset_name="⚡ TEST ALERT",
                click_mode="TURBO",
                latency_ms=12.5,
                button_label="Test Webhook",
                username="Admin"
            ),
            self.loop
        )
        return {"success": True, "message": "Đã gửi thông báo thử nghiệm tới Discord Webhook!"}

    def start_queue(self, category_name, form_config):
        self.config_mgr.save_config(form_config)

        token = form_config.get("user_token", "").strip()
        sound_alert = form_config.get("global_settings", {}).get("sound_alert", True)
        click_mode = form_config.get("global_settings", {}).get("click_mode", "turbo")
        webhook_url = form_config.get("webhook_url", "").strip() if form_config.get("webhook_enabled", True) else ""
        
        cat_meta = form_config.get(category_name, {})
        target_labels = cat_meta.get("join_button_labels", ["Join Queue", "Join", "Queue"])

        if not token:
            self.push_log("Vui lòng dán User Token trong phần SETTINGS hoặc bấm Tự Động Tìm Token!", "error")
            return {"success": False, "message": "Missing token"}

        channels_key = f"{category_name}_channels"
        channels_dict = form_config.get(channels_key, {})

        if not channels_dict:
            single_cfg = form_config.get(category_name, {})
            cid = single_cfg.get("channel_id", "").strip()
            if cid:
                channels_dict = {
                    "custom": {
                        "enabled": True,
                        "name": category_name.upper(),
                        "server_id": single_cfg.get("server_id", ""),
                        "channel_id": cid,
                        "bot_id": single_cfg.get("bot_id", "")
                    }
                }

        if not channels_dict:
            self.push_log(f"[{category_name.upper()}] Không tìm thấy channel nào để trực!", "error")
            return {"success": False, "message": "No channels configured"}

        self.engine.start_category(
            category_name=category_name,
            channels_dict=channels_dict,
            token=token,
            sound_enabled=sound_alert,
            click_mode=click_mode,
            target_labels=target_labels,
            webhook_url=webhook_url
        )
        return {"success": True, "message": "Queue listener started"}

    def stop_queue(self, category_name):
        self.engine.stop_category(category_name)
        return {"success": True}

    def stop_all(self):
        self.engine.stop_all()
        return {"success": True}

def run_async_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

def keep_anti_capture_active(config_mgr):
    if sys.platform != "win32":
        return
    time.sleep(2.5)
    last_state = None
    while True:
        try:
            anti_ss = config_mgr.config.get("global_settings", {}).get("anti_screenshot", True)
            if anti_ss != last_state:
                AntiCaptureManager.set_protection("Discord Queue Joiner", enable=anti_ss)
                last_state = anti_ss
        except Exception:
            pass
        time.sleep(3.0)

def main():
    loop = asyncio.new_event_loop()
    loop_thread = threading.Thread(target=run_async_loop, args=(loop,), daemon=True)
    loop_thread.start()

    config_mgr = ConfigManager()
    api_instance = Api(config_mgr, loop)

    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    gui_path = os.path.join(base_dir, "gui", "index.html")
    icon_path = os.path.join(base_dir, "app_icon.ico")

    window = webview.create_window(
        title="Discord Queue Joiner - MCTIERS & PVPTIERS Engine",
        url=gui_path,
        js_api=api_instance,
        width=1100,
        height=750,
        min_size=(900, 600),
        background_color="#070913",
        resizable=True
    )

    # Setup System Tray
    tray_mgr = SystemTrayManager(window, api_instance, icon_path)
    api_instance.set_tray(tray_mgr)
    tray_mgr.start()

    # Start periodic anti-capture protection thread
    threading.Thread(target=keep_anti_capture_active, args=(config_mgr,), daemon=True).start()

    # Intercept Close (X) button -> Hide to Tray
    def on_closing():
        window.hide()
        api_instance.push_log("📌 Ứng dụng đã thu nhỏ xuống khay hệ thống (System Tray).", "info")
        tray_mgr.notify("Queue Joiner", "Tool đang chạy ẩn dưới khay hệ thống.")
        return False

    window.events.closing += on_closing

    webview.start(debug=False)

if __name__ == "__main__":
    main()
