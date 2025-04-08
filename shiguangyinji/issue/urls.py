from django.urls import path
from .views import IssueManagement, IssueSearch

url_patterns = [
    path('issue/', IssueManagement.as_view(), name='issue_management'),
    path('search/', IssueSearch.as_view(), name='issue_search'),
]