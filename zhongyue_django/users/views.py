from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import UserSerializer, LoginSerializer, RoleSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.exceptions import TokenError
import logging
from .models import AsyncRoute, Role
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.core.paginator import Paginator
import json
from django.contrib.auth import get_user_model
import time
from django.core.files.base import ContentFile
import base64
import uuid
import os
from django.conf import settings
from django.core.files.storage import default_storage

User = get_user_model()
logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
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
                        'avatar': user_data['avatar'],
                        'username': user_data['username'],
                        'nickname': user_data['nickname'],
                        'roles': user_data['roles'],
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
        refresh_token = request.data.get('refreshToken')
        if not refresh_token:
            logger.error("Refresh token is missing")
            return Response({"success": False, "message": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            access_token = str(token.access_token)
            new_refresh_token = str(token)
            expires_timestamp = token.access_token.payload['exp']
            expires = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(expires_timestamp))

            response_data = {
                "success": True,
                "data": {
                    "accessToken": access_token,
                    "refreshToken": new_refresh_token,
                    "expires": expires
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

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_user_list(request):
    data = json.loads(request.body)
    username = data.get('username', '')
    status = data.get('status', 1)
    dept_id = data.get('deptId')
    page = data.get('currentPage', 1)
    page_size = data.get('pageSize', 10)

    users = User.objects.all()
    if username:
        users = users.filter(username__icontains=username)
    if status is not None:
        users = users.filter(status=status)
    if dept_id:
        users = users.filter(dept_id=dept_id)

    paginator = Paginator(users, page_size)
    users_page = paginator.get_page(page)

    serializer = UserSerializer(users_page, many=True)
    return JsonResponse({
        'success': True,
        'data': {
            'list': serializer.data,
            'total': paginator.count,
            'pageSize': page_size,
            'currentPage': page
        }
    })

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_role_ids(request):
    data = json.loads(request.body)
    user_id = data.get('userId')
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            role_names = user.roles  # 这里存储的是角色名称列表
            
            return JsonResponse({
                'success': True,
                'data': role_names
            })
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
    else:
        return JsonResponse({
            'success': False,
            'message': 'userId is required'
        }, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_user(request):
    data = json.loads(request.body)
    user_data = {
        'username': data.get('username'),
        'email': data.get('email'),
        'password': data.get('password'),
        'first_name': data.get('first_name', ''),
        'last_name': data.get('last_name', ''),
        'nickname': data.get('nickname'),
        'avatar': data.get('avatar', ''),
        'phone': data.get('phone'),
        'sex': data.get('sex'),
        'status': data.get('status'),
        'dept_id': data.get('dept_id'),
        'remark': data.get('remark'),
        'roles': data.get('roles', []),
        'user_groups': data.get('user_groups', []),
        'user_permissions': data.get('user_permissions', [])
    }
    user_serializer = UserSerializer(data=user_data)
    
    if user_serializer.is_valid():
        user = user_serializer.save()

        return JsonResponse({'success': True, 'data': user_serializer.data}, status=status.HTTP_201_CREATED)
    return JsonResponse({'success': False, 'errors': user_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_user(request):
    data = json.loads(request.body)
    user_id = data.get('id')
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    user_data = {
        'username': data.get('username'),
        'email': data.get('email'),
        'nickname': data.get('nickname'),
        'phone': data.get('phone'),
        'sex': data.get('sex'),
        'status': data.get('status'),
        'remark': data.get('remark'),
        'dept_id': data.get('parentId'),
        'roles': data.get('roles', [])
    }
    
    user_serializer = UserSerializer(user, data=user_data, partial=True)
    if user_serializer.is_valid():
        updated_user = user_serializer.save()
        return JsonResponse({'success': True, 'data': UserSerializer(updated_user).data}, status=status.HTTP_200_OK)
    return JsonResponse({'success': False, 'errors': user_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_user(request):
    
    data = json.loads(request.body)
    user_id = data.get('id')
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        return JsonResponse({'success': True, 'message': 'User deleted successfully'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reset_password(request):
    data = json.loads(request.body)
    user_id = data.get('id')
    new_password = data.get('newPwd')
    
    try:
        user = User.objects.get(id=user_id)
        user.set_password(new_password)
        user.save()
        return JsonResponse({'success': True, 'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_avatar(request):
    if not os.path.exists(settings.MEDIA_ROOT):
        os.makedirs(settings.MEDIA_ROOT)
        
    data = json.loads(request.body)
    user_id = data.get('id')
    avatar_data = data.get('avatar')
    print(avatar_data)
    
    try:
        user = User.objects.get(id=user_id)
        
        # 解码base64图片数据
        format, imgstr = avatar_data.split(';base64,')
        ext = format.split('/')[-1]
        
        # 生成唯一的文件名
        filename = f"{uuid.uuid4()}.{ext}"
        
        # 保存文件
        data = ContentFile(base64.b64decode(imgstr))
        file_path = default_storage.save(f'avatars/{filename}', data)
        
        # 更新用户的头像字段
        full_url = request.build_absolute_uri(settings.MEDIA_URL + file_path)
        user.avatar = full_url
        user.save()
        
        return JsonResponse({
            'success': True,
            'data': [{
                'avatar_url': full_url
            }]
        }, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'data': []
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_role_list(request):
    data = json.loads(request.body)
    name = data.get('name', '')
    status = data.get('status')
    code = data.get('code')
    page = data.get('currentPage', 1)
    page_size = data.get('pageSize', 10)

    roles = Role.objects.all().order_by('-create_time')  # 按创建时间降序排序
    if name:
        roles = roles.filter(name__icontains=name)
    if status is not None:
        roles = roles.filter(status=status)
    if code:
        roles = roles.filter(code=code)

    paginator = Paginator(roles, page_size)
    roles_page = paginator.get_page(page)

    serializer = RoleSerializer(roles_page, many=True)
    return JsonResponse({
        'success': True,
        'data': {
            'list': serializer.data,
            'total': paginator.count,
            'pageSize': page_size,
            'currentPage': int(page)
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_roles(request):
    roles = Role.objects.all().values('id', 'name')
    return JsonResponse({
        'success': True,
        'data': list(roles)
    })

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_user_roles(request):
    data = json.loads(request.body)
    user_id = data.get('userId')
    role_ids = data.get('ids', [])  # 前端传来的角色ID列表

    try:
        user = User.objects.get(id=user_id)
        roles = Role.objects.filter(id__in=role_ids)
        role_names = [role.name for role in roles]
        user.roles = role_names  # 更新用户的角色列表为角色名称
        user.save()

        return JsonResponse({
            'success': True,
            'message': 'User roles updated successfully'
        }, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Role.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'One or more roles not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
