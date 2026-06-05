from rest_framework import serializers
from .models import (
    Shooter, Ammunition, Firearm, TargetLane,
    CheckIn, AmmoIssue, SafetyInspection, ScoreRecord, AmmoReturn,
    AmmoBatch, TrainingPlan, TrainingSchedule, LaneReservation,
    RiskWarning, ViolationDisposal, AmmoBatchFlow
)

class ShooterSerializer(serializers.ModelSerializer):
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    violation_count = serializers.IntegerField(read_only=True)
    risk_score = serializers.FloatField(read_only=True)

    class Meta:
        model = Shooter
        fields = '__all__'

class AmmunitionSerializer(serializers.ModelSerializer):
    ammo_type_display = serializers.CharField(source='get_ammo_type_display', read_only=True)
    caliber_display = serializers.CharField(source='get_caliber_display', read_only=True)

    class Meta:
        model = Ammunition
        fields = '__all__'

class FirearmSerializer(serializers.ModelSerializer):
    firearm_type_display = serializers.CharField(source='get_firearm_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Firearm
        fields = '__all__'

class TargetLaneSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = TargetLane
        fields = '__all__'

class AmmoBatchSerializer(serializers.ModelSerializer):
    ammunition_info = AmmunitionSerializer(source='ammunition', read_only=True)
    quality_status_display = serializers.CharField(source='get_quality_status_display', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = AmmoBatch
        fields = '__all__'

class TrainingPlanSerializer(serializers.ModelSerializer):
    plan_type_display = serializers.CharField(source='get_plan_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    completion_rate = serializers.FloatField(read_only=True)
    target_shooters_count = serializers.IntegerField(read_only=True)
    total_schedules = serializers.IntegerField(read_only=True)
    completed_schedules = serializers.IntegerField(read_only=True)

    class Meta:
        model = TrainingPlan
        fields = '__all__'

class TrainingScheduleSerializer(serializers.ModelSerializer):
    training_plan_info = TrainingPlanSerializer(source='training_plan', read_only=True)
    shooter_info = ShooterSerializer(source='shooter', read_only=True)
    target_lane_info = TargetLaneSerializer(source='target_lane', read_only=True)
    firearm_info = FirearmSerializer(source='firearm', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = TrainingSchedule
        fields = '__all__'

class LaneReservationSerializer(serializers.ModelSerializer):
    target_lane_info = TargetLaneSerializer(source='target_lane', read_only=True)
    shooter_info = ShooterSerializer(source='shooter', read_only=True)
    training_schedule_info = TrainingScheduleSerializer(source='training_schedule', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = LaneReservation
        fields = '__all__'

class RiskWarningSerializer(serializers.ModelSerializer):
    warning_type_display = serializers.CharField(source='get_warning_type_display', read_only=True)
    warning_level_display = serializers.CharField(source='get_warning_level_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    shooter_info = ShooterSerializer(source='shooter', read_only=True)
    ammunition_info = AmmunitionSerializer(source='ammunition', read_only=True)
    ammo_batch_info = AmmoBatchSerializer(source='ammo_batch', read_only=True)
    target_lane_info = TargetLaneSerializer(source='target_lane', read_only=True)

    class Meta:
        model = RiskWarning
        fields = '__all__'

class CheckInSerializer(serializers.ModelSerializer):
    shooter_info = ShooterSerializer(source='shooter', read_only=True)
    training_plan_info = TrainingPlanSerializer(source='training_plan', read_only=True)
    training_schedule_info = TrainingScheduleSerializer(source='training_schedule', read_only=True)
    alcohol_test_display = serializers.CharField(source='get_alcohol_test_display', read_only=True)
    psychological_status_display = serializers.CharField(source='get_psychological_status_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = CheckIn
        fields = '__all__'

class AmmoIssueSerializer(serializers.ModelSerializer):
    shooter_info = ShooterSerializer(source='shooter', read_only=True)
    ammunition_info = AmmunitionSerializer(source='ammunition', read_only=True)
    ammo_batch_info = AmmoBatchSerializer(source='ammo_batch', read_only=True)
    target_lane_info = TargetLaneSerializer(source='target_lane', read_only=True)
    firearm_info = FirearmSerializer(source='firearm', read_only=True)
    checkin_info = CheckInSerializer(source='checkin', read_only=True)
    training_plan_info = TrainingPlanSerializer(source='training_plan', read_only=True)
    training_schedule_info = TrainingScheduleSerializer(source='training_schedule', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = AmmoIssue
        fields = '__all__'

class SafetyInspectionSerializer(serializers.ModelSerializer):
    shooter_info = ShooterSerializer(source='shooter', read_only=True)
    target_lane_info = TargetLaneSerializer(source='target_lane', read_only=True)
    ammo_issue_info = AmmoIssueSerializer(source='ammo_issue', read_only=True)
    violation_level_display = serializers.CharField(source='get_violation_level_display', read_only=True)
    has_disposal = serializers.BooleanField(read_only=True)

    class Meta:
        model = SafetyInspection
        fields = '__all__'

class ViolationDisposalSerializer(serializers.ModelSerializer):
    safety_inspection_info = SafetyInspectionSerializer(source='safety_inspection', read_only=True)
    shooter_info = ShooterSerializer(source='shooter', read_only=True)
    violation_level_display = serializers.CharField(source='get_violation_level_display', read_only=True)
    disposal_flow_display = serializers.CharField(source='get_disposal_flow_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    handling_duration = serializers.FloatField(read_only=True)

    class Meta:
        model = ViolationDisposal
        fields = '__all__'

class ScoreRecordSerializer(serializers.ModelSerializer):
    shooter_info = ShooterSerializer(source='shooter', read_only=True)
    target_lane_info = TargetLaneSerializer(source='target_lane', read_only=True)
    firearm_info = FirearmSerializer(source='firearm', read_only=True)
    ammunition_info = AmmunitionSerializer(source='ammunition', read_only=True)
    ammo_issue_info = AmmoIssueSerializer(source='ammo_issue', read_only=True)

    class Meta:
        model = ScoreRecord
        fields = '__all__'

class AmmoReturnSerializer(serializers.ModelSerializer):
    shooter_info = ShooterSerializer(source='shooter', read_only=True)
    ammunition_info = AmmunitionSerializer(source='ammunition', read_only=True)
    ammo_batch_info = AmmoBatchSerializer(source='ammo_batch', read_only=True)
    ammo_issue_info = AmmoIssueSerializer(source='ammo_issue', read_only=True)

    class Meta:
        model = AmmoReturn
        fields = '__all__'

class AmmoBatchFlowSerializer(serializers.ModelSerializer):
    ammo_batch_info = AmmoBatchSerializer(source='ammo_batch', read_only=True)
    flow_type_display = serializers.CharField(source='get_flow_type_display', read_only=True)
    related_shooter_info = ShooterSerializer(source='related_shooter', read_only=True)

    class Meta:
        model = AmmoBatchFlow
        fields = '__all__'

class ScheduleRecommendationSerializer(serializers.Serializer):
    training_plan_id = serializers.IntegerField(required=True)
    recommendations = serializers.ListField(read_only=True)
    conflicts = serializers.ListField(read_only=True)
    warnings = serializers.ListField(read_only=True)

class TrainingPlanStatsSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField()
    plan_name = serializers.CharField()
    completion_rate = serializers.FloatField()
    total_schedules = serializers.IntegerField()
    completed_schedules = serializers.IntegerField()
    pending_schedules = serializers.IntegerField()
    cancelled_schedules = serializers.IntegerField()
    total_rounds_planned = serializers.IntegerField()
    total_rounds_used = serializers.IntegerField()

class RiskShooterSerializer(serializers.Serializer):
    shooter_id = serializers.IntegerField()
    shooter_name = serializers.CharField()
    unit = serializers.CharField()
    qualification_level = serializers.CharField()
    violation_count = serializers.IntegerField()
    recent_violations = serializers.IntegerField()
    risk_score = serializers.FloatField()
    risk_level = serializers.CharField()

class ViolationClosureStatsSerializer(serializers.Serializer):
    violation_level = serializers.CharField()
    total_count = serializers.IntegerField()
    closed_count = serializers.IntegerField()
    pending_count = serializers.IntegerField()
    avg_closure_hours = serializers.FloatField()
    closure_rate = serializers.FloatField()
