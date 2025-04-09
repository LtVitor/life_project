from flask import Flask, request, render_template, redirect
from datetime import datetime
import psycopg2
import os

app = Flask(__name__)

# Conexão com o PostgreSQL (Render ou local)
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)
cursor = conn.cursor()

# Criação das tabelas se não existirem
cursor.execute('''
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
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS despertares (
    id SERIAL PRIMARY KEY,
    rotina_id INTEGER REFERENCES rotina(id),
    horario TIME,
    observacao TEXT
);
''')
conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    data_envio = datetime.now()
    campos = ['acordou', 'soneca1_inicio', 'soneca1_fim', 'almoco', 'soneca2_inicio', 'soneca2_fim',
              'soneca3_inicio', 'soneca3_fim', 'jantar', 'banho', 'mamar', 'sono_noturno']
    valores = [request.form.get(c) or None for c in campos]

    cursor.execute(f'''
        INSERT INTO rotina (data_envio, {', '.join(campos)})
        VALUES (%s, {', '.join(['%s'] * len(campos))}) RETURNING id
    ''', [data_envio] + valores)
    rotina_id = cursor.fetchone()[0]

    horarios = request.form.getlist('despertar_horario[]')
    observacoes = request.form.getlist('despertar_obs[]')
    for h, o in zip(horarios, observacoes):
        if h:
            cursor.execute('''
                INSERT INTO despertares (rotina_id, horario, observacao)
                VALUES (%s, %s, %s)
            ''', (rotina_id, h, o or ''))

    conn.commit()
    return redirect('/')

@app.route('/registros')
def registros():
    cursor.execute("SELECT * FROM rotina ORDER BY data_envio DESC LIMIT 7")
    rows = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]
    registros = [dict(zip(colnames, row)) for row in rows]

    def duracao(inicio, fim):
        if not inicio or not fim:
            return 0
        t1 = datetime.strptime(str(inicio), '%H:%M:%S')
        t2 = datetime.strptime(str(fim), '%H:%M:%S')
        return int((t2 - t1).total_seconds() // 60) % (24 * 60)

    datas = [r['data_envio'].strftime('%d/%m') for r in registros]
    s1 = [duracao(r['soneca1_inicio'], r['soneca1_fim']) for r in registros]
    s2 = [duracao(r['soneca2_inicio'], r['soneca2_fim']) for r in registros]
    s3 = [duracao(r['soneca3_inicio'], r['soneca3_fim']) for r in registros]

    return render_template('registros.html', registros=registros, datas=datas,
                           soneca1_duracoes=s1, soneca2_duracoes=s2, soneca3_duracoes=s3)

if __name__ == '__main__':
    app.run(debug=True)
