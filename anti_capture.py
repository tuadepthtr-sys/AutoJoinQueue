import ctypes
import sys
import time

WDA_NONE = 0x00000000
WDA_MONITOR = 0x00000001
WDA_EXCLUDEFROMCAPTURE = 0x00000011  # Windows 10 2004+ (Excludes window from screen capture/recording)

class AntiCaptureManager:
    @staticmethod
    def get_all_target_hwnds(title_substring="Discord Queue Joiner"):
        if sys.platform != "win32":
            return []
        user32 = ctypes.windll.user32
        target_hwnds = []

        def enum_windows_callback(hwnd, extra):
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buffer = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buffer, length + 1)
                    if title_substring.lower() in buffer.value.lower():
                        target_hwnds.append(hwnd)
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        user32.EnumWindows(WNDENUMPROC(enum_windows_callback), 0)
        return target_hwnds

    @classmethod
    def apply_affinity_to_hwnd_tree(cls, parent_hwnd, enable=True):
        if sys.platform != "win32":
            return 0
        user32 = ctypes.windll.user32
        affinity = WDA_EXCLUDEFROMCAPTURE if enable else WDA_NONE

        # Apply ONLY to top-level parent HWND.
        # Calling SetWindowDisplayAffinity on child HWNDs (e.g. WebView2/Chromium renderers)
        # causes DirectX compositing deadlock and hangs the GUI (white screen / Not Responding).
        res = user32.SetWindowDisplayAffinity(ctypes.c_void_p(parent_hwnd), ctypes.c_uint(affinity))
        if res == 0 and enable:
            user32.SetWindowDisplayAffinity(ctypes.c_void_p(parent_hwnd), ctypes.c_uint(WDA_MONITOR))
        return 1

    @classmethod
    def set_protection(cls, window_title="Discord Queue Joiner", enable=True):
        if sys.platform != "win32":
            return False
        try:
            hwnds = cls.get_all_target_hwnds(window_title)
            if not hwnds:
                return False

            total_applied = 0
            for hwnd in hwnds:
                cnt = cls.apply_affinity_to_hwnd_tree(hwnd, enable)
                total_applied += cnt

            status = "BẬT (Khóa chụp màn hình)" if enable else "TẮT (Bình thường)"
            print(f"[ANTI-CAPTURE] {status} - Applied to {len(hwnds)} top-level window(s).")
            return True
        except Exception as e:
            print(f"[ANTI-CAPTURE] Error setting display affinity: {e}")
            return False
