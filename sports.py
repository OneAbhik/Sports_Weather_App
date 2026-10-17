SPORTS = {
    "Running":    {"outdoor": True,  "temp": (8, 26),  "max_wind": 30, "rain_ok": False, "aqi_sensitive": True},
    "Cycling":    {"outdoor": True,  "temp": (10, 30), "max_wind": 25, "rain_ok": False, "aqi_sensitive": True},
    "Football":   {"outdoor": True,  "temp": (10, 30), "max_wind": 35, "rain_ok": False, "aqi_sensitive": True},
    "Cricket":    {"outdoor": True,  "temp": (15, 34), "max_wind": 40, "rain_ok": False, "aqi_sensitive": False},
    "Tennis":     {"outdoor": True,  "temp": (12, 32), "max_wind": 20, "rain_ok": False, "aqi_sensitive": False},
    "Hiking":     {"outdoor": True,  "temp": (5, 28),  "max_wind": 40, "rain_ok": False, "aqi_sensitive": True},
    "Swimming":   {"outdoor": True,  "temp": (24, 40), "max_wind": 40, "rain_ok": True,  "aqi_sensitive": False},
    "Badminton":  {"outdoor": False},
    "Gym":        {"outdoor": False},
    "Yoga":       {"outdoor": False},
}


def verdict(score):
    if score >= 80:
        return "Great"
    if score >= 60:
        return "OK"
    return "Poor"


def score_sport(rules, w):
    """w = dict: feels, wind, precip, code, aqi (aqi may be None)."""
    reasons = []

    bad_outdoor = (
        w["precip"] > 0.2
        or w["code"] >= 95
        or (w["aqi"] is not None and w["aqi"] > 150)
        or w["feels"] > 38
        or w["feels"] < 5
    )

    if not rules["outdoor"]:
        score = 90 if bad_outdoor else 70
        reasons.append("Indoor, weather no matter" if not bad_outdoor else "Bad outside, stay indoor")
        return score, reasons

    score = 100

    if w["code"] >= 95:
        score -= 80
        reasons.append("Thunderstorm")
    elif w["precip"] > 0.2 and not rules["rain_ok"]:
        score -= 50
        reasons.append("Rain")

    if w["aqi"] is not None and rules["aqi_sensitive"]:
        if w["aqi"] > 150:
            score -= 60
            reasons.append("Unhealthy air")
        elif w["aqi"] > 100:
            score -= 30
            reasons.append("Poor air")

    if w["wind"] > rules["max_wind"]:
        score -= 30
        reasons.append("Too windy")

    low, high = rules["temp"]
    if w["feels"] < low:
        score -= min(50, int((low - w["feels"]) * 3))
        reasons.append("Too cold")
    elif w["feels"] > high:
        score -= min(50, int((w["feels"] - high) * 3))
        reasons.append("Too hot")

    if w["feels"] > 30 and w["humidity"] > 80:
        score -= 15
        reasons.append("Humid")

    if not reasons:
        reasons.append("Good conditions")

    return max(score, 0), reasons


def suggest_sports(weather, top_n=5):
    results = []
    for name, rules in SPORTS.items():
        score, reasons = score_sport(rules, weather)
        results.append((name, score, ", ".join(reasons)))
    results.sort(key=lambda item: item[1], reverse=True)
    return results[:top_n]