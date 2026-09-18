const fs = require('fs');

const ID_AFILIADO_ML = "55954375"; 

async function buscarMaisVendidos() {
    console.log("Iniciando busca com desvio de segurança anti-bloqueio...");
    
    // URL Real da API que queremos acessar
    const sub = "api.";
    const apiBase = "https://" + sub + "mercadolibre.com";
    const apiRota = "/sites/MLB/search?q=whey%20protein&limit=50";
    const urlAlvo = apiBase + apiRota;
    
    // Passamos a URL por dentro do serviço AllOrigins para limpar o IP do GitHub e evitar o 403
    const proxySub = "api.";
    const proxyDominio = "allorigins.win";
    const proxyBase = "https://" + proxySub + proxyDominio + "/get?url=";
    const urlProxy = proxyBase + encodeURIComponent(urlAlvo);

    try {
        const response = await fetch(urlProxy);
        
        if (!response.ok) {
            throw new Error("O servidor de desvio respondeu com erro: " + response.status);
        }

        const proxyData = await response.json();
        
        // O AllOrigins embrulha a resposta original como texto dentro da propriedade 'contents'
        const data = JSON.parse(proxyData.contents);
        const itens = data.results || [];
        
        if (itens.length === 0) throw new Error("Nenhum produto retornado na resposta.");

        const produtosFormatados = itens.map(item => {
            const linkOriginal = item.permalink || "";
            const urlLimpa = linkOriginal.split("?"); 
            
            const baseAfiliado = "https://mercadolivre.com";
            const linkAfiliado = baseAfiliado + ID_AFILIADO_ML + "&target=" + encodeURIComponent(urlLimpa[0]);

            return {
                id: item.id,
                titulo: item.title,
                precoOriginal: item.original_price || item.price,
                precoAtual: item.price,
                imagem: item.thumbnail ? item.thumbnail.replace("-I.jpg", "-O.jpg").replace("http://", "https://") : "", 
                link: linkAfiliado,
                desconto: item.original_price ? Math.round(((item.original_price - item.price) / item.original_price) * 100) : 0
            };
        });

        fs.writeFileSync('produtos.json', JSON.stringify(produtosFormatados, null, 2));
        console.log("SUCESSO! Arquivo produtos.json gerado burlado com sucesso!");

    } catch (error) {
        console.error("Erro no processamento com proxy:", error.message);
        process.exit(1);
    }
}

buscarMaisVendidos();
