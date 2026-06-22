from datetime import datetime
from peewee import fn
from .base import BaseResource
from app.models import BorrowOrder, BorrowItem, Equipment, GradeClass, User
from app.utils import (
    ValidationError,
    render_template,
    generate_order_no,
    validate_new_borrow,
    validate_return_time,
    validate_close_order,
    check_all_items_returned
)


class BorrowOrderResource(BaseResource):
    def on_get(self, req, resp):
        data = self.parse_data(req)
        query = BorrowOrder.select().join(GradeClass).switch(BorrowOrder).join(User)
        
        status = data.get('return_status')
        class_id = data.get('class_id')
        keyword = data.get('keyword')
        
        if status:
            query = query.where(BorrowOrder.return_status == status)
        if class_id:
            query = query.where(BorrowOrder.grade_class == class_id)
        if keyword:
            query = query.where(
                (BorrowOrder.order_no.contains(keyword)) |
                (BorrowOrder.teacher.contains(keyword))
            )
        
        orders = query.order_by(BorrowOrder.borrow_time.desc())
        classes = GradeClass.select().order_by(GradeClass.grade, GradeClass.class_number)
        available_equipment = Equipment.select().where(
            Equipment.status == 'available',
            Equipment.condition == 'good'
        ).order_by(Equipment.equipment_no)
        
        context = {
            'orders': orders,
            'classes': classes,
            'available_equipment': available_equipment,
            'filters': {
                'return_status': status,
                'class_id': class_id,
                'keyword': keyword
            }
        }
        self.render(resp, 'borrow_order/list.html', context)

    def on_post(self, req, resp):
        data = self.parse_data(req)
        current_user = req.context['user']
        try:
            grade_class_id = int(data.get('grade_class_id'))
            validate_new_borrow(grade_class_id)
            
            equipment_ids = data.get('equipment_ids', [])
            if isinstance(equipment_ids, str):
                equipment_ids = [e.strip() for e in equipment_ids.split(',') if e.strip()]
            equipment_ids = [int(eid) for eid in equipment_ids if eid]
            
            if not equipment_ids:
                raise ValidationError('请选择要领用的器材')
            
            borrow_time_str = data.get('borrow_time')
            borrow_time = datetime.fromisoformat(borrow_time_str) if borrow_time_str else datetime.now()
            
            order = BorrowOrder.create(
                order_no=generate_order_no('LY'),
                grade_class=grade_class_id,
                teacher=data.get('teacher'),
                borrow_time=borrow_time,
                purpose=data.get('purpose'),
                operator=current_user.id,
                remark=data.get('remark')
            )
            
            for eq_id in equipment_ids:
                equipment = Equipment.get_by_id(eq_id)
                if equipment.status != 'available' or equipment.condition != 'good':
                    raise ValidationError(f'器材 {equipment.equipment_no} 状态异常，无法领用')
                
                BorrowItem.create(
                    borrow_order=order.id,
                    equipment=eq_id,
                    borrow_condition=equipment.condition
                )
                
                equipment.status = 'borrowed'
                equipment.save()
            
            if req.headers.get('HX-Request'):
                resp.set_header('HX-Redirect', f'/borrow-orders/{order.id}')
                resp.text = ''
                return
            self.success_json(resp, {'id': order.id, 'order_no': order.order_no}, '领用单创建成功')
            
        except ValidationError as e:
            self.handle_validation_error(resp, e)
        except Exception as e:
            self.handle_validation_error(resp, ValidationError(f'创建失败：{str(e)}'))


class BorrowOrderDetailResource(BaseResource):
    def on_get(self, req, resp, order_id):
        order = BorrowOrder.get_by_id(order_id)
        items = BorrowItem.select().where(BorrowItem.borrow_order == order_id).join(Equipment)
        
        if req.headers.get('HX-Request') and req.params.get('partial') == 'items':
            html = render_template('borrow_order/_items.html', {'order': order, 'items': items})
            resp.status = 200
            resp.content_type = 'text/html; charset=utf-8'
            resp.text = html
            return
        
        available_equipment = Equipment.select().where(
            Equipment.status == 'available',
            Equipment.condition == 'good'
        ).order_by(Equipment.equipment_no)
        
        context = {
            'order': order,
            'items': items,
            'available_equipment': available_equipment
        }
        self.render(resp, 'borrow_order/detail.html', context)


class BorrowOrderReturnResource(BaseResource):
    def on_get(self, req, resp, order_id):
        order = BorrowOrder.get_by_id(order_id)
        items = BorrowItem.select().where(BorrowItem.borrow_order == order_id).join(Equipment)
        
        html = render_template('borrow_order/_return_form.html', {'order': order, 'items': items})
        resp.status = 200
        resp.content_type = 'text/html; charset=utf-8'
        resp.text = html

    def on_post(self, req, resp, order_id):
        data = self.parse_data(req)
        current_user = req.context['user']
        try:
            order = BorrowOrder.get_by_id(order_id)
            
            return_time_str = data.get('return_time')
            return_time = datetime.fromisoformat(return_time_str) if return_time_str else datetime.now()
            validate_return_time(order.borrow_time, return_time)
            
            item_data = {}
            for key, value in data.items():
                if key.startswith('return_condition_'):
                    item_id = int(key.replace('return_condition_', ''))
                    item_data[item_id] = {
                        'condition': value,
                        'status': data.get(f'return_status_{item_id}', 'returned'),
                        'remark': data.get(f'return_remark_{item_id}', '')
                    }
            
            for item_id, info in item_data.items():
                item = BorrowItem.get_by_id(item_id)
                item.return_condition = info['condition']
                item.return_status = info['status']
                item.remark = info['remark']
                item.save()
                
                equipment = item.equipment
                if info['status'] == 'returned':
                    equipment.condition = info['condition']
                    equipment.status = 'available'
                    equipment.save()
                elif info['status'] == 'damaged':
                    equipment.condition = 'damaged'
                    equipment.status = 'maintenance'
                    equipment.save()
                elif info['status'] == 'missing':
                    equipment.condition = 'missing'
                    equipment.status = 'maintenance'
                    equipment.save()
            
            order.return_time = return_time
            if check_all_items_returned(order_id):
                has_problem = BorrowItem.select().where(
                    BorrowItem.borrow_order == order_id,
                    BorrowItem.return_status.in_(['damaged', 'missing'])
                ).exists()
                if has_problem:
                    order.return_status = 'inspecting'
                    order.liability_status = 'processing'
                else:
                    order.return_status = 'returned'
                    order.liability_status = 'pending'
            else:
                order.return_status = 'partial'
            order.save()
            
            if req.headers.get('HX-Request'):
                resp.set_header('HX-Refresh', 'true')
                resp.text = ''
                return
            self.success_json(resp, {'id': order.id}, '归还登记成功')
            
        except ValidationError as e:
            self.handle_validation_error(resp, e)
        except Exception as e:
            self.handle_validation_error(resp, ValidationError(f'归还失败：{str(e)}'))


class BorrowOrderCloseResource(BaseResource):
    def on_post(self, req, resp, order_id):
        try:
            validate_close_order(order_id)
            
            order = BorrowOrder.get_by_id(order_id)
            order.return_status = 'closed'
            order.liability_status = 'confirmed'
            order.save()
            
            if req.headers.get('HX-Request'):
                resp.set_header('HX-Refresh', 'true')
                resp.text = ''
                return
            self.success_json(resp, {'id': order.id}, '领用单已结案')
            
        except ValidationError as e:
            self.handle_validation_error(resp, e)


class BorrowOrderAddItemResource(BaseResource):
    def on_post(self, req, resp, order_id):
        data = self.parse_data(req)
        try:
            order = BorrowOrder.get_by_id(order_id)
            if order.return_status != 'pending':
                raise ValidationError('该领用单已开始归还，不能添加器材')
            
            equipment_id = int(data.get('equipment_id'))
            equipment = Equipment.get_by_id(equipment_id)
            
            if equipment.status != 'available' or equipment.condition != 'good':
                raise ValidationError('该器材状态异常，无法领用')
            
            existing = BorrowItem.select().where(
                BorrowItem.borrow_order == order_id,
                BorrowItem.equipment == equipment_id
            ).first()
            if existing:
                raise ValidationError('该器材已在领用单中')
            
            BorrowItem.create(
                borrow_order=order_id,
                equipment=equipment_id,
                borrow_condition=equipment.condition
            )
            
            equipment.status = 'borrowed'
            equipment.save()
            
            if req.headers.get('HX-Request'):
                items = BorrowItem.select().where(BorrowItem.borrow_order == order_id).join(Equipment)
                html = render_template('borrow_order/_items.html', {'order': order, 'items': items})
                resp.status = 200
                resp.content_type = 'text/html; charset=utf-8'
                resp.text = html
                return
            self.success_json(resp, message='器材添加成功')
            
        except ValidationError as e:
            self.handle_validation_error(resp, e)


class BorrowOrderRemoveItemResource(BaseResource):
    def on_delete(self, req, resp, order_id, item_id):
        try:
            order = BorrowOrder.get_by_id(order_id)
            if order.return_status != 'pending':
                raise ValidationError('该领用单已开始归还，不能移除器材')
            
            item = BorrowItem.get_by_id(item_id)
            equipment = item.equipment
            equipment.status = 'available'
            equipment.save()
            
            item.delete_instance()
            
            if req.headers.get('HX-Request'):
                items = BorrowItem.select().where(BorrowItem.borrow_order == order_id).join(Equipment)
                html = render_template('borrow_order/_items.html', {'order': order, 'items': items})
                resp.status = 200
                resp.content_type = 'text/html; charset=utf-8'
                resp.text = html
                return
            self.success_json(resp, message='器材已移除')
            
        except ValidationError as e:
            self.handle_validation_error(resp, e)
