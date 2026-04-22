from flask import Flask, render_template, request, send_file
import os
import pandas as pd
from processador import generar_pdi_per_titulacio, obtenir_titulacions

app = Flask(__name__)

# Carpeta on es guarden els Excel pujats
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
CURRENT_EXCEL = os.path.join(UPLOAD_FOLDER, "actual.xlsx")



@app.route("/", methods=["GET", "POST"])
def load_excel():
    # --- POST: utilitzar l'últim Excel ---
    if request.method == "POST" and request.form.get("use_last") == "1":
        if not os.path.exists(CURRENT_EXCEL):
            return render_template(
                "load.html",
                error="No hi ha cap fitxer anterior.",
                has_last=False
            )

        titulacions = obtenir_titulacions(CURRENT_EXCEL)
        
        return render_template(
			"options.html",
			excel_path=CURRENT_EXCEL,
			titulacions=titulacions
		)

    # --- POST: carregar un Excel nou ---
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
                error="El fitxer ha de ser .xlsx.",
                has_last=os.path.exists(CURRENT_EXCEL)
            )

        file.save(CURRENT_EXCEL)

        titulacions = obtenir_titulacions(CURRENT_EXCEL)
        
        return render_template(
			"options.html",
			excel_path=CURRENT_EXCEL,
			titulacions=titulacions
		)

    # --- GET ---
    return render_template(
        "load.html",
        has_last=os.path.exists(CURRENT_EXCEL)
    )


@app.route("/download")
def download_excel():
    return send_file(
        os.path.join(UPLOAD_FOLDER, "pdi_per_titulacions.xlsx"),
        as_attachment=True,
        download_name="pdi_per_titulacions.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.route("/options")
def tornar_a_opcions():
    # Reutilitzem l'últim Excel carregat
    if not os.path.exists(CURRENT_EXCEL):
        return redirect("/")

    titulacions = obtenir_titulacions(CURRENT_EXCEL)

    return render_template(
        "options.html",
        excel_path=CURRENT_EXCEL,
        titulacions=titulacions
    )


@app.route("/generar", methods=["POST"])
def generar():
    """
    Generar l'Excel de PDI per titulacions
    """
    acció = request.form.get("action")
    excel_path = request.form["excel_path"]
    incloure_tfg = "tfg" in request.form
    incloure_pract = "pract" in request.form
    titulacions_seleccionades = request.form.getlist("titulacions")

    resultat = generar_pdi_per_titulacio(
        excel_path,
        incloure_tfg,
        incloure_pract
    )
    
    if (titulacions_seleccionades and "__totes__" not in titulacions_seleccionades):
    	resultat = {
		    t: resultat[t]
		    for t in titulacions_seleccionades
		    if t in resultat
		}

    # Convertir el resultat a format pla (DataFrame)
    # Convertir a format pla
    
    rows = []
    for pla in sorted(resultat):
    	for pdi in sorted(resultat[pla]):
    		rows.append({
				"Pla d'estudis": pla,
				"PDI": pdi
			})
	
    df = pd.DataFrame(rows)
	
    output_path = os.path.join(UPLOAD_FOLDER, "pdi_per_titulacions.xlsx")
    df.to_excel(output_path, index=False)

    # SI VOL DESCARREGAR DIRECTAMENT
    if acció == "download":
    	return send_file(
		    output_path,
		    as_attachment=True,
		    download_name="pdi_per_titulacions.xlsx",
		    mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
		)

    # ALTRAMENT, VISUALITZAR
    return render_template(
		"result.html",
		rows=rows
	)
    
    


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000)
    #app.run(debug=True)
