from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import models
from django.db.models import Count, Sum, Avg, Q
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from datetime import timedelta
from .models import (
    Shooter, Ammunition, Firearm, TargetLane,
    CheckIn, AmmoIssue, SafetyInspection, ScoreRecord, AmmoReturn
)
from .serializers import (
    ShooterSerializer, AmmunitionSerializer, FirearmSerializer, TargetLaneSerializer,
    CheckInSerializer, AmmoIssueSerializer, SafetyInspectionSerializer,
    ScoreRecordSerializer, AmmoReturnSerializer
)

class ShooterViewSet(viewsets.ModelViewSet):
    queryset = Shooter.objects.all()
    serializer_class = ShooterSerializer
    filterset_fields = ['status', 'gender', 'unit']
    search_fields = ['name', 'id_card', 'phone', 'unit']

class AmmunitionViewSet(viewsets.ModelViewSet):
    queryset = Ammunition.objects.all()
    serializer_class = AmmunitionSerializer
    filterset_fields = ['ammo_type', 'caliber']
    search_fields = ['name', 'batch_number', 'manufacturer']

class FirearmViewSet(viewsets.ModelViewSet):
    queryset = Firearm.objects.all()
    serializer_class = FirearmSerializer
    filterset_fields = ['firearm_type', 'status']
    search_fields = ['name', 'model', 'serial_number']

class TargetLaneViewSet(viewsets.ModelViewSet):
    queryset = TargetLane.objects.all()
    serializer_class = TargetLaneSerializer
    filterset_fields = ['status']
    search_fields = ['name', 'target_type']

class CheckInViewSet(viewsets.ModelViewSet):
    queryset = CheckIn.objects.all()
    serializer_class = CheckInSerializer
    filterset_fields = {
        'shooter': ['exact'],
        'alcohol_test': ['exact'],
        'psychological_status': ['exact'],
        'status': ['exact'],
        'checkin_time': ['exact', 'date', 'gte', 'lte']
    }
    search_fields = ['shooter__name', 'operator']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class AmmoIssueViewSet(viewsets.ModelViewSet):
    queryset = AmmoIssue.objects.all()
    serializer_class = AmmoIssueSerializer
    filterset_fields = {
        'shooter': ['exact'],
        'ammunition': ['exact'],
        'target_lane': ['exact'],
        'firearm': ['exact'],
        'status': ['exact'],
        'issue_time': ['exact', 'date', 'gte', 'lte']
    }
    search_fields = ['shooter__name', 'issuer']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        ammo = serializer.validated_data['ammunition']
        issue_qty = serializer.validated_data['issue_quantity']
        
        if ammo.stock_quantity < issue_qty:
            return Response(
                {'error': f'弹药库存不足，当前库存: {ammo.stock_quantity}发'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ammo.stock_quantity -= issue_qty
        ammo.save()
        
        target_lane = serializer.validated_data['target_lane']
        target_lane.status = 'occupied'
        target_lane.save()
        
        firearm = serializer.validated_data['firearm']
        firearm.status = 'in_use'
        firearm.save()
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class SafetyInspectionViewSet(viewsets.ModelViewSet):
    queryset = SafetyInspection.objects.all()
    serializer_class = SafetyInspectionSerializer
    filterset_fields = {
        'shooter': ['exact'],
        'target_lane': ['exact'],
        'violation_level': ['exact'],
        'inspection_time': ['exact', 'date', 'gte', 'lte']
    }
    search_fields = ['shooter__name', 'inspector', 'violation_type']

class ScoreRecordViewSet(viewsets.ModelViewSet):
    queryset = ScoreRecord.objects.all()
    serializer_class = ScoreRecordSerializer
    filterset_fields = {
        'shooter': ['exact'],
        'target_lane': ['exact'],
        'firearm': ['exact'],
        'ammunition': ['exact'],
        'record_time': ['exact', 'date', 'gte', 'lte']
    }
    search_fields = ['shooter__name', 'recorder']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        firearm = serializer.validated_data['firearm']
        shots_fired = serializer.validated_data['shots_fired']
        firearm.total_rounds += shots_fired
        firearm.save()
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class AmmoReturnViewSet(viewsets.ModelViewSet):
    queryset = AmmoReturn.objects.all()
    serializer_class = AmmoReturnSerializer
    filterset_fields = ['shooter', 'ammunition']
    search_fields = ['shooter__name', 'receiver']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        ammo_issue = serializer.validated_data['ammo_issue']
        ammo = serializer.validated_data['ammunition']
        returned_qty = serializer.validated_data['returned_quantity']
        
        ammo.stock_quantity += returned_qty
        ammo.save()
        
        ammo_issue.status = 'completed'
        ammo_issue.save()
        
        target_lane = ammo_issue.target_lane
        target_lane.status = 'available'
        target_lane.save()
        
        firearm = ammo_issue.firearm
        firearm.status = 'available'
        firearm.save()
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

@api_view(['GET'])
def statistics_dashboard(request):
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    seven_days_ago = now - timedelta(days=7)
    
    lane_usage = TargetLane.objects.annotate(
        usage_count=Count('ammoissue', filter=Q(ammoissue__issue_time__gte=thirty_days_ago))
    ).values('lane_number', 'name', 'usage_count', 'distance').order_by('lane_number')
    
    ammo_trend = AmmoIssue.objects.filter(
        issue_time__gte=thirty_days_ago
    ).annotate(
        date=TruncDate('issue_time')
    ).values('date').annotate(
        total_issued=Sum('issue_quantity'),
        total_consumed=Sum('ammoreturn__consumed_quantity')
    ).order_by('date')
    
    ammo_monthly = AmmoIssue.objects.filter(
        issue_time__gte=now - timedelta(days=365)
    ).annotate(
        month=TruncMonth('issue_time')
    ).values('month').annotate(
        total=Sum('issue_quantity')
    ).order_by('month')
    
    violation_stats = SafetyInspection.objects.filter(
        inspection_time__gte=thirty_days_ago
    ).values('violation_level').annotate(
        count=Count('id')
    ).order_by('-count')
    
    shooter_attendance = CheckIn.objects.filter(
        checkin_time__gte=thirty_days_ago
    ).values('shooter__id', 'shooter__name', 'shooter__unit').annotate(
        attendance_count=Count('id')
    ).order_by('-attendance_count')[:10]
    
    total_shooters = Shooter.objects.filter(status='active').count()
    total_checkins_today = CheckIn.objects.filter(checkin_time__date=now.date()).count()
    total_ammo_issued_today = AmmoIssue.objects.filter(issue_time__date=now.date()).aggregate(
        total=Sum('issue_quantity')
    )['total'] or 0
    total_violations = SafetyInspection.objects.filter(
        inspection_time__gte=seven_days_ago,
        violation_level__in=['minor', 'major', 'critical']
    ).count()
    
    active_sessions = AmmoIssue.objects.filter(status='issued').count()
    avg_score = ScoreRecord.objects.filter(
        record_time__gte=thirty_days_ago
    ).aggregate(avg=Avg('average_score'))['avg'] or 0
    
    ammo_stock = Ammunition.objects.aggregate(
        total=Sum('stock_quantity')
    )['total'] or 0
    
    violation_types = SafetyInspection.objects.filter(
        inspection_time__gte=thirty_days_ago,
        violation_level__in=['minor', 'major', 'critical']
    ).values('violation_type').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    return Response({
        'overview': {
            'total_active_shooters': total_shooters,
            'today_checkins': total_checkins_today,
            'today_ammo_issued': total_ammo_issued_today,
            'recent_violations': total_violations,
            'active_sessions': active_sessions,
            'avg_score_30d': round(avg_score, 2),
            'total_ammo_stock': ammo_stock,
        },
        'lane_usage': list(lane_usage),
        'ammo_trend': list(ammo_trend),
        'ammo_monthly': list(ammo_monthly),
        'violation_stats': list(violation_stats),
        'shooter_attendance': list(shooter_attendance),
        'violation_types': list(violation_types),
    })
