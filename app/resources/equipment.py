from .base import BaseResource
from app.models import Equipment, EquipmentRoom, EquipmentCategory
from app.utils import ValidationError, render_template


class EquipmentResource(BaseResource):
    def on_get(self, req, resp):
        data = self.parse_data(req)
        query = Equipment.select().join(EquipmentRoom).switch(Equipment).join(EquipmentCategory)
        
        room_id = data.get('room_id')
        category_id = data.get('category_id')
        status = data.get('status')
        keyword = data.get('keyword')
        
        if room_id:
            query = query.where(Equipment.room == room_id)
        if category_id:
            query = query.where(Equipment.category == category_id)
        if status:
            query = query.where(Equipment.status == status)
        if keyword:
            query = query.where(
                (Equipment.name.contains(keyword)) | 
                (Equipment.equipment_no.contains(keyword))
            )
        
        equipment_list = query.order_by(Equipment.equipment_no)
        rooms = EquipmentRoom.select().order_by(EquipmentRoom.name)
        categories = EquipmentCategory.select().order_by(EquipmentCategory.name)
        
        context = {
            'equipment_list': equipment_list,
            'rooms': rooms,
            'categories': categories,
            'filters': {
                'room_id': room_id,
                'category_id': category_id,
                'status': status,
                'keyword': keyword
            }
        }
        self.render(resp, 'equipment/list.html', context)

    def on_post(self, req, resp):
        data = self.parse_data(req)
        try:
            equipment = Equipment.create(
                equipment_no=data.get('equipment_no'),
                name=data.get('name'),
                category=data.get('category_id'),
                room=data.get('room_id'),
                condition=data.get('condition', 'good'),
                status=data.get('status', 'available'),
                specification=data.get('specification'),
                brand=data.get('brand'),
                remark=data.get('remark')
            )
            if req.headers.get('HX-Request'):
                html = render_template('equipment/_row.html', {'equipment': equipment})
                resp.status = 200
                resp.content_type = 'text/html; charset=utf-8'
                resp.text = html
                return
            self.success_json(resp, {'id': equipment.id}, '器材创建成功')
        except Exception as e:
            self.handle_validation_error(resp, ValidationError(str(e)))


class EquipmentDetailResource(BaseResource):
    def on_get(self, req, resp, equipment_id):
        equipment = Equipment.get_by_id(equipment_id)
        if req.headers.get('HX-Request'):
            rooms = EquipmentRoom.select().order_by(EquipmentRoom.name)
            categories = EquipmentCategory.select().order_by(EquipmentCategory.name)
            html = render_template('equipment/_form.html', {'equipment': equipment, 'rooms': rooms, 'categories': categories})
            resp.status = 200
            resp.content_type = 'text/html; charset=utf-8'
            resp.text = html
            return
        self.success_json(resp, {
            'id': equipment.id,
            'equipment_no': equipment.equipment_no,
            'name': equipment.name,
            'category_id': equipment.category_id,
            'room_id': equipment.room_id,
            'condition': equipment.condition,
            'status': equipment.status,
            'specification': equipment.specification,
            'brand': equipment.brand,
            'remark': equipment.remark
        })

    def on_put(self, req, resp, equipment_id):
        data = self.parse_data(req)
        try:
            equipment = Equipment.get_by_id(equipment_id)
            equipment.equipment_no = data.get('equipment_no', equipment.equipment_no)
            equipment.name = data.get('name', equipment.name)
            equipment.category = data.get('category_id', equipment.category_id)
            equipment.room = data.get('room_id', equipment.room_id)
            equipment.condition = data.get('condition', equipment.condition)
            equipment.status = data.get('status', equipment.status)
            equipment.specification = data.get('specification', equipment.specification)
            equipment.brand = data.get('brand', equipment.brand)
            equipment.remark = data.get('remark', equipment.remark)
            equipment.save()
            if req.headers.get('HX-Request'):
                html = render_template('equipment/_row.html', {'equipment': equipment})
                resp.status = 200
                resp.content_type = 'text/html; charset=utf-8'
                resp.text = html
                return
            self.success_json(resp, {'id': equipment.id}, '器材更新成功')
        except Exception as e:
            self.handle_validation_error(resp, ValidationError(str(e)))

    def on_delete(self, req, resp, equipment_id):
        try:
            equipment = Equipment.get_by_id(equipment_id)
            equipment.delete_instance()
            if req.headers.get('HX-Request'):
                resp.status = 200
                resp.text = ''
                return
            self.success_json(resp, message='器材删除成功')
        except Exception as e:
            self.handle_validation_error(resp, ValidationError(str(e)))
