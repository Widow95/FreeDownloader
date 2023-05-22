import subprocess
import sys

# Módulos a verificar e instalar
modules_to_check = ["yt_dlp", "moviepy", "urllib", "re", "pytube"]

def install_modules():
    for module in modules_to_check:
        try:
            __import__(module)
        except ImportError:
            print(f"El módulo {module} no está instalado, instalando...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", module])

if __name__ == "__main__":
    install_modules()