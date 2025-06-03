import sys
import os
import pandas as pd
import random
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk

# Cargar datos
csv_file = "Dataset/colombian_coffee_dataset.csv"
if not os.path.exists(csv_file):
    print(f"No se encuentra el archivo '{csv_file}'.")
    sys.exit(1)

df = pd.read_csv(csv_file)

# Ventana principal
root = tk.Tk()
root.withdraw()
user_name = simpledialog.askstring("Bienvenido", "Hola, ¿Cómo te llamas?")
if not user_name:
    user_name = "amigo"
root.deiconify()
root.title("☕ AgroConecta - Café Colombiano")
root.geometry("920x660")
root.configure(bg="#f4f4f4")

# Fondo decorativo
try:
    bg_image = Image.open("paisaje_cafetero.jpg")
    bg_photo = ImageTk.PhotoImage(bg_image.resize((920, 660)))
    bg_label = tk.Label(root, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
except:
    pass

# Imagen de caficultora sonriente
try:
    collector_img = Image.open("recolectora_sonriendo.png")
    collector_img = collector_img.resize((150, 200))
    collector_photo = ImageTk.PhotoImage(collector_img)
    collector_label = tk.Label(root, image=collector_photo, bg='white')
    collector_label.place(x=710, y=20)
except FileNotFoundError:
    print("Imagen recolectora no encontrada.")

# Área de chat
chat_frame = tk.Frame(root, bg='white', bd=2)
chat_frame.place(x=20, y=20, width=600, height=420)
chat_log = tk.Text(chat_frame, wrap='word', bg='white', fg='black', font=("Helvetica", 10))
chat_log.pack(expand=True, fill='both')
chat_log.insert(tk.END, f"Recolectora: ¡Hola {user_name.capitalize()}! Soy Aracelly . Pregúntame sobre nuestras variedades de café, precios, calidad, bonos de carbono, año de cosecha.\n")

def agregar_mensaje(autor, mensaje):
    chat_log.insert(tk.END, f"\n{autor}: {mensaje}\n")
    chat_log.see(tk.END)

user_input = tk.Entry(root, width=80)
user_input.place(x=20, y=460)

def responder():
    question = user_input.get().lower()
    chat_log.insert(tk.END, f"\n{user_name.capitalize()}: {question}\n")

    response = "Lo siento, no entendí tu pregunta. ¿Quieres saber sobre variedades, precios, calidad, año de cosecha o productores?"

    variedad_keys = ["variedad", "tipo", "clase"]
    precio_keys = ["precio", "cuánto", "cuesta", "vale", "valor", "tarifa"]
    calidad_keys = ["calidad", "score", "puntaje", "ranking"]
    año_keys = ["año", "cosecha", "producción"]
    productor_keys = ["productor", "campesino", "cultivador", "quién lo produce"]
    propiedad_keys = ["propiedad", "característica", "sabores", "notas", "notes", "flavor", "propiedades"]
    lugar_keys = ["lugar", "región", "departamento", "ubicación", "sitio"]

    if any(word in question for word in variedad_keys):
        variedades = df['coffee_variety'].dropna().unique()
        respuesta = f"Nuestras variedades incluyen: {', '.join(sorted(variedades))}."

    elif any(word in question for word in precio_keys):
        encontrada = False
        for variedad in df['coffee_variety'].dropna().unique():
            if variedad.lower() in question:
                encontrada = True
                precios = df[df['coffee_variety'].str.lower() == variedad.lower()]['price']
                precio_min = round(precios.min(), 2)
                precio_max = round(precios.max(), 2)
                respuesta = f"El café de variedad {variedad} cuesta entre ${precio_min} y ${precio_max} USD por libra."
                break
        if not encontrada:
            variedades = df['coffee_variety'].dropna().unique()
            respuesta = "Por favor dime qué variedad de café te interesa. Las disponibles son:\n" + ", ".join(sorted(variedades))

    elif any(word in question for word in calidad_keys):
        ranking = df['ranking'].dropna()
        promedio = round(ranking.mean(), 2)
        respuesta = f"La calidad promedio de nuestros cafés es {promedio} puntos sobre 100."

    elif any(word in question for word in año_keys):
        años = sorted(df['year'].dropna().unique())
        respuesta = f"Tenemos cafés de las siguientes cosechas: {', '.join(map(str, años))}."

    elif any(word in question for word in productor_keys + lugar_keys):
        listado = df[['coffee_variety', 'name', 'location']].dropna()
        listado_texto = "\n".join([f"{row['coffee_variety']} - {row['name']} ({row['location']})" for _, row in listado.iterrows()])
        respuesta = f"Lista de productores y lugares de producción:\n{listado_texto}"

    elif any(word in question for word in propiedad_keys):
        listado_props = df[['coffee_variety', 'properties']].dropna()
        texto_props = "\n".join([f"{row['coffee_variety']}: {row['properties']}" for _, row in listado_props.iterrows()])
        respuesta = f"Propiedades de las variedades de café:\n{texto_props}"

    elif "bono" in question or "carbono" in question:
        resumen_bonos = df.groupby("name")["carbon_credits"].sum().sort_values(ascending=False)
        respuesta = "Bonos de carbono generados por productor:\n" + "\n".join([f"{prod}: {bonos:.2f} 🌱" for prod, bonos in resumen_bonos.items()])

    elif "hola" in question or "buenos días" in question or "saludo" in question:
        respuesta = f"¡Hola {user_name.capitalize()}! ¿Cómo estás? 😊 ¿Sobre qué café quieres saber hoy?"

    agregar_mensaje("Recolectora", respuesta)
    user_input.delete(0, tk.END)

send_btn = tk.Button(root, text="✉️ Enviar", command=responder, bg="#4CAF50", fg="white", font=("Helvetica", 10, "bold"))
send_btn.place(x=540, y=455)
user_input.bind("<Return>", lambda e: responder())

# Sección de compra
compra_frame = tk.LabelFrame(root, text="🛒 Compra tu café", font=("Helvetica", 11, "bold"), bg="#f4f4f4", padx=10, pady=10)
compra_frame.place(x=650, y=240, width=250, height=230)

ttk.Label(compra_frame, text="Variedad:", background="#f4f4f4").grid(row=0, column=0, sticky='w')
variedades = sorted(df['coffee_variety'].dropna().unique())
variedad_cb = ttk.Combobox(compra_frame, values=variedades, state="readonly")
variedad_cb.grid(row=0, column=1)
variedad_cb.set("")

ttk.Label(compra_frame, text="Productor:", background="#f4f4f4").grid(row=1, column=0, sticky='w')
productores_cb = ttk.Combobox(compra_frame, values=[], state="readonly")
productores_cb.grid(row=1, column=1)

ttk.Label(compra_frame, text="Propiedades:", background="#f4f4f4").grid(row=2, column=0, sticky='w')
propiedades_cb = ttk.Combobox(compra_frame, values=[], state="readonly")
propiedades_cb.grid(row=2, column=1)

ttk.Label(compra_frame, text="Moneda:", background="#f4f4f4").grid(row=3, column=0, sticky='w')
moneda_cb = ttk.Combobox(compra_frame, values=["USD", "COP"], state="readonly")
moneda_cb.grid(row=3, column=1)
moneda_cb.set("USD")

ttk.Label(compra_frame, text="Unidad:", background="#f4f4f4").grid(row=4, column=0, sticky='w')
unidad_cb = ttk.Combobox(compra_frame, values=["Libras", "Kilos"], state="readonly")
unidad_cb.grid(row=4, column=1)
unidad_cb.set("Libras")

ttk.Label(compra_frame, text="Cantidad:", background="#f4f4f4").grid(row=5, column=0, sticky='w')
cantidad_sb = tk.Spinbox(compra_frame, from_=1, to=100, width=10)
cantidad_sb.grid(row=5, column=1)

def actualizar_productor_propiedades(event=None):
    variedad_sel = variedad_cb.get()
    if variedad_sel:
        df_var = df[df['coffee_variety'] == variedad_sel]
        productores = sorted(df_var['name'].dropna().unique())
        propiedades = sorted(df_var['properties'].dropna().unique())
        productores_cb['values'] = productores
        propiedades_cb['values'] = propiedades
        if productores:
            productores_cb.set(productores[0])
        else:
            productores_cb.set("")
        if propiedades:
            propiedades_cb.set(propiedades[0])
        else:
            propiedades_cb.set("")
    else:
        productores_cb['values'] = []
        propiedades_cb['values'] = []
        productores_cb.set("")
        propiedades_cb.set("")

variedad_cb.bind("<<ComboboxSelected>>", actualizar_productor_propiedades)

def realizar_compra():
    variedad = variedad_cb.get()
    productor = productores_cb.get()
    propiedad = propiedades_cb.get()
    moneda = moneda_cb.get()
    unidad = unidad_cb.get()
    try:
        cantidad = float(cantidad_sb.get())
    except ValueError:
        messagebox.showwarning("Cantidad inválida", "Introduce un número válido para la cantidad.")
        return

    if not variedad:
        messagebox.showwarning("Falta información", "Selecciona una variedad de café.")
        return
    if not productor:
        messagebox.showwarning("Falta información", "Selecciona un productor.")
        return
    if not propiedad:
        messagebox.showwarning("Falta información", "Selecciona una propiedad.")
        return

    precios = df[(df['coffee_variety'] == variedad) & (df['name'] == productor)]['price']
    if precios.empty:
        precios = df[df['coffee_variety'] == variedad]['price']
        if precios.empty:
            messagebox.showerror("Sin datos", "No hay precios para esta variedad.")
            return
    precio_usd = precios.mean()

    tasa_cambio = 4000
    if unidad == "Kilos":
        cantidad_lb = cantidad * 2.20462
    else:
        cantidad_lb = cantidad
    total_usd = precio_usd * cantidad_lb
    total = total_usd if moneda == "USD" else total_usd * tasa_cambio
    simbolo = "$" if moneda == "USD" else "COL$"
    bonos = round(random.uniform(0.5, 2.5) * cantidad_lb, 2)

    resumen = (
        f"Compra de {cantidad:.2f} {unidad.lower()} de café {variedad}\n"
        f"Productor: {productor}\n"
        f"Propiedades: {propiedad}\n"
        f"Precio promedio por libra: ${precio_usd:.2f} USD\n"
        f"Total a pagar: {simbolo}{total:.2f}\n"
        f"Bonos de carbono generados: {bonos} 🌱"
    )
    agregar_mensaje("Recolectora", resumen)

comprar_btn = tk.Button(compra_frame, text="Comprar", command=realizar_compra, bg="#2196F3", fg="white", font=("Helvetica", 10, "bold"))
comprar_btn.grid(row=6, column=0, columnspan=2, pady=10)

# Sugerencias (sin Productor y Lugar)
sugerencias_frame = tk.Frame(root, bg='white')
sugerencias_frame.place(x=20, y=520)

def sugerencia(texto):
    user_input.delete(0, tk.END)
    user_input.insert(0, texto)

def crear_boton_sugerencia(texto, pregunta, color, col):
    b = tk.Button(sugerencias_frame, text=texto, command=lambda: sugerencia(pregunta),
                  bg=color, fg='black', font=('Helvetica', 10), padx=8, pady=5)
    b.grid(row=0, column=col, padx=4, pady=5)

crear_boton_sugerencia("🌱 Variedades", "¿Qué variedades de café tienen?", "#e0f7fa", 0)
crear_boton_sugerencia("💰 Precios", "¿Cuánto cuesta el café?", "#fff9c4", 1)
crear_boton_sugerencia("📈 Calidad", "¿Cuál es la calidad del café?", "#c8e6c9", 2)
crear_boton_sugerencia("📅 Cosecha", "¿De qué año es el café?", "#f8bbd0", 3)
crear_boton_sugerencia("🌍 Bonos", "¿Qué bonos de carbono generan?", "#d1c4e9", 4)
crear_boton_sugerencia("🌿 Propiedades", "¿Cuáles son las propiedades del café?", "#dcedc8", 5)

# Ejecutar interfaz
root.mainloop()