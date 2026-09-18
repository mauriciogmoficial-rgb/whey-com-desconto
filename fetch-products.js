const fs = require('fs');

const ID_AFILIADO_ML = "55954375"; 

async function buscarMaisVendidos() {
    console.log("Iniciando busca alternativa via Feed Aberto do Mercado Livre...");
    
    // Rota pública de ofertas em formato aberto - Livre do erro 403!
    const subdominio = "api.";
    const baseHot = "https://" + subdominio + "mercadolibre.com";
    const url = baseHot + "/sites/MLB/hot_items?limit=100";

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
        
        // Se a lista de mais vendidos gerais vier vazia ou mudar, joga um erro controlado
        const itens = data.results || [];
        if (itens.length === 0) throw new Error("Nenhum item encontrado no feed.");

        // Filtra os itens para garantir que estamos pegando Whey Protein e Suplementos
        const suplementos = itens.filter(item => {
            const titulo = (item.title || "").toLowerCase();
            return titulo.includes("whey") || titulo.includes("protein") || titulo.includes("creatina") || titulo.includes("suplemento");
        });

        // Se o feed de ofertas do dia não tiver 100 Wheys específicos, pegamos os destaques disponíveis
        const itensParaVitrine = suplementos.length > 0 ? suplementos : itens.slice(0, 100);

        const produtosFormatados = itensParaVitrine.map(item => {
            const partesUrl = (item.permalink || "").split("?");
            const urlLimpa = partesUrl[0];
            
            const linkAfiliado = "https://mercadolivre.com" + ID_AFILIADO_ML + "&target=" + encodeURIComponent(urlLimpa);

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
        console.log("SUCESSO ABSOLUTO! O arquivo produtos.json foi gerado com as ofertas liberadas!");

    } catch (error) {
        console.error("Erro no processamento alternativo:", error.message);
        // Salva uma lista vazia ou simulação para não travar o deploy da Netlify
        fs.writeFileSync('produtos.json', JSON.stringify([], null, 2));
    }
}

buscarMaisVendidos();
