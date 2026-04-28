"""
calculate_metrics.py
====================
Calcula para cada colegio en data_merged.json:

  1. pct_avance_global   → promedio de TODOS los criterios numéricos de todas las etapas.
  2. eje_transformacion  → promedio de los criterios cuyo 'tipo' == "Nivel de transformación de las prácticas docentes"
  3. eje_descenso        → promedio de los criterios cuyo 'tipo' contiene "descenso curricular"

Los criterios y su mapeo a ejes transversales provienen del criteriosDictionary 
definido en index.html:

  criterio{n}_{etapa} en el diccionario  →  criterios.e{etapa}.criterio_{n}  en el JSON

Criterios con tipo vacío ("") se usan en el promedio global pero NO en ningún eje.
criterio1_1 es texto (modelo pedagógico) → siempre excluido de promedios numéricos.
"""

import json
import os

# ── Mapeo de ejes ──────────────────────────────────────────────────────────────
# Formato: (etapa_key, criterio_key): 'eje_label'
# Derivado directamente del criteriosDictionary del index.html

EJE_TRANSFORMACION = "transformacion_practicas"
EJE_DESCENSO = "descenso_curricular"

CRITERIO_EJE = {
    # E1
    ("e1", "criterio_2"): EJE_DESCENSO,
    ("e1", "criterio_3"): EJE_TRANSFORMACION,
    # E2
    ("e2", "criterio_1"): EJE_DESCENSO,
    # criterio_2 e2 → tipo vacío → sin eje
    ("e2", "criterio_3"): EJE_TRANSFORMACION,
    # E3
    # criterio_1 e3 → tipo vacío → sin eje
    ("e3", "criterio_2"): EJE_TRANSFORMACION,
    # E4
    ("e4", "criterio_1"): EJE_TRANSFORMACION,
    # criterio_2 e4 → tipo vacío → sin eje
    ("e4", "criterio_3"): EJE_DESCENSO,
    # E5
    ("e5", "criterio_1"): EJE_DESCENSO,
    ("e5", "criterio_2"): EJE_DESCENSO,
    ("e5", "criterio_3"): EJE_TRANSFORMACION,
    # E6
    ("e6", "criterio_1"): EJE_TRANSFORMACION,
    ("e6", "criterio_2"): EJE_DESCENSO,
    ("e6", "criterio_3"): EJE_DESCENSO,
}

# Criterio que es siempre texto (no numérico)
TEXT_CRITERIOS = {("e1", "criterio_1")}

# Mapeo de ejes para Familia (basado en el diccionario)
FAMILIA_EJES_MAP = {
    "1. Avance en la consolidación del comité": "familia_eje_1",
    "2. Reconocimiento del componente familiar e intereses declarados sobre familia": "familia_eje_2",
    "3. Avance en la constitución y consolidación del Comité de Familia": "familia_eje_3"
}

def calcular_metricas(inst):
    """Dada una institución, calcula y retorna el dict de métricas."""
    criterios = inst.get("criterios", {})
    familia = inst.get("familia", {})

    # Métricas Formación Profesoral (Blue)
    all_vals = []
    trans_vals = []
    desc_vals = []

    for etapa_key in ["e1", "e2", "e3", "e4", "e5", "e6"]:
        for crit_key, cval in (criterios.get(etapa_key) or {}).items():
            if (etapa_key, crit_key) in TEXT_CRITERIOS:
                continue
            if not isinstance(cval, (int, float)):
                continue
            if cval != cval:  # isnan
                continue

            all_vals.append(cval)
            eje = CRITERIO_EJE.get((etapa_key, crit_key))
            if eje == EJE_TRANSFORMACION:
                trans_vals.append(cval)
            elif eje == EJE_DESCENSO:
                desc_vals.append(cval)

    # Métricas Familia (Green)
    # Necesitamos el diccionario para mapear criterios a ejes
    # Para optimizar, asumimos que el diccionario está cargado o usamos una lógica de prefijos
    # Sin embargo, como el script corre en lote, cargaremos el diccionario una vez en main
    # y lo pasaremos o lo usaremos de forma global. 
    # Por simplicidad en este bloque, usaremos la lógica de ejes directamente si ya sabemos el mapeo.
    
    fam_all_vals = []
    fam_e1_vals = []
    fam_e2_vals = []
    fam_e3_vals = []

    # El mapeo de familia lo haremos dinámico en base al prefijo o ID si es posible, 
    # pero aquí usaremos los datos ya presentes en el objeto 'inst' si merge_data hizo su trabajo.
    # Nota: merge_data.py ya integra los datos en inst['familia']
    
    def get_fam_metrics(fam_data, dicc_fam):
        f_all, f1, f2, f3 = [], [], [], []
        for crit_id, val in fam_data.items():
            if not isinstance(val, (int, float)) or val != val:
                continue
            f_all.append(val)
            # Buscar eje en el diccionario
            info = next((item for item in dicc_fam if item["id"] == crit_id), None)
            if info:
                eje_str = info.get("ejes", "")
                if "1." in eje_str: f1.append(val)
                elif "2." in eje_str: f2.append(val)
                elif "3." in eje_str: f3.append(val)
        return f_all, f1, f2, f3

    def safe_avg(lst):
        return round(sum(lst) / len(lst), 4) if lst else None

    # Estas se calcularán en el loop principal para tener acceso al diccionario
    return {
        "pct_avance_global": safe_avg(all_vals),
        "eje_transformacion_practicas": safe_avg(trans_vals),
        "eje_descenso_curricular": safe_avg(desc_vals),
    }

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(root_dir, "data", "data_merged.json")
    dicc_fam_path = os.path.join(root_dir, "data", "diccionario_familia.json")

    print(f"Leyendo {data_path} ...")
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)

    dicc_fam = []
    if os.path.exists(dicc_fam_path):
        with open(dicc_fam_path, encoding="utf-8") as f:
            dicc_fam = json.load(f)

    updated = 0
    skipped = 0
    for inst in data:
        # Calcular métricas base
        metricas = calcular_metricas(inst)
        
        # Calcular métricas Familia
        fam_data = inst.get("familia", {})
        f_all, f1, f2, f3 = [], [], [], []
        for crit_id, val in fam_data.items():
            if not isinstance(val, (int, float)) or val != val:
                continue
            f_all.append(val)
            info = next((item for item in dicc_fam if item["id"] == crit_id), None)
            if info:
                eje_str = info.get("ejes", "")
                if "1." in eje_str: f1.append(val)
                elif "2." in eje_str: f2.append(val)
                elif "3." in eje_str: f3.append(val)
        
        def safe_avg(lst):
            return round(sum(lst) / len(lst), 4) if lst else None

        metricas["familia_avance_global"] = safe_avg(f_all)
        metricas["familia_eje_1"] = safe_avg(f1)
        metricas["familia_eje_2"] = safe_avg(f2)
        metricas["familia_eje_3"] = safe_avg(f3)

        if any(v is not None for v in metricas.values()):
            inst["metricas"] = metricas
            updated += 1
        else:
            inst["metricas"] = metricas
            skipped += 1

    print(f"\nInstituciones con métricas calculadas: {updated}")
    
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nOK: data_merged.json actualizado correctamente con métricas de Familia.")

if __name__ == "__main__":
    main()
