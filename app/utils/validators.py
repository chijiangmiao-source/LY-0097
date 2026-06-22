from datetime import datetime
from peewee import fn
from app.models import BorrowOrder, InspectionRecord, LiabilityJudgment, BorrowItem
from config import db


class ValidationError(Exception):
    pass


def validate_new_borrow(grade_class_id):
    pending_orders = BorrowOrder.select().where(
        (BorrowOrder.grade_class == grade_class_id) &
        (BorrowOrder.return_status != 'closed')
    )
    if pending_orders.exists():
        raise ValidationError("该班级存在未结案的领用单，不能再次领用")
    return True


def validate_return_time(borrow_time, return_time):
    if return_time and return_time < borrow_time:
        raise ValidationError("归还时间不能早于领用时间")
    return True


def validate_close_order(order_id):
    pending_inspections = InspectionRecord.select().where(
        (InspectionRecord.borrow_order == order_id) &
        (InspectionRecord.status != 'closed')
    )
    if pending_inspections.exists():
        raise ValidationError("存在未完成的抽查记录，不能结案")
    return True


def validate_delete_inspection(inspection_id):
    judgment = LiabilityJudgment.select().where(
        (LiabilityJudgment.inspection_record == inspection_id) &
        (LiabilityJudgment.is_confirmed == True)
    ).first()
    if judgment:
        raise ValidationError("该抽查记录已关联确认的责任判定，不得删除")
    inspection = InspectionRecord.get_by_id(inspection_id)
    if not inspection.is_deletable:
        raise ValidationError("该抽查记录不允许删除")
    return True


def validate_problem_type_distinction(problem_type, handling_path):
    if problem_type == 'damaged' and handling_path not in ['repair', 'compensation', 'scrap']:
        raise ValidationError("损坏器材必须走维修、赔偿或报废路径")
    if problem_type == 'missing' and handling_path not in ['compensation', 'search']:
        raise ValidationError("缺失器材必须走赔偿或查找路径")
    return True


def check_all_items_returned(order_id):
    items = BorrowItem.select().where(BorrowItem.borrow_order == order_id)
    for item in items:
        if item.return_status not in ['returned', 'damaged', 'missing']:
            return False
    return True


def calculate_return_timeliness(week_start, week_end):
    orders = BorrowOrder.select().where(
        (BorrowOrder.borrow_time >= week_start) &
        (BorrowOrder.borrow_time <= week_end)
    )
    total = orders.count()
    if total == 0:
        return 0
    on_time = orders.where(
        (BorrowOrder.return_status == 'closed') &
        (fn.DATE(BorrowOrder.return_time) <= fn.DATE(BorrowOrder.borrow_time))
    ).count()
    return round((on_time / total) * 100, 2)


def calculate_equipment_abnormal_rate(week_start, week_end):
    from app.models import Equipment
    total = Equipment.select().count()
    if total == 0:
        return 0
    abnormal = Equipment.select().where(
        (Equipment.condition != 'good') |
        (Equipment.status != 'available')
    ).count()
    return round((abnormal / total) * 100, 2)


def calculate_liability_distribution(week_start, week_end):
    judgments = LiabilityJudgment.select().where(
        (LiabilityJudgment.judgment_time >= week_start) &
        (LiabilityJudgment.judgment_time <= week_end) &
        (LiabilityJudgment.is_confirmed == True)
    )
    total = judgments.count()
    distribution = {}
    types = ['student', 'teacher', 'school', 'natural', 'other']
    for lt in types:
        count = judgments.where(LiabilityJudgment.liability_type == lt).count()
        distribution[lt] = {
            'count': count,
            'percentage': round((count / total) * 100, 2) if total > 0 else 0
        }
    return distribution


def generate_weekly_report(week_start=None, week_end=None):
    from app.utils.helpers import get_week_range
    if week_start is None or week_end is None:
        week_start, week_end = get_week_range()
    
    return {
        'week_start': week_start.strftime('%Y-%m-%d'),
        'week_end': week_end.strftime('%Y-%m-%d'),
        'return_timeliness_rate': calculate_return_timeliness(week_start, week_end),
        'equipment_abnormal_rate': calculate_equipment_abnormal_rate(week_start, week_end),
        'liability_distribution': calculate_liability_distribution(week_start, week_end)
    }
