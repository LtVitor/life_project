from flask import Flask, request, render_template, redirect
import psycopg2
from datetime import datetime
import json
from datetime import datetime, time

app = Flask(__name__)

# Conexão fixa com os dados que você forneceu
DATABASE_URL = "dbname=cecilia user=cecilia_user password=b4amcQtpzs19yJkxGmywv80QKgV1Atll host=dpg-cvrac5juibrs73dnknig-a port=5432"

def conectar():
    return psycopg2.connect(DATABASE_URL)

# Criação das tabelas se não existirem
def criar_tabelas():
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS rotina (
            id SERIAL PRIMARY KEY,
            data_envio TIMESTAMP,
            acordou TIME,
            soneca1_inicio TIME,
            soneca1_fim TIME,
            almoco TIME,
            soneca2_inicio TIME,
            soneca2_fim TIME,
            soneca3_inicio TIME,
            soneca3_fim TIME,
            jantar TIME,
            banho TIME,
            mamar TIME,
            sono_noturno TIME
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS despertares (
            id SERIAL PRIMARY KEY,
            rotina_id INTEGER REFERENCES rotina(id),
            horario TIME,
            observacao TEXT
        );
    """)

    conn.commit()
    cur.close()
    conn.close()

criar_tabelas()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    dados = {
        'data_envio': datetime.now(),
        'acordou': request.form.get('acordou') or None,
        'soneca1_inicio': request.form.get('soneca1_inicio') or None,
        'soneca1_fim': request.form.get('soneca1_fim') or None,
        'almoco': request.form.get('almoco') or None,
        'soneca2_inicio': request.form.get('soneca2_inicio') or None,
        'soneca2_fim': request.form.get('soneca2_fim') or None,
        'soneca3_inicio': request.form.get('soneca3_inicio') or None,
        'soneca3_fim': request.form.get('soneca3_fim') or None,
        'jantar': request.form.get('jantar') or None,
        'banho': request.form.get('banho') or None,
        'mamar': request.form.get('mamar') or None,
        'sono_noturno': request.form.get('sono_noturno') or None,
    }

    despertares = []
    for i in range(1, 11):  # Suporte para até 10 despertares
        horario = request.form.get(f'despertares[{i}][horario]')
        obs = request.form.get(f'despertares[{i}][observacao]')
        if horario or obs:
            despertares.append((horario or None, obs or None))

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO rotina (
            data_envio, acordou, soneca1_inicio, soneca1_fim, almoco,
            soneca2_inicio, soneca2_fim, soneca3_inicio, soneca3_fim,
            jantar, banho, mamar, sono_noturno
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
    """, tuple(dados.values()))
    rotina_id = cur.fetchone()[0]

    for horario, observacao in despertares:
        cur.execute("""
            INSERT INTO despertares (rotina_id, horario, observacao)
            VALUES (%s, %s, %s);
        """, (rotina_id, horario, observacao))

    conn.commit()
    cur.close()
    conn.close()

    return redirect('/')
    
@app.route('/registros')
def registros():
    conn = psycopg2.connect(
        host="dpg-cvrac5juibrs73dnknig-a",
        database="cecilia",
        user="cecilia_user",
        password="b4amcQtpzs19yJkxGmywv80QKgV1Atll"
    )
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT data_envio::date FROM rotina ORDER BY data_envio DESC")
    datas = [row[0].strftime('%Y-%m-%d') for row in cur.fetchall()]
    cur.close()
    conn.close()
    return render_template("registros.html", datas=datas)
    
@app.route('/registro/<data>')
def registro_por_data(data):
    conn = psycopg2.connect(
        host="dpg-cvrac5juibrs73dnknig-a",
        database="cecilia",
        user="cecilia_user",
        password="b4amcQtpzs19yJkxGmywv80QKgV1Atll"
    )
    cur = conn.cursor()
    cur.execute("SELECT * FROM rotina WHERE data_envio::date = %s", (data,))
    colnames = [desc[0] for desc in cur.description]
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row:
        registro = dict(zip(colnames, row))
    else:
        registro = None

    return render_template("registro_detalhado.html", data=data, registro=registro)

@app.route('/graficos')
def graficos():
    conn = psycopg2.connect(
        host="dpg-cvrac5juibrs73dnknig-a",
        database="cecilia",
        user="cecilia_user",
        password="b4amcQtpzs19yJkxGmywv80QKgV1Atll"
    )
    cur = conn.cursor()
    cur.execute("SELECT * FROM rotina ORDER BY data_envio")
    colnames = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    registros = [dict(zip(colnames, row)) for row in rows]
    cur.close()
    conn.close()

    return render_template("graficos.html", registros=registros)



if __name__ == '__main__':
    app.run(debug=True)
