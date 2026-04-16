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
                "Ton rôle est d'aider les utilisateurs en fournissant des informations précises "
                "uniquement sur les hôtels de notre catalogue ci-dessous.\n\n"
                f"CONTEXTE DES HÔTELS :\n{hotel_data}\n\n"
                "RÈGLES STRICTES :\n"
                "1. Réponds UNIQUEMENT en utilisant les informations fournies dans le CONTEXTE.\n"
                "2. Si l'utilisateur pose une question qui n'est pas liée aux hôtels listés "
                "ou demande des choses générales (météo, actualités, code, etc.), réponds "
                "poliment que tu n'es là que pour aider avec les informations d'hôtels de Red Product.\n"
                "3. Réponds toujours en français.\n"
                "4. Sois concis, professionnel et serviable."
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
