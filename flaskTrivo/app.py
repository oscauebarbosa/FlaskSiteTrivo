from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/sitetrivo'
app.config['SECRET_KEY'] = '12345678'
db = SQLAlchemy(app)

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    nome_usuario = db.Column(db.String(255), nullable=False)

class Receita(db.Model):
    __tablename__ = 'receitas'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome_receita = db.Column(db.String(255), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    data = db.Column(db.Date, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    usuario = db.relationship('Usuario', backref=db.backref('receitas', lazy=True))

class Despesa(db.Model):
    __tablename__ = 'despesas'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    valor = db.Column(db.Float, nullable=False)
    data = db.Column(db.Date, nullable=False)
    nome_despesa = db.Column(db.String(255), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    usuario = db.relationship('Usuario', backref=db.backref('despesas', lazy=True))

@app.route('/', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        novo_usuario = Usuario(email=email, senha=senha, nome_usuario=nome)
        db.session.add(novo_usuario)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('registro.html')

@app.route('/inicio')
def inicio():
    totalReceita = 0
    totalDespesa = 0

    receitas = Receita.query.filter_by(usuario_id=session["usuario_id"])
    despesas = Despesa.query.filter_by(usuario_id=session["usuario_id"])

    for receita in receitas:
        totalReceita += receita.valor

    for despesa in despesas:
        totalDespesa += despesa.valor

    nome_usuario = None
    if 'usuario_id' in session:
        usuario_id = session['usuario_id']
        usuario = Usuario.query.get(usuario_id)
        if usuario:
            nome_usuario = usuario.nome_usuario

    return render_template('inicio.html', totalReceita=totalReceita, totalDespesa=totalDespesa, nome_usuario=nome_usuario)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        usuario = Usuario.query.filter_by(email=email, senha=senha).first()

        if usuario:
            session['usuario_id'] = usuario.id
            return redirect(url_for('inicio'))

    return render_template('login.html')

@app.route('/addreceitas', methods=['GET', 'POST'])
def addreceitas():
    if request.method == 'POST':
        if 'usuario_id' in session:
            usuario_id = session['usuario_id']
            nome_receita = request.form['nome_receita']
            data = request.form['data']
            valor_str = request.form['valor']
            valor = float(valor_str.replace('R$', '').replace('.', '').replace(',', '.'))  # Converter o valor para float

            nova_receita = Receita(nome_receita=nome_receita, valor=valor, data=data, usuario_id=usuario_id)
            db.session.add(nova_receita)
            db.session.commit()
        else:
            return redirect(url_for('login'))

    return render_template('AddReceitas.html')

@app.route('/adddespesas', methods=['GET', 'POST'])
def adddespesas():
    if request.method == 'POST':
        if 'usuario_id' in session:
            usuario_id = session['usuario_id']
            nome_despesa = request.form['nome_despesa']
            data = request.form['data']
            valor_str = request.form['valor']
            valor = float(valor_str.replace('R$', '').replace('.', '').replace(',', '.'))  # Converter o valor para float

            nova_despesa = Despesa(nome_despesa=nome_despesa, valor=valor, data=data, usuario_id=usuario_id)
            db.session.add(nova_despesa)
            db.session.commit()
        else:
            return redirect(url_for('login'))

    return render_template('AddDespesas.html')




@app.route('/geral')
def geral():
    nome_usuario = None
    if 'usuario_id' in session:
        usuario_id = session['usuario_id']
        usuario = Usuario.query.get(usuario_id)
        if usuario:
            nome_usuario = usuario.nome_usuario

    ultimas_receitas = Receita.query.filter_by(usuario_id=session["usuario_id"]).order_by(desc(Receita.data)).limit(5).all()
    ultimas_despesas = Despesa.query.filter_by(usuario_id=session["usuario_id"]).order_by(desc(Despesa.data)).limit(5).all()

    totalReceita = sum(receita.valor for receita in ultimas_receitas)
    totalDespesa = sum(despesa.valor for despesa in ultimas_despesas)

    return render_template('geral.html', ultimas_receitas=ultimas_receitas, ultimas_despesas=ultimas_despesas,
                           totalReceita=totalReceita, totalDespesa=totalDespesa, nome_usuario=nome_usuario)




@app.route('/logout')
def logout():
    if 'usuario_id' in session:
        session.pop('usuario_id')
    return redirect(url_for('login'));


if __name__ == '__main__':
    app.run(debug=True)
