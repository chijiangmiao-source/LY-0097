from datetime import datetime
from peewee import fn
from .base import BaseResource
from app.models import (
    LiabilityJudgment,
    InspectionRecord,
    GradeClass,
    User,
    Equipment
)
from app.utils import (
    ValidationError,
    render_template,
    get_week_range
)


class LiabilityJudgmentResource(BaseResource):
    def on_get(self, req, resp):
        data = self.parse_data(req)
        query = LiabilityJudgment.select().join(InspectionRecord).switch(LiabilityJudgment).join(GradeClass).switch(LiabilityJudgment).join(User)
        
        is_confirmed = data.get('is_confirmed')
        liability_type = data.get('liability_type')
        class_id = data.get('class_id')
        
        if is_confirmed is not None and is_confirmed != '':
            query = query.where(LiabilityJudgment.is_confirmed == (is_confirmed == 'true'))
        if liability_type:
            query = query.where(LiabilityJudgment.liability_type == liability_type)
        if class_id:
            query = query.where(LiabilityJudgment.grade_class == class_id)
        
        judgments = query.order_by(LiabilityJudgment.judgment_time.desc())
        
        pending_inspections = InspectionRecord.select().where(
            InspectionRecord.status != 'closed',
            ~InspectionRecord.id.in_(
                LiabilityJudgment.select(LiabilityJudgment.inspection_record_id)
            )
        ).join(Equipment).switch(InspectionRecord).join(GradeClass)
        
        classes = GradeClass.select().order_by(GradeClass.grade, GradeClass.class_number)
        
        context = {
            'judgments': judgments,
            'pending_inspections': pending_inspections,
            'classes': classes,
            'filters': {
                'is_confirmed': is_confirmed,
                'liability_type': liability_type,
                'class_id': class_id
            }
        }
        self.render(resp, 'liability/list.html', context)

    def on_post(self, req, resp):
        data = self.parse_data(req)
        current_user = req.context['user']
        try:
            inspection_id = int(data.get('inspection_record_id'))
            existing = LiabilityJudgment.select().where(
                LiabilityJudgment.inspection_record == inspection_id
            ).first()
            if existing:
                raise ValidationError('该抽查记录已有责任判定')
            
            inspection = InspectionRecord.get_by_id(inspection_id)
            
            judgment = LiabilityJudgment.create(
                inspection_record=inspection_id,
                grade_class=inspection.borrow_order.grade_class_id,
                judge=current_user.id,
                liability_type=data.get('liability_type'),
                liable_person=data.get('liable_person'),
                judgment_result=data.get('judgment_result'),
                remark=data.get('remark')
            )
            
            inspection.is_deletable = False
            inspection.status = 'processing'
            inspection.save()
            
            if req.headers.get('HX-Request'):
                html = render_template('liability/_row.html', {'judgment': judgment})
                resp.status = 200
                resp.content_type = 'text/html; charset=utf-8'
                resp.text = html
                return
            self.success_json(resp, {'id': judgment.id}, '责任判定创建成功')
            
        except ValidationError as e:
            self.handle_validation_error(resp, e)
        except Exception as e:
            self.handle_validation_error(resp, ValidationError(f'创建失败：{str(e)}'))


class LiabilityJudgmentDetailResource(BaseResource):
    def on_get(self, req, resp, judgment_id):
        judgment = LiabilityJudgment.get_by_id(judgment_id)
        if req.headers.get('HX-Request'):
            pending_inspections = InspectionRecord.select().where(
                InspectionRecord.status != 'closed',
                ~InspectionRecord.id.in_(
                    LiabilityJudgment.select(LiabilityJudgment.inspection_record_id)
                )
            ).join(Equipment).switch(InspectionRecord).join(GradeClass)
            classes = GradeClass.select().order_by(GradeClass.grade, GradeClass.class_number)
            html = render_template('liability/_form.html', {'judgment': judgment, 'inspections': pending_inspections, 'classes': classes})
            resp.status = 200
            resp.content_type = 'text/html; charset=utf-8'
            resp.text = html
            return
        self.success_json(resp, {
            'id': judgment.id,
            'inspection_id': judgment.inspection_record_id,
            'liability_type': judgment.liability_type,
            'liable_person': judgment.liable_person,
            'judgment_result': judgment.judgment_result,
            'is_confirmed': judgment.is_confirmed,
            'remark': judgment.remark
        })

    def on_put(self, req, resp, judgment_id):
        data = self.parse_data(req)
        try:
            judgment = LiabilityJudgment.get_by_id(judgment_id)
            if judgment.is_confirmed:
                raise ValidationError('已确认的责任判定不能修改')
            
            judgment.liability_type = data.get('liability_type', judgment.liability_type)
            judgment.liable_person = data.get('liable_person', judgment.liable_person)
            judgment.judgment_result = data.get('judgment_result', judgment.judgment_result)
            judgment.remark = data.get('remark', judgment.remark)
            judgment.save()
            
            if req.headers.get('HX-Request'):
                html = render_template('liability/_row.html', {'judgment': judgment})
                resp.status = 200
                resp.content_type = 'text/html; charset=utf-8'
                resp.text = html
                return
            self.success_json(resp, {'id': judgment.id}, '责任判定更新成功')
            
        except ValidationError as e:
            self.handle_validation_error(resp, e)


class LiabilityConfirmResource(BaseResource):
    def on_post(self, req, resp, judgment_id):
        data = self.parse_data(req)
        current_user = req.context['user']
        try:
            judgment = LiabilityJudgment.get_by_id(judgment_id)
            if judgment.is_confirmed:
                raise ValidationError('该责任判定已确认')
            
            judgment.is_confirmed = True
            judgment.confirmed_time = datetime.now()
            judgment.confirmer = current_user.id
            judgment.save()
            
            inspection = judgment.inspection_record
            inspection.status = 'resolved'
            inspection.save()
            
            if req.headers.get('HX-Request'):
                html = render_template('liability/_row.html', {'judgment': judgment})
                resp.status = 200
                resp.content_type = 'text/html; charset=utf-8'
                resp.text = html
                return
            self.success_json(resp, {'id': judgment.id}, '责任判定已确认')
            
        except ValidationError as e:
            self.handle_validation_error(resp, e)


class WeeklyReportResource(BaseResource):
    def on_get(self, req, resp):
        from app.utils import generate_weekly_report
        
        data = self.parse_data(req)
        week_offset = int(data.get('week_offset', '0'))
        
        from datetime import timedelta
        base_date = datetime.now() + timedelta(weeks=week_offset)
        week_start, week_end = get_week_range(base_date)
        
        report = generate_weekly_report(week_start, week_end)
        
        class_stats = []
        from app.models import GradeClass, BorrowOrder
        classes = GradeClass.select().order_by(GradeClass.grade, GradeClass.class_number)
        
        for cls in classes:
            orders = BorrowOrder.select().where(
                BorrowOrder.grade_class == cls.id,
                BorrowOrder.borrow_time >= week_start,
                BorrowOrder.borrow_time <= week_end
            )
            total = orders.count()
            if total > 0:
                on_time = orders.where(
                    BorrowOrder.return_status == 'closed',
                    fn.DATE(BorrowOrder.return_time) <= fn.DATE(BorrowOrder.borrow_time)
                ).count()
                timeliness = round((on_time / total) * 100, 2)
            else:
                timeliness = 0
            
            from app.models import InspectionRecord
            abnormal_count = InspectionRecord.select().where(
                InspectionRecord.borrow_order.grade_class == cls.id,
                InspectionRecord.inspection_time >= week_start,
                InspectionRecord.inspection_time <= week_end
            ).count()
            
            class_stats.append({
                'class': cls,
                'total_orders': total,
                'timeliness_rate': timeliness,
                'abnormal_count': abnormal_count
            })
        
        context = {
            'report': report,
            'class_stats': class_stats,
            'week_offset': week_offset,
            'week_start': week_start.strftime('%Y-%m-%d'),
            'week_end': week_end.strftime('%Y-%m-%d')
        }
        self.render(resp, 'weekly_report.html', context)
