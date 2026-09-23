import json
import urllib.parse
import urllib.request

def buscar_mercado_livre_github():
    # Como roda no GitHub Actions, fixamos o termo 'whey protein' diretamente aqui
    termo_busca = "whey protein"
    termo_api = urllib.parse.quote(termo_busca)
    url = f"https://mercadolivre.com{termo_api}"
    
    print(f"Iniciando busca oficial por: {termo_busca}")
    
    try:
        # Configura a requisição com cabeçalhos limpos aceitos pelo Mercado Livre
        req = urllib.request.Request(
            url, 
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'Accept': 'application/json'
            }
        )
        
        # Abre a conexão e lê os dados brutos da API
        with urllib.request.urlopen(req) as response:
            dados = json.loads(response.read().decode('utf-8'))
            
        produtos = []
        resultados = dados.get('results', [])
        
        print(f"Produtos retornados pela API: {len(resultados)}")
        
        # Extrai os campos exatamente como documentado na API oficial
        for item in resultados:
            produtos.append({
                "titulo": item.get('title'),
                "preco": float(item.get('price', 0)),
                "link": item.get('permalink')
            })
            
        # Salva o arquivo final estruturado na pasta correta
        with open('scraping/produtos.json', 'w', encoding='utf-8') as f:
            json.dump(produtos, f, ensure_ascii=False, indent=4)
            
        print(f"Sucesso total! {len(produtos)} produtos estruturados salvos em produtos.json.")
        
    except Exception as e:
        # Fallback caso a requisição HTTP falhe na nuvem
        erro_msg = [{"erro": f"Falha na API do Mercado Livre: {str(e)}"}]
        with open('scraping/produtos.json', 'w', encoding='utf-8') as f:
            json.dump(erro_msg, f, ensure_ascii=False, indent=4)
        print(f"Ocorreu um erro no processamento: {e}")

if __name__ == "__main__":
    buscar_mercado_livre_github()
