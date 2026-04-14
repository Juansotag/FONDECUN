import json

data = json.load(open('analysis/taxonomia_final.json', encoding='utf-8'))

# Mapeamos qué valores únicos existen en cada tipo
items_by_type = {
    'Logros': set(),
    'Retos': set(),
    'Sugerencias': set()
}

for k, v in data.items():
    if '_Logros' in k:
        q_type = 'Logros'
    elif '_Retos' in k:
        q_type = 'Retos'
    else:
        q_type = 'Sugerencias'
        
    for item in v:
        items_by_type[q_type].add(item.strip())

descriptions = {
    'Logros': {},
    'Retos': {},
    'Sugerencias': {}
}

def generate_desc(item, q_type):
    item_lower = item.lower()
    
    if q_type == 'Logros':
        if "evaluaci" in item_lower or "calificaci" in item_lower:
            return f"La institución evidencia un notable avance en los procesos de {item_lower}. Este logro consolida su capacidad de medir e identificar áreas formativas para potenciar el proceso de aprendizaje continuo."
        elif "curr" in item_lower or "planeaci" in item_lower or "plan " in item_lower:
            return f"Se reconoce un esfuerzo claro y efectivo hacia una mejor {item_lower}. La hoja de ruta pedagógica hoy se encuentra estructurada y visiblemente más alineada con los objetivos de la institución."
        elif "docente" in item_lower or "enseñanza" in item_lower or "pedag" in item_lower or "praxis" in item_lower:
            return f"La mejora tangible en aspectos de {item_lower} demuestra el compromiso por elevar la calidad educativa en el colegio. Se ha logrado impactar de manera profunda y positiva la forma de impartir el conocimiento."
        elif "emocion" in item_lower or "mindfulness" in item_lower or "neuro" in item_lower or "clima" in item_lower or "estrés" in item_lower:
            return f"El colegio ha implementado exitosamente enfoques centrados en {item_lower}. Este éxito propicia hoy un ambiente socioemocional significativamente más seguro y favorable para la educación."
        elif "comuni" in item_lower or "social" in item_lower or "equipo" in item_lower or "familia" in item_lower or "colaborativo" in item_lower:
            return f"Un gran logro institucional ha sido fortalecer áreas de {item_lower}. La creación de esta red de trabajo asegura y diversifica los mecanismos de apoyo para toda la comunidad."
        elif "tic" in item_lower or "tecnolog" in item_lower or "recurso" in item_lower or "herramienta" in item_lower or "conectividad" in item_lower:
            return f"La adopción de estrategias ligadas a {item_lower} representa un salto cualitativo significativo para el plantel. Esta modernización se ve reflejada en aulas más diversas y dinámicas."
        elif "reflexi" in item_lower or "análisis" in item_lower or "seguimiento" in item_lower or "autoevaluaci" in item_lower or "diagnóstico" in item_lower:
            return f"El colegio evidencia un enorme progreso implementando mecanismos de {item_lower}. La capacidad crítica adquirida permite a los equipos ajustarse iterativamente en busca de la calidad superior."
        elif "liderazgo" in item_lower or "directivo" in item_lower or "gestión" in item_lower or "institucional" in item_lower:
            return f"Como pilar clave, se valora el positivo desarrollo frente a {item_lower}. Dicha conquista permite canalizar hoy, con más orden y proyección, todos los esfuerzos pedagógicos."
        else:
            return f"La institución educativa demuestra progresos sumamente importantes y destacables en procesos relacionados con {item_lower}. El avance estructurado sobre este eje ha beneficiado fuertemente las dinámicas del colegio."

    elif q_type == 'Retos':
        if "evaluaci" in item_lower or "calificaci" in item_lower:
            return f"Uno de los principales desafíos recae en fortalecer y diversificar la {item_lower}. Resulta fundamental sortear este reto para no perder de vista los diagnósticos e impactos reales en el aprendizaje."
        elif "curr" in item_lower or "planeaci" in item_lower or "plan " in item_lower:
            return f"Persiste un nivel de desconexión o limitación en el ámbito de {item_lower}. Atender esta dificultad garantirá evitar improvisaciones que afecten las metas del periodo vigente."
        elif "docente" in item_lower or "enseñanza" in item_lower or "pedag" in item_lower or "praxis" in item_lower:
            return f"Es un desafío prioritario superar y transformar viejas metodologías asociadas a {item_lower}. Este cuello de botella impide que los estándares teóricos del programa lleguen fluidamente a las aulas."
        elif "emocion" in item_lower or "mindfulness" in item_lower or "neuro" in item_lower or "clima" in item_lower or "estrés" in item_lower:
            return f"A pesar del trabajo, persisten retos latentes en el manejo de {item_lower}. Estas tensiones o bloqueos no resueltos dificultan el ambiente indispensable para el correcto desarrollo del niño o joven."
        elif "comuni" in item_lower or "social" in item_lower or "equipo" in item_lower or "familia" in item_lower or "colaborativo" in item_lower:
            return f"Cerrar la brecha que existe respecto a mecanismos de {item_lower} requerirá un esfuerzo adicional importante. La falta de este tejido colaborativo retrasa o aísla diversos esfuerzos logrados."
        elif "tic" in item_lower or "tecnolog" in item_lower or "recurso" in item_lower or "herramienta" in item_lower or "conectividad" in item_lower:
            return f"Aún subsiste la necesidad imperiosa de integrar herramientas orientadas a {item_lower}. Evadir este obstáculo limita la pertinencia de las clases en un entorno cada día más digitalizado."
        elif "reflexi" in item_lower or "análisis" in item_lower or "seguimiento" in item_lower or "autoevaluaci" in item_lower or "diagnóstico" in item_lower:
            return f"Se observa como una debilidad sustancial el déficit en procesos recurrentes de {item_lower}. Dicha carencia reduce al máximo las posibilidades organizacionales de corregir, adaptar e innovar en fases críticas."
        elif "liderazgo" in item_lower or "directivo" in item_lower or "gestión" in item_lower or "institucional" in item_lower:
            return f"Consolidar la base que direcciona {item_lower} se mantiene como un área vulnerable y retadora. De persistir, la visión institucional y todos los recursos no terminan por cohesionar adecuadamente el cuerpo formativo."
        else:
            return f"La institución requiere sobreponerse activamente al desafiante manejo integral de {item_lower}. Subsanar las falencias de esta categoría potenciará y viabilizará los compromisos con mayor celeridad."

    else: # Sugerencias
        if "evaluaci" in item_lower or "calificaci" in item_lower:
            return f"Se recomienda diseñar e incorporar protocolos formativos con mayor peso hacia la {item_lower}. Utilizar instrumentos o rúbricas diagnósticas ayudará a ajustar gradualmente el rumbo metodológico de profesores y alumnos."
        elif "curr" in item_lower or "planeaci" in item_lower or "plan " in item_lower:
            return f"Es prioritario generar lineamientos urgentes que promuevan la homogeneización en torno a {item_lower}. Así se garantizará que todos los docentes avancen alineados de forma coherente con la filosofía central del colegio."
        elif "docente" in item_lower or "enseñanza" in item_lower or "pedag" in item_lower or "praxis" in item_lower:
            return f"Sugerimos de manera especial destinar tiempos institucionales obligatorios para renovar y afinar componentes en {item_lower}. Este es el momento propicio para buscar transformaciones reales y profundas desde el rol del formador."
        elif "emocion" in item_lower or "mindfulness" in item_lower or "neuro" in item_lower or "clima" in item_lower or "estrés" in item_lower:
            return f"Resultaría sumamente provechoso estructurar un proyecto de bienestar e insertar rutinas basadas fuertemente en {item_lower}. Esto establecerá indirectamente las redes socioemocionales básicas para un aprendizaje receptivo y sin estrés."
        elif "comuni" in item_lower or "social" in item_lower or "equipo" in item_lower or "familia" in item_lower or "colaborativo" in item_lower:
            return f"Se aconseja de forma prioritaria incentivar dinámicas sólidas que empoderen la noción de {item_lower}. Integrar apoderados u otros docentes aportará un valioso acompañamiento social e intelectual que no se consigue unilateralmente."
        elif "tic" in item_lower or "tecnolog" in item_lower or "recurso" in item_lower or "herramienta" in item_lower or "conectividad" in item_lower:
            return f"Consideramos un paso indispensable iniciar desde ya con la inclusión activa de estrategias transversales ligadas a {item_lower}. En ese aspecto recae gran parte del éxito para captar una atención motivada e inmersiva por parte del alumnado moderno."
        elif "reflexi" in item_lower or "análisis" in item_lower or "seguimiento" in item_lower or "autoevaluaci" in item_lower or "diagnóstico" in item_lower:
            return f"Nuestra recomendación máxima se centra en dedicar periodos sin interrupciones que obliguen a una sana {item_lower}. Sólo promoviendo esta cultura crítica la institución podrá generar una curva de aprendizaje adaptable a futuro."
        elif "liderazgo" in item_lower or "directivo" in item_lower or "gestión" in item_lower or "institucional" in item_lower:
            return f"Se urge empoderar las áreas responsables en la materia de {item_lower}. Facilitar estos perfiles organizativos desentrampará los ritmos y ordenará la ejecución, recursos y tiempos para todo el plantel restante."
        else:
            return f"Sugerimos encarecidamente implementar dinámicas y espacios focalizados plenamente en promover estrategias de {item_lower}. Iniciar inmediatamente la ejecución sobre este aspecto cimentará en poco tiempo mejoras pedagógicas sumamente palpables."

for q_type, items in items_by_type.items():
    for item in items:
        descriptions[q_type][item] = generate_desc(item, q_type)

with open('data/diccionario_cualitativo.json', 'w', encoding='utf-8') as f:
    json.dump(descriptions, f, ensure_ascii=False, indent=4)

total = sum(len(d) for d in descriptions.values())
print(f"Created diccionario_cualitativo.json with {total} total contextual items.")

