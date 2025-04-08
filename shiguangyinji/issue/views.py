from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .permissions import IsOwner
from .models import Issue
import os
from django.conf import settings
from django.db.models import Q

class IssueManagement(APIView):
    permission_classes = (IsOwner,)

    def get(self, request):
        """
        GET接口：返回事件ID的列表
        """
        user_id = request.user.id if request.user.is_authenticated else None
        if user_id is None:
            return JsonResponse({'error': 'User not authenticated'}, status=401)
        event_ids = Issue.objects.filter(author_id=user_id).values_list('issue_id', flat=True)
        if not event_ids:
            return JsonResponse({'error': 'No events found for this user'}, status=404)
        return JsonResponse({'event_ids': event_ids}, status=200)

    def post(self, request):
        """
        POST接口：接收事件ID，返回事件的详细属性
        """
        issue_id = request.data.get('issue_id')
        if not issue_id:
            return JsonResponse({'error': 'Issue ID is required'}, status=400)
        
        try:
            issue = Issue.objects.get(issue_id=issue_id)
        except Issue.DoesNotExist:
            return JsonResponse({'error': 'Issue not found'}, status=404)
        # 获取图片URL列表
        # 图片URL是MEDIA_URL/用户ID/issue_id/图片名
        picture_url_list = []
        if issue.pictures:
            pictures = issue.pictures.split(',')
            for picture in pictures:
                picture_url = settings.MEDIA_URL + str(issue.author.id) + "/" + str(issue.issue_id) + "/" + picture
                # 检查图片是否存在
                if not os.path.exists(picture_url):
                    return JsonResponse({'error': 'Image not found'}, status=404)
                # 如果存在，添加到列表中
                picture_url_list.append(picture_url)
        # 构建返回数据
        issue_data = {
            'issue_id': issue.issue_id,
            'author': issue.author.username if issue.author else None,
            'location': issue.location,
            'time': issue.time.strftime('%H:%M:%S') if issue.time else None,
            'pictures': picture_url_list,
            'description': issue.description
        }
        return JsonResponse(issue_data, status=200)
    

class IssueCreate(APIView):
    permission_classes = (IsOwner,)

    def post(self, request):
        """
        POST接口：接收事件的详细属性，创建新的事件
        """
        user_id = request.user.id if request.user.is_authenticated else None
        if user_id is None:
            return JsonResponse({'error': 'User not authenticated'}, status=401)

        author = request.user
        location = request.data.get('location')
        time = request.data.get('time')
        pictures = request.data.get('pictures')
        description = request.data.get('description')

        # 创建新的事件
        issue = Issue.objects.create(
            author=author,
            location=location,
            time=time,
            pictures=pictures,
            description=description
        )
        return JsonResponse({'issue_id': issue.issue_id}, status=201)



class IssueSearch(APIView):
    permission_classes = (IsOwner,)

    def post(self, request):
        """
        POST接口：接收关键词字符串，在Issue的description字段中搜索，返回符合条件的事件ID列表
        """
        keywords = request.data.get('keywords')
        if not keywords:
            return JsonResponse({'error': 'Keywords are required'}, status=400)

        # 将关键词字符串拆分为列表
        keyword_list = keywords.split()

        # 构建查询条件，使用Q对象进行模糊查询
        query = Q()
        for keyword in keyword_list:
            query |= Q(description__icontains=keyword)

        # 查询符合条件的事件
        user_id = request.user.id if request.user.is_authenticated else None
        if user_id is None:
            return JsonResponse({'error': 'User not authenticated'}, status=401)

        matching_issues = Issue.objects.filter(query, author_id=user_id).values_list('issue_id', flat=True)

        if not matching_issues:
            return JsonResponse({'error': 'No matching issues found'}, status=404)

        return JsonResponse({'matching_issue_ids': list(matching_issues)}, status=200)