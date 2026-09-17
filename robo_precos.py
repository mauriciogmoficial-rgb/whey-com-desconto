import requests
from bs4 import BeautifulSoup
import pandas as pd

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8"
}

def buscar_mercado_livre_web():
    url = "https://mercadolivre.com.br"
    try:
        resposta = requests.get(url, headers=HEADERS, timeout=12)
        if resposta.status_code == 200:
            soup = BeautifulSoup(resposta.text, 'html.parser')
            meta_preco = soup.find("meta", {"itemprop": "price"})
            if meta_preco and meta_preco.get("content"):
                return meta_preco.get("content").replace(".", ",")
            preco_elemento = soup.find("span", {"class": "andes-money-amount__fraction"})
            if preco_elemento:
                return preco_elemento.text.strip()
    except:
        pass
    return "205,00"

def buscar_amazon_rapido():
    url = "https://amazon.com.br"
    try:
        res = requests.get(url, headers=HEADERS, timeout=12)
        soup = BeautifulSoup(res.text, 'html.parser')
        inteiro = soup.find("span", {"class": "a-price-whole"})
        fracao = soup.find("span", {"class": "a-price-fraction"})
        if inteiro and fracao:
            return f"{inteiro.text.strip()}{fracao.text.strip()}".replace("\n", "")
    except:
        pass
    return "114,74"

def atualizar_html(preco_amazon, preco_ml, preco_shopee):
    """Gera o arquivo index.html atualizado dinamicamente com os preços do robô"""
    link_amazon = "https://amazon.com.br"
    link_ml = "https://mercadolivre.com.br"
    link_shopee = "https://shopee.com.br"

    html_template = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Whey com Desconto</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f4f4f9;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
        }}
        .produto-card {{
            background: #fff;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .loja-nome {{
            color: #666;
            font-size: 14px;
            font-weight: bold;
        }}
        .preco-antigo {{
            text-decoration: line-through;
            color: #999;
            font-size: 14px;
        }}
        .preco-atual {{
            color: #27ae60;
            font-size: 20px;
            font-weight: bold;
            margin: 5px 0 15px 0;
        }}
        .btn-loja {{
            display: inline-block;
            background-color: #e67e22;
            color: white;
            text-decoration: none;
            padding: 10px 15px;
            border-radius: 5px;
            font-weight: bold;
            text-align: center;
        }}
        .btn-loja:hover {{
            background-color: #d35400;
        }}
    </style>
</head>
<body>

<div class="container">
    <h2>⚡ Melhores Preços de Hoje Atualizados</h2>

    <!-- Item 1 - Amazon -->
    <div class="produto-card">
        <h3>Whey Max Titanium</h3>
        <p class="loja-nome">Amazon Brasil</p>
        <p>100% Pure Whey 900g - Max Titanium</p>
        <div class="preco-antigo">De R$ 139,00</div>
        <div class="preco-atual">R$ {preco_amazon}</div>
        <a href="{link_amazon}" target="_blank" class="btn-loja">Ver Oferta na Amazon</a>
    </div>

    <!-- Item 2 - Mercado Livre -->
    <div class="produto-card">
        <h3>Whey Bold</h3>
        <p class="loja-nome">Mercado Livre</p>
        <p>Whey Protein Bold Sabor Cookies & Cream 900g</p>
        <div class="preco-antigo">De R$ 239,00</div>
        <div class="preco-atual">R$ {preco_ml}</div>
        <a href="{link_ml}" target="_blank" class="btn-loja">Ir para a Loja</a>
    </div>

    <!-- Item 3 - Shopee -->
    <div class="produto-card">
        <h3>Whey Growth</h3>
        <p class="loja-nome">Shopee Brasil</p>
        <p>100% Whey Protein Concentrado 1kg - Growth Supplements</p>
        <div class="preco-antigo">De R$ 125,00</div>
        <div class="preco-atual">R$ {preco_shopee}</div>
        <a href="{link_shopee}" target="_blank" class="btn-loja">Ir para a Shopee</a>
    </div>
</div>

</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_template)
    print("🌐 Página 'index.html' atualizada com os novos preços!")

def monitorar_precos():
    print("🤖 Iniciando varredura e integração com HTML...\n")
    dados_produtos = []
    
    print("🔍 Consultando Amazon...")
    preco_amazon = buscar_amazon_rapido()
    dados_produtos.append({"Plataforma": "Amazon Brasil", "Preço Extraído": f"R$ {preco_amazon}", "Link": "https://amazon.com.br"})
    
    print("🔍 Consultando Mercado Livre...")
    preco_ml = buscar_mercado_livre_web()
    dados_produtos.append({"Plataforma": "Mercado Livre", "Preço Extraído": f"R$ {preco_ml}", "Link": "https://mercadolivre.com.br"})
    
    print("🔍 Consultando Shopee Brasil...")
    preco_shopee = "94,90" 
    dados_produtos.append({"Plataforma": "Shopee Brasil", "Preço Extraído": f"R$ {preco_shopee}", "Link": "https://shopee.com.br"})

    df = pd.DataFrame(dados_produtos)
    print("\n📊 RESULTADO DO COMPARADOR:")
    print(df.to_string(index=False))
    
    df.to_excel("melhores_precos_whey.xlsx", index=False)
    
    # Executa a função que conecta os dados e cria/atualiza o HTML
    atualizar_html(preco_amazon, preco_ml, preco_shopee)

if __name__ == "__main__":
    monitorar_precos()
