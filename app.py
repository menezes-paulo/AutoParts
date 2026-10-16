from flask import Flask, request, render_template, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import mysql.connector
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
banco = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="autoparts"
)   


def criar_usuario(nome, usuario, senha):
    senha_hash = generate_password_hash(senha)
    cursor = banco.cursor()
    sql = """INSERT INTO usuarios (nome,usuario, senha) VALUES (%s, %s, %s)"""
    valores = (nome, usuario, senha_hash)
    cursor.execute(sql, valores)
    banco.commit()

   
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if existe_usuario() > 0:
        return "Cadastro bloqueado."
    if request.method == "POST":
        nome = request.form["nome"]
        usuario = request.form["usuario"]
        senha = request.form["senha"]
        if not nome or not usuario or not senha:
            return "Preencha todos os campos."
        criar_usuario(nome, usuario, senha)
        return "Administrador criado com sucesso!"
    return render_template("cadastro.html")

def buscar_usuario(usuario):
    cursor = banco.cursor()
    sql = """
        SELECT usuario, senha
        FROM usuarios
        WHERE usuario = %s
    """
    cursor.execute(sql, (usuario,))
    resultado = cursor.fetchone()
    return resultado

@app.route("/login", methods=["GET", "POST"])
def login():
    if "usuario" in session:
        return redirect("/cadastrar-veiculo")
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]
        resultado = buscar_usuario(usuario)
        if resultado is None:
            return "Usuario ou senha inválidos."
        senha_hash = resultado[1]
        if not check_password_hash(senha_hash, senha):
            return "Usuário ou senha inválidos."
        session["usuario"] = usuario
        return redirect("/cadastrar-veiculo")
    return render_template("login.html")

@app.route("/logout")
def logout():
    if "usuario" in session:
        session.pop("usuario", None)
    return redirect("/login")


def inserir_veiculo(modelo, ano, versao, id_motor):
    cursor = banco.cursor()
    sql = """INSERT INTO veiculos (modelo, ano, versao, id_motor) VALUES (%s, %s, %s, %s)"""
    valores = (modelo, ano, versao, id_motor)
    cursor.execute(sql, valores)
    banco.commit()
    cursor.close()


@app.route("/cadastrar-motor", methods=["GET", "POST"])
def cadastrar_motor():
    if "usuario" not in session:
        return redirect("/login")
    if request.method == "POST":
        nome = request.form["nome"].strip()
        codigo = request.form.get("codigo", "").strip()
        if not codigo:
            return "Informe o código do motor."
        if not nome:
            return "Informe o nome do motor."
        cursor = banco.cursor()
        try:
            sql = """INSERT INTO motores (nome, codigo) VALUES (%s, %s)"""
            cursor.execute(sql, (nome, codigo))
            banco.commit()
        except mysql.connector.IntegrityError:
            banco.rollback()
            return "Esse código de motor já está cadastrado."
        finally:
            cursor.close()
        return redirect("/cadastrar-motor")
    return render_template("cadastrar-motor.html")


@app.route("/")
def inicio():
    return "AutoParts funcionando"


@app.route("/cadastrar-veiculo", methods=["GET"])
def pagina_cadastrar_veiculo():
    if "usuario" not in session:
        return redirect("/login")
    cursor = banco.cursor(dictionary=True)
    cursor.execute("SELECT id, nome, codigo FROM motores ORDER BY nome")
    motores = cursor.fetchall()
    cursor.close()
    return render_template("cadastrar-veiculo.html", motores=motores)



@app.route("/cadastrar-veiculo", methods=["POST"])
def cadastrar_veiculo():
    if "usuario" not in session:
        return redirect("/login")
    modelo = request.form["modelo"]
    ano = request.form["ano"]
    versao = request.form["versao"]
    id_motor = request.form["id_motor"]
    inserir_veiculo(modelo, ano, versao, id_motor)
    return redirect("/cadastrar-veiculo")


def existe_usuario():
    cursor = banco.cursor()
    sql = """SELECT COUNT(*) FROM usuarios"""
    cursor.execute(sql)
    resultado = cursor.fetchone()
    return resultado[0]



@app.route("/cadastrar-peca", methods=["GET", "POST"])
def cadastrar_peca():
    if "usuario" not in session:
        return redirect("/login")
    if request.method == "POST":
        titulo = request.form["titulo"]
        codigo_oem = request.form["codigo_oem"]
        marca = request.form["marca"]
        preco = request.form["preco"]
        motores = request.form.getlist("motores")
        inserir_peca(titulo, codigo_oem, marca, preco, motores)
        return redirect("/cadastrar-peca")
    cursor = banco.cursor(dictionary=True)
    sql = """SELECT id, nome, codigo FROM motores ORDER BY nome"""
    cursor.execute(sql)
    motores = cursor.fetchall()
    cursor.close()
    return render_template("cadastrar-peca.html", motores=motores)




@app.route("/cadastrar-peca/anos/<modelo>")
def buscar_anos(modelo):
    cursor = banco.cursor(dictionary=True)
    sql = """SELECT DISTINCT ano FROM veiculos WHERE modelo = %s ORDER BY ano"""
    cursor.execute(sql, (modelo,))
    anos = cursor.fetchall()
    return anos

@app.route("/cadastrar-peca/veiculos/<modelo>/<int:ano>")
def buscar_veiculos(modelo, ano):
    cursor = banco.cursor(dictionary=True)

    sql = """
        SELECT id, versao, motorizacao
        FROM veiculos
        WHERE modelo = %s
        AND ano = %s
        ORDER BY versao
    """

    cursor.execute(sql, (modelo, ano))
    veiculos = cursor.fetchall()

    return veiculos



def inserir_peca(titulo, codigo_oem, marca, preco, motores):
    cursor = banco.cursor()
    sql = """INSERT INTO pecas (titulo, codigo_oem, marca, preco) VALUES (%s, %s, %s, %s)"""
    valores = (titulo, codigo_oem, marca, preco)
    cursor.execute(sql, valores)
    id_peca = cursor.lastrowid
    for id_motor in motores:
        sql_aplicacao = """INSERT INTO aplicacoes (id_peca, id_motor) VALUES (%s, %s)"""
        valores_aplicacao = (id_peca, id_motor)
        cursor.execute(sql_aplicacao, valores_aplicacao)
    banco.commit()
    cursor.close()

@app.route("/consultar-pecas", methods=["GET", "POST"])
def consultar_pecas():
    if "usuario" not in session:
        return redirect("/login")
    cursor = banco.cursor(dictionary=True)
    cursor.execute("""SELECT DISTINCT modelo FROM veiculos ORDER BY modelo""")
    modelos = cursor.fetchall()
    pecas = []
    veiculo_selecionado = None
    if request.method == "POST":
        modelo = request.form["modelo"]
        ano = request.form["ano"]
        versao = request.form["versao"]
        sql = """SELECT p.titulo, p.codigo_oem, p.marca, p.preco
            FROM veiculos v JOIN aplicacoes a ON a.id_motor = v.id_motor JOIN pecas p ON p.id = a.id_peca WHERE v.modelo = %s AND v.ano = %s AND v.versao = %s ORDER BY p.titulo"""
        cursor.execute(sql, (modelo, ano, versao))
        pecas = cursor.fetchall()
        veiculo_selecionado = {
            "modelo": modelo,
            "ano": ano,
            "versao": versao
        }
    cursor.close()
    return render_template(
        "consultar-pecas.html",
        modelos=modelos,
        pecas=pecas,
        veiculo_selecionado=veiculo_selecionado
    )

@app.route("/consultar-pecas/anos/<modelo>")
def consultar_anos(modelo):
    cursor = banco.cursor(dictionary=True)
    sql = """SELECT DISTINCT ano FROM veiculos WHERE modelo = %s ORDER BY ano"""
    cursor.execute(sql, (modelo,))
    anos = cursor.fetchall()
    cursor.close()
    return anos


@app.route("/consultar-pecas/versoes/<modelo>/<int:ano>")
def consultar_versoes(modelo, ano):
    cursor = banco.cursor(dictionary=True)
    sql = """SELECT id, versao FROM veiculos WHERE modelo = %s AND ano = %s ORDER BY versao"""
    cursor.execute(sql, (modelo, ano))
    versoes = cursor.fetchall()
    cursor.close()
    return versoes

if __name__ == "__main__":
    app.run(debug=True)


