from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.models import Pengaduan
import boto3, uuid

pengaduan_bp = Blueprint('pengaduan', __name__, url_prefix='/pengaduan')

KATEGORI_LIST = [
    'Infrastruktur Jalan',
    'Kebersihan Lingkungan',
    'Keamanan',
    'Pelayanan Publik',
    'Bencana Alam',
    'Lainnya',
]

ALLOWED = {'jpg', 'jpeg', 'png', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED

def upload_s3(file, bucket, region, access_key, secret_key):
    s3 = boto3.client('s3', region_name=region,
                      aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key)
    ext      = file.filename.rsplit('.', 1)[1].lower()
    filename = f"pengaduan/{uuid.uuid4().hex}.{ext}"
    s3.upload_fileobj(file, bucket, filename,
                      ExtraArgs={'ACL': 'public-read', 'ContentType': file.content_type})
    url = f"https://{bucket}.s3.{region}.amazonaws.com/{filename}"
    return url, filename

@pengaduan_bp.route('/')
@login_required
def index():
    if current_user.role == 'admin':
        pengaduans = Pengaduan.query.order_by(Pengaduan.created_at.desc()).all()
    else:
        pengaduans = Pengaduan.query.filter_by(user_id=current_user.id)\
                                    .order_by(Pengaduan.created_at.desc()).all()
    return render_template('pengaduan.html', pengaduans=pengaduans, kategori_list=KATEGORI_LIST)

@pengaduan_bp.route('/kirim', methods=['POST'])
@login_required
def kirim():
    judul     = request.form.get('judul')
    kategori  = request.form.get('kategori')
    deskripsi = request.form.get('deskripsi')
    lokasi    = request.form.get('lokasi')
    file      = request.files.get('file_foto')

    file_url = file_name = None
    if file and file.filename and allowed_file(file.filename):
        try:
            file_url, file_name = upload_s3(
                file,
                current_app.config['S3_BUCKET_NAME'],
                current_app.config['AWS_REGION'],
                current_app.config['AWS_ACCESS_KEY_ID'],
                current_app.config['AWS_SECRET_ACCESS_KEY'],
            )
        except Exception as e:
            flash(f'Gagal upload foto: {str(e)}', 'danger')
            return redirect(url_for('pengaduan.index'))

    p = Pengaduan(user_id=current_user.id, judul=judul, kategori=kategori,
                  deskripsi=deskripsi, lokasi=lokasi,
                  file_foto_url=file_url, file_foto_name=file_name)
    db.session.add(p)
    db.session.commit()
    flash('Pengaduan berhasil dikirim!', 'success')
    return redirect(url_for('pengaduan.index'))

@pengaduan_bp.route('/tanggapi/<int:id>', methods=['POST'])
@login_required
def tanggapi(id):
    if current_user.role != 'admin':
        flash('Akses ditolak.', 'danger')
        return redirect(url_for('pengaduan.index'))
    p = Pengaduan.query.get_or_404(id)
    p.status    = request.form.get('status')
    p.tanggapan = request.form.get('tanggapan')
    db.session.commit()
    flash('Tanggapan berhasil dikirim.', 'success')
    return redirect(url_for('pengaduan.index'))

@pengaduan_bp.route('/hapus/<int:id>', methods=['POST'])
@login_required
def hapus(id):
    p = Pengaduan.query.get_or_404(id)
    if p.user_id != current_user.id and current_user.role != 'admin':
        flash('Akses ditolak.', 'danger')
        return redirect(url_for('pengaduan.index'))
    db.session.delete(p)
    db.session.commit()
    flash('Pengaduan dihapus.', 'info')
    return redirect(url_for('pengaduan.index'))
