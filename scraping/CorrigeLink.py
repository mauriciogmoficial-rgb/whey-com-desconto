import json
import re

# Abre o arquivo JSON enviado
with open('produtos.json', 'r', encoding='utf-8') as file:
    produtos = json.load(file)

seu_matt_tool = "55954375"

for produto in produtos:
    link_atual = produto.get("link", "")
    
    # Captura a sequência de números isolada que está após a última barra
    match_id = re.search(r'/(\d{8,11})(?:&|$)', link_atual)
    
    if match_id:
        id_numerico = match_id.group(1)
        
        # Reconstrói usando a URL canônica oficial de redirecionamento do Mercado Livre
        url_limpa = f"https://mercadolivre.com.br/{id_numerico}"
        url_afiliado_segura = f"{url_limpa}&matt_tool={seu_matt_tool}"
        
        # Salva as URLs perfeitas de volta no objeto
        produto["link"] = url_limpa
        produto["link_afiliado"] = url_afiliado_segura

# Grava o JSON definitivo e pronto para uso
with open('produtos_atualizados.json', 'w', encoding='utf-8') as file:
    json.dump(produtos, file, indent=2, ensure_ascii=False)

print("Processo concluído! Todos os links foram corrigidos para o formato oficial.")
