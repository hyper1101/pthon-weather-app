import customtkinter as ctk
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
from PIL import Image
import os
import json

# Configuration de l'interface
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Clé API OpenWeatherMap
API_KEY = "7d63394bce6d499ec6ed9c763ce2fe52"

# Variable pour stocker le graphique
canvas = None
current_weather_data = None
history_weather_data = None

def get_current_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erreur: {e}")
        return None

def get_weather_history(city):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erreur: {e}")
        return None

def save_weather_data():
    global current_weather_data, history_weather_data
    if current_weather_data and history_weather_data:
        data = {
            "current": current_weather_data,
            "history": history_weather_data
        }
        try:
            with open("weather_data.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            status_label.configure(text="Données sauvegardées avec succès!", text_color="green")
        except Exception as e:
            status_label.configure(text=f"Erreur lors de la sauvegarde: {e}", text_color="red")
    else:
        status_label.configure(text="Aucune donnée à sauvegarder", text_color="red")

def load_weather_data():
    global current_weather_data, history_weather_data
    try:
        with open("weather_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            current_weather_data = data["current"]
            history_weather_data = data["history"]
            update_display(current_weather_data)
            plot_temperature_history(history_weather_data)
            status_label.configure(text="Données chargées avec succès!", text_color="green")
    except FileNotFoundError:
        status_label.configure(text="Aucune donnée sauvegardée trouvée", text_color="red")
    except Exception as e:
        status_label.configure(text=f"Erreur lors du chargement: {e}", text_color="red")

def plot_temperature_history(data):
    global canvas
    
    if canvas:
        canvas.get_tk_widget().pack_forget()
        canvas = None

    if not data:
        return

    dates = [datetime.strptime(item['dt_txt'], '%Y-%m-%d %H:%M:%S') for item in data['list']]
    temps = [item['main']['temp'] for item in data['list']]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(dates, temps, label="Température")
    ax.set_title("Historique des températures")
    ax.set_xlabel("Date")
    ax.set_ylabel("Température (°C)")
    ax.legend()

    canvas = FigureCanvasTkAgg(fig, master=app)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10)

def create_icon_label_frame(parent, icon_path, initial_text=""):
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.pack(pady=5, fill="x", padx=20)

    # Charger et redimensionner l'icône
    if os.path.exists(icon_path):
        icon = Image.open(icon_path)
        icon = icon.resize((20, 20))
        icon_ctk = ctk.CTkImage(light_image=icon, dark_image=icon, size=(20, 20))
        icon_label = ctk.CTkLabel(frame, image=icon_ctk, text="")
        icon_label.pack(side="left", padx=(0, 10))
    
    text_label = ctk.CTkLabel(frame, text=initial_text, font=("Arial", 14))
    text_label.pack(side="left")
    
    return text_label

def update_display(weather_data):
    if weather_data:
        temp = weather_data['main']['temp']
        humidity = weather_data['main']['humidity']
        description = weather_data['weather'][0]['description']
        
        temperature_label.configure(text=f"Température : {temp}°C")
        humidity_label.configure(text=f"Humidité : {humidity}%")
        description_label.configure(text=f"Description : {description.capitalize()}")
    
def display_weather():
    global current_weather_data, history_weather_data
    city = city_entry.get()
    current_weather_data = get_current_weather(city)
    history_weather_data = get_weather_history(city)

    if current_weather_data:
        update_display(current_weather_data)
        plot_temperature_history(history_weather_data)
        status_label.configure(text="Données météo mises à jour!", text_color="green")
    else:
        temperature_label.configure(text="Erreur lors de la récupération des données.")
        humidity_label.configure(text="")
        description_label.configure(text="")
        status_label.configure(text="Erreur de récupération des données", text_color="red")

# Création de l'application principale
app = ctk.CTk()
app.geometry("900x800")
app.title("Application Météo")

# Chargement et affichage de l'image principale
if os.path.exists("weather_banner.png"):
    banner_image = Image.open("weather_banner.png")
    banner_image = banner_image.resize((800, 200))  # Redimensionnement de l'image
    banner_ctk = ctk.CTkImage(light_image=banner_image, dark_image=banner_image, size=(800, 200))
    banner_label = ctk.CTkLabel(app, image=banner_ctk, text="")
    banner_label.pack(pady=10)

# Titre
title_label = ctk.CTkLabel(app, text="Application Météo", font=("Arial", 24, "bold"))
title_label.pack(pady=20)

# Frame pour l'entrée et les boutons
input_frame = ctk.CTkFrame(app, fg_color="transparent")
input_frame.pack(pady=10)

city_entry = ctk.CTkEntry(input_frame, width=250, placeholder_text="Entrez le nom de la ville")
city_entry.pack(side="left", padx=10)

fetch_button = ctk.CTkButton(input_frame, text="Obtenir Météo", command=display_weather)
fetch_button.pack(side="left", padx=10)

# Frame pour les boutons de sauvegarde/chargement
save_load_frame = ctk.CTkFrame(app, fg_color="transparent")
save_load_frame.pack(pady=10)

save_button = ctk.CTkButton(save_load_frame, text="Sauvegarder", command=save_weather_data)
save_button.pack(side="left", padx=10)

load_button = ctk.CTkButton(save_load_frame, text="Charger", command=load_weather_data)
load_button.pack(side="left", padx=10)

# Label de statut
status_label = ctk.CTkLabel(app, text="", font=("Arial", 12))
status_label.pack(pady=5)

# Création des labels avec icônes
temperature_label = create_icon_label_frame(app, "icons/temperature.png", "Température : - - °C")
humidity_label = create_icon_label_frame(app, "icons/humidity.png", "Humidité : - - %")
description_label = create_icon_label_frame(app, "icons/weather.png", "Description : - -")

# Lancement de l'application
app.mainloop()