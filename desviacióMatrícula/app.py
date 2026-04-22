import os
from flask import (
    Flask, render_template, request, send_file,
    redirect, url_for, send_from_directory
)

from io import BytesIO
import zipfile
import pandas as pd

from desviacionsMatrícula import (
    crea_diccionari_codis,
    processa_csv,
    generaFitxers,
    agruparSubgrupsCompartides
)

app = Flask(__name__)
app.secret_key = "matricula-desviacions"

UPLOADS = "uploads" 
OUTPUTS_FOLDER = "output"
CODIS_FILE = os.path.join(UPLOADS, "codis_compartides.csv")
MATRICULA_FILE = os.path.join(UPLOADS, "matriculats.csv")

os.makedirs(UPLOADS, exist_ok=True) 
os.makedirs(OUTPUTS_FOLDER, exist_ok=True)

# ---------- PAS 1: CODIS COMPARTIDES ----------

@app.route("/", methods=["GET", "POST"])
def load_codis():
    error = request.args.get("error")

    if request.method == "POST":
        action = request.form.get("action")

        if action == "skip_codis":
            # No cal fitxer de codis
            if os.path.exists(CODIS_FILE):
                os.remove(CODIS_FILE)
            return redirect(url_for("load_matricula"))

        if action == "use_last":
            if not os.path.exists(CODIS_FILE):
                error = "No hi ha cap fitxer de codis carregat prèviament."
            else:
                return redirect(url_for("load_matricula"))

        if action == "upload":
            file = request.files.get("codis_file")
            if not file or file.filename == "":
                error = "No s'ha seleccionat cap fitxer."
            elif not file.filename.lower().endswith(".csv"):
                error = "El fitxer ha de ser CSV."
            else:
                file.save(CODIS_FILE)
                return redirect(url_for("load_matricula"))

    return render_template(
        "load.html",
        page_title="Carregar codis compartits",
        heading="Carregar fitxer de Codis compartits (CSV)",
        description=(
            "Pots carregar un fitxer de codis compartits, reutilitzar l’últim "
            "o continuar sense codis si no hi ha assignatures compartides."
        ),
        field_name="codis_file",
        has_last=os.path.exists(CODIS_FILE),
        allow_skip=True,   
        error=error
    )


# ---------- PAS 2: MATRÍCULA ----------

@app.route("/matricula", methods=["GET", "POST"])
def load_matricula():
    error = None

    if request.method == "POST":
        action = request.form.get("action")

        if action == "use_last":
            if not os.path.exists(MATRICULA_FILE):
                error = "No hi ha cap fitxer de matrícula carregat prèviament."
            else:
                return redirect(url_for("executa"))

        if action == "upload":
            file = request.files.get("matricula_file")
            if not file or file.filename == "":
                error = "No s'ha seleccionat cap fitxer."
            elif not file.filename.lower().endswith(".csv"):
                error = "El fitxer ha de ser CSV."
            else:
                file.save(MATRICULA_FILE)
                return redirect(url_for("executa"))

    return render_template(
        "load.html",
        page_title="Carregar matrícula",
        heading="Carregar fitxer de Matrícules (CSV)",
        description="Cal carregar o reutilitzar el fitxer de matrícula",
        field_name="matricula_file",
        has_last=os.path.exists(MATRICULA_FILE),
        allow_skip=False,   
        error=error
    )




# ---------- EXECUCIÓ ----------

@app.route("/executa")
def executa():
    try:
        # ✅ Netejar output abans de generar nous resultats
        for f in os.listdir(OUTPUTS_FOLDER):
            path = os.path.join(OUTPUTS_FOLDER, f)
            if os.path.isfile(path):
                os.remove(path)

        dicCodis = crea_diccionari_codis(CODIS_FILE)

        grups, subgrups, estandard, estandardCorrectes = processa_csv(
            MATRICULA_FILE, dicCodis
        )

        generaFitxers(
            os.path.join(OUTPUTS_FOLDER, "desviacions.xlsx"),
            os.path.join(OUTPUTS_FOLDER, "correctes.xlsx"),
            grups, subgrups, estandard, estandardCorrectes
        )

        if dicCodis:
            grups2, subgrups2 = agruparSubgrupsCompartides(grups, subgrups)
            generaFitxers(
                os.path.join(OUTPUTS_FOLDER, "desviacions_agrupantCompartides.xlsx"),
                os.path.join(OUTPUTS_FOLDER, "correctes_agrupantCompartides.xlsx"),
                grups2, subgrups2, estandard, estandardCorrectes
            )

        return redirect(url_for("resultats"))

    except Exception as e:
        return redirect(url_for("load_codis", error=str(e)))


# -------- VIEW FILE ---------------


PREVIEW_ROWS = 200

@app.route("/preview/<filename>")
def preview_file(filename):
    path = os.path.join(OUTPUTS_FOLDER, filename)
    if not os.path.exists(path):
        return redirect(url_for("resultats", error="Fitxer no trobat."))

    try:
        # Llegeix només el primer full i limita files
        df = pd.read_excel(path, engine="openpyxl")
        df_preview = df.head(PREVIEW_ROWS)

        table_html = df_preview.to_html(
            classes="preview-table",
            index=False,
            border=0
        )

        return render_template(
            "preview.html",
            filename=filename,
            num_rows=len(df),
            shown_rows=len(df_preview),
            table=table_html
        )

    except Exception as e:
        return redirect(url_for("resultats", error=f"No s'ha pogut generar la vista prèvia: {e}"))

@app.route("/view/<filename>")
def view_file(filename):
    return send_from_directory(
        OUTPUTS_FOLDER,
        filename,
        as_attachment=False
    )


# -------- DOWNLOAD FILE --------------

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(OUTPUTS_FOLDER, filename, as_attachment=True)

@app.route("/download_zip")
def download_zip():
    buffer = BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for filename in os.listdir(OUTPUTS_FOLDER):
            file_path = os.path.join(OUTPUTS_FOLDER, filename)
            if os.path.isfile(file_path):
                zipf.write(file_path, arcname=filename)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="resultats_matricula.zip",
        mimetype="application/zip"
    )



# ---------- RESULTATS ----------


@app.route("/resultats")
def resultats():
    error = request.args.get("error")
    files = sorted(os.listdir(OUTPUTS_FOLDER))
    return render_template("resultats.html", files=files, error=error)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
