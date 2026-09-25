import json
import re
import os
from urllib.parse import urlparse, parse_qs, unquote
from bs4 import BeautifulSoup
import requests

ID_AFILIADO = "55954375"
NOME_ARQUIVO_HTML = "pagina.html"

# Headers reais para o validador de links não ser bloqueado pelo Mercado Livre
HEADERS_VALIDADOR = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8"
}

def limpar_link_mercadolivre(link_original):
    if not link_original:
        return ""
    link_original = str(link_original)
    if "click1.mercadolivre" in link_original or "mclics/click" in link_original:
        parsed_url = urlparse(link_original)
        captured_params = parse_qs(parsed_url.query)
        if 'u' in captured_params:
            link_original = captured_params['u'] if isinstance(captured_params['u'], list) else captured_params['u']
        elif 'redirect_url' in captured_params:
            link_original = captured_params['redirect_url'] if isinstance(captured_params['redirect_url'], list) else captured_params['redirect_url']
            
    return unquote(link_original)

def definir_tag_filtro(titulo):
    tit = titulo.lower()
    if "creatina" in tit:
        return "creatina"
    elif "coqueteleira" in tit or "shaker" in tit or "copo" in tit or "acessorio" in tit:
        return "acessorios"
    return "whey"

def validar_produto_na_origem(url_produto, preco_capturado):
    """
    Acessa o link do produto em segundo plano para checar se a página existe 
    e se o preço atualizado bate com o que foi coletado.
    """
    try:
        # Faz uma requisição rápida para a página do produto
        response = requests.get(url_produto, headers=HEADERS_VALIDADOR, timeout=5)
        
        # Se retornar erro de página inexistente (404, 410) ou bloqueios graves, descarta
        if response.status_code in [404, 410] or "produto-nao-encontrado" in response.url:
            print(f"-> [Link Inválido] Produto inexistente removido: {url_produto}")
            return False, None

        # Verifica se o preço mudou dentro da página interna do produto
        soup_interno = BeautifulSoup(response.text, "html.parser")
        container_preco = soup_interno.select_one(".andes-money-amount__fraction")
        
        if container_preco:
            valor_real = container_preco.get_text(strip=True)
            centavos_el = soup_interno.select_one(".andes-money-amount__cents")
            centavos_real = centavos_el.get_text(strip=True) if centavos_el else "00"
            preco_interno_atualizado = f"R$ {valor_real},{centavos_real}"
            
            if preco_interno_atualizado != preco_capturado:
                print(f"-> [Preço Atualizado] Ajustado de {preco_capturado} para {preco_interno_atualizado}")
                return True, preco_interno_atualizado
                
        return True, preco_capturado
    except Exception:
        # Se der timeout ou falha de rede temporária, mantém o produto por segurança
        return True, preco_capturado

def extrair_link_imagem_real(container_item):
    if not container_item:
        return ""
    capa = container_item.select_one(".poly-card__portada") or container_item
    sources = capa.find_all("source")
    for source in sources:
        srcset = source.get("srcset") or source.get("data-srcset")
        if srcset:
            parts = [p.strip().split(" ") for p in srcset.split(",")]
            for p in parts:
                if "mlstatic.com" in p and "data:image" not in p:
                    return p[0] if isinstance(p, list) else p

    imagens = capa.find_all("img")
    for img in imagens:
        atributos = ["data-src", "srcset", "data-srcset", "dynamic-src", "src", "data-lazy"]
        for attr in atributos:
            valor = img.get(attr)
            if valor:
                if "," in str(valor):
                    parts = [p.strip().split(" ") for p in str(valor).split(",")]
                    for p in parts:
                        if "mlstatic.com" in p and "data:image" not in p:
                            return p[0] if isinstance(p, list) else p
                else:
                    val_str = str(valor)
                    if "mlstatic.com" in val_str and "data:image" not in val_str and "blank.gif" not in val_str:
                        return val_str
    return ""

def otimizar_resolucao_imagem(url_img):
    if not url_img:
        return ""
    url_img = url_img.replace("-I.jpg", "-O.jpg").replace("-I.webp", "-O.webp")
    url_img = url_img.replace("-O.jpg", "-V.jpg").replace("-O.webp", "-V.webp")
    return url_img

def extrair_dados_do_html_local():
    lista_produtos = []

    if not os.path.exists(NOME_ARQUIVO_HTML):
        print(f"Erro: O arquivo '{NOME_ARQUIVO_HTML}' não foi encontrado!")
        return

    print(f"Processando arquivo local '{NOME_ARQUIVO_HTML}'...")
    with open(NOME_ARQUIVO_HTML, "r", encoding="utf-8") as f:
        html_local = f.read()

    soup = BeautifulSoup(html_local, "html.parser")
    itens = soup.select(".poly-card, [class*='poly-card'], .ui-search-layout__item, .ui-search-result__wrapper, .ui-search-result")
    print(f"Estrutura localizada: {len(itens)} possíveis blocos de produtos identificados.")

    for item in itens:
        try:
            titulo_tag = (
                item.select_one("a.poly-component__title") or 
                item.select_one(".poly-component__title-wrapper a") or
                item.select_one(".ui-search-item__title") or
                item.select_one(".ui-search-link")
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

            # --- ETAPA DE VALIDAÇÃO CRUCIAL EM TEMPO REAL ---
            # Testa se o link limpo responde e se o preço interna continua igual
            print(f"Validando: {titulo[:30]}...")
            link_valido, preco_atualizado = validar_produto_na_origem(base_link, preco_atual)
            
            if not link_valido:
                # Pula o produto se ele estiver quebrado ou inexistente
                continue
            
            # Atualiza o preço atual caso ele tenha mudado no Mercado Livre
            preco_atual = preco_atualizado

            desconto_el = item.select_one(".poly-price__discount, .ui-search-price__discount, .ui-search-item__discount-percentage")
            desconto = desconto_el.get_text(strip=True) if desconto_el else "Sem desconto"

            selo_el = item.select_one(".poly-box--highlight, .ui-search-item__highlight-label")
            selo_promocional = selo_el.get_text(strip=True).upper() if selo_el else ""

            frete = "Não especificado"
            texto_bloco = item.get_text().lower()
            if "grátis" in texto_bloco or "gratis" in texto_bloco:
                frete = "Frete Grátis"
            elif "full" in texto_bloco:
                frete = "Envio Full"

            raw_imagem = extrair_link_imagem_real(item)
            imagem = otimizar_resolucao_imagem(raw_imagem)

            tag_filtro = definir_tag_filtro(titulo)

            if any(p.get("titulo") == titulo and p.get("preco_atual") == preco_atual for p in lista_produtos):
                continue

            lista_produtos.append({
                "titulo": titulo, "title": titulo,
                "preco_antigo": preco_antigo, "oldPrice": preco_antigo,
                "preco_atual": preco_atual, "price": preco_atual,
                "desconto": desconto, "discount": desconto,
                "tag": tag_filtro, "category": tag_filtro,
                "selo": selo_promocional,
                "frete": frete, "shipping": frete,
                "link_afiliado": link_afiliado, "link": link_afiliado,
                "imagem": imagem, "image": imagem
            })

        except Exception:
            continue

    with open("produtos.json", "w", encoding="utf-8") as arquivo_json:
        json.dump(lista_produtos, arquivo_json, indent=2, ensure_ascii=False)

    print(f"\n[SUCESSO] Processo concluído! Foram salvos {len(lista_produtos)} produtos validados e sem erros.")

if __name__ == "__main__":
    extrair_dados_do_html_local()
