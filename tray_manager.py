import os
import threading
from PIL import Image
import pystray

class SystemTrayManager:
    def __init__(self, window, api_instance, icon_path):
        self.window = window
        self.api = api_instance
        self.icon_path = icon_path
        self.tray_icon = None
        self.thread = None

    def show_window(self):
        if self.window:
            try:
                self.window.show()
                self.window.restore()
            except Exception as e:
                print(f"[TRAY] Error showing window: {e}")

    def stop_all_queues(self):
        if self.api:
            self.api.stop_all()

    def exit_app(self):
        if self.api:
            self.api.stop_all()
        if self.tray_icon:
            self.tray_icon.stop()
        os._exit(0)

    def create_menu(self):
        return pystray.Menu(
            pystray.MenuItem("🚀 Hiển Thị Giao Diện (Show GUI)", lambda: self.show_window(), default=True),
            pystray.MenuItem("⏹️ Dừng Tất Cả Queue", lambda: self.stop_all_queues()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("❌ Thoát Hoàn Toàn (Exit)", lambda: self.exit_app())
        )

    def run_tray(self):
        try:
            if os.path.exists(self.icon_path):
                img = Image.open(self.icon_path)
            else:
                img = Image.new('RGB', (64, 64), color=(99, 102, 241))
            
            self.tray_icon = pystray.Icon(
                "QueueJoiner",
                img,
                "Discord Queue Joiner",
                menu=self.create_menu()
            )
            self.tray_icon.run()
        except Exception as e:
            print(f"[TRAY] System tray error: {e}")

    def start(self):
        self.thread = threading.Thread(target=self.run_tray, daemon=True)
        self.thread.start()

    def notify(self, title, message):
        if self.tray_icon:
            try:
                self.tray_icon.notify(message, title)
            except Exception:
                pass
