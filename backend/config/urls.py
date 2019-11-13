"""
Rereading URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URL configuration
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from apps.common import render_react_view
from apps.readings import views as readings_views


urlpatterns = [
    # Django admin page
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/documents/', readings_views.ListDocument.as_view()),
    path('api/add-response/', readings_views.ListReadingData.as_view()),
    path('api/documents/<int:pk>/', readings_views.DetailDocument.as_view()),
    path('api/analysis/', readings_views.analysis),
    path('api/document_analysis/', readings_views.document_analysis),

    # Prototyping API endpoints
    path('api_proto/', readings_views.ListStoryPrototype.as_view()),
    path('api_proto/add-response/', readings_views.ListStudentPrototype.as_view()),
    path('api_proto/<int:pk>/', readings_views.DetailStoryPrototype.as_view()),

    # React views
    path('student/', render_react_view, {'component_name': 'StudentView'}),
    path('instructor/', render_react_view, {'component_name': 'InstructorView'}),
    path('analysis/', render_react_view, {'component_name': 'AnalysisView'}),
    path('document_analysis/', render_react_view, {'component_name': 'DocumentAnalysisView'}),
    path('project/', render_react_view, {'component_name': 'ProjectView'}),
    path('reading_sample/', render_react_view, {'component_name': 'ReadingSampleView'}),
    path('rereading_visuals/', render_react_view, {'component_name': 'RereadingVisualsView'}),
    path('rereading_values/', render_react_view, {'component_name': 'RereadingValuesView'}),
    path('reading/', render_react_view, {'component_name': 'ReadingView'}),
]
