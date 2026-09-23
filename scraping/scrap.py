import json
import urllib.request


def buscar_mercado_livre_github():
    # URL oficial estável da API pública do Mercado Livre para Whey Protein
    url = "https://mercadolivre.com"

    print("Iniciando busca oficial com cabeçalhos de navegador (Texto Puro)...")

    try:
        # Mantém a simulação do navegador, mas remove o Accept-Encoding para receber JSON puro
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
        }

        req = urllib.request.Request(url, headers=headers)

        # Abre a conexão e lê o JSON de texto puro diretamente
        with urllib.request.urlopen(req) as response:
            conteudo = response.read()
            dados = json.loads(conteudo.decode("utf-8"))

        produtos = []
        resultados = dados.get("results", [])

        # Se a API vier vazia por algum motivo, deixa um aviso
        if not resultados:
            produtos.append({"aviso": "A API respondeu, mas a lista de resultados veio zerada."})

        # Estrutura os produtos exatamente no formato do seu projeto
        for item in resultados:
            produtos.append({
                "titulo": item.get("title"),
                "preco": float(item.get("price", 0)),
                "link": item.get("permalink"),
            })

        # Grava os dados limpos no seu repositório
        with open("scraping/produtos.json", "w", encoding="utf-8") as f:
            json.dump(produtos, f, ensure_ascii=False, indent=4)

        print(f"Sucesso total! {len(produtos)} produtos reais foram salvos.")

    except Exception as e:
        # Se houver qualquer falha, registra para sabermos o motivo exato
        erro_msg = [{"erro": f"Falha na API do Mercado Livre: {str(e)}"}]
        with open("scraping/produtos.json", "w", encoding="utf-8") as f:
            json.dump(erro_msg, f, ensure_ascii=False, indent=4)
        print(f"Ocorreu um erro no processamento: {e}")


if __name__ == "__main__":
    buscar_mercado_livre_github()
