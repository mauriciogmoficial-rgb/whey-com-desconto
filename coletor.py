import json
import requests

def buscar_30_mais_vendidos():
    # Lista com os IDs reais de suplementos campeões de venda
    ids_produtos = [
        "MLB3505232971", "MLB3105435912", "MLB3344129481", "MLB4012941211", 
        "MLB2194812491", "MLB3204918231", "MLB1928491822", "MLB3029481222"
    ]
    
    ids_formatados = ",".join(ids_produtos)
    url = f"https://mercadolibre.com{ids_formatados}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }
    
    produtos_lista = []
    
    try:
        print("Realizando consulta em lote via Requests...")
        resposta = requests.get(url, headers=headers, timeout=10)
        
        if resposta.status_code == 200:
            dados = resposta.json()
            
            for bloco in dados:
                if bloco.get('code') == 200:
                    item = bloco.get('body', {})
                    
                    if item.get('status') != 'active':
                        continue
                        
                    preco_base = item.get('price', 0)
                    preco_formatado = f"{preco_base:.2f}".replace('.', ',')
                    
                    foto = item.get('thumbnail', '').replace('-I.jpg', '-O.jpg')
                    if item.get('pictures') and len(item['pictures']) > 0:
                        foto = item['pictures'][0].get('secure_url', foto)
                    
                    prod = {
                        "titulo": item.get('title'),
                        "preco": preco_formatado,
                        "tag": "🔥 Oferta Oficial" if len(produtos_lista) < 3 else "🏷️ Suplemento",
                        "imagem": foto,
                        "linkOriginal": item.get('permalink')
                    }
                    produtos_lista.append(prod)
                    print(f"Sucesso ao ler: {item.get('title')[:25]}...")
                    
            return produtos_lista
            
    except Exception as e:
        print(f"Erro na conexao: {e}")
        
    return []
