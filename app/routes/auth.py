from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.models import User, Surat, Pengaduan

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    return render_template('index.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))
    if request.method == 'POST':
        nama     = request.form.get('nama')
        email    = request.form.get('email')
        nik      = request.form.get('nik')
        password = request.form.get('password')
        role     = request.form.get('role', 'masyarakat')

        if User.query.filter_by(email=email).first():
            flash('Email sudah terdaftar.', 'danger')
            return redirect(url_for('auth.register'))
        if User.query.filter_by(nik=nik).first():
            flash('NIK sudah terdaftar.', 'danger')
            return redirect(url_for('auth.register'))

        user = User(nama=nama, email=email, nik=nik, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registrasi berhasil! Silakan login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))
    if request.method == 'POST':
        email    = request.form.get('email')
        password = request.form.get('password')
        user     = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash(f'Selamat datang, {user.nama}!', 'success')
            return redirect(url_for('auth.dashboard'))
        flash('Email atau password salah.', 'danger')
    return render_template('login.html')

@auth_bp.route('/dashboard')
@login_required
def dashboard():
    total_surat     = Surat.query.count()
    total_pengaduan = Pengaduan.query.count()
    if current_user.role == 'admin':
        surat_pending     = Surat.query.filter_by(status='menunggu').count()
        pengaduan_pending = Pengaduan.query.filter_by(status='diterima').count()
    else:
        surat_pending     = Surat.query.filter_by(user_id=current_user.id, status='menunggu').count()
        pengaduan_pending = Pengaduan.query.filter_by(user_id=current_user.id, status='diterima').count()
    return render_template('dashboard.html',
                           total_surat=total_surat,
                           total_pengaduan=total_pengaduan,
                           surat_pending=surat_pending,
                           pengaduan_pending=pengaduan_pending)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Berhasil logout.', 'info')
    return redirect(url_for('auth.index'))
