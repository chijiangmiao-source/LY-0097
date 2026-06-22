from .base import BaseResource
from app.models import EquipmentCategory
from app.utils import ValidationError, render_template


class EquipmentCategoryResource(BaseResource):
    def on_get(self, req, resp):
        data = self.parse_data(req)
        categories = EquipmentCategory.select().order_by(EquipmentCategory.name)
        self.render(resp, 'equipment_category/list.html', {'categories': categories})

    def on_post(self, req, resp):
        data = self.parse_data(req)
        try:
            category = EquipmentCategory.create(
                name=data.get('name'),
                code=data.get('code'),
                description=data.get('description')
            )
            if req.headers.get('HX-Request'):
                html = render_template('equipment_category/_row.html', {'category': category})
                resp.status = 200
                resp.content_type = 'text/html; charset=utf-8'
                resp.text = html
                return
            self.success_json(resp, {'id': category.id}, '分类创建成功')
        except Exception as e:
            self.handle_validation_error(resp, ValidationError(str(e)))


class EquipmentCategoryDetailResource(BaseResource):
    def on_get(self, req, resp, category_id):
        category = EquipmentCategory.get_by_id(category_id)
        if req.headers.get('HX-Request'):
            html = render_template('equipment_category/_form.html', {'category': category})
            resp.status = 200
            resp.content_type = 'text/html; charset=utf-8'
            resp.text = html
            return
        self.success_json(resp, {
            'id': category.id,
            'name': category.name,
            'code': category.code,
            'description': category.description
        })

    def on_put(self, req, resp, category_id):
        data = self.parse_data(req)
        try:
            category = EquipmentCategory.get_by_id(category_id)
            category.name = data.get('name', category.name)
            category.code = data.get('code', category.code)
            category.description = data.get('description', category.description)
            category.save()
            if req.headers.get('HX-Request'):
                html = render_template('equipment_category/_row.html', {'category': category})
                resp.status = 200
                resp.content_type = 'text/html; charset=utf-8'
                resp.text = html
                return
            self.success_json(resp, {'id': category.id}, '分类更新成功')
        except Exception as e:
            self.handle_validation_error(resp, ValidationError(str(e)))

    def on_delete(self, req, resp, category_id):
        try:
            category = EquipmentCategory.get_by_id(category_id)
            category.delete_instance()
            if req.headers.get('HX-Request'):
                resp.status = 200
                resp.text = ''
                return
            self.success_json(resp, message='分类删除成功')
        except Exception as e:
            self.handle_validation_error(resp, ValidationError(str(e)))
