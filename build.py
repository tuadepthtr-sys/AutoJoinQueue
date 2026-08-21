import os
import sys
import subprocess

def build_package():
    print("==================================================")
    print(f"   BUILDING DISCORD QUEUE JOINER PACKAGE ({sys.platform.upper()})   ")
    print("==================================================")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    spec_path = os.path.join(current_dir, "QueueJoiner.spec")

    if not os.path.exists(spec_path):
        print("[ERROR] 'QueueJoiner.spec' not found!")
        return

    pyinstaller_cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        spec_path
    ]

    print("[BUILD] Running PyInstaller command:")
    print(" ".join(pyinstaller_cmd))

    result = subprocess.run(pyinstaller_cmd, cwd=current_dir)

    if result.returncode == 0:
        ext = ".exe" if sys.platform == "win32" else (".app" if sys.platform == "darwin" else "")
        out_path = os.path.join(current_dir, "dist", f"QueueJoiner{ext}")
        print("\n==================================================")
        print(" SUCCESS! Package created successfully:")
        print(f" Path: {out_path}")
        print("==================================================")
    else:
        print("\n[ERROR] Build failed with return code:", result.returncode)

if __name__ == "__main__":
    build_package()
