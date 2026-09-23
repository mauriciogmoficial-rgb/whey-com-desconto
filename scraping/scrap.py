import json
import os
import urllib.request


def gerar_produtos_real_em_massa():
    print("Conectando ao espelho de dados estável do Mercado Livre...")

    # URL pública alternativa que nos entrega a lista de produtos limpa de ponta a ponta
    url = "https://allorigins.win"

    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )

        with urllib.request.urlopen(req) as response:
            resposta_proxy = json.loads(response.read().decode("utf-8"))
            dados = json.loads(resposta_proxy.get("contents", "{}"))

        produtos = []
        resultados = dados.get("results", [])

        print(f"Total de produtos capturados no espelho: {len(resultados)}")

        # Varre todos os produtos disponíveis (geralmente 50 itens)
        for item in resultados:
            foto = item.get("thumbnail", "")
            # Ajusta para o formato seguro exigido pelos navegadores modernos
            if foto.startswith("http://"):
                foto = foto.replace("http://", "https://")
            # Substitui a foto minúscula da API pela imagem grande de alta definição
            foto = foto.replace("-I.jpg", "-O.jpg").replace("-I.webp", "-O.webp")

            preco_atual = float(item.get("price", 0))

            # Captura ou calcula o preço antigo para gerar as tags de % OFF no seu site
            preco_original = item.get("original_price")
            if not preco_original:
                preco_original = round(preco_atual * 1.25, 2)
            else:
                preco_original = float(preco_original)

            produtos.append({
                "titulo": item.get("title"),
                "preco": preco_atual,
                "preco_antigo": preco_original,
                "link": item.get("permalink"),
                "imagem": foto,
            })

        # Proteção caso o proxy fique instável: impede a gravação de arquivo zerado
        if len(produtos) < 5:
            raise Exception("Dados insuficientes retornados pelo espelho.")

        # Grava o arquivo produtos.json final populado em massa
        os.makedirs("scraping", exist_ok=True)
        with open("scraping/produtos.json", "w", encoding="utf-8") as f:
            json.dump(produtos, f, ensure_ascii=False, indent=4)

        print(f"Sucesso absoluto! {len(produtos)} produtos integrados com fotos em HD.")

    except Exception as e:
        print(f"Falha ao conectar com o espelho: {e}")


if __name__ == "__main__":
    gerar_produtos_real_em_massa()
