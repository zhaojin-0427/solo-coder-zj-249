#!/usr/bin/env python
import os
import sys
import django
from datetime import date, datetime, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shooting_range.settings')
django.setup()

from range_app.models import (
    Shooter, Ammunition, Firearm, TargetLane,
    CheckIn, AmmoIssue, SafetyInspection, ScoreRecord, AmmoReturn
)

def init_shooters():
    shooters_data = [
        {'id_card': '110101199001011234', 'name': '张伟', 'gender': 'M', 'age': 34, 'unit': '特警一队', 'phone': '13800138001', 'qualification_level': '一级射手'},
        {'id_card': '110101199102022345', 'name': '李娜', 'gender': 'F', 'age': 33, 'unit': '特警一队', 'phone': '13800138002', 'qualification_level': '二级射手'},
        {'id_card': '110101199203033456', 'name': '王强', 'gender': 'M', 'age': 32, 'unit': '特警二队', 'phone': '13800138003', 'qualification_level': '一级射手'},
        {'id_card': '110101199304044567', 'name': '刘洋', 'gender': 'M', 'age': 31, 'unit': '特警二队', 'phone': '13800138004', 'qualification_level': '三级射手'},
        {'id_card': '110101199405055678', 'name': '陈静', 'gender': 'F', 'age': 30, 'unit': '特警三队', 'phone': '13800138005', 'qualification_level': '二级射手'},
        {'id_card': '110101199506066789', 'name': '赵磊', 'gender': 'M', 'age': 29, 'unit': '特警三队', 'phone': '13800138006', 'qualification_level': '一级射手'},
        {'id_card': '110101199607077890', 'name': '孙丽', 'gender': 'F', 'age': 28, 'unit': '刑警大队', 'phone': '13800138007', 'qualification_level': '三级射手'},
        {'id_card': '110101199708088901', 'name': '周涛', 'gender': 'M', 'age': 27, 'unit': '刑警大队', 'phone': '13800138008', 'qualification_level': '二级射手'},
        {'id_card': '110101199809099012', 'name': '吴鹏', 'gender': 'M', 'age': 26, 'unit': '巡警大队', 'phone': '13800138009', 'qualification_level': '三级射手'},
        {'id_card': '110101199910100123', 'name': '郑芳', 'gender': 'F', 'age': 25, 'unit': '巡警大队', 'phone': '13800138010', 'qualification_level': '三级射手'},
    ]
    for data in shooters_data:
        if not Shooter.objects.filter(id_card=data['id_card']).exists():
            Shooter.objects.create(**data)
    print(f'射手信息初始化完成，共 {Shooter.objects.count()} 名射手')

def init_ammunition():
    ammo_data = [
        {'ammo_type': 'pistol', 'caliber': '9mm', 'name': '9mm手枪弹', 'stock_quantity': 5000, 'manufacturer': '北方工业', 'batch_number': 'AMMO2024001', 'production_date': date(2024, 1, 15), 'expiry_date': date(2034, 1, 15)},
        {'ammo_type': 'rifle', 'caliber': '5.56mm', 'name': '5.56mm步枪弹', 'stock_quantity': 3000, 'manufacturer': '北方工业', 'batch_number': 'AMMO2024002', 'production_date': date(2024, 2, 20), 'expiry_date': date(2034, 2, 20)},
        {'ammo_type': 'rifle', 'caliber': '7.62mm', 'name': '7.62mm步枪弹', 'stock_quantity': 2000, 'manufacturer': '北方工业', 'batch_number': 'AMMO2024003', 'production_date': date(2024, 3, 10), 'expiry_date': date(2034, 3, 10)},
        {'ammo_type': 'shotgun', 'caliber': '12ga', 'name': '12号霰弹', 'stock_quantity': 1000, 'manufacturer': '北方工业', 'batch_number': 'AMMO2024004', 'production_date': date(2024, 4, 5), 'expiry_date': date(2029, 4, 5)},
        {'ammo_type': 'sniper', 'caliber': '7.62mm', 'name': '7.62mm高精度狙击弹', 'stock_quantity': 500, 'manufacturer': '北方工业', 'batch_number': 'AMMO2024005', 'production_date': date(2024, 5, 1), 'expiry_date': date(2034, 5, 1)},
    ]
    for data in ammo_data:
        if not Ammunition.objects.filter(name=data['name']).exists():
            Ammunition.objects.create(**data)
    print(f'弹药信息初始化完成，共 {Ammunition.objects.count()} 种弹药')

def init_firearms():
    firearm_data = [
        {'firearm_type': 'pistol', 'model': 'QSZ92', 'serial_number': 'GUN2024001', 'name': '92式9mm手枪', 'manufacturer': '北方工业', 'purchase_date': date(2020, 6, 1), 'total_rounds': 3500},
        {'firearm_type': 'pistol', 'model': 'QSZ92', 'serial_number': 'GUN2024002', 'name': '92式9mm手枪', 'manufacturer': '北方工业', 'purchase_date': date(2020, 6, 1), 'total_rounds': 4200},
        {'firearm_type': 'pistol', 'model': 'QSZ92', 'serial_number': 'GUN2024003', 'name': '92式9mm手枪', 'manufacturer': '北方工业', 'purchase_date': date(2020, 6, 1), 'total_rounds': 2800},
        {'firearm_type': 'rifle', 'model': 'QBZ95', 'serial_number': 'GUN2024004', 'name': '95式5.8mm自动步枪', 'manufacturer': '北方工业', 'purchase_date': date(2021, 3, 15), 'total_rounds': 8500},
        {'firearm_type': 'rifle', 'model': 'QBZ95', 'serial_number': 'GUN2024005', 'name': '95式5.8mm自动步枪', 'manufacturer': '北方工业', 'purchase_date': date(2021, 3, 15), 'total_rounds': 7200},
        {'firearm_type': 'shotgun', 'model': '97式', 'serial_number': 'GUN2024006', 'name': '97式18.4mm防暴枪', 'manufacturer': '北方工业', 'purchase_date': date(2022, 1, 20), 'total_rounds': 1200},
        {'firearm_type': 'sniper', 'model': 'CS/LR4', 'serial_number': 'GUN2024007', 'name': 'CS/LR4 7.62mm高精度狙击步枪', 'manufacturer': '北方工业', 'purchase_date': date(2022, 8, 10), 'total_rounds': 600},
        {'firearm_type': 'submachine', 'model': 'JH16-1', 'serial_number': 'GUN2024008', 'name': 'JH16-1 9mm冲锋枪', 'manufacturer': '北方工业', 'purchase_date': date(2023, 2, 28), 'total_rounds': 2100},
    ]
    for data in firearm_data:
        if not Firearm.objects.filter(serial_number=data['serial_number']).exists():
            Firearm.objects.create(**data)
    print(f'枪械信息初始化完成，共 {Firearm.objects.count()} 支枪械')

def init_target_lanes():
    lane_data = [
        {'lane_number': 1, 'name': '手枪训练靶道', 'distance': 25, 'target_type': '胸环靶', 'max_shooters': 2},
        {'lane_number': 2, 'name': '手枪训练靶道', 'distance': 25, 'target_type': '胸环靶', 'max_shooters': 2},
        {'lane_number': 3, 'name': '手枪训练靶道', 'distance': 25, 'target_type': '胸环靶', 'max_shooters': 2},
        {'lane_number': 4, 'name': '步枪训练靶道', 'distance': 100, 'target_type': '半身靶', 'max_shooters': 1},
        {'lane_number': 5, 'name': '步枪训练靶道', 'distance': 100, 'target_type': '半身靶', 'max_shooters': 1},
        {'lane_number': 6, 'name': '步枪训练靶道', 'distance': 100, 'target_type': '半身靶', 'max_shooters': 1},
        {'lane_number': 7, 'name': '狙击训练靶道', 'distance': 300, 'target_type': '全身靶', 'max_shooters': 1},
        {'lane_number': 8, 'name': '霰弹训练靶道', 'distance': 15, 'target_type': '飞碟靶', 'max_shooters': 1},
    ]
    for data in lane_data:
        if not TargetLane.objects.filter(lane_number=data['lane_number']).exists():
            TargetLane.objects.create(**data)
    print(f'靶道信息初始化完成，共 {TargetLane.objects.count()} 条靶道')

def generate_test_data():
    shooters = list(Shooter.objects.all())
    ammunitions = list(Ammunition.objects.all())
    firearms = list(Firearm.objects.all())
    lanes = list(TargetLane.objects.all())
    
    today = datetime.now()
    
    for day_offset in range(30, 0, -1):
        current_date = today - timedelta(days=day_offset)
        daily_shooters = random.sample(shooters, random.randint(3, 8))
        
        for shooter in daily_shooters:
            checkin_time = current_date.replace(hour=random.randint(8, 14), minute=random.randint(0, 59))
            alcohol_value = round(random.uniform(0, 35), 1)
            alcohol_test = 'fail' if alcohol_value > 20 else ('warning' if alcohol_value > 0 else 'pass')
            psychological_status = random.choices(['normal', 'normal', 'normal', 'warning'], weights=[70, 20, 5, 5])[0]
            
            checkin = CheckIn.objects.create(
                shooter=shooter,
                checkin_time=checkin_time,
                id_verified=True,
                id_verify_method='身份证+人脸识别',
                alcohol_test=alcohol_test,
                alcohol_value=alcohol_value,
                psychological_status=psychological_status,
                psychological_note='心理状态评估：正常' if psychological_status == 'normal' else '心理状态评估：需关注，建议适当休息',
                status='reject' if alcohol_test == 'fail' or psychological_status == 'abnormal' else 'pass',
                operator='系统管理员'
            )
            
            if checkin.status == 'pass':
                ammo = random.choice(ammunitions)
                firearm = next(f for f in firearms if f.firearm_type[:3] == ammo.ammo_type[:3] or True)
                lane = random.choice(lanes)
                issue_qty = random.choice([10, 20, 30, 50])
                
                ammo_issue = AmmoIssue.objects.create(
                    checkin=checkin,
                    shooter=shooter,
                    ammunition=ammo,
                    issue_quantity=issue_qty,
                    target_lane=lane,
                    firearm=firearm,
                    issue_time=checkin_time + timedelta(minutes=random.randint(5, 15)),
                    status='completed',
                    issuer='发弹员老王'
                )
                
                if random.random() < 0.3:
                    violation_levels = ['none', 'minor', 'none', 'none', 'major']
                    violation_level = random.choice(violation_levels)
                    violation_types = ['', '枪口指向违规', '未戴护具', '装弹操作不规范', '擅自捡拾弹壳', '未经许可进入射击位']
                    if violation_level != 'none':
                        SafetyInspection.objects.create(
                            ammo_issue=ammo_issue,
                            shooter=shooter,
                            target_lane=lane,
                            inspection_time=ammo_issue.issue_time + timedelta(minutes=random.randint(10, 30)),
                            inspector='安全员老李',
                            violation_level=violation_level,
                            violation_type=violation_types[random.randint(1, 5)],
                            violation_description=f'在射击过程中存在{violation_types[random.randint(1, 5)]}行为',
                            corrective_action='已当场纠正并进行安全教育',
                            score_deduction=5 if violation_level == 'minor' else 15,
                            is_training_suspended=violation_level in ['major', 'critical'],
                            remarks='已记录在案'
                        )
                
                shots_fired = random.randint(issue_qty - 5, issue_qty)
                total_score = 0
                hit_count = 0
                miss_count = 0
                ten_ring = nine_ring = eight_ring = seven_ring = six_ring = below_six = 0
                score_detail = []
                
                for i in range(shots_fired):
                    score = random.choices([0, 5, 6, 7, 8, 9, 10], weights=[2, 3, 10, 20, 30, 25, 10])[0]
                    total_score += score
                    if score == 0:
                        miss_count += 1
                    else:
                        hit_count += 1
                    if score == 10: ten_ring += 1
                    elif score == 9: nine_ring += 1
                    elif score == 8: eight_ring += 1
                    elif score == 7: seven_ring += 1
                    elif score == 6: six_ring += 1
                    elif score > 0 and score < 6: below_six += 1
                    score_detail.append({'shot': i + 1, 'score': score})
                
                ScoreRecord.objects.create(
                    ammo_issue=ammo_issue,
                    shooter=shooter,
                    target_lane=lane,
                    firearm=firearm,
                    ammunition=ammo,
                    shots_fired=shots_fired,
                    total_score=total_score,
                    average_score=round(total_score / shots_fired, 2) if shots_fired > 0 else 0,
                    hit_count=hit_count,
                    miss_count=miss_count,
                    ten_ring_count=ten_ring,
                    nine_ring_count=nine_ring,
                    eight_ring_count=eight_ring,
                    seven_ring_count=seven_ring,
                    six_ring_count=six_ring,
                    below_six_count=below_six,
                    score_detail=score_detail,
                    recorder='记录员小张'
                )
                
                consumed = shots_fired
                returned = issue_qty - consumed
                shell_returned = consumed - random.randint(0, 2)
                
                AmmoReturn.objects.create(
                    ammo_issue=ammo_issue,
                    shooter=shooter,
                    ammunition=ammo,
                    issued_quantity=issue_qty,
                    consumed_quantity=consumed,
                    returned_quantity=returned,
                    shell_casing_returned=shell_returned,
                    shell_casing_missing=consumed - shell_returned,
                    return_time=ammo_issue.issue_time + timedelta(hours=1, minutes=random.randint(10, 40)),
                    receiver='收弹员老陈',
                    quantity_verified=True,
                    shell_casing_verified=shell_returned == consumed,
                    remarks='' if shell_returned == consumed else f'缺失弹壳{consumed - shell_returned}发，已登记'
                )
    
    print(f'测试数据生成完成')
    print(f'  签到记录: {CheckIn.objects.count()} 条')
    print(f'  领用记录: {AmmoIssue.objects.count()} 条')
    print(f'  巡查记录: {SafetyInspection.objects.count()} 条')
    print(f'  成绩记录: {ScoreRecord.objects.count()} 条')
    print(f'  归还记录: {AmmoReturn.objects.count()} 条')

if __name__ == '__main__':
    print('=' * 50)
    print('开始初始化靶场管理系统数据库...')
    print('=' * 50)
    
    init_shooters()
    init_ammunition()
    init_firearms()
    init_target_lanes()
    
    print('=' * 50)
    print('基础数据初始化完成，开始生成测试数据...')
    print('=' * 50)
    
    generate_test_data()
    
    print('=' * 50)
    print('数据库初始化全部完成！')
    print('=' * 50)
