import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # Abre o navegador visível (Chrome/Chromium)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Acessa diretamente a nova URL do painel de afiliados
        await page.goto("https://mercadolivre.com.br")
        
        print("\n" + "="*60)
        print("👉 O navegador abriu. Faça o seu login manualmente na tela.")
        print("👉 Complete a segurança de duas camadas normalmente.")
        print("👉 O robô vai fechar sozinho assim que detectar o painel.")
        print("="*60 + "\n")
        
        # Loop que monitora a URL do navegador a cada 2 segundos
        while True:
            url_atual = page.url
            
            # Reconhece a nova URL do seu painel atualizado
            if "linkbuilder" in url_atual or "afiliados" in url_atual:
                # Se ainda estiver na tela de login/autenticação, continua esperando
                if "login" in url_atual or "reingresar" in url_atual:
                    await asyncio.sleep(2)
                    continue
                    
                print("🎉 Login e painel detectados com sucesso!")
                # Pequena pausa de 3 segundos para garantir o carregamento total dos cookies
                await asyncio.sleep(3)
                
                # Gera o arquivo de autenticação essencial na pasta
                await context.storage_state(path="auth.json")
                print("✅ Arquivo 'auth.json' gerado com sucesso!")
                break
                
            await asyncio.sleep(2)
            
        # Fecha o navegador de forma segura
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())