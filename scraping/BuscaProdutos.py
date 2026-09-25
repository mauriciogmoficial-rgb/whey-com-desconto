import json
import re
import os
from urllib.parse import urlparse, parse_qs, unquote
from bs4 import BeautifulSoup

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

def extrair_link_imagem_real(container_item):
    """
    Rastreia a fundo a nova estrutura poly-card buscando por tags picture,
    srcset ou atributos data para capturar o link real da imagem no mlstatic.
    """
    if not container_item:
        return ""
        
    # Busca prioritariamente na área da capa do card
    capa = container_item.select_one(".poly-card__portada") or container_item
    
    # 1. Tenta extrair de uma tag <picture> ou de múltiplos <source> se existirem
    sources = capa.find_all("source")
    for source in sources:
        srcset = source.get("srcset") or source.get("data-srcset")
        if srcset:
            # Pega o primeiro link válido que contenha o servidor do ML
            links = [l.strip().split(" ")[0] for l in srcset.split(",")]
            for link in links:
                if "mlstatic.com" in link and "data:image" not in link:
                    return link

    # 2. Varre todas as tags <img> do bloco
    imagens = capa.find_all("img")
    for img in imagens:
        # Lista ordenada de atributos onde o ML costuma esconder a foto real
        atributos = ["data-src", "srcset", "data-srcset", "dynamic-src", "src", "data-lazy"]
        for attr in atributos:
            valor = img.get(attr)
            if valor:
                # Se for uma string longa de srcset, quebra para pegar o primeiro link
                if "," in str(valor):
                    links = [l.strip().split(" ")[0] for l in str(valor).split(",")]
                    for link in links:
                        if "mlstatic.com" in link and "data:image" not in link:
                            return link
                else:
                    if "mlstatic.com" in str(valor) and "data:image" not in str(valor) and "blank.gif" not in str(valor):
                        return str(valor)
                        
    return ""

def otimizar_resolucao_imagem(url_img):
    """
    Força a imagem a puxar a versão em alta definição (-V.webp) se estiver em miniatura.
    """
    if not url_img:
        return ""
    # Converte os padrões de miniatura (-I ou -O) para o padrão grande (-V)
    url_img = url_img.replace("-I.jpg", "-O.jpg").replace("-I.webp", "-O.webp")
    url_img = url_img.replace("-O.jpg", "-V.jpg").replace("-O.webp", "-V.webp")
    return url_img

def extrair_dados_do_html_local():
    lista_produtos = []

    if not os.path.exists(NOME_ARQUIVO_HTML):
        print(f"Erro: O arquivo '{NOME_ARQUIVO_HTML}' não foi encontrado!")
        return

    print(f"Processando código renderizado do arquivo '{NOME_ARQUIVO_HTML}'...")
    with open(NOME_ARQUIVO_HTML, "r", encoding="utf-8") as f:
        html_local = f.read()

    soup = BeautifulSoup(html_local, "html.parser")
    
    # Seletores estruturais do DevTools
    itens = soup.select(".poly-card, [class*='poly-card'], .ui-search-layout__item, .ui-search-result__wrapper, .ui-search-result")
    print(f"Estrutura localizada: {len(itens)} possíveis blocos de produtos identificados.")

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
            base_link = link_limpo.split("#")[0]
            divisor = "&" if "?" in base_link else "?"
            link_afiliado = f"{base_link}{divisor}matt_tool={ID_AFILIADO}"

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

            # --- EXTRAÇÃO AVANÇADA DE IMAGENS ---
            raw_imagem = extrair_link_imagem_real(item)
            imagem = otimizar_resolucao_imagem(raw_imagem)

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

    with open("produtos.json", "w", encoding="utf-8") as arquivo_json:
        json.dump(lista_produtos, arquivo_json, indent=2, ensure_ascii=False)

    print(f"\n[SUCESSO] Arquivo 'produtos.json' regerado com as fotos extraídas a fundo! Total: {len(lista_produtos)} produtos.")

if __name__ == "__main__":
    extrair_dados_do_html_local()
