import json
import re
import os
from urllib.parse import urlparse, parse_qs, unquote
from bs4 import BeautifulSoup

# Seu ID de ferramenta/afiliado para o Mercado Livre
ID_AFILIADO = "55954375"
NOME_ARQUIVO_HTML = "pagina.html"

def limpar_link_mercadolivre(link_original):
    if not link_original:
        return ""
    link_original = str(link_original)
    if "click1.mercadolivre" in link_original or "mclics/click" in link_original:
        parsed_url = urlparse(link_original)
        captured_params = parse_qs(parsed_url.query)
        if 'u' in captured_params:
            link_original = captured_params['u'][0] if isinstance(captured_params['u'], list) else captured_params['u']
        elif 'redirect_url' in captured_params:
            link_original = captured_params['redirect_url'][0] if isinstance(captured_params['redirect_url'], list) else captured_params['redirect_url']
            
    return unquote(link_original)

def definir_tag_filtro(titulo):
    tit = titulo.lower()
    if "creatina" in tit:
        return "creatina"
    elif "coqueteleira" in tit or "shaker" in tit or "copo" in tit or "acessorio" in tit:
        return "acessorios"
    return "whey"

def extrair_dados_do_html_local():
    lista_produtos = []

    # Verifica se você salvou o arquivo na pasta certa
    if not os.path.exists(NOME_ARQUIVO_HTML):
        print(f"Erro: O arquivo '{NOME_ARQUIVO_HTML}' não foi encontrado na pasta do script!")
        print("Por favor, salve a página do Mercado Livre com este nome exato nesta pasta.")
        return

    print(f"Lendo e processando o arquivo local '{NOME_ARQUIVO_HTML}'...")
    with open(NOME_ARQUIVO_HTML, "r", encoding="utf-8") as f:
        html_local = f.read()

    soup = BeautifulSoup(html_local, "html.parser")
    
    # Seletor universal robusto para capturar os blocos de produtos salvos
    itens = soup.select(".poly-card, [class*='poly-card'], .ui-search-layout__item, .ui-search-result__wrapper, .ui-search-result, .ui-search-layout__item-v2")
    print(f"Estrutura mapeada: Encontrados {len(itens)} blocos estruturais no seu HTML salvo.")

    for item in itens:
        try:
            titulo_tag = (
                item.select_one("a.poly-component__title") or 
                item.select_one(".poly-component__title-wrapper a") or
                item.select_one(".ui-search-item__title") or
                item.select_one(".ui-search-link") or
                item.select_one("h2 a") or
                item.select_one("h3 a")
            )
            
            if titulo_tag and titulo_tag.name != "a":
                titulo_tag = titulo_tag.find_parent("a") or titulo_tag.find("a") or titulo_tag

            if not titulo_tag:
                continue

            titulo = titulo_tag.get_text(strip=True)
            if not titulo or len(titulo) < 5:
                continue

            raw_link = titulo_tag.get("href", "") or (item.select_one("a")["href"] if item.select_one("a") else "")
            if not raw_link:
                continue

            link_limpo = limpar_link_mercadolivre(raw_link)
            base_link = link_limpo.split("#")[0] # Remove âncoras internas e garante string limpa
            divisor = "&" if "?" in base_link else "?"
            link_afiliado = f"{base_link}{divisor}matt_tool={ID_AFILIADO}"

            # Extração de Preços
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

            desconto_el = item.select_one(".poly-price__discount, .ui-search-price__discount, .ui-search-item__discount-percentage")
            desconto = desconto_el.get_text(strip=True) if desconto_el else "Sem desconto"

            selo_el = item.select_one(".poly-box--highlight, .ui-search-item__highlight-label, .ui-search-item__pub-label")
            selo_promocional = selo_el.get_text(strip=True).upper() if selo_el else ""

            frete = "Não especificado"
            texto_bloco = item.get_text().lower()
            if "grátis" in texto_bloco or "gratis" in texto_bloco:
                frete = "Frete Grátis"
            elif "full" in texto_bloco:
                frete = "Envio Full"

            img_tag = item.find("img")
            imagem = ""
            if img_tag:
                imagem = img_tag.get("data-src") or img_tag.get("src") or img_tag.get("data-lazy") or ""

            tag_filtro = definir_tag_filtro(titulo)

            if any(p.get("titulo") == titulo and p.get("preco_atual") == preco_atual for p in lista_produtos):
                continue

            lista_produtos.append({
                "titulo": titulo,
                "preco_antigo": preco_antigo,
                "preco_atual": preco_atual,
                "desconto": desconto,
                "tag": tag_filtro,          
                "selo": selo_promocional,    
                "frete": frete,
                "link_afiliado": link_afiliado, 
                "imagem": imagem,
                
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

    # Salva o arquivo final que o seu index.html vai ler
    with open("produtos.json", "w", encoding="utf-8") as arquivo_json:
        json.dump(lista_produtos, arquivo_json, indent=2, ensure_ascii=False)

    print(f"\n[SUCESSO] O arquivo 'produtos.json' foi gerado instantaneamente com {len(lista_produtos)} produtos!")

if __name__ == "__main__":
    extrair_dados_do_html_local()
