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
    checkin_time = models.DateTimeField('签到时间', default=timezone.now)
    id_verified = models.BooleanField('身份核验', default=False)
    id_verify_method = models.CharField('核验方式', max_length=50, default='身份证+人脸识别')
    alcohol_test = models.CharField('酒精测试', max_length=20, choices=ALCOHOL_STATUS, default='pass')
    alcohol_value = models.FloatField('酒精含量(mg/100ml)', default=0.0)
    psychological_status = models.CharField('心理状态', max_length=20, choices=PSYCHOLOGICAL_STATUS, default='normal')
    psychological_note = models.TextField('心理评估备注', blank=True)
    status = models.CharField('签到状态', max_length=20, choices=CHECKIN_STATUS, default='pass')
    operator = models.CharField('操作员', max_length=50, blank=True)
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

    checkin = models.OneToOneField(CheckIn, on_delete=models.CASCADE, verbose_name='签到记录')
    shooter = models.ForeignKey(Shooter, on_delete=models.CASCADE, verbose_name='射手')
    ammunition = models.ForeignKey(Ammunition, on_delete=models.CASCADE, verbose_name='弹药')
    issue_quantity = models.IntegerField('领用数量')
    target_lane = models.ForeignKey(TargetLane, on_delete=models.CASCADE, verbose_name='靶道')
    firearm = models.ForeignKey(Firearm, on_delete=models.CASCADE, verbose_name='枪械')
    issue_time = models.DateTimeField('领用时间', default=timezone.now)
    expected_return_time = models.DateTimeField('预计归还时间', null=True, blank=True)
    status = models.CharField('状态', max_length=20, choices=ISSUE_STATUS, default='issued')
    issuer = models.CharField('发弹员', max_length=50, blank=True)
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
    issued_quantity = models.IntegerField('领用数量')
    consumed_quantity = models.IntegerField('消耗数量')
    returned_quantity = models.IntegerField('归还数量')
    shell_casing_returned = models.IntegerField('弹壳回收数量')
    shell_casing_missing = models.IntegerField('弹壳缺失数量', default=0)
    return_time = models.DateTimeField('归还时间', default=timezone.now)
    receiver = models.CharField('收弹员', max_length=50, blank=True)
    quantity_verified = models.BooleanField('数量核对', default=True)
    shell_casing_verified = models.BooleanField('弹壳核对', default=True)
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
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.shooter.name} 归还 {self.returned_quantity}发'
