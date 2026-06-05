from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.db import models
from django.db.models import Count, Sum, Avg, Q, F, ExpressionWrapper, FloatField, Case, When, Value
from django.db.models.functions import TruncDate, TruncMonth, ExtractHour
from django.utils import timezone
from datetime import timedelta, date, time, datetime
from io import BytesIO
import csv
from django.http import HttpResponse
from .models import (
    Shooter, Ammunition, Firearm, TargetLane,
    CheckIn, AmmoIssue, SafetyInspection, ScoreRecord, AmmoReturn,
    AmmoBatch, TrainingPlan, TrainingSchedule, LaneReservation,
    RiskWarning, ViolationDisposal, AmmoBatchFlow
)
from .serializers import (
    ShooterSerializer, AmmunitionSerializer, FirearmSerializer, TargetLaneSerializer,
    CheckInSerializer, AmmoIssueSerializer, SafetyInspectionSerializer,
    ScoreRecordSerializer, AmmoReturnSerializer, AmmoBatchSerializer,
    TrainingPlanSerializer, TrainingScheduleSerializer, LaneReservationSerializer,
    RiskWarningSerializer, ViolationDisposalSerializer, AmmoBatchFlowSerializer,
    ScheduleRecommendationSerializer, TrainingPlanStatsSerializer,
    RiskShooterSerializer, ViolationClosureStatsSerializer
)

class ExportMixin:
    def get_export_filename(self):
        return f'{self.queryset.model._meta.verbose_name}_{timezone.now().strftime("%Y%m%d%H%M%S")}.csv'

    def get_export_fields(self):
        return [field.name for field in self.queryset.model._meta.fields]

    @action(detail=False, methods=['get'])
    def export(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        fields = self.get_export_fields()
        field_labels = [field.verbose_name for field in self.queryset.model._meta.fields if field.name in fields]

        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = f'attachment; filename="{self.get_export_filename()}"'

        writer = csv.writer(response)
        writer.writerow(field_labels)

        for obj in queryset:
            row = []
            for field in fields:
                value = getattr(obj, field)
                if hasattr(value, 'strftime'):
                    value = value.strftime('%Y-%m-%d %H:%M:%S') if hasattr(value, 'hour') else value.strftime('%Y-%m-%d')
                elif hasattr(obj, f'get_{field}_display'):
                    value = getattr(obj, f'get_{field}_display')()
                row.append(str(value) if value is not None else '')
            writer.writerow(row)

        return response

class ShooterViewSet(ExportMixin, viewsets.ModelViewSet):
    queryset = Shooter.objects.all()
    serializer_class = ShooterSerializer
    filterset_fields = ['status', 'gender', 'unit', 'qualification_level']
    search_fields = ['name', 'id_card', 'phone', 'unit']

    def get_queryset(self):
        queryset = super().get_queryset()
        thirty_days_ago = timezone.now() - timedelta(days=30)
        queryset = queryset.annotate(
            violation_count=Count('safetyinspection', filter=Q(safetyinspection__violation_level__in=['minor', 'major', 'critical'])),
            recent_violations=Count('safetyinspection', filter=Q(
                safetyinspection__violation_level__in=['minor', 'major', 'critical'],
                safetyinspection__inspection_time__gte=thirty_days_ago
            )),
            risk_score=ExpressionWrapper(
                Count('safetyinspection', filter=Q(safetyinspection__violation_level='critical')) * 10 +
                Count('safetyinspection', filter=Q(safetyinspection__violation_level='major')) * 5 +
                Count('safetyinspection', filter=Q(safetyinspection__violation_level='minor')) * 2 +
                Count('violation_disposals', filter=Q(violation_disposals__status__in=['pending', 'notified', 'confirmed', 'rectified'])) * 3,
                output_field=FloatField()
            )
        )
        return queryset

class AmmunitionViewSet(ExportMixin, viewsets.ModelViewSet):
    queryset = Ammunition.objects.all()
    serializer_class = AmmunitionSerializer
    filterset_fields = ['ammo_type', 'caliber']
    search_fields = ['name', 'batch_number', 'manufacturer']

class FirearmViewSet(ExportMixin, viewsets.ModelViewSet):
    queryset = Firearm.objects.all()
    serializer_class = FirearmSerializer
    filterset_fields = ['firearm_type', 'status']
    search_fields = ['name', 'model', 'serial_number']

class TargetLaneViewSet(ExportMixin, viewsets.ModelViewSet):
    queryset = TargetLane.objects.all()
    serializer_class = TargetLaneSerializer
    filterset_fields = ['status']
    search_fields = ['name', 'target_type']

class AmmoBatchViewSet(ExportMixin, viewsets.ModelViewSet):
    queryset = AmmoBatch.objects.all()
    serializer_class = AmmoBatchSerializer
    filterset_fields = {
        'ammunition': ['exact'],
        'quality_status': ['exact'],
        'production_date': ['exact', 'gte', 'lte'],
        'expiry_date': ['exact', 'gte', 'lte']
    }
    search_fields = ['batch_number', 'manufacturer', 'storage_location']

    def get_queryset(self):
        queryset = super().get_queryset()
        today = timezone.now().date()
        queryset = queryset.annotate(
            is_expired=Case(
                When(expiry_date__lt=today, then=Value(True)),
                default=Value(False),
                output_field=models.BooleanField()
            ),
            is_low_stock=Case(
                When(current_quantity__lte=F('safety_threshold'), then=Value(True)),
                default=Value(False),
                output_field=models.BooleanField()
            )
        )
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        batch = serializer.instance
        AmmoBatchFlow.objects.create(
            ammo_batch=batch,
            flow_type='in',
            quantity=batch.initial_quantity,
            balance_before=0,
            balance_after=batch.initial_quantity,
            operator=request.data.get('operator', '系统管理员'),
            remarks='批次入库'
        )

        if batch.current_quantity <= batch.safety_threshold:
            RiskWarning.objects.create(
                warning_type='ammo_stock',
                warning_level='medium',
                title=f'弹药批次库存预警: {batch.batch_number}',
                description=f'弹药批次 {batch.batch_number} 当前库存 {batch.current_quantity} 发，低于安全阈值 {batch.safety_threshold} 发',
                ammo_batch=batch,
                ammunition=batch.ammunition
            )

        if batch.expiry_date and batch.expiry_date - today <= timedelta(days=30):
            RiskWarning.objects.create(
                warning_type='ammo_expiry',
                warning_level='high' if batch.expiry_date - today <= timedelta(days=7) else 'medium',
                title=f'弹药批次即将过期: {batch.batch_number}',
                description=f'弹药批次 {batch.batch_number} 将于 {batch.expiry_date} 过期，距离过期还有 {(batch.expiry_date - today).days} 天',
                ammo_batch=batch,
                ammunition=batch.ammunition
            )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class TrainingPlanViewSet(ExportMixin, viewsets.ModelViewSet):
    queryset = TrainingPlan.objects.all()
    serializer_class = TrainingPlanSerializer
    filterset_fields = {
        'status': ['exact'],
        'plan_type': ['exact'],
        'start_date': ['exact', 'gte', 'lte'],
        'end_date': ['exact', 'gte', 'lte']
    }
    search_fields = ['plan_name', 'description', 'creator', 'approver']

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(
            target_shooters_count=Count('target_shooters'),
            total_schedules=Count('schedules'),
            completed_schedules=Count('schedules', filter=Q(schedules__status='completed')),
            completion_rate=Case(
                When(total_schedules=0, then=Value(0.0)),
                default=ExpressionWrapper(
                    Count('schedules', filter=Q(schedules__status='completed')) * 100.0 / Count('schedules'),
                    output_field=FloatField()
                ),
                output_field=FloatField()
            )
        )
        return queryset

    @action(detail=True, methods=['post'])
    def generate_schedules(self, request, pk=None):
        plan = self.get_object()
        recommendations, conflicts, warnings = self._generate_schedule_recommendations(plan)

        for rec in recommendations:
            if not rec.get('has_conflict', False):
                schedule = TrainingSchedule.objects.create(
                    training_plan=plan,
                    shooter_id=rec['shooter_id'],
                    target_lane_id=rec['lane_id'],
                    schedule_date=rec['date'],
                    start_time=rec['start_time'],
                    end_time=rec['end_time'],
                    allocated_rounds=rec['allocated_rounds'],
                    auto_generated=True,
                    generation_reason=rec['reason'],
                    operator=request.data.get('operator', '系统管理员')
                )
                rec['schedule_id'] = schedule.id

        return Response({
            'generated_count': len([r for r in recommendations if not r.get('has_conflict')]),
            'recommendations': recommendations,
            'conflicts': conflicts,
            'warnings': warnings
        })

    def _generate_schedule_recommendations(self, plan):
        recommendations = []
        conflicts = []
        warnings = []
        today = timezone.now().date()
        thirty_days_ago = today - timedelta(days=30)

        target_shooters = plan.target_shooters.filter(status='active')
        if plan.required_qualification:
            target_shooters = target_shooters.filter(qualification_level=plan.required_qualification)

        available_lanes = TargetLane.objects.filter(status='available')
        if not available_lanes:
            available_lanes = TargetLane.objects.filter(status='occupied')

        available_firearms = Firearm.objects.filter(status='available')
        if plan.required_firearm_types:
            required_types = [t.strip() for t in plan.required_firearm_types.split(',')]
            available_firearms = available_firearms.filter(firearm_type__in=required_types)

        active_disposals = ViolationDisposal.objects.filter(
            status__in=['pending', 'notified', 'confirmed', 'rectified'],
            is_ammo_suspended=True
        ).values_list('shooter_id', flat=True)

        date_range = []
        current_date = max(plan.start_date, today)
        while current_date <= plan.end_date:
            if current_date.weekday() < 6:
                date_range.append(current_date)
            current_date += timedelta(days=1)

        for shooter in target_shooters:
            if shooter.id in active_disposals:
                warnings.append({
                    'shooter_id': shooter.id,
                    'shooter_name': shooter.name,
                    'warning': '该射手处于领弹暂停状态，已跳过排班'
                })
                continue

            recent_violations = SafetyInspection.objects.filter(
                shooter=shooter,
                violation_level__in=['major', 'critical'],
                inspection_time__gte=thirty_days_ago
            ).count()
            if recent_violations >= 2:
                warnings.append({
                    'shooter_id': shooter.id,
                    'shooter_name': shooter.name,
                    'warning': f'该射手30天内有{recent_violations}次严重违规，建议谨慎安排'
                })

            allocated = False
            for schedule_date in date_range:
                if allocated:
                    break

                for lane in available_lanes:
                    existing_schedules = TrainingSchedule.objects.filter(
                        target_lane=lane,
                        schedule_date=schedule_date,
                        start_time__lt=plan.daily_end_time,
                        end_time__gt=plan.daily_start_time,
                        status__in=['pending', 'checked_in', 'in_progress']
                    )

                    start_dt = datetime.combine(schedule_date, plan.daily_start_time)
                    end_dt = datetime.combine(schedule_date, plan.daily_end_time)
                    has_conflict = False

                    for existing in existing_schedules:
                        existing_start = datetime.combine(schedule_date, existing.start_time)
                        existing_end = datetime.combine(schedule_date, existing.end_time)
                        if start_dt < existing_end and end_dt > existing_start:
                            has_conflict = True
                            conflicts.append({
                                'shooter_id': shooter.id,
                                'shooter_name': shooter.name,
                                'lane_id': lane.id,
                                'lane_name': lane.name,
                                'date': schedule_date.isoformat(),
                                'conflict_with': existing.id,
                                'conflict_time': f'{existing.start_time} - {existing.end_time}'
                            })
                            break

                    if not has_conflict:
                        ammo_warnings = []
                        for ammo_type in plan.planned_ammo_types.all():
                            total_available = AmmoBatch.objects.filter(
                                ammunition=ammo_type,
                                quality_status__in=['normal', 'warning'],
                                expiry_date__gte=schedule_date
                            ).aggregate(total=Sum('current_quantity'))['total'] or 0

                            if total_available < plan.total_rounds_per_shooter:
                                ammo_warnings.append({
                                    'ammo_type': ammo_type.name,
                                    'available': total_available,
                                    'required': plan.total_rounds_per_shooter
                                })

                        if ammo_warnings:
                            warnings.append({
                                'shooter_id': shooter.id,
                                'shooter_name': shooter.name,
                                'date': schedule_date.isoformat(),
                                'ammo_warnings': ammo_warnings
                            })

                        recommendations.append({
                            'shooter_id': shooter.id,
                            'shooter_name': shooter.name,
                            'lane_id': lane.id,
                            'lane_name': lane.name,
                            'date': schedule_date.isoformat(),
                            'start_time': plan.daily_start_time.strftime('%H:%M'),
                            'end_time': plan.daily_end_time.strftime('%H:%M'),
                            'allocated_rounds': plan.total_rounds_per_shooter,
                            'reason': f'资质匹配: {shooter.qualification_level}, 靶道可用: {lane.name}',
                            'has_conflict': False,
                            'firearm_available': available_firearms.count() > 0
                        })
                        allocated = True
                        break

        return recommendations, conflicts, warnings

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        plan = self.get_object()
        plan.status = 'approved'
        plan.approver = request.data.get('approver', '系统管理员')
        plan.approval_time = timezone.now()
        plan.save()
        return Response({'status': 'approved', 'plan': TrainingPlanSerializer(plan).data})

class TrainingScheduleViewSet(ExportMixin, viewsets.ModelViewSet):
    queryset = TrainingSchedule.objects.all()
    serializer_class = TrainingScheduleSerializer
    filterset_fields = {
        'training_plan': ['exact'],
        'shooter': ['exact'],
        'target_lane': ['exact'],
        'status': ['exact'],
        'schedule_date': ['exact', 'gte', 'lte']
    }
    search_fields = ['shooter__name', 'generation_reason', 'remarks']

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        schedule = self.get_object()
        schedule.status = 'cancelled'
        schedule.remarks = f"{schedule.remarks}\n取消原因: {request.data.get('reason', '管理员取消')}"
        schedule.save()
        return Response({'status': 'cancelled'})

class LaneReservationViewSet(ExportMixin, viewsets.ModelViewSet):
    queryset = LaneReservation.objects.all()
    serializer_class = LaneReservationSerializer
    filterset_fields = {
        'target_lane': ['exact'],
        'shooter': ['exact'],
        'status': ['exact'],
        'reservation_date': ['exact', 'gte', 'lte']
    }
    search_fields = ['purpose', 'reserved_by', 'confirmed_by']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reservation_date = serializer.validated_data['reservation_date']
        start_time = serializer.validated_data['start_time']
        end_time = serializer.validated_data['end_time']
        target_lane = serializer.validated_data['target_lane']

        conflicts = TrainingSchedule.objects.filter(
            target_lane=target_lane,
            schedule_date=reservation_date,
            start_time__lt=end_time,
            end_time__gt=start_time,
            status__in=['pending', 'checked_in', 'in_progress']
        )

        reservation_conflicts = LaneReservation.objects.filter(
            target_lane=target_lane,
            reservation_date=reservation_date,
            start_time__lt=end_time,
            end_time__gt=start_time,
            status__in=['pending', 'confirmed', 'in_use']
        )

        if conflicts.exists() or reservation_conflicts.exists():
            serializer.validated_data['conflict_detected'] = True
            if conflicts.exists():
                serializer.validated_data['conflict_with'] = conflicts.first().id

                RiskWarning.objects.create(
                    warning_type='lane_conflict',
                    warning_level='high',
                    title=f'靶道预约冲突: {target_lane.lane_number}号靶道',
                    description=f'{reservation_date} {start_time}-{end_time} 靶道预约与现有排班冲突',
                    target_lane=target_lane
                )

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        reservation = self.get_object()
        reservation.status = 'confirmed'
        reservation.confirmed_by = request.data.get('confirmed_by', '系统管理员')
        reservation.confirm_time = timezone.now()
        reservation.save()
        return Response({'status': 'confirmed'})

class RiskWarningViewSet(ExportMixin, viewsets.ModelViewSet):
    queryset = RiskWarning.objects.all()
    serializer_class = RiskWarningSerializer
    filterset_fields = {
        'warning_type': ['exact'],
        'warning_level': ['exact'],
        'status': ['exact'],
        'create_time': ['exact', 'date', 'gte', 'lte']
    }
    search_fields = ['title', 'description', 'handler', 'handle_result']

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        warning = self.get_object()
        warning.status = 'resolved'
        warning.handler = request.data.get('handler', '系统管理员')
        warning.handle_time = timezone.now()
        warning.handle_result = request.data.get('handle_result', '')
        warning.save()
        return Response({'status': 'resolved'})

    @action(detail=True, methods=['post'])
    def ignore(self, request, pk=None):
        warning = self.get_object()
        warning.status = 'ignored'
        warning.handler = request.data.get('handler', '系统管理员')
        warning.handle_time = timezone.now()
        warning.handle_result = request.data.get('handle_result', '已忽略')
        warning.save()
        return Response({'status': 'ignored'})

class CheckInViewSet(ExportMixin, viewsets.ModelViewSet):
    queryset = CheckIn.objects.all()
    serializer_class = CheckInSerializer
    filterset_fields = {
        'shooter': ['exact'],
        'training_plan': ['exact'],
        'training_schedule': ['exact'],
        'alcohol_test': ['exact'],
        'psychological_status': ['exact'],
        'status': ['exact'],
        'checkin_time': ['exact', 'date', 'gte', 'lte']
    }
    search_fields = ['shooter__name', 'operator']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        shooter = serializer.validated_data['shooter']
        checkin_date = timezone.now().date()

        active_disposals = ViolationDisposal.objects.filter(
            shooter=shooter,
            status__in=['pending', 'notified', 'confirmed', 'rectified'],
            is_ammo_suspended=True,
            suspension_end_date__gte=checkin_date
        )
        if active_disposals.exists():
            return Response(
                {'error': '该射手处于领弹暂停状态，禁止签到入场'},
                status=status.HTTP_400_BAD_REQUEST
            )

        today_schedules = TrainingSchedule.objects.filter(
            shooter=shooter,
            schedule_date=checkin_date,
            status__in=['pending', 'checked_in']
        )

        if today_schedules.exists():
            schedule = today_schedules.first()
            serializer.validated_data['training_schedule'] = schedule
            serializer.validated_data['training_plan'] = schedule.training_plan
            serializer.validated_data['auto_associated'] = True
            schedule.status = 'checked_in'
            schedule.save()

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class AmmoIssueViewSet(ExportMixin, viewsets.ModelViewSet):
    queryset = AmmoIssue.objects.all()
    serializer_class = AmmoIssueSerializer
    filterset_fields = {
        'shooter': ['exact'],
        'training_plan': ['exact'],
        'training_schedule': ['exact'],
        'ammunition': ['exact'],
        'ammo_batch': ['exact'],
        'target_lane': ['exact'],
        'firearm': ['exact'],
        'status': ['exact'],
        'issue_time': ['exact', 'date', 'gte', 'lte']
    }
    search_fields = ['shooter__name', 'issuer', 'remarks']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        shooter = serializer.validated_data['shooter']
        ammo = serializer.validated_data['ammunition']
        issue_qty = serializer.validated_data['issue_quantity']
        ammo_batch = serializer.validated_data.get('ammo_batch')
        training_schedule = serializer.validated_data.get('training_schedule')

        active_disposals = ViolationDisposal.objects.filter(
            shooter=shooter,
            status__in=['pending', 'notified', 'confirmed', 'rectified'],
            is_ammo_suspended=True
        )
        if active_disposals.exists():
            return Response(
                {'error': '该射手处于领弹暂停状态，禁止领用弹药'},
                status=status.HTTP_400_BAD_REQUEST
            )

        planned_qty = 0
        if training_schedule:
            planned_qty = training_schedule.allocated_rounds - training_schedule.used_rounds
            serializer.validated_data['planned_quantity'] = planned_qty
            if issue_qty > planned_qty:
                serializer.validated_data['quota_exceeded'] = True
                RiskWarning.objects.create(
                    warning_type='other',
                    warning_level='medium',
                    title=f'弹药领用超计划额度: {shooter.name}',
                    description=f'射手 {shooter.name} 计划额度 {planned_qty} 发，实际领用 {issue_qty} 发',
                    shooter=shooter
                )

        if ammo_batch:
            today = timezone.now().date()
            if ammo_batch.expiry_date and ammo_batch.expiry_date < today:
                serializer.validated_data['batch_expired'] = True
                return Response(
                    {'error': f'弹药批次 {ammo_batch.batch_number} 已过期，禁止领用'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if ammo_batch.current_quantity < issue_qty:
                return Response(
                    {'error': f'批次库存不足，当前库存: {ammo_batch.current_quantity}发'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if ammo_batch.current_quantity - issue_qty <= ammo_batch.safety_threshold:
                serializer.validated_data['stock_warning'] = True
                RiskWarning.objects.create(
                    warning_type='ammo_stock',
                    warning_level='medium',
                    title=f'弹药批次库存预警: {ammo_batch.batch_number}',
                    description=f'批次 {ammo_batch.batch_number} 领用后库存将低于安全阈值',
                    ammo_batch=ammo_batch,
                    ammunition=ammo
                )

            balance_before = ammo_batch.current_quantity
            ammo_batch.current_quantity -= issue_qty
            ammo_batch.save()
            balance_after = ammo_batch.current_quantity

            AmmoBatchFlow.objects.create(
                ammo_batch=ammo_batch,
                flow_type='issue',
                quantity=issue_qty,
                balance_before=balance_before,
                balance_after=balance_after,
                related_shooter=shooter,
                operator=request.data.get('issuer', '系统管理员'),
                remarks='弹药领用'
            )

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

        if training_schedule:
            training_schedule.status = 'in_progress'
            training_schedule.used_rounds += issue_qty
            training_schedule.save()

        self.perform_create(serializer)

        if ammo_batch:
            AmmoBatchFlow.objects.filter(related_issue__isnull=True, flow_type='issue').latest('create_time').update(
                related_issue=serializer.instance
            )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class SafetyInspectionViewSet(ExportMixin, viewsets.ModelViewSet):
    queryset = SafetyInspection.objects.all()
    serializer_class = SafetyInspectionSerializer
    filterset_fields = {
        'shooter': ['exact'],
        'target_lane': ['exact'],
        'violation_level': ['exact'],
        'inspection_time': ['exact', 'date', 'gte', 'lte']
    }
    search_fields = ['shooter__name', 'inspector', 'violation_type', 'violation_description']

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(
            has_disposal=Count('disposal') > 0
        )
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        violation_level = serializer.validated_data['violation_level']
        shooter = serializer.validated_data['shooter']

        self.perform_create(serializer)
        inspection = serializer.instance

        if violation_level != 'none':
            disposal_flow = 'level1'
            is_ammo_suspended = False
            is_score_locked = False
            suspension_days = 0

            if violation_level == 'minor':
                disposal_flow = 'level1'
            elif violation_level == 'major':
                disposal_flow = 'level2'
                suspension_days = 1
            elif violation_level == 'critical':
                disposal_flow = 'level3'
                is_ammo_suspended = True
                is_score_locked = True
                suspension_days = 7

            RiskWarning.objects.create(
                warning_type='violation_risk',
                warning_level='high' if violation_level in ['major', 'critical'] else 'medium',
                title=f'违规预警: {shooter.name} - {inspection.get_violation_level_display()}',
                description=serializer.validated_data.get('violation_description', ''),
                shooter=shooter
            )

            if violation_level in ['major', 'critical']:
                ViolationDisposal.objects.create(
                    safety_inspection=inspection,
                    shooter=shooter,
                    violation_level=violation_level,
                    disposal_flow=disposal_flow,
                    status='pending',
                    is_ammo_suspended=is_ammo_suspended,
                    is_score_locked=is_score_locked,
                    suspension_end_date=timezone.now().date() + timedelta(days=suspension_days) if is_ammo_suspended else None,
                    notified_by=request.data.get('inspector', '安全员'),
                    notified_time=timezone.now()
                )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class ViolationDisposalViewSet(ExportMixin, viewsets.ModelViewSet):
    queryset = ViolationDisposal.objects.all()
    serializer_class = ViolationDisposalSerializer
    filterset_fields = {
        'shooter': ['exact'],
        'violation_level': ['exact'],
        'disposal_flow': ['exact'],
        'status': ['exact'],
        'create_time': ['exact', 'date', 'gte', 'lte'],
        'close_time': ['exact', 'date', 'gte', 'lte']
    }
    search_fields = ['shooter__name', 'confirm_remark', 'rectification_measure', 'verify_remark']

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(
            handling_duration=ExpressionWrapper(
                ExtractHour('close_time' - 'create_time') + (ExtractHour('close_time' - 'create_time') % 60) / 60.0,
                output_field=FloatField()
            )
        )
        return queryset

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        disposal = self.get_object()
        disposal.responsible_person_confirm = True
        disposal.confirm_time = timezone.now()
        disposal.confirm_remark = request.data.get('confirm_remark', '')
        disposal.status = 'confirmed'
        disposal.save()
        return Response({'status': 'confirmed'})

    @action(detail=True, methods=['post'])
    def rectify(self, request, pk=None):
        disposal = self.get_object()
        disposal.rectification_measure = request.data.get('rectification_measure', '')
        disposal.rectification_deadline = request.data.get('rectification_deadline')
        disposal.rectification_time = timezone.now()
        disposal.status = 'rectified'
        disposal.save()
        return Response({'status': 'rectified'})

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        disposal = self.get_object()
        disposal.verified_by = request.data.get('verified_by', '系统管理员')
        disposal.verify_time = timezone.now()
        disposal.verify_remark = request.data.get('verify_remark', '')
        disposal.status = 'verified'
        disposal.save()
        return Response({'status': 'verified'})

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        disposal = self.get_object()
        disposal.closed_by = request.data.get('closed_by', '系统管理员')
        disposal.close_time = timezone.now()
        disposal.status = 'closed'
        disposal.is_ammo_suspended = False
        disposal.is_score_locked = False
        disposal.save()
        return Response({'status': 'closed'})

class ScoreRecordViewSet(ExportMixin, viewsets.ModelViewSet):
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

        shooter = serializer.validated_data['shooter']

        active_disposals = ViolationDisposal.objects.filter(
            shooter=shooter,
            status__in=['pending', 'notified', 'confirmed', 'rectified'],
            is_score_locked=True
        )
        if active_disposals.exists():
            return Response(
                {'error': '该射手成绩处于锁定状态，禁止录入成绩'},
                status=status.HTTP_400_BAD_REQUEST
            )

        firearm = serializer.validated_data['firearm']
        shots_fired = serializer.validated_data['shots_fired']
        firearm.total_rounds += shots_fired
        firearm.save()

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class AmmoReturnViewSet(ExportMixin, viewsets.ModelViewSet):
    queryset = AmmoReturn.objects.all()
    serializer_class = AmmoReturnSerializer
    filterset_fields = {
        'shooter': ['exact'],
        'ammunition': ['exact'],
        'ammo_batch': ['exact'],
        'closure_complete': ['exact'],
        'has_exception': ['exact'],
        'return_time': ['exact', 'date', 'gte', 'lte']
    }
    search_fields = ['shooter__name', 'receiver', 'exception_description', 'responsible_person']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ammo_issue = serializer.validated_data['ammo_issue']
        ammo = serializer.validated_data['ammunition']
        ammo_batch = serializer.validated_data.get('ammo_batch')
        returned_qty = serializer.validated_data['returned_quantity']
        consumed_qty = serializer.validated_data['consumed_quantity']
        shell_casing_returned = serializer.validated_data['shell_casing_returned']

        ammo.stock_quantity += returned_qty
        ammo.save()

        if ammo_batch:
            balance_before = ammo_batch.current_quantity
            ammo_batch.current_quantity += returned_qty
            ammo_batch.save()
            balance_after = ammo_batch.current_quantity

            AmmoBatchFlow.objects.create(
                ammo_batch=ammo_batch,
                flow_type='return',
                quantity=returned_qty,
                balance_before=balance_before,
                balance_after=balance_after,
                related_shooter=ammo_issue.shooter,
                related_return=None,
                operator=request.data.get('receiver', '系统管理员'),
                remarks='弹药归还'
            )

            if consumed_qty > 0:
                AmmoBatchFlow.objects.create(
                    ammo_batch=ammo_batch,
                    flow_type='consume',
                    quantity=consumed_qty,
                    balance_before=balance_after,
                    balance_after=balance_after,
                    related_shooter=ammo_issue.shooter,
                    operator=request.data.get('receiver', '系统管理员'),
                    remarks=f'训练消耗 {consumed_qty} 发，回收弹壳 {shell_casing_returned} 发'
                )

        ammo_issue.status = 'completed'
        ammo_issue.save()

        target_lane = ammo_issue.target_lane
        target_lane.status = 'available'
        target_lane.save()

        firearm = ammo_issue.firearm
        firearm.status = 'available'
        firearm.save()

        if ammo_issue.training_schedule:
            schedule = ammo_issue.training_schedule
            schedule.status = 'completed'
            schedule.save()

        self.perform_create(serializer)

        if ammo_batch:
            AmmoBatchFlow.objects.filter(related_return__isnull=True, flow_type='return').latest('create_time').update(
                related_return=serializer.instance
            )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class AmmoBatchFlowViewSet(ExportMixin, viewsets.ModelViewSet):
    queryset = AmmoBatchFlow.objects.all()
    serializer_class = AmmoBatchFlowSerializer
    filterset_fields = {
        'ammo_batch': ['exact'],
        'flow_type': ['exact'],
        'related_shooter': ['exact'],
        'create_time': ['exact', 'date', 'gte', 'lte']
    }
    search_fields = ['remarks', 'operator']

@api_view(['POST'])
def generate_schedule_recommendations(request):
    serializer = ScheduleRecommendationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    plan_id = serializer.validated_data['training_plan_id']
    try:
        plan = TrainingPlan.objects.get(id=plan_id)
    except TrainingPlan.DoesNotExist:
        return Response({'error': '训练计划不存在'}, status=status.HTTP_404_NOT_FOUND)

    recommendations, conflicts, warnings = TrainingPlanViewSet._generate_schedule_recommendations(
        TrainingPlanViewSet(), plan
    )

    return Response({
        'training_plan_id': plan_id,
        'recommendations': recommendations,
        'conflicts': conflicts,
        'warnings': warnings
    })

@api_view(['GET'])
def statistics_dashboard(request):
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    seven_days_ago = now - timedelta(days=7)
    today = now.date()

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
    total_checkins_today = CheckIn.objects.filter(checkin_time__date=today).count()
    total_ammo_issued_today = AmmoIssue.objects.filter(issue_time__date=today).aggregate(
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

    plan_stats = TrainingPlan.objects.annotate(
        total_sched=Count('schedules'),
        completed_sched=Count('schedules', filter=Q(schedules__status='completed'))
    ).values('id', 'plan_name', 'total_sched', 'completed_sched', 'start_date', 'end_date')

    plan_completion_rates = []
    for plan in plan_stats:
        completion_rate = round((plan['completed_sched'] / plan['total_sched'] * 100), 2) if plan['total_sched'] > 0 else 0
        plan_completion_rates.append({
            'plan_id': plan['id'],
            'plan_name': plan['plan_name'],
            'completion_rate': completion_rate,
            'total_schedules': plan['total_sched'],
            'completed_schedules': plan['completed_sched'],
            'pending_schedules': plan['total_sched'] - plan['completed_sched'],
            'start_date': plan['start_date'],
            'end_date': plan['end_date']
        })

    all_schedules = TrainingSchedule.objects.filter(create_time__gte=thirty_days_ago)
    total_schedules = all_schedules.count()
    conflict_schedules = all_schedules.filter(conflict_warning=True).count()
    lane_conflict_rate = round((conflict_schedules / total_schedules * 100), 2) if total_schedules > 0 else 0

    daily_conflicts = LaneReservation.objects.filter(
        create_time__gte=thirty_days_ago,
        conflict_detected=True
    ).annotate(
        date=TruncDate('create_time')
    ).values('date').annotate(
        conflict_count=Count('id')
    ).order_by('date')

    batch_flow_stats = AmmoBatchFlow.objects.filter(
        create_time__gte=thirty_days_ago
    ).values('flow_type').annotate(
        total_quantity=Sum('quantity'),
        count=Count('id')
    ).order_by('flow_type')

    batch_usage = AmmoBatchFlow.objects.filter(
        flow_type='issue',
        create_time__gte=thirty_days_ago
    ).values('ammo_batch__batch_number', 'ammo_batch__ammunition__name').annotate(
        total_used=Sum('quantity')
    ).order_by('-total_used')[:10]

    risk_shooters = Shooter.objects.filter(status='active').annotate(
        total_violations=Count('safetyinspection', filter=Q(safetyinspection__violation_level__in=['minor', 'major', 'critical'])),
        recent_violations=Count('safetyinspection', filter=Q(
            safetyinspection__violation_level__in=['minor', 'major', 'critical'],
            safetyinspection__inspection_time__gte=thirty_days_ago
        )),
        critical_count=Count('safetyinspection', filter=Q(safetyinspection__violation_level='critical')),
        major_count=Count('safetyinspection', filter=Q(safetyinspection__violation_level='major')),
        minor_count=Count('safetyinspection', filter=Q(safetyinspection__violation_level='minor')),
        open_disposals=Count('violation_disposals', filter=Q(violation_disposals__status__in=['pending', 'notified', 'confirmed', 'rectified']))
    ).annotate(
        risk_score=ExpressionWrapper(
            F('critical_count') * 10 + F('major_count') * 5 + F('minor_count') * 2 + F('open_disposals') * 3,
            output_field=FloatField()
        )
    ).filter(
        Q(total_violations__gt=0) | Q(open_disposals__gt=0)
    ).order_by('-risk_score')[:10]

    risk_shooter_list = []
    for shooter in risk_shooters:
        risk_level = 'low'
        if shooter.risk_score >= 20:
            risk_level = 'critical'
        elif shooter.risk_score >= 10:
            risk_level = 'high'
        elif shooter.risk_score >= 5:
            risk_level = 'medium'
        risk_shooter_list.append({
            'shooter_id': shooter.id,
            'shooter_name': shooter.name,
            'unit': shooter.unit,
            'qualification_level': shooter.qualification_level,
            'violation_count': shooter.total_violations,
            'recent_violations': shooter.recent_violations,
            'risk_score': float(shooter.risk_score),
            'risk_level': risk_level
        })

    level_display_map = {
        'none': '无违规',
        'minor': '轻微违规',
        'major': '严重违规',
        'critical': '重大违规'
    }

    closure_agg = ViolationDisposal.objects.filter(
        create_time__gte=thirty_days_ago
    ).values('violation_level').annotate(
        total_count=Count('id'),
        closed_count=Count('id', filter=Q(status='closed')),
        pending_count=Count('id', filter=Q(status__in=['pending', 'notified', 'confirmed', 'rectified', 'verified']))
    )

    closure_stats_list = []
    for stat in closure_agg:
        level = stat['violation_level']
        closed_items = ViolationDisposal.objects.filter(
            create_time__gte=thirty_days_ago,
            violation_level=level,
            status='closed',
            close_time__isnull=False
        )
        total_hours = 0
        count = closed_items.count()
        if count > 0:
            for item in closed_items:
                delta = item.close_time - item.create_time
                total_hours += delta.total_seconds() / 3600.0
            avg_duration = round(total_hours / count, 2)
        else:
            avg_duration = 0
        closure_rate = round((stat['closed_count'] / stat['total_count'] * 100), 2) if stat['total_count'] > 0 else 0
        closure_stats_list.append({
            'violation_level': level,
            'violation_level_display': level_display_map.get(level, level),
            'total_count': stat['total_count'],
            'closed_count': stat['closed_count'],
            'pending_count': stat['pending_count'],
            'avg_closure_hours': round(avg_duration, 2),
            'closure_rate': closure_rate
        })

    daily_closure_efficiency = ViolationDisposal.objects.filter(
        create_time__gte=thirty_days_ago
    ).annotate(
        date=TruncDate('create_time')
    ).values('date').annotate(
        total_created=Count('id'),
        total_closed=Count('id', filter=Q(status='closed', close_time__isnull=False))
    ).order_by('date')

    pending_warnings = RiskWarning.objects.filter(status='pending').count()
    low_stock_batches = AmmoBatch.objects.filter(quality_status='warning').count()
    expiring_batches = AmmoBatch.objects.filter(
        expiry_date__lte=today + timedelta(days=30),
        expiry_date__gte=today
    ).count()
    expired_batches = AmmoBatch.objects.filter(quality_status='expired').count()

    return Response({
        'overview': {
            'total_active_shooters': total_shooters,
            'today_checkins': total_checkins_today,
            'today_ammo_issued': total_ammo_issued_today,
            'recent_violations': total_violations,
            'active_sessions': active_sessions,
            'avg_score_30d': round(avg_score, 2),
            'total_ammo_stock': ammo_stock,
            'pending_warnings': pending_warnings,
            'low_stock_batches': low_stock_batches,
            'expiring_batches': expiring_batches,
            'expired_batches': expired_batches,
        },
        'lane_usage': list(lane_usage),
        'ammo_trend': list(ammo_trend),
        'ammo_monthly': list(ammo_monthly),
        'violation_stats': list(violation_stats),
        'shooter_attendance': list(shooter_attendance),
        'violation_types': list(violation_types),
        'plan_completion_rates': plan_completion_rates,
        'lane_conflict_rate': lane_conflict_rate,
        'daily_conflicts': list(daily_conflicts),
        'batch_flow_stats': list(batch_flow_stats),
        'batch_usage': list(batch_usage),
        'risk_shooters': risk_shooter_list,
        'closure_stats': closure_stats_list,
        'daily_closure_efficiency': list(daily_closure_efficiency),
    })

@api_view(['GET'])
def advanced_statistics(request):
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    today = now.date()

    plan_stats = TrainingPlan.objects.annotate(
        total_sched=Count('schedules'),
        completed_sched=Count('schedules', filter=Q(schedules__status='completed'))
    ).values('id', 'plan_name', 'total_sched', 'completed_sched', 'start_date', 'end_date', 'plan_type')

    plan_completion_rates = []
    for plan in plan_stats:
        completion_rate = round((plan['completed_sched'] / plan['total_sched'] * 100), 2) if plan['total_sched'] > 0 else 0
        plan_completion_rates.append({
            'plan_id': plan['id'],
            'plan_name': plan['plan_name'],
            'plan_type': plan['plan_type'],
            'completion_rate': completion_rate,
            'total_schedules': plan['total_sched'],
            'completed_schedules': plan['completed_sched'],
            'pending_schedules': plan['total_sched'] - plan['completed_sched'],
            'start_date': plan['start_date'],
            'end_date': plan['end_date']
        })

    all_schedules = TrainingSchedule.objects.filter(create_time__gte=thirty_days_ago)
    total_schedules = all_schedules.count()
    conflict_schedules = all_schedules.filter(conflict_warning=True).count()
    lane_conflict_rate = round((conflict_schedules / total_schedules * 100), 2) if total_schedules > 0 else 0

    daily_conflicts = LaneReservation.objects.filter(
        create_time__gte=thirty_days_ago,
        conflict_detected=True
    ).annotate(
        date=TruncDate('create_time')
    ).values('date').annotate(
        conflict_count=Count('id')
    ).order_by('date')

    batch_flow_stats = AmmoBatchFlow.objects.filter(
        create_time__gte=thirty_days_ago
    ).values('flow_type').annotate(
        total_quantity=Sum('quantity'),
        count=Count('id')
    ).order_by('flow_type')

    batch_usage = AmmoBatchFlow.objects.filter(
        flow_type='issue',
        create_time__gte=thirty_days_ago
    ).values('ammo_batch__batch_number', 'ammo_batch__ammunition__name').annotate(
        total_used=Sum('quantity')
    ).order_by('-total_used')[:10]

    risk_shooters = Shooter.objects.filter(status='active').annotate(
        total_violations=Count('safetyinspection', filter=Q(safetyinspection__violation_level__in=['minor', 'major', 'critical'])),
        recent_violations=Count('safetyinspection', filter=Q(
            safetyinspection__violation_level__in=['minor', 'major', 'critical'],
            safetyinspection__inspection_time__gte=thirty_days_ago
        )),
        critical_count=Count('safetyinspection', filter=Q(safetyinspection__violation_level='critical')),
        major_count=Count('safetyinspection', filter=Q(safetyinspection__violation_level='major')),
        minor_count=Count('safetyinspection', filter=Q(safetyinspection__violation_level='minor')),
        open_disposals=Count('violation_disposals', filter=Q(violation_disposals__status__in=['pending', 'notified', 'confirmed', 'rectified']))
    ).annotate(
        risk_score=ExpressionWrapper(
            F('critical_count') * 10 + F('major_count') * 5 + F('minor_count') * 2 + F('open_disposals') * 3,
            output_field=FloatField()
        )
    ).filter(
        Q(total_violations__gt=0) | Q(open_disposals__gt=0)
    ).order_by('-risk_score')[:10]

    risk_shooter_list = []
    for shooter in risk_shooters:
        risk_level = 'low'
        if shooter.risk_score >= 20:
            risk_level = 'critical'
        elif shooter.risk_score >= 10:
            risk_level = 'high'
        elif shooter.risk_score >= 5:
            risk_level = 'medium'
        risk_shooter_list.append({
            'shooter_id': shooter.id,
            'shooter_name': shooter.name,
            'unit': shooter.unit,
            'qualification_level': shooter.qualification_level,
            'violation_count': shooter.total_violations,
            'recent_violations': shooter.recent_violations,
            'risk_score': float(shooter.risk_score),
            'risk_level': risk_level
        })

    level_display_map = {
        'none': '无违规',
        'minor': '轻微违规',
        'major': '严重违规',
        'critical': '重大违规'
    }

    closure_agg = ViolationDisposal.objects.filter(
        create_time__gte=thirty_days_ago
    ).values('violation_level').annotate(
        total_count=Count('id'),
        closed_count=Count('id', filter=Q(status='closed')),
        pending_count=Count('id', filter=Q(status__in=['pending', 'notified', 'confirmed', 'rectified', 'verified']))
    )

    closure_stats_list = []
    for stat in closure_agg:
        level = stat['violation_level']
        closed_items = ViolationDisposal.objects.filter(
            create_time__gte=thirty_days_ago,
            violation_level=level,
            status='closed',
            close_time__isnull=False
        )
        total_hours = 0
        count = closed_items.count()
        if count > 0:
            for item in closed_items:
                delta = item.close_time - item.create_time
                total_hours += delta.total_seconds() / 3600.0
            avg_duration = round(total_hours / count, 2)
        else:
            avg_duration = 0
        closure_rate = round((stat['closed_count'] / stat['total_count'] * 100), 2) if stat['total_count'] > 0 else 0
        closure_stats_list.append({
            'violation_level': level,
            'violation_level_display': level_display_map.get(level, level),
            'total_count': stat['total_count'],
            'closed_count': stat['closed_count'],
            'pending_count': stat['pending_count'],
            'avg_closure_hours': round(avg_duration, 2),
            'closure_rate': closure_rate
        })

    daily_closure_efficiency = ViolationDisposal.objects.filter(
        create_time__gte=thirty_days_ago
    ).annotate(
        date=TruncDate('create_time')
    ).values('date').annotate(
        total_created=Count('id'),
        total_closed=Count('id', filter=Q(status='closed', close_time__isnull=False))
    ).order_by('date')

    return Response({
        'plan_completion_rates': plan_completion_rates,
        'lane_conflict_rate': lane_conflict_rate,
        'daily_conflicts': list(daily_conflicts),
        'batch_flow_stats': list(batch_flow_stats),
        'batch_usage': list(batch_usage),
        'risk_shooters': risk_shooter_list,
        'closure_stats': closure_stats_list,
        'daily_closure_efficiency': list(daily_closure_efficiency),
    })
