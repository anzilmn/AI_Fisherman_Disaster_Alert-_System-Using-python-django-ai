import requests

def get_marine_weather(lat, lon):
    """
    Fetches Waves, Wind, and Sea Surface Temperature for AI Fish Analytics.
    """
    # API 1: Marine Data (Waves & Wind)
    marine_url = "https://marine-api.open-meteo.com/v1/marine"
    # API 2: Forecast Data (Sea Temperature)
    weather_url = "https://api.open-meteo.com/v1/forecast"
    
    marine_params = {
        "latitude": lat,
        "longitude": lon,
        "current": ["wave_height"],
        "hourly": ["wave_height", "wind_speed_10m"],
        "timezone": "auto"
    }
    
    temp_params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "surface_temperature",
        "timezone": "auto"
    }
    
    try:
        # Fetch Marine Data
        m_res = requests.get(marine_url, params=marine_params, timeout=10)
        m_data = m_res.json()
        
        # Fetch Temperature Data
        t_res = requests.get(weather_url, params=temp_params, timeout=10)
        t_data = t_res.json()
        
        # 1. Process Waves & Wind
        current_wave = float(m_data.get('current', {}).get('wave_height', 0.0))
        hourly_waves = [float(w) for w in m_data.get('hourly', {}).get('wave_height', [])[:24] if w is not None]
        hourly_winds = [float(w) for w in m_data.get('hourly', {}).get('wind_speed_10m', [])[:24] if w is not None]
        
        max_wave_24h = max(hourly_waves) if hourly_waves else current_wave
        max_wind_24h = max(hourly_winds) if hourly_winds else 0.0
        
        # 2. Process Sea Temperature
        # We take the current hour temperature
        temp_list = t_data.get('hourly', {}).get('surface_temperature', [])
        sea_temp = float(temp_list[0]) if temp_list else 28.0 # Fallback to Kerala average
        
        return {
            "current_wave": current_wave,
            "max_wave_24h": max_wave_24h,
            "max_wind_24h": max_wind_24h,
            "sea_temp": sea_temp,
            "status": "Success"
        }

    except Exception as e:
        print(f"❌ SATELLITE ERROR: {e}")
        return {"status": "Error", "message": str(e)}