# --- 2. FUNCIONES DE RECUPERACIÓN (VOLVEMOS A K=1) ---

def retrieve_bm25(query, top_k=1): # <- CAMBIO CRÍTICO: top_k=1
    search_payload = {
        "size": top_k,
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["title^3", "body"],
                "fuzziness": 0
            }
        },
        "_source": ["title", "body", "date", "source"]
    }
    
    try:
        response = es.search(index=INDEX_BM25, body=search_payload)
        hits = response['hits']['hits']
    except Exception as e:
        print(f"Error en Elasticsearch: {e}")
        return "", []
    
    if not hits:
        return "", []

    contexto_total = ""
    fuentes = []
    for hit in hits:
        doc = hit['_source']
        contexto_total += f"""
        TITULO: {doc.get('title')}
        FECHA: {doc.get('date', 'Desconocida')}
        FUENTE: {doc.get('source', 'Desconocida')}
        CONTENIDO: {doc.get('body')}
        """
        fuentes.append(f"{doc.get('source', 'Desconocido')} - {doc.get('title', 'Sin título')}")

    return contexto_total, fuentes

def retrieve_vectorial(query, top_k=1): # <- CAMBIO CRÍTICO: top_k=1
    vector_pregunta = embed_model.encode(query).tolist()
    
    query_knn = {
        "field": "vector_texto",
        "query_vector": vector_pregunta,
        "k": top_k,
        "num_candidates": 50
    }
    
    try:
        response = es.search(index=INDEX_VECTORIAL, knn=query_knn, _source=["title", "body", "date", "source"], size=top_k)
        hits = response['hits']['hits']
    except Exception as e:
        print(f"Error en Elasticsearch: {e}")
        return "", []
        
    if not hits:
        return "", []

    contexto_total = ""
    fuentes = []
    for hit in hits:
        doc = hit['_source']
        contexto_total += f"""
        TITULO: {doc.get('title')}
        FECHA: {doc.get('date', 'Desconocida')}
        FUENTE: {doc.get('source', 'Desconocida')}
        CONTENIDO: {doc.get('body')}
        """
        fuentes.append(f"{doc.get('source', 'Desconocido')} - {doc.get('title', 'Sin título')}")

    return contexto_total, fuentes

# --- 3. GENERACIÓN LIMPÍA (SIN WARNINGS) ---

def generar_respuesta(query, contexto_total):
    if not contexto_total.strip():
        return "No tengo información suficiente en mis archivos."
    
    messages = [
        {"role": "user", "content": f"""
        Eres un sistema de verificación de datos (Fact-Checking). 
        Tu objetivo es responder a la pregunta usando ÚNICAMENTE el texto que te proporciono abajo.

        REGLAS CRÍTICAS:
        1. Si la respuesta no aparece en el texto, responde exactamente: "No tengo información suficiente en mis archivos".
        2. No utilices conocimiento externo.
        3. No menciones otras noticias que no sean la proporcionada.

        ### TEXTO DE REFERENCIA:
        {contexto_total}
        
        ### PREGUNTA:
        {query}
        """}
    ]
    
    # Hemos quitado 'temperature' para arreglar el warning de do_sample=False
    outputs = pipe(
        messages,
        max_new_tokens=256,
        do_sample=False 
    )
    
    respuesta_limpia = outputs[0]['generated_text'][-1]['content']
    return respuesta_limpia.strip()