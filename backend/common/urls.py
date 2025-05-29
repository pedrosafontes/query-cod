from django.urls import path

from . import views


app_name = 'common'
# Routes supported by the React frontend
react_view = views.IndexView.as_view()
urlpatterns = [
    path('', react_view, name='index'),
    path('login/', react_view, name='login'),
    path('signup/', react_view, name='signup'),
    path('projects/', react_view, name='project-list'),
    path('projects/<int:project_id>/', react_view, name='project-detail'),
    path('exercises/', react_view, name='exercise-list'),
    path('exercises/<int:exercise_id>', react_view, name='exercise-detail'),
]
