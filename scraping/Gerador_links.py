import asyncio
import json
import os
from playwright.async_api import async_playwright

ARQUIVO_ENTRADA = "produtos.json"
ARQUIVO_SAIDA = "produtos_afiliados_final.json"

async def converter_links_em_massa():
    if not os.path.exists(ARQUIVO_ENTRADA):
        print(f"❌ Erro: O arquivo '{ARQUIVO_ENTRADA}' não foi encontrado.")
        return

    # 1. Carrega o seu arquivo JSON original com os novos produtos
    with open(ARQUIVO_ENTRADA, "r", encoding="utf-8") as f:
        dados_json = json.load(f)

    # Filtra e junta todos os links em uma única string gigante separada por quebra de linha (\n)
    links_filtrados = [item["link"] for item in dados_json if item.get("link")]
    if not links_filtrados:
        print("⚠️ Nenhum link válido foi encontrado no JSON para conversão.")
        return

    string_links_em_bloco = "\n".join(links_filtrados)

    async with async_playwright() as p:
        print("🤖 Inicializando o navegador com a sessão salva...")
        browser = await p.chromium.launch(headless=False) # Defina como True se quiser rodar em segundo plano depois
        context = await browser.new_context(storage_state="auth.json")
        page = await context.new_page()
        
        # Acessa a nova URL exata que você encontrou
        await page.goto("https://mercadolivre.com.br")
        await page.wait_for_load_state("networkidle")

        # Seletores baseados na nova estrutura de Bloco do Mercado Livre
        SELETOR_CAIXA_TEXTO = "textarea" # O grande campo de texto para colar os múltiplos links
        SELETOR_BOTAO_GERAR = "button:has-text('Gerar')"
        SELETOR_LINKS_CONVERTIDOS = "input[readonly]" # Onde os links gerados aparecem na tabela/lista de saída

        print(f"🔄 Enviando {len(links_filtrados)} links em massa para o painel...")
        
        try:
            # Aguarda a caixa de texto aparecer na tela
            await page.wait_for_selector(SELETOR_CAIXA_TEXTO, timeout=10000)
            
            # Preenche a caixa colando todas as URLs separadas por linha de uma só vez
            await page.fill(SELETOR_CAIXA_TEXTO, string_links_em_bloco)
            await asyncio.sleep(1) # Pausa pequena apenas para garantir o preenchimento
            
            # Clica no botão gerar em lote
            await page.click(SELETOR_BOTAO_GERAR)
            print("⏳ Processando conversão em massa no Mercado Livre...")
            
            # Aguarda os elementos readonly de resposta ficarem disponíveis na tela
            await page.wait_for_selector(SELETOR_LINKS_CONVERTIDOS, timeout=15000)
            
            # Captura todos os novos links de afiliado gerados de uma vez só
            elementos_gerados = await page.query_selector_all(SELETOR_LINKS_CONVERTIDOS)
            links_afiliados_novos = []
            for el in elementos_gerados:
                valor = await el.get_attribute("value")
                if valor:
                    links_afiliados_novos.append(valor.strip())

            print(f"✅ Capturados {len(links_afiliados_novos)} links de afiliados gerados!")

            # 3. Associa de volta os links gerados nas posições corretas do seu JSON original
            contador_sucesso = 0
            for item in dados_json:
                if item.get("link") and contador_sucesso < len(links_afiliados_novos):
                    item["link_afiliado"] = links_afiliados_novos[contador_sucesso]
                    contador_sucesso += 1
                else:
                    item["link_afiliado"] = "FALHA_OU_NAO_GERADO"

            # 4. Salva o novo arquivo JSON completo mantendo a mesma estrutura que você já tinha
            with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
                json.dump(dados_json, f, indent=2, ensure_ascii=False)
                
            print(f"🎉 Processo concluído! Novo arquivo salvo com sucesso em: '{ARQUIVO_SAIDA}'")

        except Exception as e:
            print(f"❌ Ocorreu um erro durante a automação em massa: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(converter_links_em_massa())