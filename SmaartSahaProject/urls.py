"""
URL configuration for SmaartSahaProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import DefaultRouter
from SmartSaha.views import ParcelViewSet, ParcelPointViewSet, UserViewSet, SignupView, LoginView, CropViewSet, \
    StatusCropViewSet, VarietyViewSet, ParcelCropViewSet, TaskViewSet, TaskPriorityViewSet, TaskStatusViewSet, \
    YieldRecordViewSet, SoilDataView, ClimateDataView, DataViewSet, ParcelFullDataViewSet, AgronomyAssistantAPIView, \
    YieldForecastView, YieldAnalyticsView, DashboardViewSet, dashboard, tasks_view, parcel_full_data_page, \
    assistant_agronome_page, assistant_agronome_api
from SmartSaha.views.users import ForgotPasswordView, ResetPasswordView

from django.contrib.auth import views as auth_views

schema_view = get_schema_view(
   openapi.Info(
      title="Smart Saha API",
      default_version='v1',
      description="Documentation des endpoints de Smart Saha",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@smartsaha.mg"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)
router = DefaultRouter()
router.register(r'parcels', ParcelViewSet)
router.register(r'parcel-points', ParcelPointViewSet)
router.register(r'users', UserViewSet)
router.register(r'crops', CropViewSet)
router.register(r'status-crops', StatusCropViewSet)
router.register(r'varieties', VarietyViewSet)
router.register(r'parcel-crops', ParcelCropViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'task-status', TaskStatusViewSet)
router.register(r'task-priority', TaskPriorityViewSet)
router.register(r'yield-records', YieldRecordViewSet)
router.register(r'external-data', DataViewSet, basename='external-data')
router.register(r'parcels-full', ParcelFullDataViewSet, basename='parcels-full')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')

urlpatterns = [
    path('api/signup/', SignupView.as_view(), name='signup'),
    path('api/login/', LoginView.as_view(), name='login'),
    path("api/forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("api/reset-password/<uidb64>/<token>/", ResetPasswordView.as_view(), name="reset-password"),
    path("api/soil-data/", SoilDataView.as_view(), name="soil-data"),
    path("api/climate-data/", ClimateDataView.as_view(), name="climate-data"),
    path('api/', include(router.urls)),
    path('admin/', admin.site.urls),

    path("api/assistant-agronome/", AgronomyAssistantAPIView.as_view(), name="assistant-agronome"),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('forecast/<int:parcel_crop_id>/', YieldForecastView.as_view(), name='yield_forecast'),

    path("analytics/yields/", YieldAnalyticsView.as_view(), name="yield-analytics"),



    path("dashboard/", dashboard, name="dashboard"),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('tasks/', tasks_view, name='tasks'),
    path('parcels/<uuid:parcel_uuid>/view/', parcel_full_data_page, name='parcel-full-data-page'),

    path("assistant-agronome/", assistant_agronome_page, name="assistant_agronome_page"),

    path("api/assistant-agronome/", assistant_agronome_api, name="assistant_agronome_api"),

]
