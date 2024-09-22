from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import UserSerializer, LoginSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.exceptions import TokenError
import logging
import datetime
from .models import AsyncRoute
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    # 保持原有的 post 方法不变

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
            if user:
                refresh = RefreshToken.for_user(user)
                user_data = UserSerializer(user).data
                return Response({
                    'success': True,
                    'data': {
                        'avatar': user_data['profile']['avatar'],
                        'username': user_data['username'],
                        'nickname': user_data['profile']['nickname'],
                        'roles': user_data['profile']['roles'],
                        'permissions': user_data['profile']['permissions'],
                        'accessToken': str(refresh.access_token),
                        'refreshToken': str(refresh),
                        'expires': refresh.access_token.payload['exp']
                    }
                })
            return Response({'success': False, 'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class RefreshTokenView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            logger.error("Refresh token is missing")
            return Response({"success": False, "message": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            access_token = str(token.access_token)
            new_refresh_token = str(token)
            expires = datetime.fromtimestamp(token.access_token.payload['exp'])

            response_data = {
                "success": True,
                "data": {
                    "accessToken": access_token,
                    "refreshToken": new_refresh_token,
                    "expires": expires.strftime('%Y/%m/%d %H:%M:%S')
                }
            }
            logger.info(f"Refresh token response: {response_data}")
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            return Response({"success": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_async_routes(request):
    top_level_routes = AsyncRoute.objects.filter(parent=None)
    routes_data = [route.to_dict() for route in top_level_routes]
    return Response({
        "success": True,
        "data": routes_data
    })

# Create your views here.
