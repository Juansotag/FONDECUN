import pandas as pd
import os
import json
import numpy as np


def clean_val(v):
    if v is None:
        return None
    if isinstance(v, float) and np.isnan(v):
        return None
    if pd.isna(v):
        return None
    if isinstance(v, (np.integer, int)):
        return int(v)
    if isinstance(v, (np.floating, float)):
        f = float(v)
        return None if np.isnan(f) else round(f, 4)
    s = str(v).strip()
    return s if s else None


def row_to_dict(row):
    return {k: clean_val(v) for k, v in row.to_dict().items() if not str(k).startswith('Unnamed')}


def merge_data():
    # Use absolute paths relative to this script's location
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    base_path = os.path.join(root_dir, 'data', 'stages')
    info_gen_path = os.path.join(base_path, 'Información_general_fixed.xlsx')
    reporte_path = os.path.join(root_dir, 'docs', 'REPORTE_FINAL_FONDECUN.xlsx')
    # Output path
    output_path = os.path.join(root_dir, 'data', 'data_merged.json')
    establecimientos_path = os.path.join(root_dir, 'data', 'Establecimientos.csv')

    # ── 1. Información general (mapa, avances, participantes, etapas cursadas) ──
    df_info = pd.read_excel(info_gen_path)
    print("INFO COLS:", df_info.columns.tolist())

    master_data = {}
    for _, row in df_info.iterrows():
        d_raw = row.get('id')
        if pd.isna(d_raw):
            continue
        dane = str(int(d_raw))

        master_data[dane] = {
            "id": dane,
            "cliente": clean_val(row.get('cliente')),
            "municipio": clean_val(row.get('municipio')),
            "estado": clean_val(row.get('estado')),
            "institucion": clean_val(row.get('institucion')),
            "lat": clean_val(row.get('latitud')),
            "lng": clean_val(row.get('longitud')),
            "mp": clean_val(row.get('mp')),
            "jornada": clean_val(row.get('jornada')),
            "caracter": clean_val(row.get('caracter')),
            "rector": clean_val(row.get('rector')),
            "especialidad": clean_val(row.get('especialidad')),
            "foco_e2": clean_val(row.get('foco_e2')),
            "participantes": {
                "e1": clean_val(row.get('participantes_e1')),
                "e2": clean_val(row.get('participantes_e2')),
                "e3": clean_val(row.get('participantes_e3')),
                "e4": clean_val(row.get('participantes_e4')),
                "e5": clean_val(row.get('participantes_e5')),
                "e6": clean_val(row.get('participantes_e6')),
            },
            "avances": {
                "e1": clean_val(row.get('avance_e1')),
                "e2": clean_val(row.get('avance_e2')),
                "e3": clean_val(row.get('avance_e3')),
                "e4": clean_val(row.get('avance_e4')),
                "e5": clean_val(row.get('avance_e5')),
                "e6": clean_val(row.get('avance_e6')),
            },
            "etapas_cursadas": {
                "e1": int(row.get('e1', 0)) if pd.notnull(row.get('e1', 0)) else 0,
                "e2": int(row.get('e2', 0)) if pd.notnull(row.get('e2', 0)) else 0,
                "e3": int(row.get('e3', 0)) if pd.notnull(row.get('e3', 0)) else 0,
                "e4": int(row.get('e4', 0)) if pd.notnull(row.get('e4', 0)) else 0,
                "e5": int(row.get('e5', 0)) if pd.notnull(row.get('e5', 0)) else 0,
                "e6": int(row.get('e6', 0)) if pd.notnull(row.get('e6', 0)) else 0,
            },
            # Filled from REPORTE_FINAL below
            "nombre_oficial": None,
            "modelo_declarado": None,
            "enfoque": None,
            "modelo_clasificado": None,
            "enfoque_clasificado": None,
            "familia_pedagogica": None,
            "criterios": {
                "e1": {},
                "e2": {},
                "e3": {},
                "e4": {},
                "e5": {},
                "e6": {},
            },
            "detalles": {}
        }

    # ── 2. REPORTE FINAL FONDECUN (nombre oficial, modelo, criterios) ──
    if not os.path.exists(reporte_path):
        # fall-back to root
        reporte_path_alt = os.path.join(root_dir, 'REPORTE_FINAL_FONDECUN.xlsx')
        if os.path.exists(reporte_path_alt):
            print(f"  Found {reporte_path_alt} in root, using it...")
            reporte_path = reporte_path_alt
    
    if os.path.exists(reporte_path):
        try:
            # Try to read 'GENERAL' sheet, fall-back to first sheet
            try:
                df_rep = pd.read_excel(reporte_path, sheet_name='GENERAL')
            except:
                df_rep = pd.read_excel(reporte_path, sheet_name=0)
            
            print(f"  Processing REPORTE FINAL from {reporte_path}")
            # print("REPORTE COLS:", df_rep.columns.tolist())

            for _, row in df_rep.iterrows():
                id_raw = row.get('id')
                if pd.isna(id_raw):
                    continue
                dane = str(int(id_raw))
                if dane not in master_data:
                    # try to see if it's there as int if string failed
                    if id_raw in master_data: dane = id_raw
                    else: continue

                inst = master_data[dane]

                # Use nombre_oficial from reporte (authoritative name)
                inst["nombre_oficial"] = clean_val(row.get('nombre_oficial'))
                inst["municipio_oficial"] = clean_val(row.get('municipio'))
                inst["modelo_declarado"] = clean_val(row.get('modelo_declarado'))
                inst["enfoque"] = clean_val(row.get('enfoque'))
                inst["modelo_clasificado"] = clean_val(row.get('modelo_clasificado'))
                inst["enfoque_clasificado"] = clean_val(row.get('enfoque_clasificado'))
                inst["familia_pedagogica"] = clean_val(row.get('familia_pedagogica'))

                # Parse criterios: criterio{num}_{etapa}
                for col in df_rep.columns:
                    col_str = str(col).lower().strip()
                    if col_str.startswith('criterio'):
                        # Expected format: criterio{num}_{etapa}
                        suffix = col_str[len('criterio'):]  # e.g. "1_1", "2_3"
                        parts = suffix.split('_')
                        if len(parts) == 2:
                            crit_num = parts[0]   # e.g. "1", "2", "3"
                            etapa_num = parts[1]  # e.g. "1", "2", ..., "6"
                            etapa_key = f"e{etapa_num}"
                            val = clean_val(row.get(col))
                            if val is not None:
                                inst["criterios"][etapa_key][f"criterio_{crit_num}"] = val
        except Exception as e:
            print(f"Error processing {reporte_path}: {e}")
    else:
        print(f"WARNING: REPORTE_FINAL_FONDECUN.xlsx not found in root or docs/")

    # ── 3. Semáforo files (qualitative detail: logros, retos, sugerencias) ──
    semaforo_files = {
        "e1": ("Semáforo Etapa 1.xlsx", "id"),
        "e2": ("Semáforo Etapa 2.xlsx", "id"),
        "e3": ("Semáforo Etapa 3.xlsx", "id"),
        "e4": ("Semáforo Etapa 4.xlsx", "id"),
        "e5": ("Semáforo Etapa 5.xlsx", "id"),
        "e6": ("Semáforo Etapa 6.xlsx", "id"),
    }

    for key, (file, id_col) in semaforo_files.items():
        filepath = os.path.join(base_path, file)
        if not os.path.exists(filepath):
            print(f"  ! File not found: {filepath}")
            continue
        try:
            df = pd.read_excel(filepath)
            df = df[[c for c in df.columns if not str(c).startswith('Unnamed')]]

            # Find id column
            if id_col not in df.columns:
                alts = [c for c in df.columns if 'id' in str(c).lower() or 'codigo' in str(c).lower()]
                if alts:
                    id_col_use = alts[0]
                else:
                    print(f"  ! No ID column found in {file}")
                    continue
            else:
                id_col_use = id_col

            print(f"  Processing {file} with id_col={id_col_use}")

            # Columns that are qualitative (text)
            qualitative_cols = ['logros', 'retos', 'sugerencias', 'metodología',
                                'retos_ciclo_1', 'logros_ciclo_1', 'retos_ciclo_2', 'logros_ciclo_2',
                                'aprendizajes_linea', 'retos_linea', 'nivel', 'experto',
                                'experto_ciclo_1', 'experto_ciclo_2', 'formador',
                                'accion_evaluada', 'eje', 'foco', 'documentos',
                                'institucionalizacion_escenarios_reflexion_practica_docente',
                                'impacto_reflexion_en_cualificacion_practicas_educativas',
                                'sugerencias']

            for dane, group in df.groupby(df[id_col_use].apply(
                    lambda x: str(int(x)) if pd.notnull(x) and str(x).strip() not in ('', 'nan') else None)):
                if not dane or dane not in master_data:
                    continue

                agg = {}
                for col in group.columns:
                    if col == id_col_use:
                        continue
                    col_clean = str(col).strip().replace('\n', '').strip()
                    vals = [v for v in group[col].tolist()
                            if v is not None and not (isinstance(v, float) and np.isnan(v))
                            and str(v).strip() not in ('', 'nan')]
                    if not vals:
                        agg[col_clean] = None
                    elif col_clean in qualitative_cols or not all(
                            isinstance(v, (int, float, np.integer, np.floating)) for v in vals):
                        # Text: join unique non-empty strings
                        agg[col_clean] = ' / '.join(str(v).strip() for v in vals[:2])
                    else:
                        agg[col_clean] = round(float(np.nanmean([float(v) for v in vals])), 4)

                master_data[dane]["detalles"][key] = agg

        except Exception as e:
            print(f"Error processing {file}: {e}")
            import traceback
            traceback.print_exc()

    # ── 4. Additional data from Establecimientos.csv (enriched profile) ──
    if os.path.exists(establecimientos_path):
        try:
            # Semicolon separated, stripping whitespace from column names
            df_est = pd.read_csv(establecimientos_path, sep=';', encoding='latin-1')
            df_est.columns = [c.strip() for c in df_est.columns]
            print(f"  CSV Columns found: {df_est.columns.tolist()}")
            
            # Find the DANE id column
            id_col_est = None
            for c in df_est.columns:
                lc = c.lower().strip()
                if lc == 'código': # Direct match for 'Código'
                    id_col_est = c
                    break
                if 'códig' in lc and 'dane' in lc:
                    id_col_est = c
                    break
            
            if not id_col_est:
                if 'Código' in df_est.columns:
                    id_col_est = 'Código'

            if id_col_est:
                print(f"  Enriching with {establecimientos_path} using id_col={id_col_est}")
                target_cols = ['Zona', 'Niveles', 'Jornadas', 'Caracter', 'Especialidad']
                
                # Pre-convert DANE column to string to avoid matching issues
                df_est[id_col_est] = df_est[id_col_est].apply(lambda x: str(int(x)) if pd.notnull(x) and str(x).strip().isdigit() else None)

                enrich_count = 0
                for _, row in df_est.iterrows():
                    dane = row.get(id_col_est)
                    if not dane or dane not in master_data:
                        continue
                    
                    inst = master_data[dane]
                    enrich_count += 1
                    # We create or update "perfil_institucional"
                    perf = inst.get("perfil_institucional", {})
                    
                    for col in target_cols:
                        if col in df_est.columns:
                            val = str(row.get(col)).strip() if pd.notnull(row.get(col)) else ""
                            # Store original value for simplified reporting
                            perf[col.lower()] = val
                            
                            # Create Dummies/Flags
                            # Split by common delimiters
                            parts = [p.strip().upper() for p in val.replace('/', ',').replace('-', ',').replace(';', ',').split(',') if p.strip()]
                            for p in parts:
                                # Example: zona_RURAL, niveles_SECUNDARIA
                                dummy_key = f"{col.lower()}_{p.replace(' ', '_')}"
                                perf[dummy_key] = True
                    
                    inst["perfil_institucional"] = perf
                print(f"  Successfully enriched {enrich_count} institutions from {establecimientos_path}")
            else:
                print(f"  ! Could not find a DANE ID column in {establecimientos_path}")
        except Exception as e:
            print(f"Error enriching with {establecimientos_path}: {e}")

    # ── Output ──
    # ── 5. Datos Familia ──
    familia_path = os.path.join(root_dir, 'data', 'REPORTE COLEGIOS - FAMILIA.xlsx')
    if os.path.exists(familia_path):
        try:
            df_fam = pd.read_excel(familia_path, sheet_name='FAMILIA')
            for _, row in df_fam.iterrows():
                id_raw = row.get('id')
                if pd.isna(id_raw): continue
                dane = str(int(id_raw))
                if dane in master_data:
                    fam_data = {}
                    for col in df_fam.columns:
                        if col not in ['ied', 'id']:
                            val = clean_val(row.get(col))
                            fam_data[col] = val
                    master_data[dane]["familia"] = fam_data
            print("  Successfully integrated Familia data")
            
            # Exportar diccionario Familia
            df_fam_dict = pd.read_excel(familia_path, sheet_name='Hoja1')
            fam_dict_path = os.path.join(root_dir, 'data', 'diccionario_familia.json')
            # clean nan from dictionary
            fam_dict = []
            for _, row in df_fam_dict.iterrows():
                d = {}
                for k,v in row.to_dict().items():
                    d[k] = clean_val(v)
                fam_dict.append(d)
                
            with open(fam_dict_path, 'w', encoding='utf-8') as f:
                json.dump(fam_dict, f, ensure_ascii=False, indent=2)
            print("  Successfully generated diccionario_familia.json")
        except Exception as e:
            print(f"Error processing Familia: {e}")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(list(master_data.values()), f, ensure_ascii=False, indent=2)

    print(f"\nMerged data for {len(master_data)} institutions into {output_path}")

    # Quick check
    sample = list(master_data.values())[0] if master_data else None
    if sample:
        print(f"\nSample institution: {sample['institucion']}")
        print(f"  nombre_oficial: {sample.get('nombre_oficial')}")
        if 'perfil_institucional' in sample:
            print(f"  perfil_institucional (preview): {str(sample['perfil_institucional'])[:150]}...")
        else:
            print("  ! perfil_institucional NOT FOUND")


    # ── 5. Build and save Acciones Dictionary ──
    try:
        semaforo_e1_path = os.path.join(base_path, "Semáforo Etapa 1.xlsx")
        df_acc = pd.read_excel(semaforo_e1_path, sheet_name="acciones")
        acciones_dict = {}
        for _, r in df_acc.iterrows():
            aid = str(r.get("id")).strip()
            if aid and aid != "nan":
                acciones_dict[aid] = {
                    "eje": clean_val(r.get("eje")),
                    "ciclo": clean_val(r.get("ciclo")),
                    "objetivos": clean_val(r.get("objetivos")),
                    "acciones": clean_val(r.get("acciones"))
                }
        output_deprecated = os.path.join(root_dir, 'data', 'acciones_dict_deprecated.json')
        with open(output_deprecated, "w", encoding="utf-8") as f:
            json.dump(acciones_dict, f, indent=4, ensure_ascii=False)
        print(f"Successfully generated {output_deprecated}")
    except Exception as e:
        print(f"Could not generate acciones_dict.json: {e}")

if __name__ == "__main__":
    merge_data()
