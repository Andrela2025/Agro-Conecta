import sys
import os
import pandas as pd
import random

# Verifica si se está ejecutando en un entorno sin GUI
try:
    import tkinter as tk
    from tkinter import ttk
    from PIL import Image, ImageTk
except ModuleNotFoundError as e:
    print("Este script requiere un entorno gráfico con tkinter y PIL instalados.")
    sys.exit(1)

# Verifica que el archivo exista
csv_file = "colombian_coffee_dataset.csv"
if not os.path.exists(csv_file):
    print(f"No se encuentra el archivo '{csv_file}'. Asegúrate de que esté en el mismo directorio.")
    sys.exit(1)

# Cargar datos del dataset
df = pd.read_csv(csv_file)

# Crear la ventana principal
root = tk.Tk()
root.title("Chatbot Justo Agro")
root.geometry("800x600")

# Fondo con paisaje cafetero
try:
    bg_image = Image.open("paisaje_cafetero.jpg")
    bg_photo = ImageTk.PhotoImage(bg_image.resize((800, 600)))
    bg_label = tk.Label(root, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
except FileNotFoundError:
    print("Imagen de fondo 'paisaje_cafetero.jpg' no encontrada.")

# Imagen recolectora de café
try:
    collector_img = Image.open("recolectora_sonriendo.png")
    collector_photo = ImageTk.PhotoImage(collector_img.resize((150, 200)))
    collector_label = tk.Label(root, image=collector_photo, bg='white')
    collector_label.place(x=620, y=10)
except FileNotFoundError:
    print("Imagen 'recolectora_sonriendo.png' no encontrada.")

# Área de texto del chat
chat_frame = tk.Frame(root, bg='white', bd=2)
chat_frame.place(x=20, y=20, width=580, height=460)
chat_log = tk.Text(chat_frame, wrap='word', bg='white', fg='black')
chat_log.pack(expand=True, fill='both')
chat_log.insert(tk.END, "Recolectora: ¡Hola soy Aracelly! Pregúntame sobre los cafés que tenemos disponibles.\n")

# Entrada de texto
user_input = tk.Entry(root, width=80)
user_input.place(x=20, y=500)

# Función del chatbot
def respond():
    question = user_input.get().lower()
    chat_log.insert(tk.END, f"\nTú: {question}\n")

    if "variedad" in question or "tipo" in question:
        variety = df.sample(1).iloc[0]['coffee_variety']
        response = f"Tenemos variedad del tipo: {variety}."
    elif "precio" in question or "cuánto vale" in question:
        sample = df.sample(1).iloc[0]
        response = f"El café de variedad {sample['coffee_variety']} tiene un precio de ${sample['price']} USD por libra."
    elif "productor" in question or "campesino" in question:
        name = df.sample(1).iloc[0]['name']
        response = f"Uno de nuestros campesinos es {name}, quien cultiva con mucha dedicación y procesos amigables con el medio ambiente."
    else:
        response = "Puedes preguntarme por variedades, precios o productores."

    chat_log.insert(tk.END, f"Recolectora: {response}\n")
    user_input.delete(0, tk.END)

# Botón para enviar
send_button = tk.Button(root, text="Enviar", command=respond)
send_button.place(x=700, y=495)

# Iniciar interfaz
tk.mainloop()
