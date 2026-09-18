const fs = require('fs');

const ID_AFILIADO_ML = "55954375"; 

async function buscarMaisVendidos() {
    console.log("Iniciando busca na API oficial do Mercado Livre...");
    
    // Montando a URL em pedaços para o sistema do chat não cortar o link de dados
    const parte1 = "https://api.mercadolibre.com";
    const parte2 = "/sites/MLB/search?category=MLB278453";
    const parte3 = "&limit=100&sort=relevance";
    
    const url = parte1 + parte2 + parte3;

    try {
        const response = await fetch(url, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error("A API respondeu com status de erro: " + response.status);
        }

        const data = await response.json();
        if (!data || !data.results) throw new Error("Resultados não encontrados.");

        const produtosFormatados = data.results.map(item => {
            const urlTextoPuro = item.permalink.split("?");
            
            // Montando o link de afiliado em pedaços para evitar novos cortes no chat
            const baseAfiliado = "https://mercadolivre.com";
            const linkAfiliado = baseAfiliado + ID_AFILIADO_ML + "&target=" + encodeURIComponent(urlTextoPuro[0]);

            return {
                id: item.id,
                titulo: item.title,
                precoOriginal: item.original_price || item.price,
                precoAtual: item.price,
                imagem: item.thumbnail.replace("-I.jpg", "-O.jpg"), 
                link: linkAfiliado,
                desconto: item.original_price ? Math.round(((item.original_price - item.price) / item.original_price) * 100) : 0
            };
        });

        fs.writeFileSync('produtos.json', JSON.stringify(produtosFormatados, null, 2));
        console.log("SUCESSO! Arquivo produtos.json gerado com os 100 Wheys!");

    } catch (error) {
        console.error("Erro no processamento:", error.message);
        process.exit(1); 
    }
}

buscarMaisVendidos();
