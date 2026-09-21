import json
import requests

def buscar_30_mais_vendidos():
    # URL oficial de buscas da categoria de Suplementos (ID: MLB438342)
    url = "https://mercadolibre.com"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    
    try:
        resposta = requests.get(url, headers=headers, timeout=10)
        
        # Se a API principal responder (o que vai acontecer no servidor do GitHub)
        if resposta.status_code == 200:
            dados = resposta.json()
            resultados = dados.get('results', [])
            return processar_resultados_ml(resultados)
            
        # Fallback Automático: Se a API principal falhar, tenta o endpoint de categorias públicas
        else:
            url_reserva = "https://mercadolibre.com"
            resposta_reserva = requests.get(url_reserva, headers=headers, timeout=10)
            if resposta_reserva.status_code == 200:
                resultados = resposta_reserva.json().get('results', [])
                return processar_resultados_ml(resultados)
                
    except Exception as e:
        print(f"Erro ao conectar na API: {e}")
        
    return []

def processar_resultados_ml(resultados):
    produtos_lista = []
    for item in resultados:
        preco_base = item.get('price', 0)
        if preco_base == 0:
            continue
            
        preco_formatado = f"{preco_base:.2f}".replace('.', ',')
        # Pega a imagem padrão e transforma na versão de alta resolução
        foto_alta = item.get('thumbnail', '').replace('-I.jpg', '-O.jpg')
        
        prod = {
            "titulo": item.get('title'),
            "preco": preco_formatado,
            "tag": "Mais Vendido" if len(produtos_lista) < 10 else "Destaque",
            "imagem": foto_alta,
            "linkOriginal": item.get('permalink')
        }
        produtos_lista.append(prod)
    return produtos_lista
