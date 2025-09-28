# SmartSaha/views/external_data.py
from django.contrib.sites import requests
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets

from SmartSaha.models import Parcel, SoilData, ClimateData
from SmartSaha.services.climate import get_climate_data
from SmartSaha.services.soilsGrids import get_soil_data
import requests


class SoilDataView(APIView):
    def get(self, request):
        lon = request.query_params.get("lon")
        lat = request.query_params.get("lat")
        if not lon or not lat:
            return Response({"error": "Missing lon/lat"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = get_soil_data(lon, lat)
            return Response(data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ClimateDataView(APIView):
    def get(self, request):
        lon = request.query_params.get("lon")
        lat = request.query_params.get("lat")
        start = request.query_params.get("start")
        end = request.query_params.get("end")
        if not (lon and lat and start and end):
            return Response({"error": "Missing lon/lat/start/end"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = get_climate_data(lon, lat, start, end)
            return Response(data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DataViewSet(viewsets.ViewSet):

    @action(detail=True, methods=["post"])
    def fetch_soil(self, request, pk=None):
        parcel = Parcel.objects.get(pk=pk)
        # Récupère le premier point du JSON
        first_point = parcel.points[0]  # si points est une liste
        lat, lon = first_point["lat"], first_point["lng"]
        url = f"https://rest.isric.org/soilgrids/v2.0/properties/query?lon={lon}&lat={lat}&property=phh2o&property=soc&property=nitrogen&property=sand&property=clay&property=silt&depth=0-5cm&value=mean"
        resp = requests.get(url)
        if resp.status_code == 200:
            soil = SoilData.objects.create(parcel=parcel, data=resp.json())
            return Response({"status": "soil stored", "id": soil.id})
        return Response({"error": "soil api failed"}, status=resp.status_code)

    @action(detail=True, methods=["post"])
    def fetch_climate(self, request, pk=None):
        parcel = Parcel.objects.get(pk=pk)
        # Récupère le premier point du JSON
        first_point = parcel.points[0]  # si points est une liste
        lat, lon = first_point["lat"], first_point["lng"]

        start = request.data.get("start", "20250101")
        end = request.data.get("end", "20250107")

        url = f"https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M,PRECTOTCORR&community=AG&longitude={lon}&latitude={lat}&start={start}&end={end}&format=JSON"
        resp = requests.get(url)
        if resp.status_code == 200:
            climate = ClimateData.objects.create(parcel=parcel, data=resp.json(), start=start, end=end)
            return Response({"status": "climate stored", "id": climate.id})
        return Response({"error": "climate api failed"}, status=resp.status_code)