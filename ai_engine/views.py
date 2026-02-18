from django.shortcuts import render
from django.http import JsonResponse
from .utils import get_marine_weather
from .models import SavedSpot
import json

def fisherman_dashboard(request):
    # --- 💾 SAVE SPOT LOGIC (AJAX POST) ---
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            post_data = json.loads(request.body)
            SavedSpot.objects.create(
                name=post_data.get('name', 'Marked Location'),
                lat=post_data.get('lat'),
                lon=post_data.get('lon'),
                fish_score=post_data.get('fish_score', 0)
            )
            return JsonResponse({'status': 'Success', 'message': 'Spot saved!'})
        except Exception as e:
            return JsonResponse({'status': 'Error', 'message': str(e)}, status=400)

    # --- 🌍 LIVE MAP & WEATHER LOGIC (GET) ---
    lat = float(request.GET.get('lat', 9.9312))
    lon = float(request.GET.get('lon', 76.2673))
    
    data = get_marine_weather(lat, lon)
    
    if data.get('status') == "Success":
        wave = data['current_wave']
        max_wave = data['max_wave_24h']
        max_wind = data['max_wind_24h']
        temp = data['sea_temp']
        
        # --- 🚨 DISASTER LOGIC ---
        if max_wave > 2.5 or max_wind > 45:
            risk_level, color, msg = "HIGH ALERT", "red", "🚨 STAY ASHORE: Heavy storm predicted."
        elif max_wave > 1.5 or max_wind > 30:
            risk_level, color, msg = "CAUTION", "orange", "⚠️ Rough sea conditions incoming."
        else:
            risk_level, color, msg = "SAFE", "green", "✅ Conditions are clear for sailing."

        # --- 🐟 FISH PRODUCTIVITY AI LOGIC ---
        fish_score = 100
        temp_diff = abs(temp - 27.5)
        fish_score -= (temp_diff * 15) 
        if wave > 1.0: fish_score -= 20
        if wave > 1.8: fish_score -= 40
        fish_score = max(0, min(100, int(fish_score)))
        
        if fish_score > 80:
            fish_msg = "🔥 EXCELLENT: High fish activity detected."
        elif fish_score > 50:
            fish_msg = "🎣 GOOD: Average chances of a Fish catch."
        else:
            fish_msg = "📉 POOR: Low fish movement in this zone."

        # Prepare context for BOTH Json and Render
        context = {
            'risk_level': risk_level,
            'color': color,
            'message': msg,
            'wave': wave,
            'max_wave': max_wave,
            'max_wind': max_wind,
            'sea_temp': temp,
            'fish_score': fish_score,
            'fish_message': fish_msg,
            'lat': lat,
            'lon': lon,
        }

        # --- ⚡ THE FIX: CHECK REQUEST TYPE ---
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # ONLY return the simple data for the map click (No database QuerySets here!)
            return JsonResponse(context)

        # For the regular page load, add the database list for the sidebar
        context['saved_locations'] = SavedSpot.objects.all().order_by('-created_at')
        return render(request, 'dashboard/index.html', context)

    else:
        # Handle API/Satellite Error
        error_context = {'risk_level': "OFFLINE", 'color': 'grey', 'message': "Satellite error."}
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse(error_context)
        return render(request, 'dashboard/index.html', error_context)