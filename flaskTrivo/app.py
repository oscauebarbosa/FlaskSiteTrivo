from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def inicio():
    return render_template('Inicio.html')

@app.route('/geral')
def geral():
    return render_template('Geral.html')

@app.route('/addreceitas')
def addreceitas():
    return render_template('AddReceitas.html')

@app.route('/adddespesas')
def adddespesas():
    return render_template('AddDespesas.html')



if __name__ == '__main__':
    app.run(debug=True)