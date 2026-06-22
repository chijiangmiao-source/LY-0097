from app.utils import (
    parse_form,
    json_response,
    html_response,
    redirect_response,
    render_template,
    ValidationError
)


class BaseResource:
    def get_context(self, req):
        return {
            'current_user': req.context.get('user'),
            'current_path': req.path
        }

    def render(self, resp, template_name, extra_context=None):
        context = self.get_context(
            hasattr(self, 'req') and self.req or {'context': {}}
        )
        if hasattr(self, 'req'):
            context = self.get_context(self.req)
        if extra_context:
            context.update(extra_context)
        html = render_template(template_name, context)
        html_response(resp, html)

    def success_json(self, resp, data=None, message='操作成功'):
        json_response(resp, {'success': True, 'message': message, 'data': data or {}})

    def error_json(self, resp, message='操作失败', status=400):
        json_response(resp, {'success': False, 'message': message}, status)

    def redirect(self, resp, location):
        redirect_response(resp, location)

    def parse_data(self, req):
        self.req = req
        return parse_form(req)

    def handle_validation_error(self, resp, e):
        if self.req.headers.get('HX-Request'):
            resp.status = 400
            resp.text = f'<div class="notification is-danger">{str(e)}</div>'
            return
        self.error_json(resp, str(e))
