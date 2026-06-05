from rest_framework import serializers
from .models import (
    Shooter, Ammunition, Firearm, TargetLane,
    CheckIn, AmmoIssue, SafetyInspection, ScoreRecord, AmmoReturn
)

class ShooterSerializer(serializers.ModelSerializer):
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

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

class CheckInSerializer(serializers.ModelSerializer):
    shooter_info = ShooterSerializer(source='shooter', read_only=True)
    alcohol_test_display = serializers.CharField(source='get_alcohol_test_display', read_only=True)
    psychological_status_display = serializers.CharField(source='get_psychological_status_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = CheckIn
        fields = '__all__'

class AmmoIssueSerializer(serializers.ModelSerializer):
    shooter_info = ShooterSerializer(source='shooter', read_only=True)
    ammunition_info = AmmunitionSerializer(source='ammunition', read_only=True)
    target_lane_info = TargetLaneSerializer(source='target_lane', read_only=True)
    firearm_info = FirearmSerializer(source='firearm', read_only=True)
    checkin_info = CheckInSerializer(source='checkin', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = AmmoIssue
        fields = '__all__'

class SafetyInspectionSerializer(serializers.ModelSerializer):
    shooter_info = ShooterSerializer(source='shooter', read_only=True)
    target_lane_info = TargetLaneSerializer(source='target_lane', read_only=True)
    ammo_issue_info = AmmoIssueSerializer(source='ammo_issue', read_only=True)
    violation_level_display = serializers.CharField(source='get_violation_level_display', read_only=True)

    class Meta:
        model = SafetyInspection
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
    ammo_issue_info = AmmoIssueSerializer(source='ammo_issue', read_only=True)

    class Meta:
        model = AmmoReturn
        fields = '__all__'
