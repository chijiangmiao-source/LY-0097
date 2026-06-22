import falcon
from datetime import datetime, timedelta
from .base import BaseResource
from app.models import User
from app.utils import create_session_token, render_template, redirect_response, parse_form, ValidationError


class LoginResource(BaseResource):
    def on_get(self, req, resp):
        if req.cookies.get('session_token'):
            raise falcon.HTTPFound('/')
        html = render_template('login.html', {'error': req.params.get('error')})
        resp.status = 200
        resp.content_type = 'text/html; charset=utf-8'
        resp.text = html

    def on_post(self, req, resp):
        data = parse_form(req)
        username = data.get('username', '').strip()
        password = data.get('password', '')

        if not username or not password:
            html = render_template('login.html', {'error': '请输入用户名和密码'})
            resp.status = 400
            resp.content_type = 'text/html; charset=utf-8'
            resp.text = html
            return

        try:
            user = User.get(User.username == username)
            if not user.is_active:
                raise ValidationError('账户已被禁用')
            if not user.check_password(password):
                raise ValidationError('用户名或密码错误')

            token = create_session_token(user.id)
            expires = datetime.now() + timedelta(days=1)
            
            if req.headers.get('HX-Request'):
                resp.set_header('HX-Redirect', '/')
                resp.set_header('Set-Cookie', f'session_token={token}; Path=/; HttpOnly; Expires={expires.strftime("%a, %d %b %Y %H:%M:%S GMT")}')
                resp.text = ''
                return

            resp.set_header('Set-Cookie', f'session_token={token}; Path=/; HttpOnly; Expires={expires.strftime("%a, %d %b %Y %H:%M:%S GMT")}')
            redirect_response(resp, '/')

        except User.DoesNotExist:
            html = render_template('login.html', {'error': '用户名或密码错误'})
            resp.status = 401
            resp.content_type = 'text/html; charset=utf-8'
            resp.text = html
        except ValidationError as e:
            html = render_template('login.html', {'error': str(e)})
            resp.status = 400
            resp.content_type = 'text/html; charset=utf-8'
            resp.text = html


class LogoutResource:
    def on_get(self, req, resp):
        resp.set_header('Set-Cookie', 'session_token=; Path=/; HttpOnly; Expires=Thu, 01 Jan 1970 00:00:00 GMT')
        redirect_response(resp, '/login')

    def on_post(self, req, resp):
        resp.set_header('Set-Cookie', 'session_token=; Path=/; HttpOnly; Expires=Thu, 01 Jan 1970 00:00:00 GMT')
        if req.headers.get('HX-Request'):
            resp.set_header('HX-Redirect', '/login')
            resp.text = ''
            return
        redirect_response(resp, '/login')
