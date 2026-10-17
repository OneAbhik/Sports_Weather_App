import tkinter as tk
from tkinter import messagebox
import requests

from sports import suggest_sports, verdict

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
AQI_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Rime fog",
    51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle",
    61: "Light rain", 63: "Rain", 65: "Heavy rain",
    71: "Light snow", 73: "Snow", 75: "Heavy snow",
    80: "Rain showers", 81: "Heavy showers", 82: "Violent showers",
    95: "Thunderstorm", 96: "Thunderstorm, hail", 99: "Heavy thunderstorm, hail",
}

VERDICT_COLORS = {"Great": "#1b8a3a", "OK": "#b8860b", "Poor": "#c0392b"}


class SportsWeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sports Weather App")
        self.root.geometry("560x640")
        self.root.minsize(560, 640)
        self.root.configure(bg="#f4f4f4")
        self.create_widgets()

    def create_widgets(self):
        tk.Label(
            self.root, text="Sports Weather Checker",
            font=("Arial", 18, "bold"), bg="#f4f4f4"
        ).pack(pady=15)

        self.city_entry = tk.Entry(self.root, width=25, font=("Arial", 12))
        self.city_entry.pack(pady=5)
        self.city_entry.focus()
        self.city_entry.bind("<Return>", lambda event: self.get_weather())

        self.search_button = tk.Button(
            self.root, text="Get Weather", command=self.get_weather
        )
        self.search_button.pack(pady=10)

        self.location_label = tk.Label(
            self.root, text="", font=("Arial", 14, "bold"), bg="#f4f4f4"
        )
        self.location_label.pack(pady=3)

        self.temp_label = tk.Label(
            self.root, text="", font=("Arial", 28), bg="#f4f4f4"
        )
        self.temp_label.pack(pady=3)

        self.condition_label = tk.Label(
            self.root, text="", font=("Arial", 12), bg="#f4f4f4"
        )
        self.condition_label.pack(pady=3)

        self.details_label = tk.Label(
            self.root, text="", font=("Arial", 11), bg="#f4f4f4"
        )
        self.details_label.pack(pady=3)

        tk.Label(
            self.root, text="Best sports now",
            font=("Arial", 14, "bold"), bg="#f4f4f4"
        ).pack(pady=(15, 5))

        self.sports_frame = tk.Frame(self.root, bg="#f4f4f4")
        self.sports_frame.pack(pady=5)

    def fetch_aqi(self, lat, lon):
        try:
            resp = requests.get(
                AQI_URL,
                params={"latitude": lat, "longitude": lon, "current": "us_aqi"},
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json()["current"]["us_aqi"]
        except (requests.RequestException, KeyError):
            return None

    def get_weather(self):
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showwarning("Input needed", "Enter a city name.")
            return

        try:
            geo = requests.get(
                GEO_URL, params={"name": city, "count": 1}, timeout=10
            )
            geo.raise_for_status()
            results = geo.json().get("results")
            if not results:
                messagebox.showerror("Not found", f"No city named '{city}'.")
                return
            place = results[0]

            weather = requests.get(
                WEATHER_URL,
                params={
                    "latitude": place["latitude"],
                    "longitude": place["longitude"],
                    "current": (
                        "temperature_2m,apparent_temperature,relative_humidity_2m,"
                        "precipitation,wind_speed_10m,weather_code"
                    ),
                },
                timeout=10,
            )
            weather.raise_for_status()
            current = weather.json()["current"]
        except requests.RequestException as err:
            messagebox.showerror("Network error", str(err))
            return

        aqi = self.fetch_aqi(place["latitude"], place["longitude"])
        self.show_weather(place, current, aqi)

    def show_weather(self, place, current, aqi):
        name = f"{place['name']}, {place.get('country', '')}"
        condition = WEATHER_CODES.get(current["weather_code"], "Unknown")
        aqi_text = aqi if aqi is not None else "n/a"

        self.location_label.config(text=name)
        self.temp_label.config(text=f"{current['temperature_2m']}°C")
        self.condition_label.config(text=condition)
        self.details_label.config(
            text=f"Feels {current['apparent_temperature']}°C   "
                 f"Humidity {current['relative_humidity_2m']}%   "
                 f"Wind {current['wind_speed_10m']} km/h   "
                 f"AQI {aqi_text}"
        )

        weather = {
            "feels": current["apparent_temperature"],
            "humidity": current["relative_humidity_2m"],
            "wind": current["wind_speed_10m"],
            "precip": current["precipitation"],
            "code": current["weather_code"],
            "aqi": aqi,
        }
        self.show_sports(suggest_sports(weather))

    def show_sports(self, suggestions):
        for child in self.sports_frame.winfo_children():
            child.destroy()
    
        for sport, score, note in suggestions:
            label_verdict = verdict(score)
            row = tk.Frame(self.sports_frame, bg="#f4f4f4")
            row.pack(pady=3)
    
            tk.Label(
                row, text=sport, width=10, anchor="w",
                font=("Arial", 12, "bold"), bg="#f4f4f4"
            ).pack(side="left")
            tk.Label(
                row, text=f"{score}/100 {label_verdict}", width=14, anchor="w",
                font=("Arial", 11), fg=VERDICT_COLORS[label_verdict], bg="#f4f4f4"
            ).pack(side="left")
            tk.Label(
                row, text=note, width=28, anchor="w",
                font=("Arial", 10), bg="#f4f4f4"
            ).pack(side="left")


if __name__ == "__main__":
    root = tk.Tk()
    app = SportsWeatherApp(root)
    root.mainloop()