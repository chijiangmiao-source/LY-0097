import os
import falcon
from dotenv import load_dotenv
from config import db
from app.middleware import AuthMiddleware, DatabaseMiddleware
from app.resources import (
    LoginResource,
    LogoutResource,
    HomeResource,
    GradeClassResource,
    GradeClassDetailResource,
    EquipmentRoomResource,
    EquipmentRoomDetailResource,
    EquipmentCategoryResource,
    EquipmentCategoryDetailResource,
    EquipmentResource,
    EquipmentDetailResource,
    BorrowOrderResource,
    BorrowOrderDetailResource,
    BorrowOrderReturnResource,
    BorrowOrderCloseResource,
    BorrowOrderAddItemResource,
    BorrowOrderRemoveItemResource,
    InspectionResource,
    InspectionDetailResource,
    InspectionCloseResource,
    InspectionEquipmentSearchResource,
    LiabilityJudgmentResource,
    LiabilityJudgmentDetailResource,
    LiabilityConfirmResource,
    WeeklyReportResource,
)
from app.utils import render_template, html_response, redirect_response

load_dotenv()


def create_app():
    app = falcon.App(
        middleware=[
            DatabaseMiddleware(),
            AuthMiddleware(exempt_paths=['/login', '/logout', '/static/'])
        ]
    )

    app.add_route('/login', LoginResource())
    app.add_route('/logout', LogoutResource())
    app.add_route('/', HomeResource())

    app.add_route('/grade-classes', GradeClassResource())
    app.add_route('/grade-classes/{class_id:int}', GradeClassDetailResource())
    app.add_route('/grade-classes/{class_id:int}/edit', GradeClassDetailResource())
    app.add_route('/grade-classes/new', GradeClassResource())

    app.add_route('/equipment-rooms', EquipmentRoomResource())
    app.add_route('/equipment-rooms/{room_id:int}', EquipmentRoomDetailResource())
    app.add_route('/equipment-rooms/{room_id:int}/edit', EquipmentRoomDetailResource())
    app.add_route('/equipment-rooms/new', EquipmentRoomResource())

    app.add_route('/equipment-categories', EquipmentCategoryResource())
    app.add_route('/equipment-categories/{category_id:int}', EquipmentCategoryDetailResource())
    app.add_route('/equipment-categories/{category_id:int}/edit', EquipmentCategoryDetailResource())
    app.add_route('/equipment-categories/new', EquipmentCategoryResource())

    app.add_route('/equipment', EquipmentResource())
    app.add_route('/equipment/{equipment_id:int}', EquipmentDetailResource())
    app.add_route('/equipment/{equipment_id:int}/edit', EquipmentDetailResource())
    app.add_route('/equipment/new', EquipmentResource())

    app.add_route('/borrow-orders', BorrowOrderResource())
    app.add_route('/borrow-orders/{order_id:int}', BorrowOrderDetailResource())
    app.add_route('/borrow-orders/{order_id:int}/return', BorrowOrderReturnResource())
    app.add_route('/borrow-orders/{order_id:int}/close', BorrowOrderCloseResource())
    app.add_route('/borrow-orders/{order_id:int}/items', BorrowOrderAddItemResource())
    app.add_route('/borrow-orders/{order_id:int}/items/{item_id:int}', BorrowOrderRemoveItemResource())
    app.add_route('/borrow-orders/new', BorrowOrderResource())

    app.add_route('/inspections', InspectionResource())
    app.add_route('/inspections/{inspection_id:int}', InspectionDetailResource())
    app.add_route('/inspections/{inspection_id:int}/edit', InspectionDetailResource())
    app.add_route('/inspections/{inspection_id:int}/close', InspectionCloseResource())
    app.add_route('/inspections/equipment/{order_id:int}', InspectionEquipmentSearchResource())
    app.add_route('/inspections/equipment-options', InspectionEquipmentSearchResource())
    app.add_route('/inspections/new', InspectionResource())

    app.add_route('/liability', LiabilityJudgmentResource())
    app.add_route('/liability/{judgment_id:int}', LiabilityJudgmentDetailResource())
    app.add_route('/liability/{judgment_id:int}/edit', LiabilityJudgmentDetailResource())
    app.add_route('/liability/{judgment_id:int}/confirm', LiabilityConfirmResource())
    app.add_route('/liability/new', LiabilityJudgmentResource())

    app.add_route('/weekly-report', WeeklyReportResource())

    def handle_404(req, resp):
        if req.context.get('user'):
            html = render_template('404.html')
            html_response(resp, html, 404)
        else:
            redirect_response(resp, '/login')

    app.add_sink(handle_404, '/')

    return app
