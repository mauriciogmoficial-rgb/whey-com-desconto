import json
import re
from urllib.parse import urlparse, parse_qs, unquote
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

URL_BASE = "https://mercadolivre.com.br"
ID_AFILIADO = "55954375"

def limpar_link_mercadolivre(link_original):
    if not link_original:
        return ""
    if "click1.mercadolivre" in link_original or "mclics/click" in link_original:
        parsed_url = urlparse(link_original)
        captured_params = parse_qs(parsed_url.query)
        if 'u' in captured_params:
            return unquote(captured_params['u'])
        elif 'redirect_url' in captured_params:
            return unquote(captured_params['redirect_url'])
    return link_original

def definir_tag_filtro(titulo):
    """
    Define a tag de filtro exata para que os botões do seu index.html
    consigam separar os blocos na tela sem sumir com tudo.
    """
    tit = titulo.lower()
    if "creatina" in tit:
        return "creatina"
    elif "coqueteleira" in tit or "shaker" in tit or "copo" in tit or "acessorio" in tit:
        return "acessorios"
    # Como a página mãe já é filtrada, tudo o mais entra como whey por padrão
    return "whey"

def extrair_dados_com_playwright():
    lista_produtos = []

    with sync_playwright() as p:
        print("Abrindo navegador em modo visível...")
        browser = p.chromium.launch(headless=False) 
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print("Acessando a listagem de produtos no Mercado Livre...")
        page.goto(URL_BASE, wait_until="load", timeout=60000)
        
        print("Aguardando carregamento da estrutura visual...")
        page.wait_for_timeout(4000)

        # Rola a página em blocos médios idêntico ao script que trouxe os 110 itens
        print("Rolando a página para forçar o carregamento de todos os itens...")
        for i in range(1, 6):
            page.evaluate(f"window.scrollTo(0, (document.body.scrollHeight / 5) * {i});")
            page.wait_for_timeout(1000)

        html_conteudo = page.content()
        browser.close()

    soup = BeautifulSoup(html_conteudo, "html.parser")
    
    # SELETOR CAMPEÃO: O mesmo que encontrou os 110 blocos estruturais soltos na página
    itens = soup.select(".poly-card, [class*='poly-card'], .ui-search-layout__item")
    print(f"\n[HTML Lido] Sucesso! Encontrados {len(itens)} blocos de produtos na página.")

    for item in itens:
        try:
            titulo_tag = item.select_one("a.poly-component__title") or item.select_one(".poly-component__title-wrapper a")
            if not titulo_tag:
                titulo_tag = item.select_one(".ui-search-item__title, h2 a, h3 a")

            if not titulo_tag:
                continue

            titulo = titulo_tag.get_text(strip=True)
            if not titulo:
                continue

            raw_link = titulo_tag.get("href", "")
            if not raw_link:
                continue

            link_limpo = limpar_link_mercadolivre(raw_link)
            base_link = link_limpo.split("#")
            divisor = "&" if "?" in base_link else "?"
            link_afiliado = f"{base_link}{divisor}matt_tool={ID_AFILIADO}"

            # Mapeamento do Preço Atual e Preço Antigo
            valores_container = item.find_all("span", class_="andes-money-amount")
            preco_antigo = "Não informado"
            preco_atual = "Não informado"

            for v in valores_container:
                is_original = (
                    v.find_parent("s") 
                    or "original" in str(v.get("class", ""))
                    or v.find_parent(class_=re.compile(r".*comparison.*"))
                )

                fracao = v.find("span", class_="andes-money-amount__fraction")
                centavos_el = v.find("span", class_="andes-money-amount__cents")
                centavos = centavos_el.get_text(strip=True) if centavos_el else "00"

                if fracao:
                    valor_txt = f"R$ {fracao.get_text(strip=True)},{centavos}"
                    if is_original:
                        preco_antigo = valor_txt
                    else:
                        preco_atual = valor_txt

            # Desconto, Selo promocional e Frete
            desconto_el = item.select_one(".poly-price__discount, .ui-search-price__discount")
            desconto = desconto_el.get_text(strip=True) if desconto_el else "Sem desconto"

            selo_el = item.select_one(".poly-box--highlight, .ui-search-item__highlight-label")
            selo_promocional = selo_el.get_text(strip=True).upper() if selo_el else ""

            frete = "Não especificado"
            texto_bloco = item.get_text().lower()
            if "grátis" in texto_bloco or "gratis" in texto_bloco:
                frete = "Frete Grátis"
            elif "full" in texto_bloco:
                frete = "Envio Full"

            # Imagem do Produto
            img_tag = item.find("img")
            imagem = ""
            if img_tag:
                imagem = img_tag.get("data-src") or img_tag.get("src") or img_tag.get("data-lazy") or ""

            # Vincula dinamicamente a tag ("whey", "creatina", "acessorios") para bater com o index.html
            tag_filtro = definir_tag_filtro(titulo)

            # Evita duplicidade na listagem
            if any(p.get("titulo") == titulo and p.get("preco_atual") == preco_atual for p in lista_produtos):
                continue

            lista_produtos.append({
                "titulo": titulo,
                "preco_antigo": preco_antigo,
                "preco_atual": preco_atual,
                "desconto": desconto,
                "tag": tag_filtro,          # Atributo crucial corrigido para os filtros do seu site
                "selo": selo_promocional,    
                "frete": frete,
                "link_afiliado": link_afiliado,
                "imagem": imagem,
                
                # Mapeamento espelho para blindagem total do front-end
                "title": titulo,
                "oldPrice": preco_antigo,
                "price": preco_atual,
                "discount": desconto,
                "category": tag_filtro,
                "shipping": frete,
                "link": link_afiliado,
                "image": imagem
            })

        except Exception:
            continue

    # Gravação direta do JSON sem travas locais
    with open("produtos.json", "w", encoding="utf-8") as arquivo_json:
        json.dump(lista_produtos, arquivo_json, indent=2, ensure_ascii=False)

    print(f"\n[SUCESSO] O arquivo 'produtos.json' foi restaurado e gerou {len(lista_produtos)} itens integrados!")

if __name__ == "__main__":
    extrair_dados_com_playwright()
