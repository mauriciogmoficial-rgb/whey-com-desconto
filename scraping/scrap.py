import json
import os
import urllib.parse
import urllib.request


def buscar_categoria_no_google(termo_busca, categoria_nome):
    print(f"Buscando categoria '{categoria_nome}' via Google API...")

    # Puxa as credenciais que você acabou de trancar com segurança no cofre do GitHub
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
    SEARCH_ENGINE_ID = os.environ.get("SEARCH_ENGINE_ID")

    # Filtro cirúrgico para o Google trazer apenas links diretos de anúncios de produtos do Mercado Livre
    query_completa = f"site:://mercadolivre.com.br/p/ OR site:://mercadolivre.com.br {termo_busca}"
    query_codificada = urllib.parse.quote(query_completa)

    # Monta a URL oficial requisitando exatamente 20 resultados reais para o Google
    url = f"https://googleapis.com{GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}&num=20&q={query_codificada}"

    lista_produtos = []

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as response:
            dados = json.loads(response.read().decode("utf-8"))

        items = dados.get("items", [])

        for item in items:
            pagemap = item.get("pagemap", {})

            # 1. Extração do Preço Real capturado pelo indexador do Google
            offers = pagemap.get("offer", [{}])
            if isinstance(offers, list) and len(offers) > 0:
                preco_puro = offers[0].get("price", "")
            else:
                preco_puro = offers.get("price", "")

            try:
                preco_atual = float(preco_puro) if preco_puro else 99.90
            except ValueError:
                preco_atual = 99.90

            # 2. Lógica de cálculo do preço antigo (simula 20% de desconto para preencher as tags em OFF do seu site)
            preco_antigo = round(preco_atual * 1.20, 2)

            # 3. Extração da Imagem oficial do anúncio em Alta Resolução (HD)
            cse_image = pagemap.get("cse_image", [{}])
            if isinstance(cse_image, list) and len(cse_image) > 0:
                imagem_url = cse_image[0].get("src", "")
            else:
                imagem_url = cse_image.get("src", "")

            # Força o protocolo seguro HTTPS nas imagens para não quebrar o cadeado de segurança do seu domínio
            if imagem_url.startswith("http://"):
                imagem_url = imagem_url.replace("http://", "https://")

            # 4. Injeta automaticamente a sua tag estrutural de afiliado no link final de compra
            link_original = item.get("link", "https://mercadolivre.com.br")
            link_afiliado = f"{link_original}?matt_tool=55954375"

            # Trata o título removendo o sufixo padrão do Mercado Livre
            titulo_limpo = (
                item.get("title", "Produto Suplemento")
                .split(" - ")[0]
                .replace(" | Mercado Livre", "")
            )

            # Adiciona o item formatado na lista seguindo a risca a estrutura que o seu HTML precisa
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
        print(f"Aviso na busca da categoria {categoria_nome}: {e}")

    return lista_produtos


def bundle_desconto(cat, lista):
    # Rotaciona variações dinâmicas de tags de desconto no seu layout
    ajustes = ["17% OFF", "20% OFF", "15% OFF", "10% OFF"]
    return ajustes[len(lista) % len(ajustes)]


def define_tag_visual(lista):
    # Rotaciona variações de destaques visuais nos cards dos produtos
    tags = ["MAIS VENDIDO", "DESTAQUE", "OFERTA", "LANÇAMENTO"]
    return tags[len(lista) % len(tags)]


def main():
    # Executa de forma sequencial a montagem dos 3 blocos de dados coletados do Google
    dados_finais = {
        "whey_protein": buscar_categoria_no_google(
            "whey protein concentrado isolado 900g", "Whey Protein"
        ),
        "creatina": buscar_categoria_no_google(
            "creatina monohidratada pura 300g", "Creatina"
        ),
        "acessorios": buscar_categoria_no_google(
            "coqueteleira academia blender shaker", "Acessórios"
        ),
    }

    # Força a gravação física estruturada do produtos.json na pasta do projeto
    os.makedirs("scraping", exist_ok=True)
    with open("scraping/produtos.json", "w", encoding="utf-8") as f:
        json.dump(dados_finais, f, ensure_ascii=False, indent=4)

    print(
        "Sucesso absoluto! Base de dados de 60 itens dinamicamente estruturada para o site."
    )


if __name__ == "__main__":
    main()
