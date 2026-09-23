import json
import os
import sys
from playwright.sync_api import sync_playwright


def raspar_mercado_livre_nuvem():
    print("Iniciando simulador de navegador Playwright na nuvem...")

    with sync_playwright() as p:
        # Abre o navegador em modo "headless" (sem tela, ideal para servidores em nuvem)
        # Configura um tamanho de tela padrão de computador para simular fidelidade humana
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720},
        )

        page = context.new_page()

        # URL de busca real que você abriria no seu navegador
        url = "https://mercadolivre.com.br[A:whey%20protein]"
        print(f"Acessando a página de busca: {url}")

        try:
            # Navega até o site aguardando o carregamento completo dos elementos visuais
            page.goto(url, wait_until="networkidle", timeout=60000)

            print("Página carregada com sucesso! Extraindo dados dos produtos...")

            # Seleciona todos os blocos de anúncios na tela do Mercado Livre
            # Esse seletor captura o container principal de cada produto na lista
            anuncios = page.query_selector_all(".ui-search-result__wrapper")

            if not anuncios:
                # Caso a interface mude levemente, tenta o seletor alternativo de grid
                anuncios = page.query_selector_all(".ui-search-layout__item")

            print(f"Total de anúncios detectados na tela: {len(anuncios)}")

            produtos = []

            # Percorre a tela raspando os dados de cada item de forma cirúrgica
            for anuncio in anuncios[:20]:  # Limita aos 20 primeiros para teste rápido
                # Captura o título
                elemento_titulo = anuncio.query_selector(".ui-search-item__title")
                titulo = (
                    elemento_titulo.inner_text().strip() if elemento_titulo else "Sem título"
                )

                # Captura o preço
                elemento_preco = anuncio.query_selector(
                    ".poly-price__current .andes-money-amount__fraction"
                )
                if not elemento_preco:
                    elemento_preco = anuncio.query_selector(
                        ".ui-search-price__part--medium .andes-money-amount__fraction"
                    )

                preco = (
                    float(elemento_preco.inner_text().replace(".", "").replace(",", "."))
                    if elemento_preco
                    else 0.0
                )

                # Captura o link direto
                elemento_link = anuncio.query_selector("a.ui-search-link")
                if not elemento_link:
                    elemento_link = anuncio.query_selector("a.poly-component__title")
                link = elemento_link.get_attribute("href") if elemento_link else ""

                if link and titulo != "Sem título":
                    produtos.append({"titulo": titulo, "preco": preco, "link": link})

            # Se o robô não encontrou nada na estrutura visual, joga um aviso de diagnóstico
            if not produtos:
                produtos.append({
                    "aviso": "O navegador abriu a página, mas os seletores visuais não encontraram produtos."
                })

            # Salva o arquivo produtos.json limpo
            # Garante a criação da pasta caso não exista na máquina virtual
            os.makedirs("scraping", exist_ok=True)
            with open("scraping/produtos.json", "w", encoding="utf-8") as f:
                json.dump(produtos, f, ensure_ascii=False, indent=4)

            print(
                f"Sucesso absoluto! {len(produtos)} produtos reais foram salvos em 'produtos.json'."
            )

        except Exception as e:
            erro_msg = [{"erro": f"Falha na simulação visual do navegador: {str(e)}"}]
            with open("scraping/produtos.json", "w", encoding="utf-8") as f:
                json.dump(erro_msg, f, ensure_ascii=False, indent=4)
            print(f"Ocorreu um erro no processamento do navegador: {e}")

        finally:
            browser.close()


if __name__ == "__main__":
    raspar_mercado_livre_nuvem()
