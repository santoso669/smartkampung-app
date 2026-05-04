from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.models.models import Surat, Pengaduan

tracking_bp = Blueprint('tracking', __name__, url_prefix='/tracking')

@tracking_bp.route('/')
@login_required
def index():
    if current_user.role == 'admin':
        surats     = Surat.query.order_by(Surat.updated_at.desc()).all()
        pengaduans = Pengaduan.query.order_by(Pengaduan.created_at.desc()).all()
    else:
        surats     = Surat.query.filter_by(user_id=current_user.id)\
                               .order_by(Surat.updated_at.desc()).all()
        pengaduans = Pengaduan.query.filter_by(user_id=current_user.id)\
                                    .order_by(Pengaduan.created_at.desc()).all()
    return render_template('tracking.html', surats=surats, pengaduans=pengaduans)
