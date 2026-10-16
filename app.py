"""Flask app: routes lang ito. Lahat ng logic ay nasa services."""
import hmac
from functools import wraps

from flask import (Flask, flash, jsonify, redirect, render_template,
                   request, session, url_for)

from config import Config
from models.complaint import Status
from repositories.memory_repository import InMemoryComplaintRepository
from services.complaint_service import (CATEGORIES, ComplaintNotFound,
                                        ComplaintService, ValidationError)
from services.email_service import (ComplaintNotifier, ConsoleEmailSender,
                                    SmtpEmailSender)


def build_service(config: Config) -> ComplaintService:
    """Dito pinipili kung anong database at email ang gagamitin."""
    if config.dev_mode:
        repo = InMemoryComplaintRepository()
        sender = ConsoleEmailSender()
    else:
        from repositories.sheets_repository import GoogleSheetsComplaintRepository
        repo = GoogleSheetsComplaintRepository(
            config.credentials_file, config.sheet_id, config.worksheet_name)
        sender = SmtpEmailSender(config.gmail_user, config.gmail_app_password)
    return ComplaintService(repo, ComplaintNotifier(sender))


def create_app(config: Config = None, service: ComplaintService = None) -> Flask:
    config = config or Config.from_env()
    service = service or build_service(config)

    app = Flask(__name__)
    app.secret_key = config.secret_key
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    def admin_required(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            if not session.get("is_admin"):
                return redirect(url_for("admin_login"))
            return view(*args, **kwargs)
        return wrapper

    # ---------------- Student pages ----------------
    @app.get("/")
    def index():
        return render_template("index.html", categories=CATEGORIES)

    @app.post("/api/complaints")
    def submit_complaint():
        data = request.get_json(silent=True) or {}
        try:
            result = service.submit(data.get("name"), data.get("email"),
                                    data.get("category"), data.get("message"))
        except ValidationError as exc:
            return jsonify(success=False, error=str(exc)), 400
        except Exception:
            app.logger.exception("Submit failed")
            return jsonify(success=False, error="May problema sa server. Subukan ulit."), 500
        return jsonify(success=True, **result), 201

    @app.get("/track")
    def track_page():
        return render_template("track.html", prefill=request.args.get("id", ""))

    @app.get("/api/complaints/<complaint_id>")
    def track_complaint(complaint_id):
        try:
            return jsonify(found=True, **service.track(complaint_id))
        except ComplaintNotFound:
            return jsonify(found=False), 404

    # ---------------- Admin ----------------
    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        if request.method == "POST":
            password = request.form.get("password", "")
            if hmac.compare_digest(password.encode(), config.admin_password.encode()):
                session["is_admin"] = True
                return redirect(url_for("admin_dashboard"))
            flash("Maling password.")
        return render_template("admin_login.html")

    @app.post("/admin/logout")
    def admin_logout():
        session.clear()
        return redirect(url_for("admin_login"))

    @app.get("/admin")
    @admin_required
    def admin_dashboard():
        status = request.args.get("status") or None
        try:
            complaints = service.list_complaints(status)
        except ValueError:
            complaints = service.list_complaints()
            status = None
        return render_template("admin.html", complaints=complaints, stats=service.stats(),
                               statuses=[s.value for s in Status], current=status)

    @app.post("/admin/complaints/<complaint_id>/status")
    @admin_required
    def admin_update_status(complaint_id):
        try:
            result = service.update_status(complaint_id, request.form.get("status"),
                                           request.form.get("remarks", ""))
            msg = f"{result['complaint_id']} → {result['status']}"
            if result["email_sent"] is True:
                msg += " (email naipadala)"
            elif result["email_sent"] is False:
                msg += " (HINDI naipadala ang email, i-check ang Gmail settings)"
            flash(msg)
        except (ValidationError, ComplaintNotFound) as exc:
            flash(f"Error: {exc}")
        return redirect(url_for("admin_dashboard", status=request.args.get("status")))

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
