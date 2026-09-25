import json
import re
from urllib.parse import urlparse, parse_qs, unquote
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# Separamos a URL de forma limpa para o navegador não se perder na inicialização
URL_BASE = "https://mercadolivre.com.br"
ID_AFILIADO = "55954375"

def limpar_link_mercadolivre(link_original):
    if not link_original:
        return ""
    if "click1.mercadolivre" in link_original or "mclics/click" in link_original:
        parsed_url = urlparse(link_original)
        captured_params = parse_qs(parsed_url.query)
        if 'u' in captured_params:
            return unquote(captured_params['u'][0])
        elif 'redirect_url' in captured_params:
            return unquote(captured_params['redirect_url'][0])
    return link_original

def extrair_dados_com_playwright():
    lista_produtos = []

    with sync_playwright() as p:
        print("Abrindo navegador em modo visível...")
        # headless=False garante que você vai ver exatamente qual página ele abriu
        browser = p.chromium.launch(headless=False) 
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print("Navegando até a lista de Whey Protein...")
        # Acessa a URL Base robusta
        page.goto(URL_BASE, wait_until="domcontentloaded", timeout=60000)
        
        # Aguarda 3 segundos para garantir que a grade de produtos carregou na tela
        print("Aguardando carregamento dos blocos de produtos...")
        page.wait_for_timeout(3000)

        # Rola a página para baixo para carregar as imagens dinâmicas (Lazy load)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2);")
        page.wait_for_timeout(1500)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
        page.wait_for_timeout(1500)

        html_conteudo = page.content()
        browser.close()

    soup = BeautifulSoup(html_conteudo, "html.parser")
    
    # Seletor cirúrgico baseado no seu print do poly-card
    itens = soup.select(".poly-card, [class*='poly-card'], .ui-search-layout__item")

    print(f"\n[HTML Lido] Encontrados {len(itens)} blocos de produtos na página mapeada.")

    for item in itens:
        try:
            # Título e Link extraído da classe contida no seu print
            titulo_tag = item.select_one("a.poly-component__title") or item.select_one(".poly-component__title-wrapper a")
            
            if not titulo_tag:
                titulo_tag = item.select_one(".ui-search-item__title, h2 a, h3 a")

            if not titulo_tag:
                continue

            titulo = titulo_tag.get_text(strip=True)
            raw_link = titulo_tag.get("href", "")

            if not raw_link or not titulo:
                continue

            link_limpo = limpar_link_mercadolivre(raw_link)
            base_link = link_limpo.split("#")[0]
            divisor = "&" if "?" in base_link else "?"
            link_afiliado = f"{base_link}{divisor}matt_tool={ID_AFILIADO}"

            # Mapeamento de Preços
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

            # Desconto
            desconto_el = item.select_one(".poly-price__discount, .ui-search-price__discount")
            desconto = desconto_el.get_text(strip=True) if desconto_el else "Sem desconto"

            # Tag
            tag_el = item.select_one(".poly-box--highlight, .ui-search-item__highlight-label")
            tag = tag_el.get_text(strip=True).upper() if tag_el else ""

            # Frete
            frete = "Não especificado"
            texto_bloco = item.get_text().lower()
            if "grátis" in texto_bloco or "gratis" in texto_bloco:
                frete = "Frete Grátis"
            elif "full" in texto_bloco:
                frete = "Envio Full"

            # Imagem
            img_tag = item.find("img")
            imagem = ""
            if img_tag:
                imagem = img_tag.get("data-src") or img_tag.get("src") or img_tag.get("data-lazy") or ""

            # Evita duplicados na mesma raspagem
            if any(p["titulo"] == titulo and p["preco_atual"] == preco_atual for p in lista_produtos):
                continue

            lista_produtos.append({
                "titulo": titulo,
                "preco_antigo": preco_antigo,
                "preco_atual": preco_atual,
                "desconto": desconto,
                "tag": tag,
                "frete": frete,
                "link_afiliado": link_afiliado,
                "imagem": imagem
            })

        except Exception:
            continue

    # Escreve no JSON
    with open("produtos.json", "w", encoding="utf-8") as arquivo_json:
        json.dump(lista_produtos, arquivo_json, indent=2, ensure_ascii=False)

    print(f"Sucesso! Arquivo 'produtos.json' gerado com {len(lista_produtos)} produtos.")

if __name__ == "__main__":
    extrair_dados_com_playwright()
