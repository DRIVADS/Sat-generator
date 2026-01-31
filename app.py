from flask import Flask, request, send_file, jsonify
from generador import generar_constancia
import os

app = Flask(__name__)

CODIGO_SECRETO = "LILIYROSY"  # 👈 CÓDIGO REQUERIDO


# ===================== RUTA PRINCIPAL =====================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "ok",
        "mensaje": "API Generador de Constancia SAT activa"
    })


# ===================== GENERAR CONSTANCIA =====================
@app.route("/generar", methods=["POST"])
def generar():
    id_cif = request.form.get("id_cif")
    rfc = request.form.get("rfc")
    codigo = request.form.get("codigo")  # 👈 NUEVO CAMPO

    # Validar campos obligatorios
    if not id_cif or not rfc or not codigo:
        return jsonify({
            "error": "El id_cif, rfc y código son obligatorios"
        }), 400

    # Validar código secreto
    if codigo != CODIGO_SECRETO:
        return jsonify({
            "error": "Código inválido"
        }), 403

    rfc = rfc.strip().upper()

    # Render solo permite escritura en /tmp
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

    finally:
        if os.path.exists(salida):
            pass


# ===================== MAIN =====================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

