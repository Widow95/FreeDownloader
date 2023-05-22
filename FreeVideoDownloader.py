# Módulos a verificar
modules_to_check = ["yt_dlp", "moviepy", "urllib", "re"]

def check_dependencies():
    for module in modules_to_check:
        try:
            __import__(module)
        except ImportError:
            print(f"El módulo {module} no está instalado, instalando...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", module])
            
import urllib.request
import re
import tkinter as tk
import subprocess
import sys
import tkinter.ttk as ttk
from tkinter import messagebox
from tkinter import filedialog
from moviepy.editor import VideoFileClip
import os
  
try:
    import pytube
except ImportError:
    print("El módulo pytube no está instalado, instalando...")
    subprocess.check_call(['pip', 'install', 'pytube'])
    
try:
    from yt_dlp import YoutubeDL
except ImportError:
    subprocess.check_call(['pip', 'install', 'yt-dlp'])



downloads_path = ""


def download_video(url, format_code):
    try:
        if format_code == 'mp3':
            format_code = 'mp4'
            convert_to_mp3 = True
        else:
            convert_to_mp3 = False

        ydl_opts = {
            'outtmpl': os.path.join(downloads_path, '%(title)s.%(ext)s'),
            'format': format_code
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_title = info['title']
            print(f"Descargando video: {video_title}")

        if convert_to_mp3:
            video_path = os.path.join(downloads_path, f"{video_title}.mp4")
            audio_path = os.path.join(downloads_path, f"{video_title}.mp3")
            video_clip = VideoFileClip(video_path)
            audio_clip = video_clip.audio
            audio_clip.write_audiofile(audio_path, ffmpeg_params=["-ac", "2", "-vol", "256"])
            audio_clip.close()
            video_clip.close()

            # Eliminar el archivo de video MP4
            os.remove(video_path)

            return video_title + ".mp3"
        else:
            return video_title
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo descargar el video.\n{str(e)}")


def download_multiple(urls, format_code):
    total_videos = len(urls)
    successful_downloads = []

    for i, url in enumerate(urls, start=1):
        video_title = download_video(url, format_code)
        if video_title:
            successful_downloads.append(video_title)

    if len(successful_downloads) == total_videos:
        success_message = "Descarga completada:\n\n"
        for title in successful_downloads:
            success_message += f"- {title}\n"
        messagebox.showinfo("Descarga completada", success_message)
    else:
        messagebox.showerror("Error", "No se pudo descargar uno o más videos.")


def save_settings(path):
    # Guardar la ruta de descarga en el archivo de configuración
    with open("settings.txt", "w") as f:
        f.write(path)

    # Cerrar el diálogo de configuración
    messagebox.showinfo("Configuración guardada", "La configuración se ha guardado correctamente.")


def open_downloads_folder():
    # Abre la carpeta de descargas configurada en `downloads_path`
    if downloads_path:
        os.startfile(downloads_path)


root = tk.Tk()


def open_settings_dialog():
    global downloads_path

    # Crear la ventana de configuración
    settings_dialog = tk.Toplevel()
    settings_dialog.title("Configuración")

    # Crear el botón para seleccionar la ruta de descargas
    downloads_path_label = tk.Label(settings_dialog, text="Ruta de descargas:")
    downloads_path_label.pack()
    downloads_path_entry = tk.Entry(settings_dialog, width=50)
    downloads_path_entry.insert(0, downloads_path)
    downloads_path_entry.pack()

    def browse_downloads_path():
        path = filedialog.askdirectory()
        if path:
            downloads_path_entry.delete(0, tk.END)
            downloads_path_entry.insert(0, path)

    browse_button = tk.Button(settings_dialog, text="Seleccionar ruta", command=browse_downloads_path)
    browse_button.pack()

    # Crear el botón para guardar la configuración
    def save_settings():
        global downloads_path
        downloads_path = downloads_path_entry.get()
        with open("settings.txt", "w") as f:
            f.write(downloads_path)
        settings_dialog.destroy()

    save_button = tk.Button(settings_dialog, text="Guardar", command=save_settings)
    save_button.pack()

    # Alinear la ventana en la pantalla
    settings_dialog.geometry("+%d+%d" % (root.winfo_rootx() + 50, root.winfo_rooty() + 50))


def search_and_download(urls):
    try:
        for url in urls:
            query = url.strip()
            query = query.replace(" ", "+")
            html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + query)
            video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
            url = "https://www.youtube.com/watch?v=" + video_ids[0]
            download_video(url)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo descargar el video.\n{str(e)}")


def main():
    # Verificar la existencia del archivo de configuración
    if not os.path.exists("settings.txt"):
        with open("settings.txt", "w") as f:
            f.write("")

    # Leer la ruta de descarga desde el archivo de configuración
    global downloads_path
    with open("settings.txt", "r") as f:
        downloads_path = f.read()

    def download():
        user_input = entry.get("1.0", tk.END).strip()
        urls = user_input.split('\n')
        total_videos = len(urls)

        progress_bar["maximum"] = total_videos
        progress_bar["value"] = 0
        successful_downloads = []

        format_code = format_combobox.get()

        for i, url in enumerate(urls, start=1):
            video_title = download_video(url, format_code)
            progress_bar["value"] = i
            progress_label.config(text=f"Descargando video {i}/{total_videos}")
            root.update()
            if video_title:
                successful_downloads.append(video_title)

        if len(successful_downloads) == total_videos:
            success_message = "Descarga completada:\n\n"
            for title in successful_downloads:
                success_message += f"- {title}\n"
            messagebox.showinfo("Descarga completada", success_message)
        else:
            messagebox.showerror("Error", "No se pudo descargar uno o más videos.")

    # Crear la ventana principal
    root.title("FreeVideoDownloader 1.0")

    # Crear la barra de menú
    menubar = tk.Menu(root)
    root.config(menu=menubar)

    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Archivo", menu=file_menu)
    file_menu.add_command(label="Configuración", command=open_settings_dialog)
    file_menu.add_command(label="Abrir carpeta de descarga", command=open_downloads_folder)
    file_menu.add_separator()
    file_menu.add_command(label="Salir", command=root.quit)

    # Crear el marco principal
    main_frame = tk.Frame(root)
    main_frame.pack(pady=10)

    # Crear la etiqueta y el cuadro de texto para ingresar las URLs
    entry_label = tk.Label(main_frame, text="Ingrese las URLs de los videos (uno por línea):")
    entry_label.grid(row=0, column=0, sticky="w")

    entry = tk.Text(main_frame, width=50, height=10)
    entry.grid(row=1, column=0)

    # Crear el botón de descarga
    download_button = tk.Button(root, text="Descargar", command=download)
    download_button.pack(pady=10)

    # Crear la etiqueta y el cuadro de selección para el formato de descarga
    format_label = tk.Label(root, text="Formato de descarga:")
    format_label.pack()

    format_combobox = ttk.Combobox(root, values=["mp4", "mp3"], state="readonly")
    format_combobox.current(0)
    format_combobox.pack()

    # Crear la barra de progreso
    progress_frame = tk.LabelFrame(root, text="Progreso de descarga")
    progress_frame.pack(pady=10)

    progress_label = tk.Label(progress_frame, text="")
    progress_label.pack(pady=5)

    progress_bar = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=300, mode="determinate")
    progress_bar.pack()

    # Ejecutar la aplicación
    root.mainloop()


if __name__ == "__main__":
    main()