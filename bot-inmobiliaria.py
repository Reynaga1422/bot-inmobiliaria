import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests

app = Flask(__name__)

API_KEY_ANTHROPIC = os.environ.get("ANTHROPIC_KEY") 
url_anthropic = "https://api.anthropic.com/v1/messages"

instrucciones_santi = "Eres Santi, asistente de Bienes Raíces Coatzacoalcos. Da respuestas cortas y persuasivas. Propiedades: 1. Casa Lomas de Barrillas $1,200,000. 2. Depa Malecón renta $8,500. Pregunta presupuesto y método de pago."

historial = []

@app.route('/whatsapp', methods=['POST'])
def bot():
    global historial
    mensaje_cliente = request.values.get('Body', '')
    historial.append({"role": "user", "content": mensaje_cliente})
    
    # Escáner 1: Revisar si la llave de Anthropic se guardó bien en Render
    if not API_KEY_ANTHROPIC:
        resp = MessagingResponse()
        resp.message("Error: No se encontró la llave ANTHROPIC_KEY en Render.")
        return str(resp)

    headers = {
        "x-api-key": API_KEY_ANTHROPIC,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    payload = {
        "model": "claude-3-haiku-20240307", 
        "max_tokens": 300,
        "system": instrucciones_santi,
        "messages": historial
    }
    
    # Escáner 2: Ver exactamente qué responde Anthropic
    try:
        response = requests.post(url_anthropic, headers=headers, json=payload)
        if response.status_code == 200:
            respuesta_ia = response.json()["content"][0]["text"]
            historial.append({"role": "assistant", "content": respuesta_ia})
        else:
            print("🚨 ERROR ANTHROPIC:", response.text)
            respuesta_ia = f"Falla en Anthropic. Código: {response.status_code}"
    except Exception as e:
        print("🚨 ERROR PYTHON:", e)
        respuesta_ia = "Falla de conexión en código."

    resp = MessagingResponse()
    resp.message(respuesta_ia)
    return str(resp)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
