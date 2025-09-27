# SmartSaha/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from SmartSaha.models import ParcelCrop
from SmartSaha.services import YieldForecastService


class YieldForecastView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, parcel_crop_id):
        # Vérifier que le parcel de ce ParcelCrop appartient à l'utilisateur connecté
        try:
            parcel_crop = ParcelCrop.objects.get(
                id=parcel_crop_id,
                parcel__owner=request.user  # Vérification via la relation Parcel
            )
        except ParcelCrop.DoesNotExist:
            return Response(
                {"error": "Cette parcelle n'existe pas ou n'appartient pas à l'utilisateur"},
                status=403
            )

        # Calculer la prévision
        service = YieldForecastService(parcel_crop)
        forecast = service.save_forecast(days_ahead=7)
        if forecast:
            return Response({
                "parcelCrop": forecast.parcelCrop.id,
                "forecast_date": forecast.forecast_date,
                "predicted_yield": round(forecast.predicted_yield, 2)
            })
        else:
            return Response({"error": "Pas assez de données pour prévoir"}, status=400)
