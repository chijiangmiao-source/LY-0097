from peewee import fn
from .base import BaseResource
from app.models import BorrowOrder, Equipment, InspectionRecord, LiabilityJudgment
from app.utils import generate_weekly_report


class HomeResource(BaseResource):
    def on_get(self, req, resp):
        data = self.parse_data(req)
        
        pending_orders = BorrowOrder.select().where(
            BorrowOrder.return_status != 'closed'
        ).count()
        
        total_equipment = Equipment.select().count()
        
        available_equipment = Equipment.select().where(
            Equipment.status == 'available',
            Equipment.condition == 'good'
        ).count()
        
        pending_inspections = InspectionRecord.select().where(
            InspectionRecord.status != 'closed'
        ).count()
        
        weekly_report = generate_weekly_report()
        
        recent_orders = BorrowOrder.select().order_by(
            BorrowOrder.borrow_time.desc()
        ).limit(10)
        
        context = {
            'pending_orders': pending_orders,
            'total_equipment': total_equipment,
            'available_equipment': available_equipment,
            'pending_inspections': pending_inspections,
            'weekly_report': weekly_report,
            'recent_orders': recent_orders
        }
        self.render(resp, 'home.html', context)
