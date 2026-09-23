import json
import ssl
import urllib.request

def buscar_mercado_livre_oficial(termo_busca):
    # Formata o termo de busca para a URL oficial da API do Mercado Livre
    termo_api = urllib.parse.quote(termo_busca.strip())
    url = f"https://mercadolivre.com{termo_api}"
    
    print(f"Buscando por '{termo_busca}' no Mercado Livre...")
    
    # Ignora validações locais de SSL que o seu Windows antigo falha em checar
    contexto_ssl = ssl._create_unverified_context()
    
    try:
        # Define os cabeçalhos padrão recomendados pela documentação
        req = urllib.request.Request(
            url, 
            headers={
                'User-Agent': 'Mozilla/5.0',
                'Accept': 'application/json'
            }
        )
        
        # Abre a conexão usando o motor nativo do Python
        with urllib.request.urlopen(req, context=contexto_ssl) as response:
            # Converte o texto recebido diretamente em um dicionário Python
            dados = json.loads(response.read().decode('utf-8'))
            
        produtos = []
        
        # Lê a lista de resultados exatamente como documentado na API do Mercado Livre
        for item in dados.get('results', []):
            produtos.append({
                "titulo": item.get('title'),
                "preco": float(item.get('price', 0)),
                "link": item.get('permalink')
            })
            
        # Salva o arquivo final estruturado
        with open('produtos.json', 'w', encoding='utf-8') as f:
            json.dump(produtos, f, ensure_ascii=False, indent=4)
            
        print(f"Sucesso total! O arquivo 'produtos.json' foi criado com {len(produtos)} produtos.")
        
    except Exception as e:
        print(f"Ocorreu um erro ao processar os dados: {e}")

if __name__ == "__main__":
    termo = input("Digite o produto que deseja buscar: ")
    buscar_mercado_livre_oficial(termo)
