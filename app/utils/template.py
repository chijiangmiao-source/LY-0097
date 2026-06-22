import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from app.utils import format_date, get_status_label, STATUS_LABELS

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'app', 'templates')

env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(['html', 'xml']),
    trim_blocks=True,
    lstrip_blocks=True
)

env.filters['format_date'] = format_date
env.filters['status_label'] = get_status_label
env.globals['STATUS_LABELS'] = STATUS_LABELS


def render_template(template_name, context=None):
    if context is None:
        context = {}
    template = env.get_template(template_name)
    return template.render(**context)
