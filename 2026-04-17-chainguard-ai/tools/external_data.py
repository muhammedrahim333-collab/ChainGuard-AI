from __future__ import annotations

from dataclasses import dataclass

import requests


PUNJAB_COORDS = {
    "amritsar": (31.6340, 74.8723),
    "ludhiana": (30.9000, 75.8573),
    "jalandhar": (31.3260, 75.5762),
    "mohali": (30.7046, 76.7179),
    "bathinda": (30.2110, 74.9455),
    "patiala": (30.3398, 76.3869),
}


@dataclass
class IndiaIntelTool:
    settings: any
    web_search: any

    def weather_and_event_snapshot(self, city: str) -> dict:
        city_key = city.lower()
        if self.settings.openweather_api_key and city_key in PUNJAB_COORDS:
            lat, lon = PUNJAB_COORDS[city_key]
            try:
                response = requests.get(
                    "https://api.openweathermap.org/data/2.5/weather",
                    params={
                        "lat": lat,
                        "lon": lon,
                        "appid": self.settings.openweather_api_key,
                        "units": "metric",
                    },
                    timeout=20,
                )
                response.raise_for_status()
                payload = response.json()
                return {
                    "temperature_c": payload["main"]["temp"],
                    "condition": payload["weather"][0]["description"],
                }
            except Exception as exc:
                return {"weather_note": f"Weather API unavailable: {exc}"}
        hits = self.web_search.search(f"{city} Punjab weather disruption flood storm strike today", max_results=3)
        return {"weather_note": "Fallback web intelligence", "hits": hits}

    def agmarknet_snapshot(self, commodity: str) -> dict:
        hits = self.web_search.search(
            f"Agmarknet Punjab {commodity} price mandi India",
            max_results=3,
        )
        return {"commodity": commodity, "market_signals": hits}

    def government_scheme_alerts(self, industry: str) -> dict:
        hits = self.web_search.search(
            f"site:msme.gov.in OR site:dgft.gov.in OR site:pib.gov.in India subsidy scheme alert {industry}",
            max_results=4,
        )
        return {"industry": industry, "scheme_hits": hits}

    def logistics_snapshot(self, city: str) -> dict:
        hits = self.web_search.search(
            f"{city} transport strike highway closure rail logistics export delay India",
            max_results=4,
        )
        return {"city": city, "logistics_hits": hits}
