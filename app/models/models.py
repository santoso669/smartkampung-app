from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id         = db.Column(db.Integer, primary_key=True)
    nama       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    nik        = db.Column(db.String(20), unique=True, nullable=False)
    password   = db.Column(db.String(255), nullable=False)
    role       = db.Column(db.String(20), default='masyarakat')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    surats     = db.relationship('Surat', backref='user', lazy=True)
    pengaduans = db.relationship('Pengaduan', backref='user', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Surat(db.Model):
    __tablename__ = 'surats'
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    jenis_surat  = db.Column(db.String(100), nullable=False)
    keperluan    = db.Column(db.Text, nullable=False)
    file_ktp_url = db.Column(db.String(500))
    file_ktp_name= db.Column(db.String(200))
    status       = db.Column(db.String(30), default='menunggu')
    catatan_admin= db.Column(db.Text)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at   = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Pengaduan(db.Model):
    __tablename__ = 'pengaduans'
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    judul        = db.Column(db.String(200), nullable=False)
    kategori     = db.Column(db.String(100), nullable=False)
    deskripsi    = db.Column(db.Text, nullable=False)
    lokasi       = db.Column(db.String(200))
    file_foto_url= db.Column(db.String(500))
    file_foto_name=db.Column(db.String(200))
    status       = db.Column(db.String(30), default='diterima')
    tanggapan    = db.Column(db.Text)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
