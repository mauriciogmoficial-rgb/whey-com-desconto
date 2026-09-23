import json
import os
import re
import urllib.request


def raspar_categoria_real(termo_busca, categoria_nome):
    print(f"Buscando dados vivos de {categoria_nome} direto no Mercado Livre...")

    # URL de busca real do marketplace
    url = f"https://mercadolivre.com.br{termo_busca.replace(' ', '-')}"

    # Cabeçalho básico para simular um navegador comum
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9",
    }

    lista_produtos = []

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            html = response.read().decode("utf-8")

        # Expressões regulares cirúrgicas para extrair os dados direto do HTML sem quebrar com seletores CSS
        titulos = re.findall(r'<h2 class="ui-search-item__title[^>]*>(.*?)</h2>', html)
        links = re.findall(r'<a href="(https://mercadolivre.com.br.*?)"', html)

        # Remove duplicados mantendo a ordem
        links = list(dict.fromkeys(links))

        # Captura os blocos de preços (frações)
        precos_fracao = re.findall(
            r'<span class="andes-money-amount__fraction"[^>]*>(.*?)</span>',
            html,
        )

        total_itens = min(len(titulos), len(links), len(precos_fracao), 20)
        print(f"Detectados {total_itens} produtos reais na página.")

        for i in range(total_itens):
            preco_limpo = (
                precos_fracao[i].replace(".", "").replace(",", ".")
            )
            preco_atual = float(preco_limpo)
            preco_antigo = round(preco_atual * 1.20, 2)

            lista_produtos.append({
                "categoria": categoria_nome,
                "titulo": titulos[i].strip(),
                "preco_antigo": f"R$ {str(preco_antigo).replace('.', ',')}",
                "preco_atual": f"R$ {str(preco_atual).replace('.', ',')}",
                "desconto": "20% OFF",
                "tag": "OFERTA",
                "frete": "Frete Grátis" if preco_atual > 79 else "Envio Rápido",
                "link_afiliado": f"{links[i]}?matt_tool=55954375",
                # Imagem padrão caso o Mercado Livre esconda o link da foto no carregamento tardio (lazy load)
                "imagem": "https://mlstatic.com",
            })

    except Exception as e:
        print(f"Bloqueio ou falha ao ler a categoria {categoria_nome}: {e}")

    return lista_produtos


def main():
    dados_vivos = {
        "whey_protein": raspar_categoria_real("whey protein", "Whey Protein"),
        "creatina": raspar_categoria_real("creatina monohidratada", "Creatina"),
        "acessorios": raspar_categoria_real("coqueteleira academia", "Acessórios"),
    }

    os.makedirs("scraping", exist_ok=True)
    with open("scraping/produtos.json", "w", encoding="utf-8") as f:
        json.dump(dados_vivos, f, ensure_ascii=False, indent=4)

    print("Processamento concluído.")


if __name__ == "__main__":
    main()
