from django.shortcuts import render # type: ignore
from rest_framework.views import APIView # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework import status # type: ignore
from rest_framework_simplejwt.tokens import RefreshToken # type: ignore
from django.contrib.auth import authenticate # type: ignore
from .serializers import UserSerializer, LoginSerializer, RoleSerializer, DepartmentSerializer  
from django.utils.decorators import method_decorator # type: ignore
from django.views.decorators.csrf import csrf_exempt # type: ignore
from rest_framework_simplejwt.exceptions import TokenError # type: ignore
import logging
from .models import AsyncRoute, Role, Department, Permission
from rest_framework.decorators import api_view, permission_classes # type: ignore
from rest_framework.permissions import IsAuthenticated # type: ignore
from django.http import JsonResponse # type: ignore
from django.core.paginator import Paginator # type: ignore
import json
from django.contrib.auth import get_user_model # type: ignore
import time
from django.core.files.base import ContentFile # type: ignore
import base64
import uuid
import os
from django.conf import settings # type: ignore
from django.core.files.storage import default_storage # type: ignore
from django.utils import timezone # type: ignore
from django.db import transaction # type: ignore
from django.db.models import Model # type: ignore
from django.db import models # type: ignore
from django.db.models import Q # type: ignore
from storages.backends.s3boto3 import S3Boto3Storage # type: ignore

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
    top_level_routes = AsyncRoute.objects.filter(parent=None)  # 只获取启用的顶路由
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
    status = data.get('status')
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
    user_data = serializer.data
    
    # 确保每个用户都有 dept 字段，即使它可能为空
    for user in user_data:
        if 'dept' not in user or user['dept'] is None:
            user['dept'] = {'id': None, 'name': None}
    return JsonResponse({
        'success': True,
        'data': {
            'list': user_data,
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
            role_names = user.roles  # 假设这是角色名称列表
            
            # 获取对应的角色ID
            role_ids = Role.objects.filter(name__in=role_names).values_list('id', flat=True)
            
            return JsonResponse({
                'success': True,
                'data': list(role_ids)  # 转换为列表，因为 QuerySet 不能直接 JSON 序列化
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
    
    # 只更新提供的字段
    user_data = {}
    for field in ['username', 'email', 'nickname', 'phone', 'sex', 'status', 'remark', 'dept_id', 'roles']:
        if field in data:
            user_data[field] = data[field]
    
    # 特殊处理 parentId，如果存在则映射到 dept_id
    if 'parentId' in data:
        user_data['dept_id'] = data['parentId']
    
    user_serializer = UserSerializer(user, data=user_data, partial=True)
    if user_serializer.is_valid():
        updated_user = user_serializer.save()
        return JsonResponse({'success': True, 'data': UserSerializer(updated_user).data}, status=status.HTTP_200_OK)
    
    print("Serializer errors:", user_serializer.errors)  # 打印序列化器错误，用于调试
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
    try:
        data = json.loads(request.body)
        user_id = data.get('id')
        avatar_data = data.get('avatar')
        
        if not avatar_data or not user_id:
            return JsonResponse({
                'success': False,
                'message': '参数不完整'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 获取用户信息
            user = User.objects.get(id=user_id)
            # 优先使用昵称，如果没有昵称则使用用户名
            file_prefix = user.nickname or user.username
            
            # 生成时间戳
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            
            format, imgstr = avatar_data.split(';base64,')
            ext = format.split('/')[-1].lower()
            
            # 验证文件格式
            if ext not in ['jpg', 'jpeg', 'png', 'gif']:
                return JsonResponse({
                    'success': False,
                    'message': '不支持的图片格式'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 生成文件名: avatars/用户名或昵称_时间戳.扩展名
            filename = f"avatars/{file_prefix}_{timestamp}.{ext}"
            
            # 解码并保存文件
            content = base64.b64decode(imgstr)
            file_obj = ContentFile(content)
            
            # 使用事务保证数据一致性
            with transaction.atomic():
                storage = default_storage
                file_path = storage.save(filename, file_obj)
                
                # 更新用户头像
                User.objects.filter(id=user_id).update(avatar=file_path)
                
                # 修改返回格式,匹配前端期望的数据结构
                return JsonResponse({
                    'success': True,
                    'data': [{
                        'avatar_url': file_path  # 返回相对路径即可,前端会通过 getMinioUrl 处理
                    }]
                })
                
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '用户不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Upload error: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'上传失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': '无效的请求数据'
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
    if status != '':
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

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_role(request):
    try:
        with transaction.atomic():
            data = json.loads(request.body)
            role = Role.objects.create(
                name=data['name'],
                code=data['code'],
                status=data.get('status', 1),
                remark=data.get('remark', '')
            )
            # 信号处理器会自动创建对应的权限记录
            return JsonResponse({
                'success': True,
                'message': '角色创建成功',
                'data': {
                    'id': role.id,
                    'name': role.name,
                    'code': role.code,
                    'status': role.status,
                    'remark': role.remark
                }
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'角色创建失败: {str(e)}'
        }, status=400)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_role(request, role_id):
    try:
        with transaction.atomic():
            role = Role.objects.get(id=role_id)
            data = json.loads(request.body)
            
            # 更新角色信息
            role.name = data.get('name', role.name)
            role.code = data.get('code', role.code)
            role.status = data.get('status', role.status)
            role.remark = data.get('remark', role.remark)
            role.save()
            
            return JsonResponse({
                'success': True,
                'message': '角色更新成功',
                'data': {
                    'id': role.id,
                    'name': role.name,
                    'code': role.code,
                    'status': role.status,
                    'remark': role.remark
                }
            })
    except Role.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '角色不存在'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'角色更新失败: {str(e)}'
        }, status=400)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_role(request):
    try:
        with transaction.atomic():
            data = json.loads(request.body)
            role_id = data.get('id')
            
            role = Role.objects.get(id=role_id)
            role_name = role.name
            
            # 删除角色（会触发信号处理器）
            role.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'角色 {role_name} 已删除'
            })
    except Role.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '角色不存在'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'删除角色失败: {str(e)}'
        }, status=400)
def convert_to_frontend_format(data):
    """将后端字段名转换为前端所需的格式"""
    field_mapping = {
        'parent_id': 'parentId',
        'create_time': 'createTime'
    }
    if isinstance(data, list):
        return [convert_to_frontend_format(item) for item in data]
    elif isinstance(data, dict):
        result = {}
        for key, value in data.items():
            new_key = field_mapping.get(key, key)
            if new_key == 'createTime':
                if isinstance(value, str):
                    value = timezone.datetime.fromisoformat(value.replace('Z', '+00:00'))
                value = int(value.timestamp() * 1000) if value else None
            elif new_key == 'parentId':
                value = value or 0  # 如果 parent_id 为 None，则设置为 0
            result[new_key] = value
        return result
    return data

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_dept_list(request):
    departments = Department.objects.all()
    serializer = DepartmentSerializer(departments, many=True)
    converted_data = convert_to_frontend_format(serializer.data)
    return JsonResponse({
        'success': True,
        'data': converted_data
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_dept(request):
    data = json.loads(request.body)
    parent_id = data.get('parentId')
    if parent_id == 0:
        parent_id = None
    
    backend_data = {
        'parent_id': parent_id,
        'name': data.get('name'),
        'sort': data.get('sort'),
        'phone': data.get('phone'),
        'principal': data.get('principal'),
        'email': data.get('email'),
        'status': data.get('status'),
        'type': data.get('type', 3),
        'remark': data.get('remark')
    }
    serializer = DepartmentSerializer(data=backend_data)
    if serializer.is_valid():
        serializer.save()
        converted_data = convert_to_frontend_format(serializer.data)
        return JsonResponse({'success': True, 'data': converted_data}, status=status.HTTP_201_CREATED)
    return JsonResponse({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_dept(request):
    data = json.loads(request.body)
    dept_id = data.get('id')
    
    if dept_id is None:
        return JsonResponse({'success': False, 'message': 'Department ID is required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        department = Department.objects.get(id=dept_id)
        
        # 提取需要更新的字段
        backend_data = {
            'parent_id': data.get('parentId'),
            'name': data.get('name'),
            'sort': data.get('sort'),
            'phone': data.get('phone'),
            'principal': data.get('principal'),
            'email': data.get('email'),
            'status': data.get('status'),
            'type': data.get('type', department.type),  # 如果没有提供，保持原来的值
            'remark': data.get('remark')
        }
        
        # 如果 parentId 为 0，将其置为 None（表示顶级部门）
        if backend_data['parent_id'] == 0:
            backend_data['parent_id'] = None
        
        serializer = DepartmentSerializer(department, data=backend_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            converted_data = convert_to_frontend_format(serializer.data)
            return JsonResponse({'success': True, 'data': converted_data}, status=status.HTTP_200_OK)
        return JsonResponse({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Department.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Department not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_dept(request):
    dept_id = json.loads(request.body)

    try:
        department = Department.objects.get(id=dept_id)
        department.delete()
        return JsonResponse({'success': True, 'message': 'Department deleted successfully'}, status=status.HTTP_200_OK)
    except Department.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Department not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_roles(request):
    user = request.user
    roles = user.roles
    return Response({
        'success': True,
        'data': {
            'roles': roles
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_permissions_list(request):
    """获取所有角色的权限列表"""
    try:
        # 获取所有启用的角色
        roles = Role.objects.filter(status=1)
        permissions_data = []

        for role in roles:
            # 构建权限数据结构
            permissions = {
                'expense': {
                    'data': {
                        'view_all': False,
                        'view_by_location': False,
                        'view_department_submissions': False,
                        'view_own': False
                    },
                    'action': {
                        'create': False,
                        'edit': False,
                        'delete': False,
                        'audit': False,
                        'cancel_audit': False,
                        'view_receipt': False
                    }
                },
                'customer': {
                    'data': {
                        'view_all': False,
                        'view_by_location': False,
                        'view_department_submissions': False,
                        'view_own': False
                    },
                    'action': {
                        'create': False,
                        'edit': False,
                        'delete': False
                    }
                },
                'contract': {  # 新增合同管理权限
                    'data': {
                        'view_all': False,
                        'view_by_location': False,
                        'view_department_submissions': False,
                        'view_own': False
                    },
                    'action': {
                        'create': False,
                        'edit': False,
                        'delete': False
                    }
                }
            }

            # 获取该角色的所有权限记录
            role_permissions = Permission.objects.filter(role=role)

            # 设置权限值
            for perm in role_permissions:
                parts = perm.permission_name.split('_')
                if len(parts) >= 3:
                    module = parts[0]  # expense/customer/contract
                    perm_type = parts[1]  # data/action
                    action = '_'.join(parts[2:])  # view_all/create 等
                    
                    if module in permissions and perm_type in permissions[module]:
                        if action in permissions[module][perm_type]:
                            permissions[module][perm_type][action] = perm.permission_value

            # 添加到结果列表
            role_data = {
                'role_name': role.name,
                'permissions': permissions
            }
            permissions_data.append(role_data)

        return JsonResponse({
            'success': True,
            'data': permissions_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'获取权限列表失败: {str(e)}'
        }, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_permission(request):
    """更新角色权限"""
    try:
        data = json.loads(request.body)
        role_name = data.get('role')
        field = data.get('field')  # 格式如: 'expense_data_view_all'
        is_allowed = data.get('isAllowed')

        if not all([role_name, field, is_allowed is not None]):
            return JsonResponse({
                'success': False,
                'message': '缺少必要参数'
            }, status=400)

        # 获取角色
        role = Role.objects.get(name=role_name)
        
        # 更新权限
        permission = Permission.objects.get(
            role=role,
            permission_name=field
        )
        permission.permission_value = is_allowed
        permission.save()

        return JsonResponse({
            'success': True,
            'message': f'已更新 {role_name} 的权限'
        })

    except Role.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '角色不存在'
        }, status=404)
    except Permission.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '权限不存在'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'更新权限失败: {str(e)}'
        }, status=500)

def get_user_permissions_helper(user):
    """获取用户权限的辅助函数"""
    user_roles = user.roles

    # 获取用户所有角色的权限
    permissions = Permission.objects.filter(role_name__in=user_roles)

    # 初始化权限字典
    combined_permissions = {
        'expense': {'data': {}, 'action': {}},
        'customer': {'data': {}, 'action': {}},
        'contract': {'data': {}, 'action': {}}  # 新增合同管理权限
    }

    # 合并权限（任一角色有权限即为True）
    for permission in permissions:
        perm_dict = permission.to_dict()
        parts = permission.permission_name.split('_')
        if len(parts) >= 3:
            module = parts[0]  # expense/customer/contract
            perm_type = parts[1]  # data/action
            action = '_'.join(parts[2:])  # view_all/create 等
            
            if module in combined_permissions and perm_type in combined_permissions[module]:
                if action not in combined_permissions[module][perm_type] or permission.permission_value:
                    combined_permissions[module][perm_type][action] = permission.permission_value

    return {
        'roles': user_roles,
        'permissions': combined_permissions
    }

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user_permissions(request):
    """获取当前用户的权限"""
    permissions_data = get_user_permissions_helper(request.user)
    return Response({
        'success': True,
        'data': permissions_data
    })

