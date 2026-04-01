import json
import pandas as pd
import os
import openai
from tqdm import tqdm
import time

# --- CONFIGURACIÓN ---
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "") 
MODEL = "gpt-4o-mini"
INPUT_FILE = "data/data_merged.json"
OUTPUT_FILE = "analysis/analisis_cualitativo_normalizado.csv"

# Diccionario Global de Taxonomía: (Etapa, Tipo) -> List[Categorias]
# El script irá llenando esto dinámicamente
global_taxonomy = {} 
LIMIT_SAMPLES = None
MAX_CATEGORIES_PER_GROUP = 20

def get_text_from_details(details_stage):
    """Extrae y limpia los campos cualitativos."""
    if not details_stage: return {}
    res = {}
    
    # Mapeo de campos
    mapping = {
        "Logros": ["logros", "logros_ciclo_1", "logros_ciclo_2", "logros_linea"],
        "Retos": ["retos", "retos_ciclo_1", "retos_ciclo_2", "retos_linea"],
        "Sugerencias": ["sugerencias", "recomendaciones"]
    }
    
    for label, fields in mapping.items():
        text = " ".join([str(details_stage.get(f, "")) for f in fields if details_stage.get(f)]).strip()
        if text: res[label] = text
    return res

def categorize_with_taxonomy(text, stage, field_type, api_key):
    """Clasifica el texto usando la taxonomía descubierta hasta ahora."""
    client = openai.OpenAI(api_key=api_key)
    
    # Obtener categorías existentes para este grupo específico
    taxonomy_key = f"{stage}_{field_type}"
    existing_categories = global_taxonomy.get(taxonomy_key, [])
    
    prompt = f"""
    Eres un analista de datos educativos. Tu objetivo es clasificar el texto en categorías NORMALIZADAS.
    
    ETAPA: {stage}
    TIPO DE CAMPO: {field_type}
    
    CATEGORÍAS EXISTENTES HASTA AHORA (Usa estas prioritariamente):
    {", ".join(existing_categories) if existing_categories else "Ninguna aún (serás el primero en definirlas)"}
    
    TEXTO A ANALIZAR:
    "{text}"
    
    TAREA:
    1. Identifica hasta 5 conceptos clave en el texto.
    2. Si un concepto encaja con una "CATEGORÍA EXISTENTE", usa EXACTAMENTE ese nombre.
    3. Si es un concepto nuevo, crea una etiqueta breve (1-3 palabras). 
    4. IMPORTANTE: No crees sinónimos. Si ya existe "Conectividad", no uses "Falta de Internet".
    {"5. LÍMITE ALCANZADO: No crees categorías nuevas, fuerza el mapeo a las existentes." if len(existing_categories) >= MAX_CATEGORIES_PER_GROUP else ""}
    
    FORMATO DE SALIDA:
    Solo las etiquetas separadas por comas.
    Ejemplo: Conectividad, Capacitación Docente, Infraestructura
    """
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=80,
            temperature=0
        )
        tags = [t.strip() for t in response.choices[0].message.content.split(",") if t.strip()]
        tags = tags[:5]
        
        # Actualizar Taxonomía Global con nuevos descubrimientos (si no hemos llegado al límite)
        if len(existing_categories) < MAX_CATEGORIES_PER_GROUP:
            for tag in tags:
                if tag not in existing_categories:
                    existing_categories.append(tag)
            global_taxonomy[taxonomy_key] = existing_categories
            
        return tags
    except Exception as e:
        print(f"Error API: {e}")
        return ["ERROR"]

def run_analysis():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    records = []
    api_key = os.environ.get("OPENAI_API_KEY", OPENAI_API_KEY)
    
    # Procesamiento secuencial para mantener la memoria de la taxonomía
    processed_count = 0
    for inst in tqdm(data, desc="Procesando colegios"):
        
        # --- Freno de seguridad ---
        if LIMIT_SAMPLES is not None and processed_count >= LIMIT_SAMPLES:
            print(f"\nAlcanzado el límite de {LIMIT_SAMPLES} colegios. Deteniendo...")
            break
            
        ied_id = inst.get("id")
        detalles = inst.get("detalles", {})
        
        for stage in ["e1", "e2", "e3", "e4", "e5", "e6"]:
            stage_data = detalles.get(stage)
            if not stage_data: continue
            
            fields = get_text_from_details(stage_data)
            
            for f_type, f_text in fields.items():
                # Esta llamada ahora conoce lo que aprendimos de los colegios anteriores
                categories = categorize_with_taxonomy(f_text, stage, f_type, api_key)
                
                row = {
                    "ID_Colegio": ied_id,
                    "Institucion": inst.get("institucion"),
                    "Municipio": inst.get("municipio"),
                    "Etapa": stage,
                    "Tipo": f_type,
                    "Cat_1": categories[0] if len(categories) > 0 else "",
                    "Cat_2": categories[1] if len(categories) > 1 else "",
                    "Cat_3": categories[2] if len(categories) > 2 else "",
                    "Cat_4": categories[3] if len(categories) > 3 else "",
                    "Cat_5": categories[4] if len(categories) > 4 else ""
                }
                records.append(row)
        
        processed_count += 1

    # Guardar
    df = pd.DataFrame(records)
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    
    # Guardar la taxonomía resultante para ver qué categorías se crearon
    with open("analysis/taxonomia_final.json", "w", encoding="utf-8") as f:
        json.dump(global_taxonomy, f, indent=4, ensure_ascii=False)
    
    print(f"\n¡Listo! Análisis normalizado en: {OUTPUT_FILE}")
    print(f"Taxonomía de referencia en: analysis/taxonomia_final.json")

if __name__ == "__main__":
    run_analysis()
