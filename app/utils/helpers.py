import json
import hmac
import hashlib
import os
from datetime import datetime, timedelta
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')


def parse_json(req):
    if req.content_type and 'application/json' in req.content_type:
        return json.load(req.stream)
    return {}


def parse_form(req):
    data = {}
    for key in req.params:
        data[key] = req.params[key]
    return data


def json_response(resp, data, status=200):
    resp.status = status
    resp.content_type = 'application/json'
    resp.text = json.dumps(data, ensure_ascii=False, default=str)


def html_response(resp, html, status=200):
    resp.status = status
    resp.content_type = 'text/html; charset=utf-8'
    resp.text = html


def redirect_response(resp, location, status=302):
    resp.status = status
    resp.set_header('Location', location)


def generate_order_no(prefix='LY'):
    now = datetime.now()
    return f"{prefix}{now.strftime('%Y%m%d%H%M%S')}"


def create_session_token(user_id):
    timestamp = str(int(datetime.now().timestamp()))
    message = f"{user_id}:{timestamp}"
    signature = hmac.new(SECRET_KEY.encode(), message.encode(), hashlib.sha256).hexdigest()
    return f"{message}:{signature}"


def verify_session_token(token):
    try:
        parts = token.split(':')
        if len(parts) != 3:
            return None
        user_id, timestamp, signature = parts
        message = f"{user_id}:{timestamp}"
        expected_signature = hmac.new(SECRET_KEY.encode(), message.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_signature):
            return None
        if int(timestamp) < int(datetime.now().timestamp()) - 86400:
            return None
        return int(user_id)
    except Exception:
        return None


def get_week_range(date=None):
    if date is None:
        date = datetime.now()
    start = date - timedelta(days=date.weekday())
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=6, hours=23, minutes=59, seconds=59)
    return start, end


def format_date(dt):
    if dt is None:
        return ''
    if isinstance(dt, str):
        return dt
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def build_url(path, params=None):
    if params:
        return f"{path}?{urlencode(params)}"
    return path


STATUS_LABELS = {
    'equipment_condition': {
        'good': '完好',
        'damaged': '损坏',
        'missing': '缺失',
        'repairing': '维修中'
    },
    'equipment_status': {
        'available': '可用',
        'borrowed': '已借出',
        'maintenance': '维护中',
        'scrapped': '已报废'
    },
    'return_status': {
        'pending': '待归还',
        'partial': '部分归还',
        'returned': '已归还',
        'inspecting': '抽查中',
        'closed': '已结案'
    },
    'liability_status': {
        'pending': '待判定',
        'processing': '处理中',
        'confirmed': '已确认',
        'appealed': '已申诉'
    },
    'inspection_status': {
        'pending': '待处理',
        'processing': '处理中',
        'resolved': '已解决',
        'closed': '已结案'
    },
    'problem_type': {
        'damaged': '损坏',
        'missing': '缺失',
        'overdue': '逾期',
        'other': '其他'
    },
    'liability_type': {
        'student': '学生责任',
        'teacher': '教师责任',
        'school': '学校责任',
        'natural': '自然损耗',
        'other': '其他'
    }
}


def get_status_label(category, key):
    return STATUS_LABELS.get(category, {}).get(key, key)
