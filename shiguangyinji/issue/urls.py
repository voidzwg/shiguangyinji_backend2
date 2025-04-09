from django.urls import path
from .views import IssueManagement, IssueSearch

urlpatterns = [
    path('issue/', IssueManagement.as_view(), name='issue_management'),
    path('search/', IssueSearch.as_view(), name='issue_search'),
]