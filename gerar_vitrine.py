import json
from coletor import buscar_30_mais_vendidos

def criar_pagina_web():
    lista_suplementos = buscar_30_mais_vendidos()
    if not lista_suplementos:
        print("Nenhum dado foi coletado. Processo abortado.")
        return

    dados_convertidos_json = json.dumps(lista_suplementos, ensure_ascii=False, indent=4)

    html_final = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Whey com Desconto | Melhores Ofertas</title>
    <style>
        :root {{ --primary: #ffdb00; --dark: #2d3238; --light: #f5f5f5; }}
        body {{ font-family: Arial, sans-serif; background-color: var(--light); margin: 0; padding: 0; }}
        header {{ background-color: var(--primary); text-align: center; padding: 2rem 1rem; }}
        header h1 {{ margin: 0; font-size: 2rem; }}
        .cta-grupo {{ background: #25d366; color: white; display: inline-block; padding: 0.8rem 1.5rem; border-radius: 25px; text-decoration: none; font-weight: bold; margin-top: 1rem; }}
        .container {{ max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }}
        .vitrine {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 2rem; }}
        .card {{ background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05); display: flex; flex-direction: column; }}
        .card-img {{ width: 100%; height: 220px; object-fit: contain; padding: 1rem; box-sizing: border-box; }}
        .card-body {{ padding: 1.5rem; display: flex; flex-direction: column; flex-grow: 1; }}
        .card-tag {{ background: #3483fa; color: white; font-size: 0.75rem; font-weight: bold; padding: 0.3rem 0.6rem; border-radius: 4px; align-self: flex-start; }}
        .card-title {{ font-size: 1rem; margin: 0.5rem 0; font-weight: bold; height: 2.8rem; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }}
        .card-price {{ font-size: 1.5rem; font-weight: bold; margin: 0.5rem 0; }}
        .btn-comprar {{ background-color: #2d3238; color: white; text-align: center; padding: 0.8rem; border-radius: 6px; text-decoration: none; font-weight: bold; margin-top: auto; }}
        @media (max-width: 600px) {{ .vitrine {{ grid-template-columns: 1fr 1fr; gap: 1rem; }} }}
    </style>
</head>
<body>

<header>
    <h1>💪 Whey com Desconto</h1>
    <p>Os 30 Suplementos Mais Vendidos do Mercado Livre atualizados diariamente!</p>
    <a href="SEU_LINK_DO_WHATSAPP" target="_blank" class="cta-grupo">📢 Entrar no Grupo VIP de Ofertas</a>
</header>

<div class="container">
    <div class="vitrine" id="vitrine"></div>
</div>

<script>
    const produtos = {dados_convertidos_json};
    const vitrine = document.getElementById('vitrine');
    
    produtos.forEach(prod => {{
        let linkAfiliado = "https://mercadolivre.com.br" + encodeURIComponent(prod.linkOriginal);

        vitrine.innerHTML += `
            <div class="card">
                <img src="${{prod.imagem}}" alt="${{prod.titulo}}" class="card-img">
                <div class="card-body">
                    <span class="card-tag">${{prod.tag}}</span>
                    <h3 class="card-title">${{prod.titulo}}</h3>
                    <div class="card-price">R$ ${{prod.preco}}</div>
                    <a href="${{linkAfiliado}}" target="_blank" class="btn-comprar">Ver no Mercado Livre</a>
                </div>
            </div>
        `;
    }});
</script>
</body>
</html>"""

    import os
    diretorio_raiz = os.path.dirname(os.path.abspath(__file__))
    caminho_index = os.path.join(diretorio_raiz, "index.html")
    
    with open(caminho_index, "w", encoding="utf-8") as f:
        f.write(html_final)
    print("Sucesso! index.html gerado.")

if __name__ == "__main__":
    criar_pagina_web()
