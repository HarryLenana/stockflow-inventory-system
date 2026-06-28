from .auth import auth
from .dashboard import dashboard_bp
from .users import users_bp
from .products import products_bp
from .suppliers import suppliers_bp
from .purchases import purchases_bp
from .sales import sales_bp
from .reports import reports_bp
from .settings import settings_bp


def register_routes(app):

    app.register_blueprint(auth)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(purchases_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)
