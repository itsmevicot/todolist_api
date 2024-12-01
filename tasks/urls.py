from django.urls import path

from tasks.views import TaskListView, TaskDetailView

app_name = 'tasks'

urlpatterns = [
    path('', TaskListView.as_view(), name='task_list'),
    path('<int:task_id>/', TaskDetailView.as_view(), name='task_detail'),
]
