from flask import Flask, request, send_file, jsonify
from generador import generar_constancia
from pdfco import convertir_a_pdf_pdfco   # 👈 IMPORT NUEVO
import uuid
import os

app = Flask(__name__)

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

    if not id_cif or not rfc:
        return jsonify({
            "error": "El id_cif y el rfc son obligatorios"
        }), 400

    rfc = rfc.strip().upper()

    # Render solo permite escritura en /tmp
    nombre_archivo = f"{rfc}.docx"  # 👈 RFC COMO NOMBRE
    salida = f"/tmp/{nombre_archivo}"

    try:
        generar_constancia(
            plantilla="plantilla.docx",
            salida=salida,
            id_cif=id_cif.strip(),
            rfc=rfc
        )

        salida_pdf = convertir_a_pdf_pdfco(salida)

        return send_file(
            salida_pdf,
            as_attachment=True,
            download_name=f"{rfc}.pdf",
            mimetype="application/pdf"
        )

    except Exception as e:
        return jsonify({
            "error": "Error al generar la constancia",
            "detalle": str(e)
        }), 500

    finally:
        # Limpieza opcional (Render borra /tmp solo)
        if os.path.exists(salida):
            pass


# ===================== MAIN =====================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)




