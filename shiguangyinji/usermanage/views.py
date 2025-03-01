import json

from django.contrib.auth.hashers import check_password, make_password
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
import random
import json
import smtplib
import os

from shiguangyinji.usermanage.models import User, VerificationCode


@api_view(['POST'])
@csrf_exempt
def login(request):
    data = json.loads(request.body.decode('utf-8'))

    username = data.get('username')
    password = data.get('password')

    try:
        user = User.objects.get(username=username)
        if check_password(password, user.password):
            token, created = Token.objects.get_or_create(user=user)
            return JsonResponse({"status": "success", "token": str(token.key)}, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse({"status": "wrong password"}, status=status.HTTP_401_UNAUTHORIZED)
    except User.DoesNotExist:
        return JsonResponse({"status": "user does not exist"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@csrf_exempt
def register(request):
    data = json.loads(request.body.decode('utf-8'))
    username = data.get('username')
    password = data.get('password')
    real_name = data.get('real_name')
    email = data.get('email')
    code = data.get('code')

    if not password or not email or not code or not username or not real_name:
        return JsonResponse({"status": "error", "message": "ALL messages are required"},
                            status=status.HTTP_400_BAD_REQUEST)

    verification_code = VerificationCode.objects.filter(email=email).order_by('-created_at').first()

    if not verification_code or verification_code.code != code:
        return JsonResponse({"status": "error", "message": "ERROR CODE"}, status=status.HTTP_401_UNAUTHORIZED)

    if verification_code.expires_at < timezone.now():
        return JsonResponse({"status": "error", "message": "Verification code expired"},
                            status=status.HTTP_401_UNAUTHORIZED)

    if get_user_by_username(username):
        return JsonResponse({"status": "error", "message": "User already exists"}, status=status.HTTP_409_CONFLICT)

    hashed_password = make_password(password)
    verification_code.delete()
    new_user = User(password=hashed_password, username=username, real_name=real_name, email=email)
    new_user.save()

    default_avatar_path = 'resources/avatars/default_avatar.png'
    with open(default_avatar_path, 'rb') as f:
        avatar_content = f.read()
    new_filename = f"{username}_avatar.png"
    new_file = ContentFile(avatar_content)
    new_file.name = new_filename
    new_user.avatar.save(new_filename, new_file, save=True)

    return JsonResponse({"status": "success", "message": "User successfully registered"},
                        status=status.HTTP_200_OK)


@api_view(['POST'])
@csrf_exempt
def get_verification_code(request):
    email = request.GET.get('email')

    if not email:
        return JsonResponse({"status": "error", "message": "email is required"}, status=status.HTTP_400_BAD_REQUEST)

    code = str(random.randint(1000, 9999))

    # 保存验证码
    VerificationCode.objects.create(email=email, code=code)
    # 在这里添加发送邮件的代码
    send_email(email, code)

    return JsonResponse({"status": "success", "message": "Verification code sent"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@csrf_exempt
def logout(request):
    try:
        # 获取当前用户的Token
        token = Token.objects.get(user=request.user)
        # 删除Token
        token.delete()
        return JsonResponse({"status": "success", "message": "Successfully logged out."}, status=status.HTTP_200_OK)
    except Token.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Token not found."}, status=status.HTTP_400_BAD_REQUEST)



def get_user_by_email(email):
    users = User.objects.filter(email=email)
    if users.exists():
        return users.first()
    return None


def get_user_by_username(username: str):
    users = User.objects.filter(username=username)
    if users.exists():
        return users.first()
    return None


def send_email(email, code):
    from email.mime.text import MIMEText
    from email.header import Header

    # 配置SMTP服务器和端口
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT'))  # 确保这是一个整数
    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASS')

    # 创建SMTP对象
    server = smtplib.SMTP_SSL(smtp_server, smtp_port)
    server.login(smtp_user, smtp_pass)

    # 创建邮件内容
    validity_duration = 10  # 假设验证码有效时间是 10 分钟

    msg = MIMEText(f'Your verification code is {code}. This code will expire in {validity_duration} minutes.', 'plain',
                   'utf-8')
    msg['From'] = Header(smtp_user)
    msg['To'] = Header(email)
    msg['Subject'] = Header('Verification code')

    # 发送邮件
    server.sendmail(smtp_user, [email], msg.as_string())
    server.quit()