from django.db import models
from django.utils import timezone

class Shooter(models.Model):
    GENDER_CHOICES = [('M', '男'), ('F', '女')]
    STATUS_CHOICES = [('active', '在岗'), ('inactive', '离岗'), ('suspended', '停训')]

    id_card = models.CharField('身份证号', max_length=18, unique=True)
    name = models.CharField('姓名', max_length=50)
    gender = models.CharField('性别', max_length=1, choices=GENDER_CHOICES)
    age = models.IntegerField('年龄')
    unit = models.CharField('所属单位', max_length=100)
    phone = models.CharField('联系电话', max_length=20)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='active')
    qualification_level = models.CharField('资质等级', max_length=50, blank=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '射手信息'
        verbose_name_plural = '射手信息'
        ordering = ['-create_time']

    def __str__(self):
        return f'{self.name} - {self.id_card}'

class Ammunition(models.Model):
    TYPE_CHOICES = [
        ('pistol', '手枪弹'),
        ('rifle', '步枪弹'),
        ('shotgun', '霰弹'),
        ('sniper', '狙击弹'),
    ]
    CALIBER_CHOICES = [
        ('9mm', '9mm'),
        ('5.56mm', '5.56mm'),
        ('7.62mm', '7.62mm'),
        ('12ga', '12号霰弹'),
        ('other', '其他'),
    ]

    ammo_type = models.CharField('弹药类型', max_length=20, choices=TYPE_CHOICES)
    caliber = models.CharField('口径', max_length=20, choices=CALIBER_CHOICES)
    name = models.CharField('弹药名称', max_length=100)
    stock_quantity = models.IntegerField('库存数量', default=0)
    unit = models.CharField('计量单位', max_length=10, default='发')
    manufacturer = models.CharField('生产厂商', max_length=100, blank=True)
    production_date = models.DateField('生产日期', null=True, blank=True)
    expiry_date = models.DateField('有效期至', null=True, blank=True)
    batch_number = models.CharField('批次号', max_length=50, blank=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '弹药信息'
        verbose_name_plural = '弹药信息'
        ordering = ['-create_time']

    def __str__(self):
        return f'{self.name} ({self.caliber})'

class Firearm(models.Model):
    TYPE_CHOICES = [
        ('pistol', '手枪'),
        ('rifle', '步枪'),
        ('shotgun', '霰弹枪'),
        ('sniper', '狙击步枪'),
        ('submachine', '冲锋枪'),
    ]
    STATUS_CHOICES = [
        ('available', '可用'),
        ('in_use', '使用中'),
        ('maintenance', '维护中'),
        ('damaged', '损坏'),
    ]

    firearm_type = models.CharField('枪械类型', max_length=20, choices=TYPE_CHOICES)
    model = models.CharField('型号', max_length=50)
    serial_number = models.CharField('枪号', max_length=50, unique=True)
    name = models.CharField('枪械名称', max_length=100)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='available')
    manufacturer = models.CharField('生产厂商', max_length=100, blank=True)
    purchase_date = models.DateField('购置日期', null=True, blank=True)
    last_maintenance = models.DateField('上次维护日期', null=True, blank=True)
    total_rounds = models.IntegerField('累计发射弹数', default=0)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '枪械信息'
        verbose_name_plural = '枪械信息'
        ordering = ['-create_time']

    def __str__(self):
        return f'{self.name} ({self.serial_number})'

class TargetLane(models.Model):
    STATUS_CHOICES = [
        ('available', '空闲'),
        ('occupied', '使用中'),
        ('maintenance', '维护中'),
        ('closed', '关闭'),
    ]

    lane_number = models.IntegerField('靶道编号', unique=True)
    name = models.CharField('靶道名称', max_length=50)
    distance = models.IntegerField('射击距离(米)', default=25)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='available')
    target_type = models.CharField('靶纸类型', max_length=50, blank=True)
    max_shooters = models.IntegerField('最大同时射击人数', default=1)
    remarks = models.TextField('备注', blank=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '靶道信息'
        verbose_name_plural = '靶道信息'
        ordering = ['lane_number']

    def __str__(self):
        return f'{self.lane_number}号靶道 - {self.name}'

class AmmoBatch(models.Model):
    ammunition = models.ForeignKey(Ammunition, on_delete=models.CASCADE, verbose_name='弹药类型', related_name='batches')
    batch_number = models.CharField('批次号', max_length=50, unique=True)
    production_date = models.DateField('生产日期', null=True, blank=True)
    expiry_date = models.DateField('有效期至', null=True, blank=True)
    manufacturer = models.CharField('生产厂商', max_length=100, blank=True)
    initial_quantity = models.IntegerField('初始数量', default=0)
    current_quantity = models.IntegerField('当前数量', default=0)
    safety_threshold = models.IntegerField('安全阈值', default=100)
    storage_location = models.CharField('存储位置', max_length=100, blank=True)
    quality_status = models.CharField('质量状态', max_length=20, choices=[
        ('normal', '正常'),
        ('warning', '预警'),
        ('expired', '已过期'),
        ('damaged', '破损')
    ], default='normal')
    inspector = models.CharField('检验员', max_length=50, blank=True)
    inspection_date = models.DateField('检验日期', null=True, blank=True)
    remarks = models.TextField('备注', blank=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '弹药批次'
        verbose_name_plural = '弹药批次'
        ordering = ['-create_time']

    def __str__(self):
        return f'{self.ammunition.name} - {self.batch_number}'

    def save(self, *args, **kwargs):
        if self.current_quantity <= self.safety_threshold:
            self.quality_status = 'warning'
        if self.expiry_date and timezone.now().date() > self.expiry_date:
            self.quality_status = 'expired'
        super().save(*args, **kwargs)

class TrainingPlan(models.Model):
    PLAN_STATUS = [
        ('draft', '草稿'),
        ('approved', '已批准'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('cancelled', '已取消')
    ]

    plan_name = models.CharField('计划名称', max_length=200)
    plan_type = models.CharField('训练类型', max_length=50, choices=[
        ('basic', '基础训练'),
        ('advanced', '进阶训练'),
        ('assessment', '考核评估'),
        ('emergency', '应急训练'),
        ('special', '专项训练')
    ], default='basic')
    description = models.TextField('训练描述', blank=True)
    start_date = models.DateField('开始日期')
    end_date = models.DateField('结束日期')
    daily_start_time = models.TimeField('每日开始时间', default='08:00')
    daily_end_time = models.TimeField('每日结束时间', default='18:00')
    target_shooters = models.ManyToManyField(Shooter, related_name='training_plans', verbose_name='目标射手', blank=True)
    required_qualification = models.CharField('要求资质等级', max_length=50, blank=True)
    total_rounds_per_shooter = models.IntegerField('每人预计弹数', default=0)
    planned_ammo_types = models.ManyToManyField(Ammunition, related_name='training_plans', verbose_name='计划弹药类型', blank=True)
    required_firearm_types = models.CharField('要求枪械类型', max_length=200, blank=True)
    lanes_count = models.IntegerField('需用靶道数', default=1)
    creator = models.CharField('创建人', max_length=50, blank=True)
    approver = models.CharField('批准人', max_length=50, blank=True)
    approval_time = models.DateTimeField('批准时间', null=True, blank=True)
    status = models.CharField('状态', max_length=20, choices=PLAN_STATUS, default='draft')
    remarks = models.TextField('备注', blank=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '训练计划'
        verbose_name_plural = '训练计划'
        ordering = ['-create_time']

    def __str__(self):
        return self.plan_name

    def get_completion_rate(self):
        total_schedules = self.schedules.count()
        if total_schedules == 0:
            return 0
        completed = self.schedules.filter(status='completed').count()
        return round((completed / total_schedules) * 100, 2)

class TrainingSchedule(models.Model):
    SCHEDULE_STATUS = [
        ('pending', '待签到'),
        ('checked_in', '已签到'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
        ('no_show', '未出席')
    ]

    training_plan = models.ForeignKey(TrainingPlan, on_delete=models.CASCADE, related_name='schedules', verbose_name='训练计划')
    shooter = models.ForeignKey(Shooter, on_delete=models.CASCADE, related_name='schedules', verbose_name='射手')
    target_lane = models.ForeignKey(TargetLane, on_delete=models.CASCADE, related_name='schedules', verbose_name='靶道')
    firearm = models.ForeignKey(Firearm, on_delete=models.SET_NULL, related_name='schedules', verbose_name='枪械', null=True, blank=True)
    schedule_date = models.DateField('训练日期')
    start_time = models.TimeField('开始时间')
    end_time = models.TimeField('结束时间')
    allocated_rounds = models.IntegerField('分配弹数', default=0)
    used_rounds = models.IntegerField('已用弹数', default=0)
    status = models.CharField('状态', max_length=20, choices=SCHEDULE_STATUS, default='pending')
    auto_generated = models.BooleanField('是否自动生成', default=True)
    generation_reason = models.TextField('生成理由', blank=True)
    conflict_warning = models.BooleanField('是否有冲突', default=False)
    conflict_description = models.TextField('冲突描述', blank=True)
    operator = models.CharField('操作员', max_length=50, blank=True)
    remarks = models.TextField('备注', blank=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '训练排班'
        verbose_name_plural = '训练排班'
        ordering = ['-schedule_date', 'start_time']

    def __str__(self):
        return f'{self.shooter.name} - {self.schedule_date}'

class LaneReservation(models.Model):
    RESERVATION_STATUS = [
        ('pending', '待确认'),
        ('confirmed', '已确认'),
        ('in_use', '使用中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
        ('no_show', '未到')
    ]

    target_lane = models.ForeignKey(TargetLane, on_delete=models.CASCADE, related_name='reservations', verbose_name='靶道')
    shooter = models.ForeignKey(Shooter, on_delete=models.CASCADE, related_name='reservations', verbose_name='射手')
    training_schedule = models.ForeignKey(TrainingSchedule, on_delete=models.SET_NULL, related_name='reservations', verbose_name='训练排班', null=True, blank=True)
    reservation_date = models.DateField('预约日期')
    start_time = models.TimeField('开始时间')
    end_time = models.TimeField('结束时间')
    purpose = models.CharField('用途', max_length=200, blank=True)
    reserved_by = models.CharField('预约人', max_length=50, blank=True)
    confirmed_by = models.CharField('确认人', max_length=50, blank=True)
    confirm_time = models.DateTimeField('确认时间', null=True, blank=True)
    status = models.CharField('状态', max_length=20, choices=RESERVATION_STATUS, default='pending')
    conflict_detected = models.BooleanField('检测到冲突', default=False)
    conflict_with = models.IntegerField('冲突排班ID', null=True, blank=True)
    remarks = models.TextField('备注', blank=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '靶道预约'
        verbose_name_plural = '靶道预约'
        ordering = ['-reservation_date', 'start_time']

    def __str__(self):
        return f'{self.target_lane.lane_number}号靶道 - {self.reservation_date}'

class RiskWarning(models.Model):
    WARNING_LEVEL = [
        ('low', '低风险'),
        ('medium', '中风险'),
        ('high', '高风险'),
        ('critical', '严重风险')
    ]
    WARNING_STATUS = [
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('resolved', '已解决'),
        ('ignored', '已忽略')
    ]
    WARNING_TYPE = [
        ('ammo_stock', '弹药库存预警'),
        ('ammo_expiry', '弹药过期预警'),
        ('lane_conflict', '靶道冲突预警'),
        ('shooter_risk', '射手风险预警'),
        ('firearm_maintenance', '枪械维护预警'),
        ('violation_risk', '违规风险预警'),
        ('other', '其他预警')
    ]

    warning_type = models.CharField('预警类型', max_length=30, choices=WARNING_TYPE)
    warning_level = models.CharField('预警等级', max_length=20, choices=WARNING_LEVEL)
    title = models.CharField('预警标题', max_length=200)
    description = models.TextField('预警描述')
    related_model = models.CharField('关联模型', max_length=50, blank=True)
    related_id = models.IntegerField('关联ID', null=True, blank=True)
    shooter = models.ForeignKey(Shooter, on_delete=models.SET_NULL, related_name='risk_warnings', verbose_name='关联射手', null=True, blank=True)
    ammunition = models.ForeignKey(Ammunition, on_delete=models.SET_NULL, related_name='risk_warnings', verbose_name='关联弹药', null=True, blank=True)
    ammo_batch = models.ForeignKey(AmmoBatch, on_delete=models.SET_NULL, related_name='risk_warnings', verbose_name='关联批次', null=True, blank=True)
    target_lane = models.ForeignKey(TargetLane, on_delete=models.SET_NULL, related_name='risk_warnings', verbose_name='关联靶道', null=True, blank=True)
    status = models.CharField('处理状态', max_length=20, choices=WARNING_STATUS, default='pending')
    handler = models.CharField('处理人', max_length=50, blank=True)
    handle_time = models.DateTimeField('处理时间', null=True, blank=True)
    handle_result = models.TextField('处理结果', blank=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '风险预警'
        verbose_name_plural = '风险预警'
        ordering = ['-create_time']

    def __str__(self):
        return f'{self.get_warning_level_display()} - {self.title}'

class CheckIn(models.Model):
    ALCOHOL_STATUS = [
        ('pass', '正常(≤0.0mg/100ml)'),
        ('warning', '疑似(0.0-20mg/100ml)'),
        ('fail', '不合格(>20mg/100ml)'),
    ]
    PSYCHOLOGICAL_STATUS = [
        ('normal', '正常'),
        ('warning', '需关注'),
        ('abnormal', '异常'),
    ]
    CHECKIN_STATUS = [
        ('pending', '待检查'),
        ('pass', '通过'),
        ('reject', '拒绝入场'),
    ]

    shooter = models.ForeignKey(Shooter, on_delete=models.CASCADE, verbose_name='射手')
    training_plan = models.ForeignKey(TrainingPlan, on_delete=models.SET_NULL, related_name='checkins', verbose_name='训练计划', null=True, blank=True)
    training_schedule = models.ForeignKey(TrainingSchedule, on_delete=models.SET_NULL, related_name='checkins', verbose_name='训练排班', null=True, blank=True)
    checkin_time = models.DateTimeField('签到时间', default=timezone.now)
    id_verified = models.BooleanField('身份核验', default=False)
    id_verify_method = models.CharField('核验方式', max_length=50, default='身份证+人脸识别')
    alcohol_test = models.CharField('酒精测试', max_length=20, choices=ALCOHOL_STATUS, default='pass')
    alcohol_value = models.FloatField('酒精含量(mg/100ml)', default=0.0)
    psychological_status = models.CharField('心理状态', max_length=20, choices=PSYCHOLOGICAL_STATUS, default='normal')
    psychological_note = models.TextField('心理评估备注', blank=True)
    status = models.CharField('签到状态', max_length=20, choices=CHECKIN_STATUS, default='pass')
    operator = models.CharField('操作员', max_length=50, blank=True)
    auto_associated = models.BooleanField('是否自动关联计划', default=False)
    remarks = models.TextField('备注', blank=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '射手签到'
        verbose_name_plural = '射手签到'
        ordering = ['-checkin_time']

    def __str__(self):
        return f'{self.shooter.name} - {self.checkin_time.strftime("%Y-%m-%d %H:%M")}'

class AmmoIssue(models.Model):
    ISSUE_STATUS = [
        ('issued', '已领用'),
        ('returning', '归还中'),
        ('completed', '已完成'),
    ]

    checkin = models.OneToOneField(CheckIn, on_delete=models.CASCADE, verbose_name='签到记录', null=True, blank=True)
    training_schedule = models.ForeignKey(TrainingSchedule, on_delete=models.SET_NULL, related_name='ammo_issues', verbose_name='训练排班', null=True, blank=True)
    training_plan = models.ForeignKey(TrainingPlan, on_delete=models.SET_NULL, related_name='ammo_issues', verbose_name='训练计划', null=True, blank=True)
    shooter = models.ForeignKey(Shooter, on_delete=models.CASCADE, verbose_name='射手')
    ammunition = models.ForeignKey(Ammunition, on_delete=models.CASCADE, verbose_name='弹药')
    ammo_batch = models.ForeignKey(AmmoBatch, on_delete=models.SET_NULL, related_name='ammo_issues', verbose_name='弹药批次', null=True, blank=True)
    issue_quantity = models.IntegerField('领用数量')
    planned_quantity = models.IntegerField('计划额度', default=0)
    target_lane = models.ForeignKey(TargetLane, on_delete=models.CASCADE, verbose_name='靶道')
    firearm = models.ForeignKey(Firearm, on_delete=models.CASCADE, verbose_name='枪械')
    issue_time = models.DateTimeField('领用时间', default=timezone.now)
    expected_return_time = models.DateTimeField('预计归还时间', null=True, blank=True)
    status = models.CharField('状态', max_length=20, choices=ISSUE_STATUS, default='issued')
    issuer = models.CharField('发弹员', max_length=50, blank=True)
    quota_exceeded = models.BooleanField('是否超计划额度', default=False)
    batch_expired = models.BooleanField('批次是否过期', default=False)
    stock_warning = models.BooleanField('库存预警', default=False)
    remarks = models.TextField('备注', blank=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '弹药领用'
        verbose_name_plural = '弹药领用'
        ordering = ['-issue_time']

    def __str__(self):
        return f'{self.shooter.name} 领用 {self.ammunition.name} x{self.issue_quantity}'

class SafetyInspection(models.Model):
    VIOLATION_LEVEL = [
        ('none', '无违规'),
        ('minor', '轻微违规'),
        ('major', '严重违规'),
        ('critical', '重大违规'),
    ]

    ammo_issue = models.ForeignKey(AmmoIssue, on_delete=models.CASCADE, verbose_name='领用记录')
    shooter = models.ForeignKey(Shooter, on_delete=models.CASCADE, verbose_name='射手')
    target_lane = models.ForeignKey(TargetLane, on_delete=models.CASCADE, verbose_name='靶道')
    inspection_time = models.DateTimeField('巡查时间', default=timezone.now)
    inspector = models.CharField('安全员', max_length=50)
    violation_level = models.CharField('违规等级', max_length=20, choices=VIOLATION_LEVEL, default='none')
    violation_type = models.CharField('违规类型', max_length=100, blank=True)
    violation_description = models.TextField('违规描述', blank=True)
    corrective_action = models.TextField('整改措施', blank=True)
    score_deduction = models.IntegerField('扣分', default=0)
    is_training_suspended = models.BooleanField('是否暂停训练', default=False)
    remarks = models.TextField('备注', blank=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '安全巡查'
        verbose_name_plural = '安全巡查'
        ordering = ['-inspection_time']

    def __str__(self):
        return f'{self.shooter.name} - {self.inspection_time.strftime("%Y-%m-%d %H:%M")}'

class ViolationDisposal(models.Model):
    DISPOSAL_STATUS = [
        ('pending', '待处置'),
        ('notified', '已通知'),
        ('confirmed', '责任人确认'),
        ('rectified', '已整改'),
        ('verified', '已验证'),
        ('closed', '已闭环')
    ]

    safety_inspection = models.OneToOneField(SafetyInspection, on_delete=models.CASCADE, related_name='disposal', verbose_name='安全检查记录')
    shooter = models.ForeignKey(Shooter, on_delete=models.CASCADE, related_name='violation_disposals', verbose_name='违规射手')
    violation_level = models.CharField('违规等级', max_length=20, choices=SafetyInspection.VIOLATION_LEVEL)
    disposal_flow = models.CharField('处置流程', max_length=50, choices=[
        ('level1', '一级处置：口头警告+记录'),
        ('level2', '二级处置：书面警告+暂停当日训练'),
        ('level3', '三级处置：暂停训练+限制领弹+成绩锁定'),
        ('level4', '四级处置：立即停止+列入黑名单+上报')
    ])
    status = models.CharField('处置状态', max_length=20, choices=DISPOSAL_STATUS, default='pending')
    is_ammo_suspended = models.BooleanField('是否暂停领弹', default=False)
    is_score_locked = models.BooleanField('是否锁定成绩', default=False)
    suspension_end_date = models.DateField('暂停结束日期', null=True, blank=True)
    notified_by = models.CharField('通知人', max_length=50, blank=True)
    notified_time = models.DateTimeField('通知时间', null=True, blank=True)
    responsible_person_confirm = models.BooleanField('责任人确认', default=False)
    confirm_time = models.DateTimeField('确认时间', null=True, blank=True)
    confirm_remark = models.TextField('责任人备注', blank=True)
    rectification_measure = models.TextField('整改措施', blank=True)
    rectification_deadline = models.DateField('整改期限', null=True, blank=True)
    rectification_time = models.DateTimeField('整改完成时间', null=True, blank=True)
    verified_by = models.CharField('验证人', max_length=50, blank=True)
    verify_time = models.DateTimeField('验证时间', null=True, blank=True)
    verify_remark = models.TextField('验证备注', blank=True)
    closed_by = models.CharField('闭环人', max_length=50, blank=True)
    close_time = models.DateTimeField('闭环时间', null=True, blank=True)
    remarks = models.TextField('备注', blank=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '违规处置'
        verbose_name_plural = '违规处置'
        ordering = ['-create_time']

    def __str__(self):
        return f'{self.shooter.name} - {self.get_violation_level_display()}'

    def get_handling_duration(self):
        if self.close_time and self.create_time:
            return (self.close_time - self.create_time).total_seconds() / 3600
        return None

class ScoreRecord(models.Model):
    ammo_issue = models.ForeignKey(AmmoIssue, on_delete=models.CASCADE, verbose_name='领用记录')
    shooter = models.ForeignKey(Shooter, on_delete=models.CASCADE, verbose_name='射手')
    target_lane = models.ForeignKey(TargetLane, on_delete=models.CASCADE, verbose_name='靶道')
    firearm = models.ForeignKey(Firearm, on_delete=models.CASCADE, verbose_name='枪械')
    ammunition = models.ForeignKey(Ammunition, on_delete=models.CASCADE, verbose_name='弹药')
    shots_fired = models.IntegerField('发射弹数')
    total_score = models.FloatField('总环数', default=0)
    average_score = models.FloatField('平均环数', default=0)
    hit_count = models.IntegerField('命中数', default=0)
    miss_count = models.IntegerField('脱靶数', default=0)
    ten_ring_count = models.IntegerField('10环数', default=0)
    nine_ring_count = models.IntegerField('9环数', default=0)
    eight_ring_count = models.IntegerField('8环数', default=0)
    seven_ring_count = models.IntegerField('7环数', default=0)
    six_ring_count = models.IntegerField('6环数', default=0)
    below_six_count = models.IntegerField('6环以下', default=0)
    score_detail = models.JSONField('成绩详情', default=list, blank=True)
    recorder = models.CharField('记录员', max_length=50, blank=True)
    record_time = models.DateTimeField('记录时间', default=timezone.now)
    remarks = models.TextField('备注', blank=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '射击成绩'
        verbose_name_plural = '射击成绩'
        ordering = ['-record_time']

    def save(self, *args, **kwargs):
        if self.shots_fired > 0:
            self.average_score = round(self.total_score / self.shots_fired, 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.shooter.name} - {self.total_score}环/{self.shots_fired}发'

class AmmoReturn(models.Model):
    ammo_issue = models.OneToOneField(AmmoIssue, on_delete=models.CASCADE, verbose_name='领用记录')
    shooter = models.ForeignKey(Shooter, on_delete=models.CASCADE, verbose_name='射手')
    ammunition = models.ForeignKey(Ammunition, on_delete=models.CASCADE, verbose_name='弹药')
    ammo_batch = models.ForeignKey(AmmoBatch, on_delete=models.SET_NULL, related_name='ammo_returns', verbose_name='弹药批次', null=True, blank=True)
    issued_quantity = models.IntegerField('领用数量')
    consumed_quantity = models.IntegerField('消耗数量')
    returned_quantity = models.IntegerField('归还数量')
    shell_casing_returned = models.IntegerField('弹壳回收数量')
    shell_casing_missing = models.IntegerField('弹壳缺失数量', default=0)
    has_exception = models.BooleanField('是否有异常', default=False)
    exception_description = models.TextField('异常说明', blank=True)
    responsible_person = models.CharField('责任人', max_length=50, blank=True)
    responsible_person_confirm = models.BooleanField('责任人确认', default=False)
    confirm_time = models.DateTimeField('确认时间', null=True, blank=True)
    return_time = models.DateTimeField('归还时间', default=timezone.now)
    receiver = models.CharField('收弹员', max_length=50, blank=True)
    quantity_verified = models.BooleanField('数量核对', default=True)
    shell_casing_verified = models.BooleanField('弹壳核对', default=True)
    closure_complete = models.BooleanField('闭环完成', default=False)
    remarks = models.TextField('备注', blank=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '弹药归还'
        verbose_name_plural = '弹药归还'
        ordering = ['-return_time']

    def save(self, *args, **kwargs):
        if self.issued_quantity and self.consumed_quantity:
            self.returned_quantity = self.issued_quantity - self.consumed_quantity
            self.shell_casing_missing = self.consumed_quantity - self.shell_casing_returned
        if self.shell_casing_missing > 0 or self.returned_quantity < 0:
            self.has_exception = True
        if self.quantity_verified and self.shell_casing_verified and self.responsible_person_confirm:
            self.closure_complete = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.shooter.name} 归还 {self.returned_quantity}发'

class AmmoBatchFlow(models.Model):
    FLOW_TYPE = [
        ('in', '入库'),
        ('out', '出库'),
        ('issue', '领用'),
        ('return', '归还'),
        ('consume', '消耗'),
        ('adjust', '调整'),
        ('scrap', '报废')
    ]

    ammo_batch = models.ForeignKey(AmmoBatch, on_delete=models.CASCADE, related_name='flows', verbose_name='弹药批次')
    flow_type = models.CharField('流向类型', max_length=20, choices=FLOW_TYPE)
    quantity = models.IntegerField('变动数量')
    balance_before = models.IntegerField('变动前数量')
    balance_after = models.IntegerField('变动后数量')
    related_shooter = models.ForeignKey(Shooter, on_delete=models.SET_NULL, related_name='ammo_flows', verbose_name='关联射手', null=True, blank=True)
    related_issue = models.ForeignKey(AmmoIssue, on_delete=models.SET_NULL, related_name='batch_flows', verbose_name='关联领用', null=True, blank=True)
    related_return = models.ForeignKey(AmmoReturn, on_delete=models.SET_NULL, related_name='batch_flows', verbose_name='关联归还', null=True, blank=True)
    operator = models.CharField('操作员', max_length=50, blank=True)
    remarks = models.TextField('备注', blank=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '弹药批次流向'
        verbose_name_plural = '弹药批次流向'
        ordering = ['-create_time']

    def __str__(self):
        return f'{self.ammo_batch.batch_number} - {self.get_flow_type_display()}'
