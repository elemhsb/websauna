from pyramid.view import view_config, view_defaults

from .admin import UserAdmin
from .admin import GroupAdmin

from pyramid_layout.panel import panel_config
from pyramid_web20.system import crud
from pyramid_web20.system.crud import listing
from pyramid_web20.system.admin import views as admin_views

from pyramid_web20 import DBSession


@panel_config(name='admin_panel', context=UserAdmin, renderer='admin/user_panel.html')
def default_model_admin_panel(context, request):
    """Admin panel for Users."""
    model_admin = context
    admin = model_admin.__parent__
    model = model_admin.get_model()

    title = model_admin.title
    count = DBSession.query(model).count()
    latest_user = DBSession.query(model).order_by(model.activated_at.desc()).first()
    latest_user_url = request.resource_url(admin.get_admin_resource(latest_user))

    return locals()



@view_defaults(context=UserAdmin)
class UserListing(admin_views.Listing):
    """Listing view for Users."""
    title = "All users"

    table = listing.Table(
        columns = [
            listing.Column("id", "Id",),
            listing.Column("friendly_name", "Friendly name"),
            listing.Column("email", "Email"),
            listing.ControlsColumn()
        ]
    )

    def order_query(self, query):
        return query.order_by(self.get_model().created_at.Desc())


@view_defaults(context=GroupAdmin)
class GroupListing(admin_views.Listing):
    """Listing view for Groups."""

    title = "All groups"

    table = listing.Table(
        columns = [
            listing.Column("id", "Id",),
            listing.Column("name", "Name"),
            listing.ControlsColumn()
        ]
    )

    def order_query(self, query):
        return query.order_by(self.get_model().created_at.Desc())