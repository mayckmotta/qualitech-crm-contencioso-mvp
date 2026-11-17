import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from models import db, Usuario, Demanda, Tratativa

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-desenvolvimento-qualitech')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///qualitech_crm.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # Limite de 5 MB (RNF02)

EXTENSOES_PERMITIDAS = {'pdf', 'jpg', 'jpeg', 'png'}

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

def arquivo_permitido(nome_arquivo):
    return '.' in nome_arquivo and nome_arquivo.rsplit('.', 1)[1].lower() in EXTENSOES_PERMITIDAS

@app.route('/')
@login_required
def fila_unica():
    canal = request.args.get('canal', '')
    status = request.args.get('status', '')
    protocolo = request.args.get('protocolo', '').strip()

    consulta = Demanda.query.filter(Demanda.status != 'Concluído')
    if canal:
        consulta = consulta.filter_by(canal=canal)
    if status:
        consulta = consulta.filter_by(status=status)
    if protocolo:
        consulta = consulta.filter(Demanda.protocolo.ilike(f'%{protocolo}%'))

    demandas = consulta.order_by(Demanda.data_limite.asc()).all()
    return render_template('fila.html', demandas=demandas)

@app.route('/demanda/nova', methods=['GET', 'POST'])
@login_required
def nova_demanda():
    if request.method == 'POST':
        protocolo = request.form.get('protocolo', '').strip()
        if Demanda.query.filter_by(protocolo=protocolo).first():
            flash('Protocolo já cadastrado no sistema. Verifique o número informado.', 'danger')
            return render_template('formulario.html')

        demanda = Demanda(
            protocolo=protocolo,
            canal=request.form.get('canal'),
            reclamante=request.form.get('reclamante'),
            cpf=request.form.get('cpf'),
            data_limite=datetime.strptime(request.form.get('data_limite'), '%Y-%m-%dT%H:%M'),
            resumo=request.form.get('resumo'),
            status='Aberto'
        )
        db.session.add(demanda)
        db.session.commit()
        flash('Demanda registrada com sucesso na fila única.', 'success')
        return redirect(url_for('fila_unica'))
    return render_template('formulario.html')

@app.route('/demanda/<int:demanda_id>/tratar', methods=['POST'])
@login_required
def registrar_tratativa(demanda_id):
    demanda = Demanda.query.get_or_404(demanda_id)
    novo_status = request.form.get('status')
    descricao = request.form.get('descricao', '').strip()

    if novo_status == 'Concluído' and not descricao:
        flash('O parecer final é obrigatório para encerrar a demanda.', 'danger')
        return redirect(url_for('fila_unica'))

    nome_anexo = None
    arquivo = request.files.get('anexo')
    if arquivo and arquivo.filename:
        if not arquivo_permitido(arquivo.filename):
            flash('Formato de arquivo inválido. Envie apenas PDF, JPG ou PNG.', 'danger')
            return redirect(url_for('fila_unica'))
        nome_anexo = secure_filename(arquivo.filename)

    tratativa = Tratativa(
        demanda_id=demanda.id,
        autor=current_user.nome,
        descricao=descricao,
        status_registrado=novo_status,
        anexo_nome=nome_anexo
    )
    demanda.status = novo_status
    if novo_status == 'Concluído':
        demanda.parecer_final = descricao

    db.session.add(tratativa)
    db.session.commit()
    flash(f'Demanda {demanda.protocolo} atualizada com sucesso.', 'success')
    return redirect(url_for('fila_unica'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False)
    
