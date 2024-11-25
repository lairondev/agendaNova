from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transportes.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://lairondev:Dontcare_30@localhost/cehab_online'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Veiculo(db.Model):
    __tablename__ = 'veiculos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='disponível')  # disponível, em_corrida, em_manutencao
    localizacao_atual = db.Column(db.String(20), default='parque')  # parque ou em_transporte

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

class Agendamento(db.Model):
    __tablename__ = 'agendamentos'
    id = db.Column(db.Integer, primary_key=True)
    veiculo_id = db.Column(db.Integer, db.ForeignKey('veiculos.id'), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    hora_saida = db.Column(db.DateTime, nullable=False)
    hora_retorno = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pendente')  # pendente, confirmado, finalizado
    detalhes = db.Column(db.Text, nullable=True)

    veiculo = db.relationship('Veiculo', backref='agendamentos')
    usuario = db.relationship('Usuario', backref='agendamentos')

class HistoricoMovimentacao(db.Model):
    __tablename__ = 'historico_movimentacoes'
    id = db.Column(db.Integer, primary_key=True)
    veiculo_id = db.Column(db.Integer, db.ForeignKey('veiculos.id'), nullable=False)
    tipo_movimentacao = db.Column(db.String(20))  # saida, retorno
    hora_movimentacao = db.Column(db.DateTime, default=datetime.utcnow)
    agendamento_id = db.Column(db.Integer, db.ForeignKey('agendamentos.id'), nullable=True)

    veiculo = db.relationship('Veiculo', backref='movimentacoes')
    agendamento = db.relationship('Agendamento', backref='movimentacoes')
