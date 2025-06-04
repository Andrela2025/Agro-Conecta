import sys
import os
import random
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk

# --- Importaciones para Machine Learning ---
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# ============================
# 1. Carga y preparación del dataset
# ============================

csv_file = "Dataset/colombian_coffee_dataset.csv"
if not os.path.exists(csv_file):
    print(f"No se encuentra el archivo '{csv_file}'.")
    sys.exit(1)

df = pd.read_csv(csv_file)

# Verificar columnas críticas
columnas_necesarias = [
    'coffee_variety', 'price', 'ranking', 'year',
    'name', 'location', 'properties', 'carbon_credits'
]
for col in columnas_necesarias:
    if col not in df.columns:
        print(f"Falta la columna '{col}' en el CSV.")
        sys.exit(1)

# Eliminar filas donde 'coffee_variety' sea NaN (clave para muchas consultas)
df = df.dropna(subset=['coffee_variety'])

# Asegurar tipos numéricos
df['price'] = pd.to_numeric(df['price'], errors='coerce')
df['ranking'] = pd.to_numeric(df['ranking'], errors='coerce')
df['year'] = pd.to_numeric(df['year'], errors='coerce')
df['carbon_credits'] = pd.to_numeric(df['carbon_credits'], errors='coerce')

# ============================
# 2. Extracción de listados únicos
# ============================

variedades_unicas = sorted(df['coffee_variety'].dropna().unique())
años_unicos = sorted(df['year'].dropna().unique())

# ============================
# 3. Preparación de entrenamiento para el clasificador de intención
# ============================

# Lista de tuplas (frase_de_entrenamiento, etiqueta_intención)
train_phrases = [
    # ----------------- Variedad -----------------
    ("¿Qué variedades de café tienen?", "variedad"),
    ("Muéstrame los tipos de café disponibles", "variedad"),
    ("Dime las clases de café que ofrecen", "variedad"),
    ("¿Qué tipos de café manejan?", "variedad"),
    ("Quiero saber qué variedades hay", "variedad"),

    # ----------------- Precio general -----------------
    ("¿Cuánto cuesta una libra de Caturra?", "precio"),
    ("Precio del café Geisha", "precio"),
    ("¿Cuál es el valor del café Typica?", "precio"),
    ("¿A cuánto está el café Arcadia?", "precio"),
    ("Dime el costo del café", "precio"),
    ("¿Cuánto vale el café de mi región?", "precio"),
    ("¿Cuál es el precio del café más caro?", "precio_max"),          # aquí va a precio_max
    ("¿Cuál es el café más costoso?", "precio_max"),
    ("¿Cuál es el café que vale más?", "precio_max"),
    ("¿Qué variedad es la más cara?", "precio_max"),
    ("Dime la variedad de café de mayor precio", "precio_max"),
    ("¿Cuál es la variedad más económica?", "precio_min"),
    ("¿Qué café es más barato?", "precio_min"),
    ("Dime la variedad de menor precio", "precio_min"),
    ("¿Cuál es el café con precio más bajo?", "precio_min"),

    # ----------------- Calidad -----------------
    ("¿Cuál es la calidad promedio del café?", "calidad"),
    ("Dime el puntaje de calidad general", "calidad"),
    ("¿Cómo califican sus cafés?", "calidad"),
    ("¿Cuál es el ranking de calidad?", "calidad"),
    ("¿Qué score tienen sus cafés?", "calidad"),
    ("¿Cuál es el café con mejor ranking?", "calidad_max"),
    ("Dime la variedad de café con mejor puntaje", "calidad_max"),
    ("¿Qué café tiene la puntuación más alta?", "calidad_max"),
    ("¿Cuál es el café mejor calificado?", "calidad_max"),

    # ----------------- Año de cosecha -----------------
    ("¿De qué año es el café?", "año"),
    ("¿Qué cosechas tienen disponibles?", "año"),
    ("¿En qué años se cosechó este café?", "año"),
    ("Muéstrame los años de cosecha", "año"),
    ("¿Tienen café del 2021?", "año"),
    ("¿Hay café de 2022?", "año"),

    # ----------------- Productor / Lugar -----------------
    ("¿Quién produce el café Caturra?", "productor_lugar"),
    ("¿Dónde se cultiva el café Geisha?", "productor_lugar"),
    ("Dime los productores del café Typica", "productor_lugar"),
    ("¿Qué región cultiva Arcadia?", "productor_lugar"),
    ("Quiero saber el productor y la región", "productor_lugar"),

    # ----------------- Propiedades organolépticas -----------------
    ("¿Cuáles son las propiedades del café Caturra?", "propiedad"),
    ("Dime las notas de sabor de Geisha", "propiedad"),
    ("¿Qué características tiene el café Typica?", "propiedad"),
    ("Muéstrame las propiedades organolépticas", "propiedad"),
    ("¿Qué sabor tiene Arcadia?", "propiedad"),

    # ----------------- Bonos de carbono -----------------
    ("¿Qué bonos de carbono generan?", "bonos"),
    ("Muéstrame los créditos de carbono por productor", "bonos"),
    ("¿Cuántos bonos de carbono hay?", "bonos"),
    ("Dime los bonos de carbono acumulados", "bonos"),
    ("¿Quiénes generan más créditos de carbono?", "bonos_max"),
    ("¿Qué productor genera mayor bonos de carbono?", "bonos_max"),
    ("Dime el campesino con más bonos de carbono", "bonos_max"),
    ("¿Quién genera el mayor bono de carbono?", "bonos_max"),

    # ----------------- Saludo -----------------
    ("Hola", "saludo"),
    ("Buenos días", "saludo"),
    ("Buenas tardes", "saludo"),
    ("Saludos", "saludo"),
    ("Qué tal", "saludo"),
]

# Separar textos y etiquetas
X_train = [texto for texto, etiqueta in train_phrases]
y_train = [etiqueta for texto, etiqueta in train_phrases]

# Vectorizador TF-IDF
vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2))
X_vect = vectorizer.fit_transform(X_train)

# Clasificador de regresión logística
clf = LogisticRegression(max_iter=500)
clf.fit(X_vect, y_train)

# ============================
# 4. Funciones auxiliares para respuestas
# ============================

def predecir_intencion(texto_usuario: str) -> str:
    """
    Dada una frase del usuario, retorna la etiqueta (intención) predicha.
    """
    vect = vectorizer.transform([texto_usuario])
    etiqueta_pred = clf.predict(vect)[0]
    return etiqueta_pred


def agregar_mensaje(autor: str, mensaje: str):
    """
    Inserta un mensaje en el chat y hace scroll automático.
    """
    chat_log.insert(tk.END, f"\n{autor}: {mensaje}\n")
    chat_log.see(tk.END)


# --- Respuestas para cada intención ---

def obtener_info_variedades() -> str:
    return "Nuestras variedades incluyen: " + ", ".join(variedades_unicas) + "."


def obtener_info_precios(question: str) -> str:
    """
    Busca si en la pregunta hay alguna variedad; si la encuentra, devuelve el rango de precio.
    Si no, pide especificar la variedad.
    """
    for variedad in variedades_unicas:
        if variedad.lower() in question.lower():
            precios = df[df['coffee_variety'].str.lower() == variedad.lower()]['price'].dropna()
            if not precios.empty:
                precio_min = round(precios.min(), 2)
                precio_max = round(precios.max(), 2)
                return f"El café de variedad {variedad} cuesta entre ${precio_min} y ${precio_max} USD por libra."
    return "Por favor dime qué variedad de café te interesa. Las disponibles son:\n" + ", ".join(variedades_unicas)


def obtener_info_precio_max() -> str:
    """
    Retorna la variedad de café con el precio más alto registrado en el DataFrame.
    """
    df_sin_na = df.dropna(subset=['price', 'coffee_variety'])
    if df_sin_na.empty:
        return "Lo siento, no cuento con datos de precios para determinar el café más costoso."
    fila_max = df_sin_na.loc[df_sin_na['price'].idxmax()]
    variedad_top = fila_max['coffee_variety']
    precio_top = round(fila_max['price'], 2)
    return f"La variedad más costosa es {variedad_top}, con un precio de ${precio_top:.2f} USD por libra."


def obtener_info_precio_min() -> str:
    """
    Retorna la variedad de café con el precio más bajo registrado en el DataFrame.
    """
    df_sin_na = df.dropna(subset=['price', 'coffee_variety'])
    if df_sin_na.empty:
        return "Lo siento, no cuento con datos de precios para determinar el café más económico."
    fila_min = df_sin_na.loc[df_sin_na['price'].idxmin()]
    variedad_baja = fila_min['coffee_variety']
    precio_bajo = round(fila_min['price'], 2)
    return f"La variedad más económica es {variedad_baja}, con un precio de ${precio_bajo:.2f} USD por libra."


def obtener_info_calidad() -> str:
    ranking = df['ranking'].dropna()
    if ranking.empty:
        return "Lo siento, no cuento con datos de calidad en este momento."
    promedio = round(ranking.mean(), 2)
    return f"La calidad promedio de nuestros cafés es {promedio} puntos sobre 100."


def obtener_info_calidad_max() -> str:
    """
    Retorna la variedad de café con el ranking más alto.
    """
    df_sin_na = df.dropna(subset=['ranking', 'coffee_variety'])
    if df_sin_na.empty:
        return "Lo siento, no cuento con datos de ranking para determinar el mejor café."
    fila_max = df_sin_na.loc[df_sin_na['ranking'].idxmax()]
    variedad_top = fila_max['coffee_variety']
    ranking_top = round(fila_max['ranking'], 2)
    return f"La variedad con mejor ranking es {variedad_top}, con un puntaje de {ranking_top} sobre 100."


def obtener_info_años() -> str:
    años = [str(int(a)) for a in años_unicos]
    return "Tenemos cafés de las siguientes cosechas: " + ", ".join(años) + "."


def obtener_info_productor_lugar() -> str:
    listado = df[['coffee_variety', 'name', 'location']].dropna(subset=['coffee_variety', 'name', 'location'])
    if listado.empty:
        return "Lo siento, no cuento con datos de productores y lugares en este momento."
    filas = []
    for _, row in listado.iterrows():
        filas.append(f"{row['coffee_variety']} – {row['name']} ({row['location']})")
    return "Lista de productores y lugares de producción:\n" + "\n".join(filas)


def obtener_info_propiedades() -> str:
    listado_props = df[['coffee_variety', 'properties']].dropna(subset=['coffee_variety', 'properties'])
    if listado_props.empty:
        return "Lo siento, no cuento con datos de propiedades organolépticas en este momento."
    filas = []
    for _, row in listado_props.iterrows():
        filas.append(f"{row['coffee_variety']}: {row['properties']}")
    return "Propiedades de las variedades de café:\n" + "\n".join(filas)


def obtener_info_bonos() -> str:
    if 'carbon_credits' not in df.columns or df['carbon_credits'].dropna().empty:
        return "Lo siento, no cuento con datos de bonos de carbono en este momento."
    resumen_bonos = df.groupby("name")["carbon_credits"].sum().sort_values(ascending=False)
    filas = [f"{prod}: {bonos:.2f} 🌱" for prod, bonos in resumen_bonos.items()]
    return "Bonos de carbono generados por productor:\n" + "\n".join(filas)


def obtener_info_bonos_max() -> str:
    """
    Retorna el productor que genera la mayor cantidad de bonos de carbono.
    """
    if 'carbon_credits' not in df.columns or df['carbon_credits'].dropna().empty:
        return "Lo siento, no cuento con datos de bonos de carbono en este momento."
    resumen_bonos = df.groupby("name")["carbon_credits"].sum()
    if resumen_bonos.empty:
        return "Lo siento, no cuento con datos para determinar el productor con mayor bonos de carbono."
    prod_max = resumen_bonos.idxmax()
    bonos_max = round(resumen_bonos.max(), 2)
    return f"El productor que genera mayor bonos de carbono es {prod_max}, con {bonos_max:.2f} 🌱."


# ============================
# 5. Generar respuesta según intención
# ============================

def generar_respuesta(question: str, user_name: str) -> str:
    intent = predecir_intencion(question)

    if intent == "variedad":
        return obtener_info_variedades()

    elif intent == "precio":
        return obtener_info_precios(question)

    elif intent == "precio_max":
        return obtener_info_precio_max()

    elif intent == "precio_min":
        return obtener_info_precio_min()

    elif intent == "calidad":
        return obtener_info_calidad()

    elif intent == "calidad_max":
        return obtener_info_calidad_max()

    elif intent == "año":
        return obtener_info_años()

    elif intent == "productor_lugar":
        return obtener_info_productor_lugar()

    elif intent == "propiedad":
        return obtener_info_propiedades()

    elif intent == "bonos":
        return obtener_info_bonos()

    elif intent == "bonos_max":
        return obtener_info_bonos_max()

    elif intent == "saludo":
        return f"¡Hola {user_name.capitalize()}! ¿Cómo estás? 😊 ¿Sobre qué café quieres saber hoy?"

    # Si no se identifica claramente la intención:
    return (
        "Lo siento, no entendí tu pregunta. "
        "¿Quieres saber sobre variedades, precios (incluido el más caro o más barato), "
        "calidad (promedio o mejor), años de cosecha, productor, propiedades o bonos de carbono?"
    )


# ============================
# 6. Construcción de la interfaz gráfica (Tkinter)
# ============================

root = tk.Tk()
root.withdraw()
user_name = simpledialog.askstring("Bienvenido", "¿Cómo te llamas?")
if not user_name:
    user_name = "amigo"
root.deiconify()
root.title("☕ AgroConecta con ML - Café Colombiano")
root.geometry("1050x660")
root.configure(bg="#f4f4f4")

# --- Fondo decorativo ---
try:
    bg_image = Image.open("paisaje_cafetero.jpg")
    bg_photo = ImageTk.PhotoImage(bg_image.resize((1050, 660)))
    bg_label = tk.Label(root, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
except (FileNotFoundError, OSError):
    pass

# --- Imagen de caficultora sonriente ---
try:
    collector_img = Image.open("recolectora_sonriendo.png")
    collector_img = collector_img.resize((150, 200))
    collector_photo = ImageTk.PhotoImage(collector_img)
    collector_label = tk.Label(root, image=collector_photo, bg='white')
    collector_label.place(x=710, y=20)
except FileNotFoundError:
    print("Imagen recolectora no encontrada.")

# --- Área de chat ---
chat_frame = tk.Frame(root, bg='white', bd=2)
chat_frame.place(x=20, y=20, width=600, height=420)
chat_log = tk.Text(chat_frame, wrap='word', bg='white', fg='black', font=("Helvetica", 10))
chat_log.pack(expand=True, fill='both')
chat_log.insert(tk.END,
                f"Recolectora: ¡Hola {user_name.capitalize()}! Soy Aracelly 😊. "
                "Pregúntame sobre variedades, precios (incluido el más caro o más barato), "
                "calidad (promedio o mejor), año de cosecha, productor, propiedades o bonos de carbono.")

# Función para procesar la respuesta
def responder():
    question = user_input.get().strip()
    if not question:
        return
    chat_log.insert(tk.END, f"\n{user_name.capitalize()}: {question}\n")
    respuesta = generar_respuesta(question, user_name)
    agregar_mensaje("Recolectora", respuesta)
    user_input.delete(0, tk.END)

# Campo de entrada y botón de enviar
user_input = tk.Entry(root, width=80)
user_input.place(x=20, y=460)
user_input.bind("<Return>", lambda e: responder())

send_btn = tk.Button(root, text="✉️ Enviar", command=responder,
                     bg="#4CAF50", fg="white", font=("Helvetica", 10, "bold"))
send_btn.place(x=540, y=455)

# ============================
# 7. Sección de compra
# ============================

compra_frame = tk.LabelFrame(root, text="🛒 Compra tu café", font=("Helvetica", 11, "bold"),
                             bg="#f4f4f4", padx=10, pady=10)
compra_frame.place(x=650, y=240, width=250, height=230)

ttk.Label(compra_frame, text="Variedad:", background="#f4f4f4").grid(row=0, column=0, sticky='w')
variedad_cb = ttk.Combobox(compra_frame, values=variedades_unicas, state="readonly")
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
        productores_cb.set(productores[0] if productores else "")
        propiedades_cb.set(propiedades[0] if propiedades else "")
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

    precios = df[(df['coffee_variety'] == variedad) & (df['name'] == productor)]['price'].dropna()
    if precios.empty:
        precios = df[df['coffee_variety'] == variedad]['price'].dropna()
        if precios.empty:
            messagebox.showerror("Sin datos", "No hay precios para esta variedad.")
            return
    precio_usd = precios.mean()

    tasa_cambio = 4132
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


comprar_btn = tk.Button(compra_frame, text="Comprar", command=realizar_compra,
                        bg="#2196F3", fg="white", font=("Helvetica", 10, "bold"))
comprar_btn.grid(row=6, column=0, columnspan=2, pady=10)

# ============================
# 8. Sugerencias rápidas
# ============================

sugerencias_frame = tk.Frame(root, bg='white')
sugerencias_frame.place(x=20, y=520)


def sugerencia(texto: str):
    user_input.delete(0, tk.END)
    user_input.insert(0, texto)


def crear_boton_sugerencia(texto: str, pregunta: str, color: str, col: int):
    b = tk.Button(sugerencias_frame, text=texto, command=lambda: sugerencia(pregunta),
                  bg=color, fg='black', font=('Helvetica', 10), padx=8, pady=5)
    b.grid(row=0, column=col, padx=4, pady=5)


crear_boton_sugerencia("🌱 Variedades", "¿Qué variedades de café tienen?", "#e0f7fa", 0)
crear_boton_sugerencia("💰 Precios", "¿Cuál es el precio del café Geisha?", "#fff9c4", 1)
crear_boton_sugerencia("💎 Café más caro", "¿Cuál es el café más costoso?", "#ffe0b2", 2)
crear_boton_sugerencia("💵 Café más económico", "¿Cuál es la variedad más económica?", "#d7ccc8", 3)
crear_boton_sugerencia("📈 Mejor ranking", "¿Cuál es el café con mejor ranking?", "#c8e6c9", 4)
crear_boton_sugerencia("🌍 Bonos top", "¿Cuál productor genera mayor bonos de carbono?", "#d1c4e9", 5)
crear_boton_sugerencia("📅 Años cosecha", "¿De qué año es el café?", "#f8bbd0", 6)
crear_boton_sugerencia("🌿 Propiedades", "¿Cuáles son las propiedades del café Typica?", "#dcedc8", 7)

# ============================
# 9. Ejecutar la interfaz
# ============================

root.mainloop()