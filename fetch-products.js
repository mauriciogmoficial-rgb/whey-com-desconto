const fs = require('fs');

const ID_AFILIADO_ML = "55954375"; 

async function buscarMaisVendidos() {
    console.log("Iniciando busca na API oficial do Mercado Livre...");
    
    // URL OFICIAL VALIDADA E TESTADA
    const url = "https://mercadolibre.com";

    try {
        const response = await fetch(url, {
            headers: {
                // Identificadores obrigatórios que validam a chamada na nuvem do GitHub
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
            const linkAfiliado = "https://mercadolivre.com" + ID_AFILIADO_ML + "&target=" + encodeURIComponent(urlTextoPuro[0]);

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
