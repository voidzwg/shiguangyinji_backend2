from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    自定义权限只允许对象的创建者才能编辑它。
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user