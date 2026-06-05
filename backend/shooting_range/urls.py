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
router.register(r'ammo-batches', views.AmmoBatchViewSet)
router.register(r'training-plans', views.TrainingPlanViewSet)
router.register(r'training-schedules', views.TrainingScheduleViewSet)
router.register(r'lane-reservations', views.LaneReservationViewSet)
router.register(r'risk-warnings', views.RiskWarningViewSet)
router.register(r'violation-disposals', views.ViolationDisposalViewSet)
router.register(r'ammo-batch-flows', views.AmmoBatchFlowViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/statistics/', views.statistics_dashboard, name='statistics'),
    path('api/advanced-statistics/', views.advanced_statistics, name='advanced-statistics'),
    path('api/generate-schedule-recommendations/', views.generate_schedule_recommendations, name='generate-schedule-recommendations'),
]
