import falcon
from app.utils import verify_session_token
from app.models import User
from config import db


class AuthMiddleware:
    def __init__(self, exempt_paths=None):
        self.exempt_paths = exempt_paths or ['/login', '/static/']

    def process_request(self, req, resp):
        for path in self.exempt_paths:
            if req.path.startswith(path):
                return

        token = req.cookies.get('session_token')
        if not token:
            if req.headers.get('HX-Request'):
                resp.status = falcon.HTTP_401
                resp.set_header('HX-Redirect', '/login')
                resp.text = ''
                return
            raise falcon.HTTPFound('/login')

        user_id = verify_session_token(token)
        if not user_id:
            if req.headers.get('HX-Request'):
                resp.status = falcon.HTTP_401
                resp.set_header('HX-Redirect', '/login')
                resp.text = ''
                return
            raise falcon.HTTPFound('/login')

        try:
            user = User.get_by_id(user_id)
            if not user.is_active:
                raise falcon.HTTPFound('/login')
            req.context['user'] = user
        except User.DoesNotExist:
            raise falcon.HTTPFound('/login')

    def process_resource(self, req, resp, resource, params):
        pass

    def process_response(self, req, resp, resource, req_succeeded):
        pass


class DatabaseMiddleware:
    def process_request(self, req, resp):
        db.connect()

    def process_response(self, req, resp, resource, req_succeeded):
        if not db.is_closed():
            db.close()
