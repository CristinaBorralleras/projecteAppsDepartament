from flask import (
    Flask, render_template, request, redirect,
    send_file, send_from_directory, abort
)
import os
import io
import zipfile
import pdfkit

from Dedicacions import Dedicacions
from genDeds import (
    genAllFixDept, genAllAssDept,
    genAllAltresCentres,
    gen1FDept, gen1ADept, gen1AltresCentres,
    genDirs
)

# =====================================================
# CONFIGURACIÓ GENERAL
# =====================================================

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

WKHTMLTOPDF_PATH = "/usr/bin/wkhtmltopdf"
config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)


# Carpetes de sortida
genDirs()   # crea output/plantilla_ENG, associats_ENG, etc.


UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

CURRENT_EXCEL = os.path.join(app.config["UPLOAD_FOLDER"], "actual.xlsx")

deds = None


# =====================================================
# càrrega fitxer i generació de deds
# =====================================================

@app.route("/load", methods=["GET", "POST"])
def load_excel():
    global deds

    # --- POST: utilitzar l'últim Excel ---
    if request.method == "POST" and request.form.get("use_last") == "1":
        if not os.path.exists(CURRENT_EXCEL):
            return render_template(
                "load.html",
                error="No hi ha cap fitxer anterior.",
                has_last=False
            )

        deds = Dedicacions(CURRENT_EXCEL)
        return redirect("/")

    # --- POST: carregar Excel nou ---
    if request.method == "POST":
        file = request.files.get("excel")

        if not file or file.filename == "":
            return render_template(
                "load.html",
                error="No s'ha seleccionat cap fitxer.",
                has_last=os.path.exists(CURRENT_EXCEL)
            )

        if not file.filename.lower().endswith(".xlsx"):
            return render_template(
                "load.html",
                error="El fitxer ha de ser .xlsx",
                has_last=os.path.exists(CURRENT_EXCEL)
            )

        file.save(CURRENT_EXCEL)
        deds = Dedicacions(CURRENT_EXCEL)

        return redirect("/")

    # --- GET ---
    return render_template(
        "load.html",
        has_last=os.path.exists(CURRENT_EXCEL)
    )


# =====================================================
# FUNCIONS AUXILIARS
# =====================================================

def llistar_pdfs(carpeta):
    """Llista els PDFs d'una carpeta dins output/"""
    path = os.path.join("output", carpeta)
    if not os.path.isdir(path):
        return []
    return sorted(f for f in os.listdir(path) if f.lower().endswith(".pdf"))


def crear_zip_de_carpetes(carpetes):
    """Crea un ZIP en memòria amb totes les carpetes indicades"""
    memory_file = io.BytesIO()

    with zipfile.ZipFile(memory_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for carpeta in carpetes:
            base = os.path.join("output", carpeta)
            if not os.path.isdir(base):
                continue

            for root, _, files in os.walk(base):
                for file in files:
                    if file.lower().endswith(".pdf"):
                        full_path = os.path.join(root, file)
                        arcname = os.path.relpath(full_path, "output")
                        zf.write(full_path, arcname)

    memory_file.seek(0)
    return memory_file


def netejar_output():
    """
    Esborra tot el contingut dins la carpeta output/,
    però no la carpeta output en si.
    """
    base = "output"

    for nom in os.listdir(base):
        path = os.path.join(base, nom)

        # Esborra arxius
        if os.path.isfile(path):
            os.remove(path)

        # Esborra carpetes i el seu contingut
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path, topdown=False):
                for f in files:
                    os.remove(os.path.join(root, f))
                for d in dirs:
                    os.rmdir(os.path.join(root, d))

# =====================================================
# MENÚ PRINCIPAL
# =====================================================

@app.route("/")
def index():
    if deds is None:
        return redirect("/load")

    return render_template("index.html")


# =====================================================
# GENERAR TOTS (GLOBAL)
# =====================================================

@app.route("/generar/tots")
def generar_tots_ui():
    return render_template(
        "loading.html",
        message="Generant tots els documents…",
        next_url="/_do/generar/tots"
    )


@app.route("/_do/generar/tots")
def do_generar_tots():
    netejar_output()
    
    genAllFixDept(deds, config, "ENGINYERIES")
    genAllFixDept(deds, config, "BIOCIÈNCIES")

    genAllAssDept(deds, config, "ENGINYERIES")
    genAllAssDept(deds, config, "BIOCIÈNCIES")

    genAllAltresCentres(deds, config)

    carpetes = [
        "plantilla_ENG", "plantilla_BIO",
        "associats_ENG", "associats_BIO",
        "altresCentres"
    ]

    return render_template(
        "downloads.html",
        message="Tots els documents generats correctament",
        carpetes=carpetes,
        llistar_pdfs=llistar_pdfs
    )


# =====================================================
# GENERAR PER DEPARTAMENT + TIPUS (perm / ass / tots)
# =====================================================

@app.route("/generar/<tipus>/dept/<dept>")
def generar_departament_tipus_ui(tipus, dept):
    return render_template(
        "loading.html",
        message=f"Generant documents {tipus.upper()} del departament {dept}…",
        next_url=f"/_do/generar/{tipus}/dept/{dept}"
    )


@app.route("/_do/generar/<tipus>/dept/<dept>")
def generar_departament_tipus(tipus, dept):
    netejar_output()

    tipus = tipus.lower()
    suf = "_BIO" if "BIO" in dept else "_ENG"

    if tipus == "perm":
        genAllFixDept(deds, config, dept)
        carpetes = [f"plantilla{suf}"]

    elif tipus == "ass":
        genAllAssDept(deds, config, dept)
        carpetes = [f"associats{suf}"]

    elif tipus == "tots":
        genAllFixDept(deds, config, dept)
        genAllAssDept(deds, config, dept)
        carpetes = [f"plantilla{suf}", f"associats{suf}"]

    else:
        return render_template(
            "result.html",
            ok=False,
            message="Tipus no vàlid"
        )

    return render_template(
        "downloads.html",
        message=f"Documents generats per {dept}",
        carpetes=carpetes,
        llistar_pdfs=llistar_pdfs
    )


# =====================================================
# ALTRES CENTRES
# =====================================================

@app.route("/generar/altres-centres")
def altres_centres_ui():
    return render_template(
        "loading.html",
        message="Generant documents del PDI d'Altres Centres…",
        next_url="/_do/generar/altres-centres"
    )


@app.route("/_do/generar/altres-centres")
def altres_centres():
    netejar_output()
    
    genAllAltresCentres(deds, config)

    return render_template(
        "downloads.html",
        message="Documents d'Altres Centres generats",
        carpetes=["altresCentres"],
        llistar_pdfs=llistar_pdfs
    )


# =====================================================
# GENERAR UN SOL PDI
# =====================================================

@app.route("/generar/pdi", methods=["GET", "POST"])
def generar_pdi():

    pdis = sorted(
        list(deds.getPDIFix().keys()) +
        list(deds.getPDIAss().keys())
    )

    if request.method == "POST":
        netejar_output()

        nom = (
            request.form.get("pdi_select")
            or request.form.get("pdi_text", "").strip().upper()
        )

        if not nom:
            return render_template("result.html", ok=False, message="Cap PDI indicat")

        if nom in deds.getPDIFix():
            dept = deds.getDept(nom)
            gen1FDept(nom, deds, config, dept)
            carpeta = "plantilla_BIO" if "BIO" in dept else "plantilla_ENG"

        elif nom in deds.getPDIAss():
            if deds.getPDIAss()[nom]["observacions"] == "Altre centre":
                gen1AltresCentres(nom, deds, config)
                carpeta = "altresCentres"
            else:
                dept = deds.getDept(nom)
                gen1ADept(nom, deds, config, dept)
                carpeta = "associats_BIO" if "BIO" in dept else "associats_ENG"

        else:
            return render_template("result.html", ok=False, message="PDI no trobat")

        return render_template(
            "downloads.html",
            message=f"Document generat per {nom}",
            carpetes=[carpeta],
            single=True,
            pdi_nom=nom,
            llistar_pdfs=llistar_pdfs
        )

    return render_template("pdi.html", pdis=pdis)


# =====================================================
# DESCÀRREGA INDIVIDUAL
# =====================================================
													
@app.route("/download/<carpeta>/<nom_pdf>")
def download_pdf(carpeta, nom_pdf):
    base = os.path.join("output", carpeta)
    baixar = request.args.get("dl") == "1"

    return send_from_directory(
        base,
        nom_pdf,
        as_attachment=baixar
    )


# =====================================================
# DESCÀRREGA ZIP
# =====================================================

@app.route("/download/zip")
def download_zip():
    carpetes = request.args.getlist("carpeta")
    zip_data = crear_zip_de_carpetes(carpetes)

    return send_file(
        zip_data,
        as_attachment=False,
        download_name="documents_generats.zip",
        mimetype="application/zip"
    )


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
