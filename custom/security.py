from flask import current_app as app, flash, g, redirect, request, Response
from flask_appbuilder import AppBuilder
from flask_appbuilder.security.views import AuthDBView, expose
from flask_login import login_user

from superset import db
from superset.security import SupersetSecurityManager


class CustomAuthDBView(AuthDBView):
    login_template = "appbuilder/general/security/login_db.html"

    @expose("/login/", methods=["GET", "POST"])
    def login(self) -> Response:
        token = request.args.get("token")
        if (username := request.args.get("username")) is not None:
            user = self.appbuilder.sm.find_user(username=username)
            if user is None:
                flash("Credentials doesnt match")
                return redirect(self.appbuilder.get_url_for_index)
            else:
                with app.app_context():
                    from superset.models.external_token import ExternalToken

                    externalToken = (
                        db.session.query(ExternalToken)
                        .where(
                            ExternalToken.username == username,
                            ExternalToken.token == token,
                        )
                        .first()
                    )

                    if not externalToken:
                        flash("User not found", "warning")
                        return redirect(self.appbuilder.get_url_for_index)
                    else:
                        flash(f"Hallo {externalToken.username}", "success")
                        login_user(user, remember=False)
                        return redirect(self.appbuilder.get_url_for_index)

                flash("Admin auto logged in", "success")
                login_user(user, remember=False)
                return redirect(self.appbuilder.get_url_for_index)
        else:
            return super().login()


class CustomSecurityManager(SupersetSecurityManager):
    authdbview = CustomAuthDBView

    def __init__(self, appbuilder: AppBuilder) -> None:
        super().__init__(appbuilder)
