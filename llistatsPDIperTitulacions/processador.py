import pandas as pd
from collections import defaultdict

def process_sheet(df, plan_col, pdi_col):
    result = defaultdict(set)
    for _, row in df.iterrows():
        plan = row[plan_col]
        pdi = row[pdi_col]
        if pd.notna(plan) and pd.notna(pdi):
            plan = str(plan).strip()
            pdi = str(pdi).strip()

            if pdi.lower().startswith('fora dedicació'):
                pdi = str(row.get('Observacions', '')).strip()

            if plan and pdi \
               and not pdi.lower().startswith("conferències") \
               and not pdi.lower().startswith("docència"):
                result[plan].add(pdi)
    return result


def merge_results(*dicts):
    merged = defaultdict(set)
    for d in dicts:
        for plan, pdis in d.items():
            merged[plan].update(pdis)
    return merged

def obtenir_titulacions(excel_path):
    df = pd.read_excel(excel_path, sheet_name='DOCÈNCIA 26_27')

    titulacions = (
        df['Descripció Pla']
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
    )

    return sorted(titulacions)

def generar_pdi_per_titulacio(excel_path, incloure_tfg=False, incloure_pract=False):
    docencia_df = pd.read_excel(excel_path, sheet_name='DOCÈNCIA 26_27')
    result_docencia = process_sheet(docencia_df, 'Descripció Pla', 'PDI')

    result_tfg = {}
    if incloure_tfg:
        tfg_df = pd.read_excel(excel_path, sheet_name='TFG_M')
        result_tfg = process_sheet(tfg_df, 'Grau/Màster', 'PDI')

    result_pract = {}
    if incloure_pract:
        pract_df = pd.read_excel(excel_path, sheet_name='PRÀCT')
        result_pract = process_sheet(pract_df, 'Grau', 'PDI')

    return merge_results(result_docencia, result_tfg, result_pract)
