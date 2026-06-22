from datetime import datetime
from .base import BaseResource
from app.models import (
    InspectionRecord,
    BorrowOrder,
    BorrowItem,
    Equipment,
    User,
    GradeClass
)
from app.utils import (
    ValidationError,
    render_template,
    validate_delete_inspection,
    validate_problem_type_distinction
)


class InspectionResource(BaseResource):
    def on_get(self, req, resp):
        data = self.parse_data(req)
        query = InspectionRecord.select().join(BorrowOrder).switch(InspectionRecord).join(Equipment).switch(InspectionRecord).join(User)
        
        status = data.get('status')
        problem_type = data.get('problem_type')
        order_id = data.get('order_id')
        
        if status:
            query = query.where(InspectionRecord.status == status)
        if problem_type:
            query = query.where(InspectionRecord.problem_type == problem_type)
        if order_id:
            query = query.where(InspectionRecord.borrow_order == order_id)
        
        inspections = query.order_by(InspectionRecord.inspection_time.desc())
        
        orders = BorrowOrder.select().where(
            BorrowOrder.return_status.in_(['inspecting', 'partial'])
        ).order_by(BorrowOrder.borrow_time.desc())
        
        context = {
            'inspections': inspections,
            'orders': orders,
            'filters': {
                'status': status,
                'problem_type': problem_type,
                'order_id': order_id
            }
        }
        self.render(resp, 'inspection/list.html', context)

    def on_post(self, req, resp):
        data = self.parse_data(req)
        current_user = req.context['user']
        try:
            order_id = int(data.get('borrow_order_id'))
            borrow_item_id = data.get('borrow_item_id')
            equipment_id = int(data.get('equipment_id'))
            problem_type = data.get('problem_type')
            handling_path = data.get('handling_path')
            
            validate_problem_type_distinction(problem_type, handling_path)
            
            inspection = InspectionRecord.create(
                borrow_order=order_id,
                borrow_item=borrow_item_id if borrow_item_id else None,
                equipment=equipment_id,
                inspector=current_user.id,
                problem_type=problem_type,
                problem_description=data.get('problem_description'),
                handling_path=handling_path,
                status='pending',
                remark=data.get('remark')
            )
            
            if req.headers.get('HX-Request'):
                html = render_template('inspection/_row.html', {'inspection': inspection})
                resp.status = 200
                resp.content_type = 'text/html; charset=utf-8'
                resp.text = html
                return
            self.success_json(resp, {'id': inspection.id}, '抽查记录创建成功')
            
        except ValidationError as e:
            self.handle_validation_error(resp, e)
        except Exception as e:
            self.handle_validation_error(resp, ValidationError(f'创建失败：{str(e)}'))


class InspectionDetailResource(BaseResource):
    def on_get(self, req, resp, inspection_id):
        inspection = InspectionRecord.get_by_id(inspection_id)
        if req.headers.get('HX-Request'):
            orders = BorrowOrder.select().where(
                BorrowOrder.return_status.in_(['inspecting', 'partial'])
            ).order_by(BorrowOrder.borrow_time.desc())
            html = render_template('inspection/_form.html', {'inspection': inspection, 'orders': orders})
            resp.status = 200
            resp.content_type = 'text/html; charset=utf-8'
            resp.text = html
            return
        self.success_json(resp, {
            'id': inspection.id,
            'borrow_order_id': inspection.borrow_order_id,
            'borrow_item_id': inspection.borrow_item_id,
            'equipment_id': inspection.equipment_id,
            'problem_type': inspection.problem_type,
            'problem_description': inspection.problem_description,
            'status': inspection.status,
            'is_deletable': inspection.is_deletable,
            'remark': inspection.remark
        })

    def on_put(self, req, resp, inspection_id):
        data = self.parse_data(req)
        try:
            inspection = InspectionRecord.get_by_id(inspection_id)
            if inspection.status == 'closed':
                raise ValidationError('已结案的抽查记录不能修改')
            
            problem_type = data.get('problem_type', inspection.problem_type)
            handling_path = data.get('handling_path')
            if handling_path:
                validate_problem_type_distinction(problem_type, handling_path)
            
            inspection.problem_type = problem_type
            inspection.problem_description = data.get('problem_description', inspection.problem_description)
            inspection.status = data.get('status', inspection.status)
            inspection.remark = data.get('remark', inspection.remark)
            inspection.save()
            
            if req.headers.get('HX-Request'):
                html = render_template('inspection/_row.html', {'inspection': inspection})
                resp.status = 200
                resp.content_type = 'text/html; charset=utf-8'
                resp.text = html
                return
            self.success_json(resp, {'id': inspection.id}, '抽查记录更新成功')
            
        except ValidationError as e:
            self.handle_validation_error(resp, e)

    def on_delete(self, req, resp, inspection_id):
        try:
            validate_delete_inspection(inspection_id)
            inspection = InspectionRecord.get_by_id(inspection_id)
            inspection.delete_instance()
            if req.headers.get('HX-Request'):
                resp.status = 200
                resp.text = ''
                return
            self.success_json(resp, message='抽查记录删除成功')
        except ValidationError as e:
            self.handle_validation_error(resp, e)


class InspectionCloseResource(BaseResource):
    def on_post(self, req, resp, inspection_id):
        data = self.parse_data(req)
        try:
            inspection = InspectionRecord.get_by_id(inspection_id)
            inspection.status = 'closed'
            inspection.save()
            
            if req.headers.get('HX-Request'):
                html = render_template('inspection/_row.html', {'inspection': inspection})
                resp.status = 200
                resp.content_type = 'text/html; charset=utf-8'
                resp.text = html
                return
            self.success_json(resp, {'id': inspection.id}, '抽查记录已结案')
        except Exception as e:
            self.handle_validation_error(resp, ValidationError(str(e)))


class InspectionEquipmentSearchResource(BaseResource):
    def on_get(self, req, resp, order_id):
        order = BorrowOrder.get_by_id(order_id)
        items = BorrowItem.select().where(
            BorrowItem.borrow_order == order_id,
            BorrowItem.return_status.in_(['damaged', 'missing'])
        ).join(Equipment)
        
        if req.headers.get('HX-Request'):
            html = render_template('inspection/_equipment_options.html', {'items': items})
            resp.status = 200
            resp.content_type = 'text/html; charset=utf-8'
            resp.text = html
            return
        equipment_list = [{
            'id': item.equipment.id,
            'equipment_no': item.equipment.equipment_no,
            'name': item.equipment.name,
            'return_status': item.return_status
        } for item in items]
        self.success_json(resp, {'equipment': equipment_list})
