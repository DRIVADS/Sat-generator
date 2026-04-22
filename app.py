from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from generador import generar_constancia
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)

# ✅ HABILITAR CORS (permite peticiones desde tu HTML)
CORS(app)

CODIGO_SECRETO = "LILIYROSY"

# ===================== CONEXIÓN A BD =====================
def get_conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


# ===================== RUTA PRINCIPAL =====================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "ok",
        "mensaje": "API activa con base de datos 🚀"
    })


# ===================== GENERAR CONSTANCIA =====================
@app.route("/generar", methods=["POST"])
def generar():
    id_cif = request.form.get("id_cif")
    rfc = request.form.get("rfc")
    codigo = request.form.get("codigo")

    if not id_cif or not rfc or not codigo:
        return jsonify({
            "error": "El id_cif, rfc y código son obligatorios"
        }), 400

    if codigo != CODIGO_SECRETO:
        return jsonify({
            "error": "Código inválido"
        }), 403

    rfc = rfc.strip().upper()
    nombre_archivo = f"{rfc}.docx"
    salida = f"/tmp/{nombre_archivo}"

    try:
        generar_constancia(
            plantilla="plantilla.docx",
            salida=salida,
            id_cif=id_cif.strip(),
            rfc=rfc
        )

        return send_file(
            salida,
            as_attachment=True,
            download_name=nombre_archivo,
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    except Exception as e:
        return jsonify({
            "error": "Error al generar la constancia",
            "detalle": str(e)
        }), 500


# ===================== CREAR SOCIO =====================
@app.route("/api/socios", methods=["POST"])
def crear_socio():
    data = request.json

    try:
        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO socios (clave, usuario, nombre, apellido_pa, saldo)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            data["clave"],
            data["usuario"],
            data["nombre"],
            data["apellido_pa"],
            data["saldo"]
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"mensaje": "Socio creado correctamente"})

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        return jsonify({"error": str(e)}), 500


# ===================== LISTAR SOCIOS =====================
@app.route("/api/socios", methods=["GET"])
def listar_socios():
    try:
        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM socios")
        datos = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(datos)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===================== RECARGA =====================
@app.route("/api/recargas", methods=["POST"])
def crear_recarga():
    data = request.json

    try:
        conn = get_conn()
        cursor = conn.cursor()

        fecha = datetime.now().date()
        hora = datetime.now().time()

        # Insertar recarga
        cursor.execute("""
            INSERT INTO recargas (clave_socio, recarga, fecha, hora)
            VALUES (%s, %s, %s, %s)
        """, (
            data["clave_socio"],
            data["recarga"],
            fecha,
            hora
        ))

        # Actualizar saldo automáticamente
        cursor.execute("""
            UPDATE socios
            SET saldo = saldo + %s
            WHERE clave = %s
        """, (
            data["recarga"],
            data["clave_socio"]
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"mensaje": "Recarga aplicada y saldo actualizado 💰"})

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        return jsonify({"error": str(e)}), 500


# ===================== REGISTRO =====================
@app.route("/api/registros", methods=["POST"])
def crear_registro():
    data = request.json

    try:
        conn = get_conn()
        cursor = conn.cursor()

        fecha = datetime.now().date()
        hora = datetime.now().time()

        cursor.execute("""
            INSERT INTO registros (clave_socio, rfc, fecha, hora)
            VALUES (%s, %s, %s, %s)
        """, (
            data["clave_socio"],
            data["rfc"],
            fecha,
            hora
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"mensaje": "Registro guardado 📄"})

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        return jsonify({"error": str(e)}), 500


# ===================== MAIN =====================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
