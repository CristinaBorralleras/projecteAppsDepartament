import csv
from collections import defaultdict
import pandas as pd


# --------------------------------------------------------------------
# Llegeix codis_compartides.csv
# --------------------------------------------------------------------
def crea_diccionari_codis(nom_fitxer):
    diccionari = {}
    try:
        with open(nom_fitxer, mode="r", encoding="utf-8") as fitxer:
            lector = csv.reader(fitxer, delimiter=";")
            for fila in lector:
                if len(fila) < 4:
                    continue
                primer_codi = fila[2].strip()
                segon_codi = fila[3].strip()
                titulacio = fila[0].strip()
                diccionari[segon_codi] = (primer_codi, titulacio)
                diccionari[primer_codi] = (primer_codi, titulacio)
        return diccionari
    except (FileNotFoundError, IndexError):
        print("Generació sense agrupar assignatures compartides")
        return {}


# --------------------------------------------------------------------
# Processa Matriculats_per_assignatura.csv
# --------------------------------------------------------------------
def processa_csv(nom_fitxer, dicCodis):
    grups_classe = {}
    subgrups_info = defaultdict(
        lambda: defaultdict(lambda: {"places": 0, "num_subgrups": 0})
    )
    assig_estandard = {}
    assig_estandard_correctes = {}

    with open(nom_fitxer, newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=";")

        # Cercar inici de dades
        try:
            while True:
                fila = next(reader)
                if fila and fila[0].upper().strip() == "IDENTIFICADOR ELEMENT":
                    break
        except StopIteration:
            raise ValueError("No s'ha trobat 'IDENTIFICADOR ELEMENT' al CSV")

        for fila in reader:
            if len(fila) < 22:
                continue

            titulacio = fila[4].strip().upper()
            codi_assignatura = fila[5].strip()
            nom_assignatura = fila[6].strip()
            curs = fila[7].strip()
            categoria = fila[11].strip().upper()
            tipologia = fila[12].strip()
            codi_grup = fila[13].strip()
            semestre = fila[21].strip()

            if codi_assignatura in dicCodis:
                codi_assignatura = dicCodis[codi_assignatura][0]
                titulacio = dicCodis[codi_assignatura][1]
                categoria = "NO ESTÀNDARD"

            try:
                estudiants_matriculats = int(fila[15].strip())
            except ValueError:
                estudiants_matriculats = 0

            try:
                places = int(fila[16].strip())
            except ValueError:
                places = 0

            if categoria not in ["ESTÀNDARD", "NO ESTÀNDARD"]:
                continue

            # ---------------------
            # ESTÀNDARD
            # ---------------------
            if categoria == "ESTÀNDARD":
                clau = (codi_assignatura, codi_grup)
                dades = (
                    titulacio,
                    nom_assignatura,
                    curs,
                    semestre,
                    estudiants_matriculats,
                )
                if estudiants_matriculats > 50:
                    assig_estandard[clau] = dades
                else:
                    assig_estandard_correctes[clau] = dades

            # ---------------------
            # NO ESTÀNDARD
            # ---------------------
            else:
                if tipologia.startswith("Grup Classe"):
                    clau = (codi_assignatura, codi_grup)
                    if clau in grups_classe:
                        grups_classe[clau]["estudiants_matriculats"] += estudiants_matriculats
                    else:
                        grups_classe[clau] = {
                            "titulacio": titulacio,
                            "nom_assignatura": nom_assignatura,
                            "curs": curs,
                            "semestre": semestre,
                            "estudiants_matriculats": estudiants_matriculats,
                        }
                else:
                    for (cod_assig, grup_classe), info in grups_classe.items():
                        if cod_assig == codi_assignatura and codi_grup.startswith(grup_classe):
                            if places <= 0:
                                break
                            clau_subgrup = (codi_assignatura, grup_classe)
                            if subgrups_info[clau_subgrup][tipologia]["places"] == 0:
                                subgrups_info[clau_subgrup][tipologia]["places"] = places
                            subgrups_info[clau_subgrup][tipologia]["num_subgrups"] += 1
                            break

    return (
        grups_classe,
        subgrups_info,
        assig_estandard,
        assig_estandard_correctes,
    )


# --------------------------------------------------------------------
# Generació de fitxers XLSX
# --------------------------------------------------------------------
def generaFitxers(nomFdesv, nomFcorrectes,
                  grups, subgrups, estandard, estandardCorrectes):

    desviacions = []
    correctes = []

    # NO ESTÀNDARD
    for (codiAssignatura, codiGrup), val in grups.items():
        estudiants = val["estudiants_matriculats"]
        if (codiAssignatura, codiGrup) not in subgrups:
            continue

        for tipus, info in subgrups[(codiAssignatura, codiGrup)].items():
            places = info["places"]
            nsubgrups = info["num_subgrups"]

            if places <= 0:
                continue

            numReal = int((estudiants / places) + (estudiants % places > 0))

            fila = {
                "Titulació": val["titulacio"],
                "Curs": val["curs"],
                "Semestre": val["semestre"],
                "Codi Assignatura": codiAssignatura,
                "Nom Assignatura": val["nom_assignatura"],
                "Categoria": "NO ESTÀNDARD",
                "Codi Grup": codiGrup,
                "Tipus Subgrup": tipus,
                "Matriculats": estudiants,
                "Places per subgrup": places,
                "Num Subgrups Planificats": nsubgrups,
                "Num Subgrups Reals": numReal,
            }

            if numReal != nsubgrups:
                fila["Subgrups que sobren/falten"] = numReal - nsubgrups
                desviacions.append(fila)
            else:
                correctes.append(fila)

    # ESTÀNDARD (desviacions)
    for (codi, grup), dades in estandard.items():
        desviacions.append({
            "Titulació": dades[0],
            "Curs": dades[2],
            "Semestre": dades[3],
            "Codi Assignatura": codi,
            "Nom Assignatura": dades[1],
            "Categoria": "ESTÀNDARD",
            "Codi Grup": grup,
            "Matriculats": dades[4],
        })

    # ESTÀNDARD (correctes)
    for (codi, grup), dades in estandardCorrectes.items():
        correctes.append({
            "Titulació": dades[0],
            "Curs": dades[2],
            "Semestre": dades[3],
            "Codi Assignatura": codi,
            "Nom Assignatura": dades[1],
            "Categoria": "ESTÀNDARD",
            "Codi Grup": grup,
            "Matriculats": dades[4],
        })

    # Escriure XLSX
    pd.DataFrame(desviacions).to_excel(nomFdesv, index=False, engine="openpyxl")
    pd.DataFrame(correctes).to_excel(nomFcorrectes, index=False, engine="openpyxl")


# --------------------------------------------------------------------
# Agrupació d'assignatures compartides
# --------------------------------------------------------------------
def agruparSubgrupsCompartides(dicGrups, dicSubgrups):
    dG = {}
    for (codi_assignatura, _), dicGrup in dicGrups.items():
        clau = (codi_assignatura, "-")
        if clau in dG:
            dG[clau]["estudiants_matriculats"] += dicGrup["estudiants_matriculats"]
        else:
            dG[clau] = dicGrup.copy()

    dic = {}
    for (codi_assignatura, _), dSub in dicSubgrups.items():
        clau = (codi_assignatura, "-")
        if clau not in dic:
            dic[clau] = {}
        for tipus, val in dSub.items():
            if tipus in dic[clau]:
                dic[clau][tipus]["num_subgrups"] += val["num_subgrups"]
            else:
                dic[clau][tipus] = val.copy()

    return dG, dic
