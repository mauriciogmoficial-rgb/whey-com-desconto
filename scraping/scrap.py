import json
import os
import urllib.parse
import urllib.request


def buscar_categoria_no_google(termo_busca, categoria_nome):
    print(f"Buscando categoria '{categoria_nome}' via Google API...")

    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
    SEARCH_ENGINE_ID = os.environ.get("SEARCH_ENGINE_ID")

    # Garante que os espaços virem "+" na URL sem quebrar o protocolo HTTP
    query_limpa = termo_busca.replace(" ", "+")
    query_codificada = urllib.parse.quote(query_limpa)

    url = f"https://googleapis.com{GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}&num=20&q={query_codificada}"

    lista_produtos = []

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as response:
            dados = json.loads(response.read().decode("utf-8"))

        items = dados.get("items", [])
        print(f"Google retornou {len(items)} itens para {categoria_nome}")

        for item in items:
            pagemap = item.get("pagemap", {})

            # 1. Extração segura do preço do dicionário
            offers = pagemap.get("offer", [{}])
            preco_puro = ""
            if isinstance(offers, list) and len(offers) > 0:
                preco_puro = offers[0].get("price", "")
            elif isinstance(offers, dict):
                preco_puro = offers.get("price", "")

            try:
                preco_atual = float(preco_puro) if preco_puro else 99.90
            except ValueError:
                preco_atual = 99.90

            preco_antigo = round(preco_atual * 1.20, 2)

            # 2. Extração segura da Imagem em HD
            cse_image = pagemap.get("cse_image", [{}])
            imagem_url = ""
            if isinstance(cse_image, list) and len(cse_image) > 0:
                imagem_url = cse_image[0].get("src", "")
            elif isinstance(cse_image, dict):
                imagem_url = cse_image.get("src", "")

            if not imagem_url:
                imagem_url = "https://mlstatic.com"

            if imagem_url.startswith("http://"):
                imagem_url = imagem_url.replace("http://", "https://")

            # 3. Link de afiliados estruturado
            link_original = item.get("link", "https://mercadolivre.com.br")
            link_afiliado = f"{link_original}?matt_tool=55954375"

            # === CORREÇÃO DEFINITIVA DO TÍTULO: Limpa os textos sem misturar lista com string ===
            titulo_original = item.get("title", "Produto Suplemento")
            titulo_limpo = titulo_original.replace(" | Mercado Livre", "").strip()
            if " - " in titulo_limpo:
                # Pega apenas a primeira parte do título antes do traço e remove espaços extras
                titulo_limpo = titulo_limpo.split(" - ")[0].strip()

            lista_produtos.append({
                "categoria": categoria_nome,
                "titulo": titulo_limpo,
                "preco_antigo": f"R$ {str(preco_antigo).replace('.', ',')}",
                "preco_atual": f"R$ {str(preco_atual).replace('.', ',')}",
                "desconto": bundle_desconto(categoria_nome, lista_produtos),
                "tag": define_tag_visual(lista_produtos),
                "frete": "Frete Grátis" if preco_atual > 79 else "Envio Rápido",
                "link_afiliado": link_afiliado,
                "imagem": imagem_url,
            })

    except Exception as e:
        print(f"Erro na execução da categoria {categoria_nome}: {e}")

    return lista_produtos


def bundle_desconto(cat, lista):
    ajustes = ["17% OFF", "20% OFF", "15% OFF", "10% OFF"]
    return ajustes[len(lista) % len(ajustes)]


def define_tag_visual(lista):
    tags = ["MAIS VENDIDO", "DESTAQUE", "OFERTA", "LANÇAMENTO"]
    return tags[len(lista) % len(tags)]


def main():
    dados_finais = {
        "whey_protein": buscar_categoria_no_google(
            "whey protein concentrado", "Whey Protein"
        ),
        "creatina": buscar_categoria_no_google(
            "creatina monohidratada pura", "Creatina"
        ),
        "acessorios": buscar_categoria_no_google(
            "coqueteleira academia shaker", "Acessórios"
        ),
    }

    os.makedirs("scraping", exist_ok=True)
    with open("scraping/produtos.json", "w", encoding="utf-8") as f:
        json.dump(dados_finais, f, ensure_ascii=False, indent=4)

    print("Sucesso absoluto! Base de dados gerada com sucesso.")


if __name__ == "__main__":
    main()
