import httpx
import os
from django.conf import settings

from SmartSaha.services.context_builder import ContextBuilder

BASE_PROMPT = """
Tu es un ingenieur agronome expert à Madagascar.
Reponds toujours de maniere précise, pratique, court et adaptee aux conditions locales :
- Inclue les saisons, sols et pratiques agricoles typiques.
- Ne donne jamais de reponses vagues.
- si cest un estimation, calcule avec les donnees qu on te fourni et tes connaissances
- Si tu ne sais pas, indique clairement que l’information n’est pas disponible.
"""

class DeepSeekClient:
    def __init__(self, model="deepseek/deepseek-r1:free"):
        self.api_key = getattr(settings, "OPENROUTER_API_KEY", None) or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY manquant dans settings ou .env")

        self.base_url = "https://openrouter.ai/api/v1"
        self.model = model

    def ask(self, question: str, parcel_uuid: str = None, user_modules: dict = None):
        context_data = ContextBuilder.build_context(parcel_uuid, user_modules)
        print(context_data)
        full_prompt = f"{BASE_PROMPT}\n\nDonnées locales:\n{context_data}\n\nQuestion: {question}\nRéponse:"
        print(full_prompt)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": full_prompt}]
        }

        with httpx.Client(timeout=60.0) as client:
            try:
                response = client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
                print("Status:", response.status_code)
                print("Response:", response.text[:500])  # debug rapide
                response.raise_for_status()
                data = response.json()
            except httpx.HTTPStatusError as e:
                return f"Erreur API OpenRouter ({e.response.status_code}): {e.response.text}"
            except Exception as e:
                return f"Erreur interne: {str(e)}"

        # Retourne le contenu de la réponse
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            return "Aucune réponse reçue du modèle."
