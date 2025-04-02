from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Role, User, Department  # 修改这行导入语句

User = get_user_model()



class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    roles = serializers.ListField(child=serializers.CharField(), required=False)
    dept = serializers.SerializerMethodField()
    createTime = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'nickname', 'avatar', 'phone', 'sex', 'status', 'dept', 'remark', 'createTime', 'roles', 'password', 'dept_id')
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'required': False},
            'email': {'required': False},
            'nickname': {'required': False},
            'avatar': {'required': False},
            'phone': {'required': False},
            'sex': {'required': False},
            'status': {'required': False},
            'remark': {'required': False},
            'dept_id': {'required': False},
        }

    def get_createTime(self, obj):
        return int(obj.date_joined.timestamp() * 1000)

    def get_dept(self, obj):
        if obj.dept_id:
            try:
                department = Department.objects.get(id=obj.dept_id)
                return {'id': department.id, 'name': department.name}
            except Department.DoesNotExist:
                pass
        return {'id': None, 'name': None}

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['dept'] = self.get_dept(instance)
        return ret

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

    def validate_roles(self, value):
        # 确保所有提供的角色名称都是有效的
        valid_roles = set(Role.objects.values_list('name', flat=True))
        for role_name in value:
            if role_name not in valid_roles:
                raise serializers.ValidationError(f"Invalid role name: {role_name}")
        return value

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class RoleSerializer(serializers.ModelSerializer):
    createTime = serializers.SerializerMethodField()
    updateTime = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = ('id', 'name', 'code', 'status', 'remark', 'createTime', 'updateTime')
        read_only_fields = ('id', 'createTime', 'updateTime')

    def get_createTime(self, obj):
        return obj.create_time.strftime('%Y-%m-%d %H:%M:%S')

    def get_updateTime(self, obj):
        return obj.update_time.strftime('%Y-%m-%d %H:%M:%S')

class DepartmentSerializer(serializers.ModelSerializer):
    parent_id = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), source='parent', allow_null=True)

    class Meta:
        model = Department
        fields = ('id', 'name', 'parent_id', 'sort', 'phone', 'principal', 'email', 'status', 'type', 'create_time', 'remark')
        extra_kwargs = {
            'parent_id': {'allow_null': True}
        }
