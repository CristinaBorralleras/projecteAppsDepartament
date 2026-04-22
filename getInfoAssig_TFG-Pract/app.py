from flask import Flask, render_template, request, send_file
import os
from io import BytesIO
from processador import generar_info_pdi

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

INPUT_EXCEL = os.path.join(UPLOAD_FOLDER, "entrada.xlsx")
OUTPUT_EXCEL = os.path.join(UPLOAD_FOLDER, "info_PDI.xlsx")


@app.route("/", methods=["GET", "POST"])
def load():
    if request.method == "POST":
        f = request.files.get("excel")

        if not f or not f.filename.lower().endswith(".xlsx"):
            return render_template(
                "load.html",
                error="Cal seleccionar un fitxer Excel (.xlsx)"
            )

        # Guardem només l'entrada (si vols, també la podries fer en memòria)
        input_path = os.path.join(UPLOAD_FOLDER, "entrada.xlsx")
        f.save(input_path)

        # ✅ Generem el dataframe
        df = generar_info_pdi(input_path)

        # ✅ Excel EN MEMÒRIA
        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)

        # ✅ Descarreguem directament
        return send_file(
            output,
            as_attachment=True,
            download_name="info_PDI.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    return render_template("load.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)