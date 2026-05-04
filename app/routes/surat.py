from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.models import Surat
import boto3, uuid

surat_bp = Blueprint('surat', __name__, url_prefix='/surat')

JENIS_SURAT = [
    'Surat Keterangan Domisili',
    'Surat Keterangan Usaha',
    'Surat Keterangan Tidak Mampu',
    'Surat Pengantar KTP',
    'Surat Keterangan Kelahiran',
    'Surat Keterangan Kematian',
    'Surat Izin Keramaian',
]

ALLOWED = {'pdf', 'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED

def upload_s3(file, bucket, region, access_key, secret_key):
    s3 = boto3.client('s3', region_name=region,
                      aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key)
    ext      = file.filename.rsplit('.', 1)[1].lower()
    filename = f"dokumen/{uuid.uuid4().hex}.{ext}"
    s3.upload_fileobj(file, bucket, filename,
                      ExtraArgs={'ACL': 'public-read', 'ContentType': file.content_type})
    url = f"https://{bucket}.s3.{region}.amazonaws.com/{filename}"
    return url, filename

@surat_bp.route('/')
@login_required
def index():
    if current_user.role == 'admin':
        surats = Surat.query.order_by(Surat.created_at.desc()).all()
    else:
        surats = Surat.query.filter_by(user_id=current_user.id)\
                            .order_by(Surat.created_at.desc()).all()
    return render_template('surat.html', surats=surats, jenis_list=JENIS_SURAT)

@surat_bp.route('/ajukan', methods=['POST'])
@login_required
def ajukan():
    jenis    = request.form.get('jenis_surat')
    keperluan= request.form.get('keperluan')
    file     = request.files.get('file_ktp')

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
            flash(f'Gagal upload file: {str(e)}', 'danger')
            return redirect(url_for('surat.index'))

    surat = Surat(user_id=current_user.id, jenis_surat=jenis,
                  keperluan=keperluan, file_ktp_url=file_url, file_ktp_name=file_name)
    db.session.add(surat)
    db.session.commit()
    flash('Pengajuan surat berhasil dikirim!', 'success')
    return redirect(url_for('surat.index'))

@surat_bp.route('/update/<int:id>', methods=['POST'])
@login_required
def update(id):
    if current_user.role != 'admin':
        flash('Akses ditolak.', 'danger')
        return redirect(url_for('surat.index'))
    surat = Surat.query.get_or_404(id)
    surat.status        = request.form.get('status')
    surat.catatan_admin = request.form.get('catatan_admin')
    db.session.commit()
    flash('Status surat diperbarui.', 'success')
    return redirect(url_for('surat.index'))

@surat_bp.route('/hapus/<int:id>', methods=['POST'])
@login_required
def hapus(id):
    surat = Surat.query.get_or_404(id)
    if surat.user_id != current_user.id and current_user.role != 'admin':
        flash('Akses ditolak.', 'danger')
        return redirect(url_for('surat.index'))
    db.session.delete(surat)
    db.session.commit()
    flash('Pengajuan dihapus.', 'info')
    return redirect(url_for('surat.index'))
