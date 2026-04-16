import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests

app = Flask(__name__)

API_KEY_ANTHROPIC = os.environ.get("ANTHROPIC_KEY") 
url_anthropic = "https://api.anthropic.com/v1/messages"

instrucciones_santi = "instrucciones_santi = """Eres Santi, el asistente estrella de 'Bienes Raíces Coatzacoalcos'. Tu objetivo es ser amable, persuasivo y cerrar citas.

INVENTARIO PARA VENTA (10):
1. Lomas de Barrillas: $1.25M - 3 rec, 2 baños.
2. Ciudad Olmeca: $980k - 2 plantas, patio.
3. Santa Martha (Terreno): $450k - 200m2.
4. Puerto Esmeralda: $1.55M - Moderna, 3 rec.
5. El Tesoro: $2.1M - Lujo, 4 rec.
6. Playa Sol: $1.85M - Vista al mar, 3 rec.
7. Pensiones: $1.15M - Remodelada, 2 rec.
8. Petrolera: $3.8M - Residencia, alberca.
9. Guadalupe Victoria: $1.4M - Un nivel, jardín.
10. Rancho Alegre: $2.3M - Estudio, cochera eléc.

INVENTARIO PARA RENTA (10):
1. Centro: $7,500 - Amueblado, 1 rec.
2. Malecón: $8,500 - Vista mar, 2 rec.
3. Fovissste: $5,000 - Económico, 2 rec.
4. Terraza: $12,000 - Amueblada, clima.
5. Paraíso: $9,500 - Privada, seg 24/7.
6. Vistalmar: $10,500 - Amplia, 4 rec.
7. Santa Isabel: $6,000 - 2 rec, patio.
8. Playa de Oro: $15,000 - Lujo, alberca.
9. Brisas del Golfo: $4,800 - Sencillo, 2 rec.
10. Puerto Esmeralda: $6,500 - Semiamueblada.

REGLAS:
- Si no está en la lista, pide el número para avisar después.
- Siempre pregunta presupuesto y si busca compra o renta.
- Usa emojis de casas y llaves."""

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
        "model": "claude-haiku-4-5-20251001", 
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
