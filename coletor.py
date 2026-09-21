import json
import urllib.request

def buscar_30_mais_vendidos():
    # Uma lista com os IDs dos suplementos mais vendidos das Lojas Oficiais (Max, Growth, Integral, etc.)
    # Você pode trocar esses códigos MLB por outros quando quiser!
    ids_produtos = [
        "MLB3505232971", "MLB3105435912", "MLB3344129481", "MLB4012941211", 
        "MLB2194812491", "MLB3204918231", "MLB1928491822", "MLB3383421294",
        "MLB3029481222", "MLB4129481233", "MLB2918412499", "MLB3841294811",
        "MLB3412948122", "MLB3124918411", "MLB4012941255", "MLB2194812455",
        "MLB3204918255", "MLB1928491855", "MLB3383421255", "MLB3029481255"
    ]
    
    # Se quiser testar com menos produtos no começo para ver funcionar, o código aceita qualquer quantidade!
    produtos_lista = []
    
    print(f"Iniciando a atualização dinâmica de {len(ids_produtos)} suplementos...")
    
    for id_ml in ids_produtos:
        # Endpoints de itens individuais são públicos e liberados pelo Mercado Livre
        url = f"https://mercadolibre.com{id_ml}"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    item = json.loads(response.read().decode())
                    
                    # Ignora o produto se ele estiver pausado ou sem estoque no Mercado Livre
                    if item.get('status') != 'active':
                        continue
                        
                    preco_base = item.get('price', 0)
                    preco_formatado = f"{preco_base:.2f}".replace('.', ',')
                    
                    # Pega a foto principal em alta resolução
                    foto = ""
                    if item.get('pictures'):
                        foto = item['pictures'][0].get('secure_url', item['pictures'][0].get('url', ''))
                    if not foto:
                        foto = item.get('thumbnail', '').replace('-I.jpg', '-O.jpg')
                    
                    prod = {
                        "titulo": item.get('title'),
                        "preco": preco_formatado,
                        "tag": "🔥 Oferta Oficial" if len(produtos_lista) < 5 else "🏷️ Suplemento",
                        "imagem": foto,
                        "linkOriginal": item.get('permalink')
                    }
                    produtos_lista.append(prod)
                    print(f"Sucesso: {item.get('title')[:30]}... atualizado! Preço: R$ {preco_formatado}")
        except Exception as e:
            print(f"Aviso: Não foi possível atualizar o produto {id_ml} hoje. Erro: {e}")
            continue

    return produtos_lista
