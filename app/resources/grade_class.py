from .base import BaseResource
from app.models import GradeClass
from app.utils import ValidationError, render_template


class GradeClassResource(BaseResource):
    def on_get(self, req, resp):
        data = self.parse_data(req)
        classes = GradeClass.select().order_by(GradeClass.grade, GradeClass.class_number)
        context = {'classes': classes, 'grades': ['一年级', '二年级', '三年级', '四年级', '五年级', '六年级', '初一', '初二', '初三', '高一', '高二', '高三']}
        self.render(resp, 'grade_class/list.html', context)

    def on_post(self, req, resp):
        data = self.parse_data(req)
        try:
            grade_class = GradeClass.create(
                grade=data.get('grade'),
                class_name=data.get('class_name'),
                class_number=int(data.get('class_number')),
                head_teacher=data.get('head_teacher')
            )
            if req.headers.get('HX-Request'):
                context = {'grade_class': grade_class}
                html = render_template('grade_class/_row.html', context)
                resp.status = 200
                resp.content_type = 'text/html; charset=utf-8'
                resp.text = html
                return
            self.success_json(resp, {'id': grade_class.id}, '班级创建成功')
        except Exception as e:
            self.handle_validation_error(resp, ValidationError(str(e)))


class GradeClassDetailResource(BaseResource):
    def on_get(self, req, resp, class_id):
        grade_class = GradeClass.get_by_id(class_id)
        if req.headers.get('HX-Request'):
            context = {'grade_class': grade_class}
            html = render_template('grade_class/_form.html', context)
            resp.status = 200
            resp.content_type = 'text/html; charset=utf-8'
            resp.text = html
            return
        self.success_json(resp, {
            'id': grade_class.id,
            'grade': grade_class.grade,
            'class_name': grade_class.class_name,
            'class_number': grade_class.class_number,
            'head_teacher': grade_class.head_teacher
        })

    def on_put(self, req, resp, class_id):
        data = self.parse_data(req)
        try:
            grade_class = GradeClass.get_by_id(class_id)
            grade_class.grade = data.get('grade', grade_class.grade)
            grade_class.class_name = data.get('class_name', grade_class.class_name)
            grade_class.class_number = int(data.get('class_number', grade_class.class_number))
            grade_class.head_teacher = data.get('head_teacher', grade_class.head_teacher)
            grade_class.save()
            if req.headers.get('HX-Request'):
                context = {'grade_class': grade_class}
                html = render_template('grade_class/_row.html', context)
                resp.status = 200
                resp.content_type = 'text/html; charset=utf-8'
                resp.text = html
                return
            self.success_json(resp, {'id': grade_class.id}, '班级更新成功')
        except Exception as e:
            self.handle_validation_error(resp, ValidationError(str(e)))

    def on_delete(self, req, resp, class_id):
        try:
            grade_class = GradeClass.get_by_id(class_id)
            grade_class.delete_instance()
            if req.headers.get('HX-Request'):
                resp.status = 200
                resp.text = ''
                return
            self.success_json(resp, message='班级删除成功')
        except Exception as e:
            self.handle_validation_error(resp, ValidationError(str(e)))
