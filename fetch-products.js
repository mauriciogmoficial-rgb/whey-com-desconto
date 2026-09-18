const fs = require('fs');

const ID_AFILIADO_ML = "55954375"; 

async function buscarMaisVendidos() {
    console.log("Iniciando busca definitiva de Wheys na API publica...");
    
    // Montagem blindada em pedaços pequenos para o chat não cortar nada no código
    const protocolo = "https://";
    const subdominio = "api.";
    const dominioBase = "mercadolibre.com";
    const rotaBusca = "/sites/MLB/search?q=whey%20protein&limit=50";
    
    const url = protocolo + subdominio + dominioBase + rotaBusca;

    try {
        const response = await fetch(url, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        });
        
        if (!response.ok) {
            throw new Error("O servidor respondeu com status: " + response.status);
        }

        const data = await response.json();
        const itens = data.results || [];
        
        if (itens.length === 0) throw new Error("Nenhum item encontrado.");

        const produtosFormatados = itens.map(item => {
            const linkOriginal = item.permalink || "";
            const urlLimpa = linkOriginal.split("?")[0]; // Pega estritamente a parte estável do link
            
            const baseAfiliado = "https://mercadolivre.com";
            const linkAfiliado = baseAfiliado + ID_AFILIADO_ML + "&target=" + encodeURIComponent(urlLimpa);

            return {
                id: item.id,
                titulo: item.title,
                precoOriginal: item.original_price || item.price,
                precoAtual: item.price,
                imagem: item.thumbnail ? item.thumbnail.replace("-I.jpg", "-O.jpg") : "", 
                link: linkAfiliado,
                desconto: item.original_price ? Math.round(((item.original_price - item.price) / item.original_price) * 100) : 0
            };
        });

        fs.writeFileSync('produtos.json', JSON.stringify(produtosFormatados, null, 2));
        console.log("SUCESSO! O arquivo produtos.json foi gerado com os Wheys reais.");

    } catch (error) {
        console.error("Erro no processamento:", error.message);
        process.exit(1);
    }
}

buscarMaisVendidos();
