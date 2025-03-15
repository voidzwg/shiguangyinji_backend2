from django.contrib.auth import get_user_model, authenticate
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import RegisterSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class CheckUsernameExistView(APIView):
    def post(self, request):
        username = request.data.get('username')
        if not username:
            return Response({"error": "必须填写用户名"}, status=status.HTTP_400_BAD_REQUEST)

        user_exists = User.objects.filter(username=username).exists()
        return Response({"exists": user_exists}, status=status.HTTP_200_OK)


class CheckPhoneExistView(APIView):
    def post(self, request):
        phone = request.data.get("phone")

        if not phone:
            return Response({"error": "必须填写手机号"}, status=status.HTTP_400_BAD_REQUEST)

        if not phone.isdigit() or len(phone) != 11:
            return Response({"error": "手机号不合法，必须为11位数字"}, status=status.HTTP_400_BAD_REQUEST)

        phone_exists = User.objects.filter(phone=phone).exists()
        return Response({"exists": phone_exists}, status=status.HTTP_200_OK)


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "用户名和密码是必填项"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)

        if user:
            response = super().post(request, *args, **kwargs)
            response.data["message"] = "登录成功"
            return response
        else:
            return Response({"error": "用户名或密码错误"}, status=status.HTTP_401_UNAUTHORIZED)


class CheckLoginStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"logged_in": True, "username": request.user.username}, status=200)


class LogoutView(APIView):
    authentication_classes = [JWTAuthentication]  # 确保验证 JWT
    permission_classes = [IsAuthenticated]  # 确保用户已认证

    def post(self, request):
        # 登出逻辑
        return Response(status=status.HTTP_200_OK)