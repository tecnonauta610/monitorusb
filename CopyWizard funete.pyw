import os
import tkinter as tk
from tkinter import messagebox, filedialog, Toplevel
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
from PIL import Image, ImageDraw, ImageFont, ImageTk
from datetime import datetime
import ctypes
import qrcode  # Asegúrate de tener instalada la biblioteca qrcode

class CopyMonitorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("CopyWizard")
        self.master.geometry("600x400")

        self.selected_drive = tk.StringVar()
        self.selected_price = tk.StringVar()  # Cambiado a StringVar para incluir el símbolo de $
        self.output_text = tk.Text(self.master, height=15, width=70)
        self.output_text.pack(pady=10)

        self.total_size = 0
        self.file_count = 0
        self.copied_files = []  # Lista para almacenar nombres de ficheros
        self.copied_files_set = set()  # Conjunto para rastrear ficheros únicos
        self.is_monitoring = False

        self.create_widgets()

    def create_widgets(self):
        # Marco para la selección de USB y selección de precio
        frame = tk.Frame(self.master)
        frame.pack(pady=10)

        # Etiqueta para seleccionar unidad USB
        self.drive_label = tk.Label(frame, text="Unidad USB:")
        self.drive_label.pack(side=tk.LEFT)

        self.drive_dropdown = tk.OptionMenu(frame, self.selected_drive, *self.get_drives(), command=self.start_monitoring)
        self.drive_dropdown.pack(side=tk.LEFT)

        # Etiqueta para seleccionar precio
        self.price_label = tk.Label(frame, text="Precio:")
        self.price_label.pack(side=tk.LEFT)

        # Dropdown para seleccionar precio
        self.price_dropdown = tk.OptionMenu(frame, self.selected_price, *[f"${i}" for i in range(1, 9001)])  # Opciones de $1 a $9000
        self.price_dropdown.pack(side=tk.LEFT)

        # Botón para crear factura
        self.create_invoice_button = tk.Button(frame, text="Crear Factura", command=self.create_invoice)
        self.create_invoice_button.pack(side=tk.LEFT)

        # Botón "Acerca de"
        self.about_button = tk.Button(frame, text="Acerca de", command=self.show_about)
        self.about_button.pack(side=tk.LEFT)

        # Botón "Ver QR"
        self.qr_button = tk.Button(frame, text="Ver QR", command=self.show_qr)
        self.qr_button.pack(side=tk.LEFT)

    def get_drives(self):
        # Obtener unidades disponibles (incluyendo discos duros internos, externos y teléfonos celulares)
        drives = []
        for letter in range(65, 91):  # A-Z
            drive = f"{chr(letter)}:\\"
            if os.path.exists(drive):
                drives.append(drive)
        return drives

    def start_monitoring(self, selected_drive):
        if not selected_drive or self.is_monitoring:
            return

        self.output_text.delete(1.0, tk.END)  # Limpiar texto anterior
        self.total_size = 0
        self.file_count = 0
        self.copied_files.clear()  # Limpiar la lista de ficheros
        self.copied_files_set.clear()  # Limpiar el conjunto de ficheros
        self.is_monitoring = True

        # Iniciar monitoreo en un hilo separado
        threading.Thread(target=self.monitor_drive, args=(selected_drive,), daemon=True).start()

    def monitor_drive(self, drive):
        event_handler = FileEventHandler(self.output_text, self)
        observer = Observer()
        observer.schedule(event_handler, drive, recursive=True)
        observer.start()
        try:
            while self.is_monitoring:
                pass  # Mantener el hilo activo
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    def stop_monitoring(self):
        self.is_monitoring = False
        summary = f"Ficheros: {self.file_count}, Capacidad Total Copiada: {self.total_size:.2f} MB\n"
        self.output_text.insert(tk.END, summary)
        self.output_text.see(tk.END)  # Desplazarse al final

    def create_invoice(self):
        # Crear una imagen para la factura
        copied_files_str = "\n".join(self.copied_files)  # Unir nombres de ficheros para la factura
        invoice_text = f"Ficheros: {self.file_count}\n" \
 f"Capacidad Total Copiada: {self.total_size:.2f} MB\n" \
                       f"Costo: {self.selected_price.get()}\n\n" \
                       f" Ficheros:\n{copied_files_str}"

        # Abrir cuadro de diálogo para seleccionar dónde guardar la factura
        current_date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        file_name = f"Factura-{current_date}.jpg"
        file_path = filedialog.asksaveasfilename(defaultextension=".jpg", initialfile=file_name)

        if file_path:
            # Crear una imagen más grande
            img = Image.new('RGB', (600, 500), color='white')  # Aumentar altura para más texto
            d = ImageDraw.Draw(img)

            # Cargar una fuente
            try:
                font = ImageFont.truetype("arial.ttf", 16)
            except IOError:
                font = ImageFont.load_default()

            # Dibujar el texto en la imagen
            d.text((10, 10), invoice_text, fill=(0, 0, 0), font=font)

            # Guardar la imagen
            img.save(file_path)
            messagebox.showinfo("Factura Creada", f"Factura guardada en {file_path}")

    def show_about(self):
        messagebox.showinfo("Acerca de", "Creado por Tecnonauta Numero: (+53)56639178 , Gmail: tecnonauta.net@gmail.com , Correo Nauta: naruteuu@nauta.cu , Dirección:Banes Holguin Cuba ,uso de la app: Esta Erramienta La e Creado Para Monitorias sus Grbaciones y Crear facturas para sus clientes es esencial para los que llenan memorias esto es una vercion de miron pero sin licensia es de codigo avierto libere de visrus Saludos Su creador Rodolfo Jara alia: Tecnonauta ")

    def show_qr(self):
        # Generar código QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data("https://tecnonauta610.github.io/infoQR/")
        qr.make(fit=True)

        # Crear una imagen desde el código QR
        img = qr.make_image(fill_color="black", back_color="white")
        img.save("qr_code.png")  # Guardar el código QR como imagen

        # Mostrar el código QR en una ventana emergente
        popup = Toplevel(self.master)
        popup.title("Código QR")
        popup.geometry("400x400")

        # Cargar la imagen del código QR
        qr_image = ImageTk.PhotoImage(img)
        qr_label = tk.Label(popup, image=qr_image)
        qr_label.image = qr_image  # Mantener la referencia
        qr_label.pack(expand=True)  # Centrar el código QR

        # Agregar un botón para cerrar la ventana emergente
        close_button = tk.Button(popup, text="Cerrar", command=popup.destroy)
        close_button.pack(pady=10)

class FileEventHandler(FileSystemEventHandler):
    def __init__(self, output_text, app):
        self.output_text = output_text
        self.app = app

    def on_created(self, event):
        if not event.is_directory:  # Verificar si no es un directorio
            file_path = event.src_path
            if file_path not in self.app.copied_files_set:  # Verificar si el archivo no está en el conjunto
                size = os.path.getsize(file_path) / (1024 * 1024)  # Tamaño en MB
                file_name, file_extension = os.path.splitext(file_path)
                self.app.total_size += size
                self.app.file_count += 1
                self.app.copied_files.append(f"{os.path.basename(file_name)}{file_extension} - Tamaño: {size:.2f} MB")  # Agregar nombre y tamaño del archivo a la lista
                self.app.copied_files_set.add(file_path)  # Agregar ruta del archivo al conjunto

                # Registrar archivo copiado
                self.output_text.insert(tk.END, f"Nombre Del Fichero: {os.path.basename(file_name)}{file_extension} - Tamaño : {size:.2f} MB\n")
                self.output_text.see(tk.END)  # Desplazarse al final

                # Detener monitoreo después de copiar el primer archivo (para demostración)
                self.app.stop_monitoring()  # Quitar esta línea si deseas monitorear continuamente

if __name__ == "__main__":
    root = tk.Tk()
    app = CopyMonitorApp(root)
    root.mainloop()