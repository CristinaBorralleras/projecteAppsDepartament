import pandas as pd
import warnings

# Amaguem warnings sorollosos d'openpyxl
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")


def generar_info_pdi(
    input_file,
    sheet_dedicacio="Total_Dedicació_PDI",
    sheet_pdi="PDI_Formac_AAA_Doctor_Acr",
    sheet_practiques="PRÀCT",
    gea="Enginyeria de l'Automoció"
):
    """
    Genera el dataframe final d'informació PDI a partir d'un Excel d'entrada.
    Retorna un DataFrame amb columnes finals estables.
    """

    # ------------------------------------------------------------------
    # 1. Llegim fulls necessaris
    # ------------------------------------------------------------------

    df_dedicacio = pd.read_excel(input_file, sheet_name=sheet_dedicacio)
    df_pdi = pd.read_excel(input_file, sheet_name=sheet_pdi)
    df_pract = pd.read_excel(input_file, sheet_name=sheet_practiques)

    # ------------------------------------------------------------------
    # 2. Normalització de columnes PRÀCT
    # ------------------------------------------------------------------

    df_pract.columns = df_pract.columns.str.strip()

    required_pract_cols = {"Grau", "NIF", "Hores en dedicació", "Hores en AAA"}
    missing = required_pract_cols - set(df_pract.columns)

    if missing:
        raise ValueError(
            f"A la pestanya PRÀCT falten columnes necessàries: {missing}"
        )

    # ------------------------------------------------------------------
    # 3. Merge dedicació + PDI
    # ------------------------------------------------------------------

    df = df_dedicacio.merge(
        df_pdi,
        left_on="COGNOMS NOM",
        right_on="COGNOMS_NOM",
        how="left",
        suffixes=("_DED", "_PDI")
    )

    # ------------------------------------------------------------------
    # 4. Departament correcte (font DED)
    # ------------------------------------------------------------------

    if "DEPARTAMENT_DED" in df.columns:
        df["DEPARTAMENT"] = df["DEPARTAMENT_DED"]

    df.drop(columns=["DEPARTAMENT_PDI"], errors="ignore", inplace=True)

    # ------------------------------------------------------------------
    # 5. Separació cognoms / nom (robusta)
    # ------------------------------------------------------------------

    if "COGNOMS NOM" in df.columns:
        split = df["COGNOMS NOM"].astype(str).str.split(",", n=1, expand=True)
        df["COGNOMS"] = split[0].str.strip()
        df["NOM"] = split[1].str.strip() if split.shape[1] > 1 else ""
    else:
        df["COGNOMS"] = ""
        df["NOM"] = ""

    # ------------------------------------------------------------------
    # 6. Columna PDI (derivada i garantida)
    # ------------------------------------------------------------------

    df["PDI"] = df["COGNOMS"] + ", " + df["NOM"]

    # ------------------------------------------------------------------
    # 7. Càlcul d'hores de pràctiques
    # ------------------------------------------------------------------

    # Inicialitzem columnes de pràctiques
    pract_cols = [
        "Total hores pràctiques (sense AAA)",
        "Total hores pràctiques AAA",
        "Total hores pràctiques GEA (sense AAA)",
        "Total hores pràctiques GEA AAA",
    ]

    for col in pract_cols:
        df_pract[col] = 0

    mask_gea = df_pract["Grau"] == gea
    mask_no_gea = ~mask_gea

    df_pract.loc[mask_no_gea, "Total hores pràctiques (sense AAA)"] = (
        df_pract.loc[mask_no_gea, "Hores en dedicació"]
    )

    df_pract.loc[mask_no_gea, "Total hores pràctiques AAA"] = (
        df_pract.loc[mask_no_gea, "Hores en AAA"]
    )

    df_pract.loc[mask_gea, "Total hores pràctiques GEA (sense AAA)"] = (
        df_pract.loc[mask_gea, "Hores en dedicació"]
    )

    df_pract.loc[mask_gea, "Total hores pràctiques GEA AAA"] = (
        df_pract.loc[mask_gea, "Hores en AAA"]
    )

    # ------------------------------------------------------------------
    # 8. Agregació pràctiques per NIF
    # ------------------------------------------------------------------

    df_pract_agg = (
        df_pract
        .groupby("NIF", as_index=False)[pract_cols]
        .sum()
    )

    # ------------------------------------------------------------------
    # 9. Merge pràctiques amb dataframe principal
    # ------------------------------------------------------------------

    if "NIF" in df.columns:
        df = df.merge(df_pract_agg, on="NIF", how="left")

    for col in pract_cols:
        df[col] = df.get(col, 0).fillna(0)

    # ------------------------------------------------------------------
    # 10. Columnes FINALS (blindades)
    # ------------------------------------------------------------------

    final_columns = [
        "NIF",
        "PDI",
        "COGNOMS",
        "NOM",
        "CATEGORIA",
        "DEPARTAMENT",
        "TOTAL DEDICACIÓ",
        "Altra Activitat",
        "Tutoritzacions TFG en dedicació (sense AAA)",
        *pract_cols
    ]

    # Garantim que totes existeixen
    for col in final_columns:
        if col not in df.columns:
            df[col] = 0

    df_final = df[final_columns].copy()

    return df_final