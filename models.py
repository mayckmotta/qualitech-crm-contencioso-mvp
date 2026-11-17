from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(256), nullable=False)
    perfil = db.Column(db.String(20), nullable=False, default='Analista')

    def definir_senha(self, senha):
        self.senha_hash = generate_password_hash(senha, method='pbkdf2:sha256')

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

class Demanda(db.Model):
    __tablename__ = 'demandas'
    id = db.Column(db.Integer, primary_key=True)
    protocolo = db.Column(db.String(50), unique=True, nullable=False)
    canal = db.Column(db.String(50), nullable=False)
    reclamante = db.Column(db.String(120), nullable=False)
    cpf = db.Column(db.String(14), nullable=False)
    data_limite = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(30), nullable=False, default='Aberto')
    resumo = db.Column(db.Text, nullable=False)
    parecer_final = db.Column(db.Text, nullable=True)
    tratativas = db.relationship('Tratativa', backref='demanda', lazy=True)

    def calcular_sla(self):
        agora = datetime.now()
        if self.data_limite < agora:
            return 'Vencido'
        elif self.data_limite.date() == agora.date():
            return 'Vence hoje'
        return 'No prazo'

class Tratativa(db.Model):
    __tablename__ = 'tratativas'
    id = db.Column(db.Integer, primary_key=True)
    demanda_id = db.Column(db.Integer, db.ForeignKey('demandas.id'), nullable=False)
    autor = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    status_registrado = db.Column(db.String(30), nullable=False)
    anexo_nome = db.Column(db.String(200), nullable=True)
    criado_em = db.Column(db.DateTime, default=datetime.now)
