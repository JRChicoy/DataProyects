import torch
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
def ask_rag(query, top_k=1): 
    """
    Función RAG para TFG: Recupera 1 noticia y genera respuesta basada estrictamente en ella.
    Retorna un diccionario con los datos separados.
    """
    # --- A. BÚSQUEDA ---
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
        response = es.search(index="noticias_tfg", body=search_payload)
        hits = response['hits']['hits']
    except Exception as e:
        return {"error": f"Error en Elasticsearch: {e}"}
    
    if not hits:
        return {"error": " NO ENCONTRADO: No hay ninguna noticia que coincida exactamente con la búsqueda."}

    # --- B. EXTRACCIÓN --- modificamos para concatenar todas las noticias recuperadas en un solo contexto (top_k mayor a 1)
    contexto_unico = ""
    for i, hit in enumerate(hits):
        doc = hit['_source']
        contexto_unico += f"""
        --- NOTICIA {i+1} ---
        TITULO: {doc.get('title')}
        FECHA: {doc.get('date', 'Desconocida')}
        FUENTE: {doc.get('source', 'Desconocida')}
        CONTENIDO: {doc.get('body')}
        \n"""

    # --- C. PROMPT ---
    messages = [
        {"role": "user", "content": f"""
        Eres un sistema de verificación de datos (Fact-Checking). 
        Tu objetivo es responder a la pregunta usando ÚNICAMENTE el texto que te proporciono abajo.

        REGLAS CRÍTICAS:
        1. Si la respuesta no aparece en el texto, responde exactamente: "No tengo información suficiente en mis archivos".
        2. Formula tu respuesta usando solo los datos del texto. Puedes conectar ideas que estén en la noticia, pero NUNCA uses conocimiento externo ni inventes datos.
        3. No menciones otras noticias que no sean las proporcionadas.
        4. Se claro y conciso.

        ### TEXTO DE REFERENCIA:
        {contexto_unico}
        
        ### PREGUNTA:
        {query}
        """}
    ]

    # --- D. GENERACIÓN ---
    outputs = pipe(
        messages,
        max_new_tokens=256,
        do_sample=False,
        temperature=0.0, 
    )
    
    # --- E. RETORNO ESTRUCTURADO  ---
    respuesta_limpia = outputs[0]['generated_text'][-1]['content']
    
    return {
        "titulo": [hit['_source'].get('title') for hit in hits],
        "contenido": [hit['_source'].get('body') for hit in hits],
        "fecha": [hit['_source'].get('date', 'Desconocida') for hit in hits],
        "fuente": [hit['_source'].get('source', 'Desconocida') for hit in hits],
        "respuesta_rag": respuesta_limpia
    }

print("Sistema RAG (k=1) reconfigurado para devolver datos separados.")


def ask_rag_vectorial(query, top_k=1): 
    """
    Función RAG Vectorial: Recupera 1 noticia (kNN) y genera respuesta basada estrictamente en ella.
    Retorna un diccionario con los datos separados.
    """
    # --- A. BÚSQUEDA VECTORIAL (kNN) ---
    vector_pregunta = embed_model.encode(query).tolist()
    
    query_knn = {
        "field": "vector_texto",
        "query_vector": vector_pregunta,
        "k": top_k,
        "num_candidates": 50
    }
    
    try:
        response = es.search(
            index="noticias_tfg_vectores", 
            knn=query_knn, 
            _source=["title", "body", "date", "source"], 
            size=top_k
        )
        hits = response['hits']['hits']
    except Exception as e:
        return {"error": f"Error en Elasticsearch: {e}"}
    
    if not hits:
        return {"error": " NO ENCONTRADO: No hay ninguna noticia cercana a esta búsqueda."}

    # --- B. EXTRACCIÓN ---
    contexto_unico = ""
    for i, hit in enumerate(hits):
        doc = hit['_source']
        contexto_unico += f"""
        --- NOTICIA {i+1} ---
        TITULO: {doc.get('title')}
        FECHA: {doc.get('date', 'Desconocida')}
        FUENTE: {doc.get('source', 'Desconocida')}
        CONTENIDO: {doc.get('body')}
        \n"""

    # --- C. PROMPT ---
    messages = [
        {"role": "user", "content": f"""
        Eres un sistema de verificación de datos (Fact-Checking). 
        Tu objetivo es responder a la pregunta usando ÚNICAMENTE el texto que te proporciono abajo.

        REGLAS CRÍTICAS:
        1. Si la respuesta no aparece en el texto, responde exactamente: "No tengo información suficiente en mis archivos".
        2. Formula tu respuesta usando solo los datos del texto. Puedes conectar ideas que estén en la noticia, pero NUNCA uses conocimiento externo ni inventes datos.
        3. No menciones otras noticias que no sean las proporcionadas.
        4. Se claro y conciso.

        ### TEXTO DE REFERENCIA:
        {contexto_unico}
        
        ### PREGUNTA:
        {query}
        """}
    ]

    # --- D. GENERACIÓN ---
    outputs = pipe(
        messages,
        max_new_tokens=256,
        do_sample=False,
        temperature=0.0, 
    )
    
    # --- E. RETORNO ESTRUCTURADO  ---
    respuesta_limpia = outputs[0]['generated_text'][-1]['content']
    
    return {
        "titulo": [hit['_source'].get('title') for hit in hits],
        "contenido": [hit['_source'].get('body') for hit in hits],
        "fecha": [hit['_source'].get('date', 'Desconocida') for hit in hits],
        "fuente": [hit['_source'].get('source', 'Desconocida') for hit in hits],
        "respuesta_rag": respuesta_limpia
    }


print("Sistema RAG Vectorial (k=1) configurado.")