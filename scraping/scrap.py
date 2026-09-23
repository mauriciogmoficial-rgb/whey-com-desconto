import json
import os
import urllib.parse
import urllib.request


def buscar_mercado_livre_oficial():
    # O Python puxa as credenciais direto do cofre seguro do GitHub Actions
    client_id = os.environ.get("ML_CLIENT_ID")
    client_secret = os.environ.get("ML_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("Erro crítico: As chaves secretas não foram encontradas no ambiente.")
        return

    print("Iniciando fluxo de autenticação oficial OAuth 2.0...")

    try:
        # 1. SOLICITAÇÃO DO ACCESS TOKEN OFICIAL
        url_auth = "https://mercadolivre.com"
        payload = urllib.parse.urlencode({
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        }).encode("utf-8")

        req_auth = urllib.request.Request(
            url_auth, data=payload, headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        with urllib.request.urlopen(req_auth) as response_auth:
            dados_auth = json.loads(response_auth.read().decode("utf-8"))
            access_token = dados_auth.get("access_token")

        print("Token de acesso obtido com sucesso! Consultando produtos...")

        # 2. BUSCA AUTENTICADA DE PRODUTOS (WHEY PROTEIN)
        url_busca = "https://mercadolivre.com"
        req_busca = urllib.request.Request(
            url_busca,
            headers={
                "Authorization": f"Bearer {access_token}",
                "User-Agent": "WheyComDescontoApp/1.0",
                "Accept": "application/json",
            },
        )

        with urllib.request.urlopen(req_busca) as response_busca:
            dados_busca = json.loads(response_busca.read().decode("utf-8"))

        produtos = []
        resultados = dados_busca.get("results", [])

        # Estrutura os produtos reais da API
        for item in resultados:
            produtos.append({
                "titulo": item.get("title"),
                "preco": float(item.get("price", 0)),
                "link": item.get("permalink"),
            })

        if not produtos:
            produtos.append({"aviso": "Autenticado com sucesso, mas a busca não trouxe itens."})

        # 3. GRAVAÇÃO DO ARQUIVO FINAL NO REPOSITÓRIO
        with open("scraping/produtos.json", "w", encoding="utf-8") as f:
            json.dump(produtos, f, ensure_ascii=False, indent=4)

        print(f"Sucesso absoluto! {len(produtos)} produtos reais salvos via API Oficial.")

    except Exception as e:
        erro_msg = [{"erro": f"Erro no fluxo oficial de API: {str(e)}"}]
        with open("scraping/produtos.json", "w", encoding="utf-8") as f:
            json.dump(erro_msg, f, ensure_ascii=False, indent=4)
        print(f"Falha na execução: {e}")


if __name__ == "__main__":
    buscar_mercado_livre_oficial()
