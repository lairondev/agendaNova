from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agendamentos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de Veículo
class Veiculo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    total = db.Column(db.Integer, default=2)  # Coluna total de veículos (valor padrão 2)
    disponivel = db.Column(db.Integer, nullable=False, default=2)  # Coluna de veículos disponíveis

# Modelo de Agendamento
class Agendamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    veiculo_id = db.Column(db.Integer, db.ForeignKey('veiculo.id'), nullable=False)
    veiculo = db.relationship('Veiculo', backref=db.backref('agendamentos', lazy=True))
    detalhes = db.Column(db.String(200), nullable=False)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)

@app.route("/")
def index():
    veiculos = Veiculo.query.first()
    return render_template("index.html", veiculos_disponiveis=veiculos.total)

# Rota para contar veículos disponíveis
@app.route("/api/veiculos/contagem")
def veiculos_contagem():
    veiculos = Veiculo.query.all()
    total_disponiveis = sum([veiculo.disponivel for veiculo in veiculos])
    return jsonify({"disponiveis": total_disponiveis})

# Rota para listar os veículos disponíveis
@app.route("/api/veiculos")
def veiculos():
    veiculos = Veiculo.query.filter_by(disponivel=True).all()
    return jsonify([{
        "id": veiculo.id,
        "nome": veiculo.nome
    } for veiculo in veiculos])

# Rota para buscar e salvar os agendamentos
@app.route("/api/agendamentos", methods=["GET", "POST"])
def agendamentos():
    if request.method == "GET":
        eventos = Agendamento.query.all()
        return jsonify([{
            "id": evento.id,
            "title": f"{evento.veiculo.nome} - {evento.detalhes}",
            "start": evento.start.isoformat(),
            "end": evento.end.isoformat()
        } for evento in eventos])

    if request.method == "POST":
        data = request.json
        start = datetime.fromisoformat(data['start'])
        end = datetime.fromisoformat(data['end'])
        
        # Verifica se a data de agendamento é o dia atual
        if start.date() == datetime.today().date():
            # Decrementa a disponibilidade do veículo
            veiculo = Veiculo.query.get(data['veiculo_id'])
            if veiculo and veiculo.disponivel > 0:
                veiculo.disponivel -= 1
                db.session.commit()
            else:
                return jsonify({"error": "Veículo não disponível."}), 400
        
        novo_evento = Agendamento(
            veiculo_id=data['veiculo_id'],
            detalhes=data['detalhes'],
            start=start,
            end=end
        )
        db.session.add(novo_evento)
        db.session.commit()
        
        return jsonify({
            "data": {
                "id": novo_evento.id,
                "title": f"{novo_evento.veiculo.nome} - {novo_evento.detalhes}",
                "start": novo_evento.start.isoformat(),
                "end": novo_evento.end.isoformat()
            }
        }), 201

# Rota para marcar o veículo como livre novamente
@app.route("/api/veiculo/<int:id>/liberar", methods=["POST"])
def liberar_veiculo(id):
    veiculo = Veiculo.query.get(id)
    if veiculo:
        veiculo.disponivel = veiculo.total  # Restaura a disponibilidade total
        db.session.commit()
        return jsonify({"message": "Veículo liberado."}), 200
    return jsonify({"error": "Veículo não encontrado."}), 404


@app.route('/api/veiculos/contagem')
def get_veiculos_disponiveis():
    # Lógica para contar os veículos disponíveis
    veiculos_disponiveis = contar_veiculos_disponiveis()  # Você precisa implementar essa função
    return jsonify({'disponiveis': veiculos_disponiveis})



# Criação do banco de dados
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
