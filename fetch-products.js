const fs = require('fs');

const ID_AFILIADO_ML = "55954375"; 

async function buscarMaisVendidos() {
    console.log("Iniciando busca automatizada na API do Mercado Livre...");
    const CATEGORIA_WHEY = "MLB278453"; 
    const url = "https://mercadolibre.com" + CATEGORIA_WHEY + "&limit=100&sort=relevance";

    try {
        const response = await fetch(url, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            }
        });
        
        if (!response.ok) {
            throw new Error("A API respondeu com erro Código: " + response.status);
        }

        const data = await response.json();
        if (!data || !data.results) throw new Error("Resultados não encontrados.");

        const produtosFormatados = data.results.map(item => {
            const urlTextoPuro = item.permalink.split("?")[0];
            const linkAfiliado = "https://mercadolivre.com" + ID_AFILIADO_ML + "&target=" + encodeURIComponent(urlTextoPuro);

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
        console.log("SUCESSO! Arquivo produtos.json gerado!");

    } catch (error) {
        console.error("Erro no processamento:", error.message);
        process.exit(1); 
    }
}

buscarMaisVendidos();
