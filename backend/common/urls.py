from django.urls import path

from . import views


app_name = 'common'
# Routes supported by the React frontend
urlpatterns = [path('projects/<int:project_id>/', views.IndexView.as_view(), name='project-detail')]
