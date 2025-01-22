from flask import current_app as app, flash, g, redirect, request, Response
from flask_appbuilder import AppBuilder
from flask_appbuilder.security.views import AuthDBView, expose
from flask_appbuilder.security.sqla.models import User
from flask_login import login_user

from superset import db
from superset.app import logger
from superset.security import SupersetSecurityManager


class CustomAuthDBView(AuthDBView):
    login_template = "appbuilder/general/security/login_db.html"

    @expose("/login/", methods=["GET", "POST"])
    def login(self) -> Response:
        token = request.args.get("token")
        logger.info(f"Token: {token} Username: {request.args.get('username')}")
        if (username := request.args.get("username")) is not None:
            user = self.appbuilder.sm.find_user(username=username)
            logger.info(f"found user; {user}")
            if user is None:
                flash("Credentials doesnt match")
                return redirect(self.appbuilder.get_url_for_index)
            else:
                with app.app_context():
                    from superset.models.external_token import ExternalToken

                    externalToken = (
                        db.session.query(ExternalToken)
                        .where(
                            ExternalToken.user.has(User.username == username),
                            ExternalToken.token == token,
                        )
                        .first()
                    )
                    
                    logger.info(f"externalToken: {externalToken}")
                    logger.info(f"user: {user}")

                    if not externalToken:
                        flash("User not found", "warning")
                        return redirect(self.appbuilder.get_url_for_index)
                    # else:
                    #     flash(f"Hallo {externalToken.username}", "success")
                    #     login_user(user, remember=False)
                    #     return redirect(self.appbuilder.get_url_for_index)

                logger.info(f"User: {user}")
                flash("Admin auto logged in", "success")
                is_login = login_user(user, remember=False)
                
                logger.info(f"Is login: {is_login}")
                return redirect(self.appbuilder.get_url_for_index)
        else:
            return super().login()


class CustomSecurityManager(SupersetSecurityManager):
    authdbview = CustomAuthDBView

    def __init__(self, appbuilder: AppBuilder) -> None:
        super().__init__(appbuilder)
