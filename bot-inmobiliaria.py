import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests

app = Flask(__name__)

# --- CONFIGURACIÓN DE IA SEGURA ---
# Ahora la llave está protegida. El servidor la inyectará automáticamente.
API_KEY_ANTHROPIC = os.environ.get("ANTHROPIC_KEY") 
url_anthropic = "https://api.anthropic.com/v1/messages"

instrucciones_santi = """Eres "Santi", el asistente virtual de Bienes Raíces Coatzacoalcos. Tu objetivo es perfilar a los interesados en propiedades.
Propiedades:
1. Casa Lomas de Barrillas: 3 recámaras, $1,200,000 MXN.
2. Depa Malecón: 2 recámaras, renta $8,500 MXN.

Reglas: 
- Respuestas cortas, amables y persuasivas.
- Antes de dar una cita, DEBES preguntar su presupuesto y si usarán crédito (Infonavit/Bancario) o pago de contado.
- Si ya te dieron esos datos, diles que un asesor humano confirmará la cita pronto."""

historial = []

@app.route('/whatsapp', methods=['POST'])
def bot():
    global historial
    
    mensaje_cliente = request.values.get('Body', '')
    historial.append({"role": "user", "content": mensaje_cliente})
    
    headers = {
        "x-api-key": API_KEY_ANTHROPIC,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    payload = {
        "model": "claude-sonnet-4-6", 
        "max_tokens": 300,
        "system": instrucciones_santi,
        "messages": historial
    }
    
    respuesta_ia = "Lo siento, estoy en mantenimiento."
    try:
        response = requests.post(url_anthropic, headers=headers, json=payload)
        if response.status_code == 200:
            respuesta_ia = response.json()["content"][0]["text"]
            historial.append({"role": "assistant", "content": respuesta_ia})
    except Exception as e:
        print("Error técnico:", e)

    resp = MessagingResponse()
    resp.message(respuesta_ia)
    return str(resp)

if __name__ == '__main__':
    # Usamos el puerto que el servidor en la nube nos asigne
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
