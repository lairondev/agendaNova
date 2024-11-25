from flask import Flask, jsonify, request, render_template, redirect, url_for
from datetime import datetime
from models import Veiculo, Usuario, Agendamento, HistoricoMovimentacao, app, db



@app.route("/", methods=["POST","GET"])
def index():
    qtde_carros = Veiculo.query.filter_by(status="disponivel", localizacao_atual="parque").count()
    veiculos = Veiculo.query.filter_by(status="disponivel", localizacao_atual="parque").all()
    return render_template("index.html", qtde=qtde_carros, veiculos=veiculos)
    
    
    
@app.route("/cad-veiculo", methods=["POST", "GET"])
def cad_veiculo():
    if request.method == "POST":
        marca = request.form.get("marca")
        modelo = request.form.get("modelo")
        
        veiculo = Veiculo(marca=marca, modelo=modelo)
        db.session.add(veiculo)
        db.session.commit()
        
    return redirect("/")
    

# Rota para obter agendamentos para o FullCalendar
@app.route('/agendamento', methods=['GET'])
def get_agendamentos():
    agendamentos = Agendamento.query.all()
    eventos = [
        {
            'id': agendamento.id,
            'title': f"Evento {agendamento.id} - {agendamento.usuario.nome}",
            'start': agendamento.hora_saida.isoformat(),
            'end': agendamento.hora_retorno.isoformat(),
            'status': agendamento.status,
            'details': agendamento.detalhes
        }
        for agendamento in agendamentos
    ]
    return jsonify(eventos)

# Rota para criar um novo agendamento
@app.route('/agendamento', methods=['POST'])
def create_agendamento():
    
    if request.method == "POST":
        hora_saida = request.form.get("horaInicio")
        hora_retorno = request.form.get("horaFim")
        veiculo_id = request.form.get("id_veiculo")
        usuario_id = 1
        detalhes = request.form.get("detalhes")
        
        print(hora_saida)

        # Verificar veículos disponíveis
        veiculos_disponiveis = Veiculo.query.filter_by(status='disponível', localizacao_atual='parque').all()
        if veiculos_disponiveis:
            veiculo = veiculos_disponiveis[0]  # Seleciona o primeiro disponível
            veiculo.status = 'em_corrida'
            veiculo.localizacao_atual = 'em_transporte'
            agendamento = Agendamento(
                veiculo_id=veiculo.id,
                usuario_id=usuario_id,
                hora_saida=hora_saida,
                hora_retorno=hora_retorno,
                status="confirmado",
                detalhes=detalhes
            )
        else:
            agendamento = Agendamento(
                usuario_id=usuario_id,
                hora_saida=hora_saida,
                hora_retorno=hora_retorno,
                status='pendente',
                detalhes=detalhes
            )
    
        db.session.add(agendamento)
        db.session.commit()
        
        return redirect("/")

    return jsonify({'message': 'Agendamento criado com sucesso!', 'id': agendamento.id}), 201

# Rota para retornar veículo ao parque
@app.route('/api/veiculos/retorno/<int:veiculo_id>', methods=['POST'])
def retornar_veiculo(veiculo_id):
    veiculo = Veiculo.query.get_or_404(veiculo_id)
    veiculo.status = 'disponível'
    veiculo.localizacao_atual = 'parque'
    db.session.commit()
    return jsonify({'message': 'Veículo retornado ao parque com sucesso!'}), 200



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
