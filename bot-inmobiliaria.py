import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests

app = Flask(__name__)

API_KEY_ANTHROPIC = os.environ.get("ANTHROPIC_KEY") 
url_anthropic = "https://api.anthropic.com/v1/messages"

instrucciones_santi = "Eres Santi, asistente de Bienes Raíces Coatzacoalcos. Da respuestas cortas y persuasivas. Propiedades: 1. Casa Lomas de Barrillas $1,200,000. 2. Depa Malecón renta $8,500. Pregunta presupuesto y método de pago."

@app.route('/whatsapp', methods=['POST'])
def bot():
    mensaje_cliente = request.values.get('Body', '')
    
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
        "model": "claude-3-5-sonnet-20240620", 
        "max_tokens": 300,
        "system": instrucciones_santi,
        "messages": [{"role": "user", "content": mensaje_cliente}]
    }
    
    try:
        response = requests.post(url_anthropic, headers=headers, json=payload)
        if response.status_code == 200:
            respuesta_ia = response.json()["content"][0]["text"]
        else:
            respuesta_ia = f"🚨 Error Anthropic {response.status_code}:\n{response.text}"
    except Exception as e:
        respuesta_ia = f"🚨 Falla en el servidor:\n{str(e)}"

    resp = MessagingResponse()
    resp.message(respuesta_ia)
    return str(resp)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
