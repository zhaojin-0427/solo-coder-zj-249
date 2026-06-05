from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from range_app import views

router = DefaultRouter()
router.register(r'shooters', views.ShooterViewSet)
router.register(r'ammunitions', views.AmmunitionViewSet)
router.register(r'firearms', views.FirearmViewSet)
router.register(r'target-lanes', views.TargetLaneViewSet)
router.register(r'check-ins', views.CheckInViewSet)
router.register(r'ammo-issues', views.AmmoIssueViewSet)
router.register(r'safety-inspections', views.SafetyInspectionViewSet)
router.register(r'score-records', views.ScoreRecordViewSet)
router.register(r'ammo-returns', views.AmmoReturnViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/statistics/', views.statistics_dashboard, name='statistics'),
]
