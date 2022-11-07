from django.shortcuts import render

from .model import get_prediction
# For when we hook up the model

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
# Create your views here.

class PredictionAPIView(APIView):
    def post(self, request, *args, **kwargs):
        zipc  = request.data.get('zipcode')
        beds  = request.data.get('beds')
        baths = request.data.get('baths')
        sqft  = request.data.get('sqft')

        pred = get_prediction(zipc, beds, baths, sqft)
        if pred['result']:
            return Response(pred['data'], status=status.HTTP_202_ACCEPTED)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)



