from django.contrib import admin
from .models import (
    Shooter, Ammunition, Firearm, TargetLane,
    CheckIn, AmmoIssue, SafetyInspection, ScoreRecord, AmmoReturn
)

@admin.register(Shooter)
class ShooterAdmin(admin.ModelAdmin):
    list_display = ['id_card', 'name', 'gender', 'age', 'unit', 'status', 'create_time']
    list_filter = ['gender', 'status', 'unit']
    search_fields = ['name', 'id_card', 'phone', 'unit']

@admin.register(Ammunition)
class AmmunitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'ammo_type', 'caliber', 'stock_quantity', 'unit', 'batch_number', 'create_time']
    list_filter = ['ammo_type', 'caliber']
    search_fields = ['name', 'batch_number', 'manufacturer']

@admin.register(Firearm)
class FirearmAdmin(admin.ModelAdmin):
    list_display = ['name', 'firearm_type', 'model', 'serial_number', 'status', 'total_rounds', 'create_time']
    list_filter = ['firearm_type', 'status']
    search_fields = ['name', 'model', 'serial_number']

@admin.register(TargetLane)
class TargetLaneAdmin(admin.ModelAdmin):
    list_display = ['lane_number', 'name', 'distance', 'status', 'max_shooters']
    list_filter = ['status']
    search_fields = ['name', 'target_type']

@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ['shooter', 'checkin_time', 'id_verified', 'alcohol_test', 'psychological_status', 'status']
    list_filter = ['alcohol_test', 'psychological_status', 'status', 'checkin_time']
    search_fields = ['shooter__name', 'operator']

@admin.register(AmmoIssue)
class AmmoIssueAdmin(admin.ModelAdmin):
    list_display = ['shooter', 'ammunition', 'issue_quantity', 'target_lane', 'firearm', 'issue_time', 'status']
    list_filter = ['status', 'issue_time']
    search_fields = ['shooter__name', 'issuer']

@admin.register(SafetyInspection)
class SafetyInspectionAdmin(admin.ModelAdmin):
    list_display = ['shooter', 'target_lane', 'inspection_time', 'inspector', 'violation_level', 'score_deduction']
    list_filter = ['violation_level', 'inspection_time']
    search_fields = ['shooter__name', 'inspector', 'violation_type']

@admin.register(ScoreRecord)
class ScoreRecordAdmin(admin.ModelAdmin):
    list_display = ['shooter', 'target_lane', 'shots_fired', 'total_score', 'average_score', 'hit_count', 'record_time']
    list_filter = ['record_time']
    search_fields = ['shooter__name', 'recorder']

@admin.register(AmmoReturn)
class AmmoReturnAdmin(admin.ModelAdmin):
    list_display = ['shooter', 'ammunition', 'issued_quantity', 'consumed_quantity', 'returned_quantity', 'shell_casing_returned', 'return_time']
    list_filter = ['return_time']
    search_fields = ['shooter__name', 'receiver']
