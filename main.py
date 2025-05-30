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
csv_file = "Dataset/colombian_coffee_dataset.csv"
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
chat_log.insert(tk.END, "Recolectora: ¡Hola soy Aracelly! Pregúntame sobre los cafés que tenemos disponibles.")

# Entrada de texto
user_input = tk.Entry(root, width=80)
user_input.place(x=20, y=500)

# Función del chatbot
def respond():
    question = user_input.get().lower()
    chat_log.insert(tk.END, f"\nTú: {question}\n")

    if "variedad" in question or "tipo" in question:
        variedades = df['coffee_variety'].unique()
        lista = ', '.join(sorted(variedades))
        response = f"Trabajamos con las siguientes variedades de café: {lista}."

    elif "precio" in question or "cuánto vale" in question:
        encontrada = False
        for variedad in df['coffee_variety'].unique():
            if variedad.lower() in question:
                encontrada = True
                precios = df[df['coffee_variety'].str.lower() == variedad.lower()]['price']
                precio_min = round(precios.min(), 2)
                precio_max = round(precios.max(), 2)
                response = f"El café de variedad {variedad} tiene un precio entre ${precio_min} y ${precio_max} USD por libra."
                break
        if not encontrada:
            response = "Por favor especifica una variedad de café para darte el precio correspondiente."

    elif "productor" in question or "campesino" in question:
        name = df.sample(1).iloc[0]['name']
        response = f"Uno de nuestros campesinos es {name}, quien cultiva con dedicación y procesos sostenibles."

    else:
        response = "Puedes preguntarme por variedades, precios o productores."

    chat_log.insert(tk.END, f"Recolectora: {response}\n")
    user_input.delete(0, tk.END)

# Botón para enviar
send_button = tk.Button(root, text="Enviar", command=respond)
send_button.place(x=700, y=495)

# Iniciar interfaz
tk.mainloop()
