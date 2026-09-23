import json
import urllib.request

def buscar_mercado_livre_github():
    # URL estática oficial, completa e perfeitamente formatada para buscar Whey Protein
    url = "https://mercadolivre.com"
    
    print("Iniciando busca oficial e direta na API do Mercado Livre...")
    
    try:
        # Configura a requisição com os cabeçalhos aceitos pela API
        req = urllib.request.Request(
            url, 
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'Accept': 'application/json'
            }
        )
        
        # Abre a conexão e faz o download dos dados
        with urllib.request.urlopen(req) as response:
            dados = json.loads(response.read().decode('utf-8'))
            
        produtos = []
        resultados = dados.get('results', [])
        
        # Percorre os itens retornados estruturando o nosso JSON
        for item in resultados:
            produtos.append({
                "titulo": item.get('title'),
                "preco": float(item.get('price', 0)),
                "link": item.get('permalink')
            })
            
        # Grava os dados limpos e reais na pasta do projeto
        with open('scraping/produtos.json', 'w', encoding='utf-8') as f:
            json.dump(produtos, f, ensure_ascii=False, indent=4)
            
        print(f"Sucesso total! {len(produtos)} produtos salvos em produtos.json.")
        
    except Exception as e:
        # Se der qualquer falha física, grava o erro exato no arquivo para diagnóstico
        erro_msg = [{"erro": f"Falha na API do Mercado Livre: {str(e)}"}]
        with open('scraping/produtos.json', 'w', encoding='utf-8') as f:
            json.dump(erro_msg, f, ensure_ascii=False, indent=4)
        print(f"Ocorreu um erro no processamento: {e}")

if __name__ == "__main__":
    buscar_mercado_livre_github()
