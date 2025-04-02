from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .services import generate_presigned_url

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_presigned_url(request):
    """
    获取预签名上传URL
    
    请求参数:
    {
        "filename": "example.jpg",  // 文件名(将作为存储名)
        "content_type": "image/jpeg",  // 文件类型
        "subdirectory": "uploads"  // 可选，存储子目录
    }
    """
    filename = request.data.get('filename')
    content_type = request.data.get('content_type')
    subdirectory = request.data.get('subdirectory', 'uploads')
    
    if not filename:
        return Response({
            'success': False,
            'message': '文件名不能为空'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 直接使用原始文件名
    object_key = f"{subdirectory}/{filename}"
    
    try:
        result = generate_presigned_url(
            object_key=object_key,
            content_type=content_type
        )
        
        return Response({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)