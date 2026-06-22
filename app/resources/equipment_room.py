from .base import BaseResource
from app.models import EquipmentRoom
from app.utils import ValidationError, render_template


class EquipmentRoomResource(BaseResource):
    def on_get(self, req, resp):
        data = self.parse_data(req)
        rooms = EquipmentRoom.select().order_by(EquipmentRoom.name)
        self.render(resp, 'equipment_room/list.html', {'rooms': rooms})

    def on_post(self, req, resp):
        data = self.parse_data(req)
        try:
            room = EquipmentRoom.create(
                name=data.get('name'),
                location=data.get('location'),
                manager=data.get('manager'),
                description=data.get('description')
            )
            if req.headers.get('HX-Request'):
                html = render_template('equipment_room/_row.html', {'room': room})
                resp.status = 200
                resp.content_type = 'text/html; charset=utf-8'
                resp.text = html
                return
            self.success_json(resp, {'id': room.id}, '器材室创建成功')
        except Exception as e:
            self.handle_validation_error(resp, ValidationError(str(e)))


class EquipmentRoomDetailResource(BaseResource):
    def on_get(self, req, resp, room_id):
        room = EquipmentRoom.get_by_id(room_id)
        if req.headers.get('HX-Request'):
            html = render_template('equipment_room/_form.html', {'room': room})
            resp.status = 200
            resp.content_type = 'text/html; charset=utf-8'
            resp.text = html
            return
        self.success_json(resp, {
            'id': room.id,
            'name': room.name,
            'location': room.location,
            'manager': room.manager,
            'description': room.description
        })

    def on_put(self, req, resp, room_id):
        data = self.parse_data(req)
        try:
            room = EquipmentRoom.get_by_id(room_id)
            room.name = data.get('name', room.name)
            room.location = data.get('location', room.location)
            room.manager = data.get('manager', room.manager)
            room.description = data.get('description', room.description)
            room.save()
            if req.headers.get('HX-Request'):
                html = render_template('equipment_room/_row.html', {'room': room})
                resp.status = 200
                resp.content_type = 'text/html; charset=utf-8'
                resp.text = html
                return
            self.success_json(resp, {'id': room.id}, '器材室更新成功')
        except Exception as e:
            self.handle_validation_error(resp, ValidationError(str(e)))

    def on_delete(self, req, resp, room_id):
        try:
            room = EquipmentRoom.get_by_id(room_id)
            room.delete_instance()
            if req.headers.get('HX-Request'):
                resp.status = 200
                resp.text = ''
                return
            self.success_json(resp, message='器材室删除成功')
        except Exception as e:
            self.handle_validation_error(resp, ValidationError(str(e)))
