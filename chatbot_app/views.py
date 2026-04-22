import os
import google.generativeai as genai
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .utils import get_hotel_context

class ChatbotView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_message = request.data.get('message')

        if not user_message:
            return Response(
                {"error": "Le message est obligatoire."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key or api_key == "VOTRE_CLE_API_ICI":
            return Response(
                {"error": "Clé API Gemini non configurée sur le serveur."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-flash-latest')

            hotel_data = get_hotel_context()

            system_instruction = (
                "Tu es l'assistant IA de Red Product, une plateforme de gestion d'hôtels. "
                "Ton rôle est d'aider les utilisateurs. Tu es autorisé à répondre à toutes les questions, "
                "y compris sur l'actualité, la météo et les hôtels du monde entier.\n\n"
                f"CONTEXTE DES HÔTELS RED PRODUCT :\n{hotel_data}\n\n"
                "RÈGLES :\n"
                "1. Tu peux discuter librement de l'actualité, de la météo et des hôtels partout dans le monde.\n"
                "2. Utilise les informations du catalogue Red Product quand cela est pertinent.\n"
                "3. Réponds toujours en français.\n"
                "4. Sois concis, professionnel et serviable.\n"
                "5. MISE EN FORME : Pour mettre en valeur du texte, utilise exclusivement le GRAS (**texte**). "
                "N'utilise JAMAIS d'astérisques simples (*) pour l'italique ou pour mettre en valeur. "
                "Évite d'afficher des caractères d'astérisques si possible, sauf pour le format gras standard."
            )

            prompt = f"{system_instruction}\n\nUtilisateur : {user_message}\nAssistant :"
            response = model.generate_content(prompt)

            return Response({
                "reply": response.text,
                "status": "success"
            })

        except Exception as e:
            return Response(
                {"error": f"Erreur lors de la communication avec l'IA : {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
