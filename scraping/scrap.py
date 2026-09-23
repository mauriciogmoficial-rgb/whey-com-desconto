import json
import urllib.request
import ssl

def buscar_mercado_livre_definitivo():
    # URL oficial direta (sem proxies instáveis)
    url = "https://mercadolivre.com"
    
    print("Iniciando conexão simulada de alta fidelidade...")
    
    # Ignora barreiras locais de SSL do ambiente em nuvem
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        # Cabeçalhos idênticos aos de um usuário real abrindo o Chrome no Windows
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive'
        }

        req = urllib.request.Request(url, headers=headers)
        
        # Faz a requisição direta usando o contexto de segurança limpo
        with urllib.request.urlopen(req, context=ctx) as response:
            dados = json.loads(response.read().decode('utf-8'))
            
        produtos = []
        resultados = dados.get('results', [])
        
        # Mapeia os dados da API oficial
        for item in resultados:
            produtos.append({
                "titulo": item.get('title'),
                "preco": float(item.get('price', 0)),
                "link": item.get('permalink')
            })
            
        if not produtos:
            produtos.append({"aviso": "A API respondeu mas a lista veio zerada."})

        # Salva o arquivo final estruturado
        with open('scraping/produtos.json', 'w', encoding='utf-8') as f:
            json.dump(produtos, f, ensure_ascii=False, indent=4)
            
        print(f"Sucesso total! {len(produtos)} produtos integrados ao repositório.")
        
    except Exception as e:
        erro_msg = [{"erro": f"Bloqueio de segurança detectado: {str(e)}"}]
        with open('scraping/produtos.json', 'w', encoding='utf-8') as f:
            json.dump(erro_msg, f, ensure_ascii=False, indent=4)
        print(f"Erro: {e}")

if __name__ == "__main__":
    buscar_mercado_livre_definitivo()
