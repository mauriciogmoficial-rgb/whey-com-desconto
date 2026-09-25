import json
import re
import os
from urllib.parse import urlparse, parse_qs, unquote
from bs4 import BeautifulSoup
import requests

# === CONFIGURAÇÕES DE AFILIADO E API ===
ID_AFILIADO = "55954375"
NOME_ARQUIVO_HTML = "pagina.html"

# Insira aqui o seu Access Token gerado pelas suas chaves do Mercado Livre
ACCESS_TOKEN = "2151377171450257" 

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
            lista_u = captured_params.get('u')
            link_original = lista_u.pop(0) if isinstance(lista_u, list) else lista_u
        elif 'redirect_url' in captured_params:
            lista_redir = captured_params.get('redirect_url')
            link_original = lista_redir.pop(0) if isinstance(lista_redir, list) else lista_redir
            
    return unquote(link_original)

def definir_tag_filtro(titulo):
    tit = titulo.lower()
    if "creatina" in tit:
        return "creatina"
    elif "coqueteleira" in tit or "shaker" in tit or "copo" in tit or "acessorio" in tit:
        return "acessorios"
    return "whey"

def gerar_link_afiliado_api(url_produto, access_token):
    """
    Envia a URL limpa do produto para a API do Mercado Livre para gerar
    o link encurtado oficial já com o rastreio de afiliado embutido.
    """
    url_api = "https://mercadolibre.com"
    
    headers = {
        "Authorization": "Bearer " + str(access_token),
        "Content-Type": "application/json"
    }
    
    url_com_afiliado = (
        str(url_produto) + "?matt_tool=" + str(ID_AFILIADO) +
        "&matt_word=afiliado" +
        "&matt_source=share" +
        "&matt_campaign=automacao_html"
    )
    
    payload = {
        "url": url_com_afiliado
    }
    
    try:
        response = requests.post(url_api, json=payload, headers=headers, timeout=5)
        if response.status_code == 201:
            dados = response.json()
            return dados.get("short_url", url_com_afiliado)
        else:
            print(" -> [Erro API] Status " + str(response.status_code) + ": " + str(response.text))
            return url_com_afiliado
    except Exception as e:
        print(" -> [Erro Conexão API]: " + str(e))
        return url_com_afiliado

def validar_produto_na_origem(url_produto, preco_capturado):
    """
    Acessa o link do produto em segundo plano para checar se a página existe 
    e se o preço atualizado bate com o que foi coletado.
    """
    try:
        response = requests.get(url_produto, headers=HEADERS_VALIDADOR, timeout=5)
        
        codigos_erro = (404, 410)
        if response.status_code in codigos_erro or "produto-nao-encontrado" in response.url:
            print("-> [Link Inválido] Produto inexistente removido: " + str(url_produto))
            return False, None

        soup_interno = BeautifulSoup(response.text, "html.parser")
        container_preco = soup_interno.select_one(".andes-money-amount__fraction")
        
        if container_preco:
            valor_real = container_preco.get_text(strip=True)
            centavos_el = soup_interno.select_one(".andes-money-amount__cents")
            centavos_real = centavos_el.get_text(strip=True) if centavos_el else "00"
            preco_interno_atualizado = "R$ " + str(valor_real) + "," + str(centavos_real)
            
            if preco_interno_atualizado != preco_capturado:
                print("-> [Preço Atualizado] Ajustado de " + str(preco_capturado) + " para " + str(preco_interno_atualizado))
                return True, preco_interno_atualizado
                
        return True, preco_capturado
    except Exception:
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
                    return p.pop(0) if isinstance(p, list) else p

    imagens = capa.find_all("img")
    for img in imagens:
        atributos = ("data-src", "srcset", "data-srcset", "dynamic-src", "src", "data-lazy")
        for attr in atributos:
            valor = img.get(attr)
            if valor:
                if "," in str(valor):
                    parts = [p.strip().split(" ") for p in str(valor).split(",")]
                    for p in parts:
                        if "mlstatic.com" in p and "data:image" not in p:
                            return p.pop(0) if isinstance(p, list) else p
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
        print("Erro: O arquivo '" + str(NOME_ARQUIVO_HTML) + "' não foi encontrado!")
        return

    print("Processando arquivo local '" + str(NOME_ARQUIVO_HTML) + "'...")
    with open(NOME_ARQUIVO_HTML, "r", encoding="utf-8") as f:
        html_local = f.read()

    soup = BeautifulSoup(html_local, "html.parser")
    itens = soup.select(".poly-card, [class*='poly-card'], .ui-search-layout__item, .ui-search-result__wrapper, .ui-search-result")
    print("Estrutura localizada: " + str(len(itens)) + " possíveis blocos de produtos identificados.")

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
            
            # Limpeza segura usando pop(0) em vez de colchetes de índices
            base_link = link_limpo.split("#").pop(0).split("?").pop(0)

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
                    valor_txt = "R$ " + str(fracao.get_text(strip=True)) + "," + str(centavos)
                    if is_original:
                        preco_antigo = valor_txt
                    else:
                        preco_atual = valor_txt

            print("Validando e gerando link: " + str(titulo[:30]) + "...")
            link_valido, preco_atualizado = validar_produto_na_origem(base_link, preco_atual)
            
            if not link_valido:
                continue
            
            preco_atual = preco_atualizado

            # --- CHAMADA DA API DE ENCURTAMENTO ---
            link_afiliado = gerar_link_afiliado_api(base_link, ACCESS_TOKEN)

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

            produto_formatado = {
                "titulo": titulo, "title": titulo,
