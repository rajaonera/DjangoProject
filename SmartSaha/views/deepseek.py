import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from SmartSaha.services import DeepSeekClient
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

deepseek = DeepSeekClient()

class AgronomyAssistantAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        question = request.data.get("question")
        question_type = request.data.get("question_type", "general")
        parcel_id = request.data.get("parcel_id")
        crop_name = request.data.get("crop_name")
        user_modules = request.data.get("user_modules", {})

        if not question:
            return Response({"error": "No question provided."}, status=status.HTTP_400_BAD_REQUEST)

        # On passe tout à DeepSeekClient
        answer = deepseek.ask(
            question=question,
            parcel_uuid=parcel_id,
            user_modules=user_modules
        )

        return Response({
            "answer": answer,
            "meta": {
                "question_type": question_type,
                "parcel_id": parcel_id,
                "crop_name": crop_name,
                "modules": user_modules
            }
        }, status=status.HTTP_200_OK)

@login_required(login_url="login")
def assistant_agronome_page(request):
    """
    Vue qui rend la page HTML avec le formulaire.
    """
    return render(request, "assistant_agronome.html")


@csrf_exempt
@login_required(login_url="login")
def assistant_agronome_api(request):
    """
    Vue qui reçoit la question, appelle le moteur IA et renvoie la réponse JSON.
    """
    if request.method == "POST":
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Payload JSON invalide"}, status=400)

        question = payload.get("question")
        question_type = payload.get("question_type")
        parcel_id = payload.get("parcel_id")
        crop_name = payload.get("crop_name")
        user_modules = payload.get("user_modules", {})

        if not question or not question_type:
            return JsonResponse({"error": "Champs obligatoires manquants"}, status=400)

            # On passe tout à DeepSeekClient
        response = deepseek.ask(
            question=question,
            parcel_uuid=parcel_id,
            user_modules=user_modules
        )

        return JsonResponse(response, safe=False)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)