import json
import os
import requests

# === CONFIGURAÇÕES DO PROGRAMA DE AFILIADOS ===
ID_AFILIADO = "55954375"

# Cole aqui o seu token que começa com APP_USR-...
ACCESS_TOKEN = "SEU_ACCESS_TOKEN_AQUI"

ARQUIVO_ENTRADA = "produtos.json"
ARQUIVO_SAIDA = "produtos_afiliados.json"

def gerar_link_afiliado_api(url_produto, access_token):
    """
    Envia a URL do produto para a API do Mercado Livre para gerar
    o link encurtado oficial (/sec/) com o rastreio de comissão.
    """
    url_api = "https://mercadolibre.com"
    
    headers = {
        "Authorization": "Bearer " + str(access_token),
        "Content-Type": "application/json"
    }
    
    # Monta os parâmetros oficiais exigidos para computar sua comissão
    url_com_afiliado = (
        str(url_produto) + "?matt_tool=" + str(ID_AFILIADO) +
        "&matt_word=afiliado" +
        "&matt_source=share" +
        "&matt_campaign=conversao_json"
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
            print(" -> [Aviso API] Erro status " + str(response.status_code) + ". Mantendo link parametrizado.")
            return url_com_afiliado
    except Exception as e:
        print(" -> [Erro Conexão API]: " + str(e))
        return url_com_afiliado

def converter_links_do_json():
    # Verifica se o arquivo gerado pelo scraper existe
    if not os.path.exists(ARQUIVO_ENTRADA):
        print("Erro: O arquivo '" + str(ARQUIVO_ENTRADA) + "' nao foi encontrado na pasta!")
        print("Por favor, rode o seu script de scraping primeiro.")
        return

    print("Lendo o arquivo '" + str(ARQUIVO_ENTRADA) + "'...")
    with open(ARQUIVO_ENTRADA, "r", encoding="utf-8") as f:
        lista_produtos = json.load(f)

    total_produtos = len(lista_produtos)
    print("Foram encontrados " + str(total_produtos) + " produtos para converter.\n")

    lista_atualizada = []
    contador = 0

    for produto in lista_produtos:
        contador = contador + 1
        titulo = produto.get("titulo", "Produto")
        # Pega a URL limpa que o seu scraper salvou na chave 'link'
        url_original = produto.get("link")

        if not url_original:
            continue

        print(str(contador) + "/" + str(total_produtos) + " - Convertendo: " + str(titulo[:30]) + "...")
        
        # Chama a API do Mercado Livre para gerar o link curto premiado
        novo_link_afiliado = gerar_link_afiliado_api(url_original, ACCESS_TOKEN)
        
        # Atualiza as chaves do dicionario com o link encurtado correto
        produto["link_afiliado"] = novo_link_afiliado
        produto["link"] = novo_link_afiliado
        
        lista_atualizada.append(produto)

    # Salva todos os produtos atualizados em um novo arquivo JSON
    print("\nSalvando os resultados em '" + str(ARQUIVO_SAIDA) + "'...")
    with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as arquivo_json:
        json.dump(lista_atualizada, arquivo_json, indent=2, ensure_ascii=False)

    print("[SUCESSO] Todos os links foram processados e salvos com seguranca!")

if __name__ == "__main__":
    converter_links_do_json()
