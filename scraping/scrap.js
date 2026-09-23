const fs = require('fs');

async function buscarMercadoLivre(termo) {
    const termoLimpo = encodeURIComponent(termo.trim());
    const url = `https://mercadolivre.com{termoLimpo}`;
    
    console.log(`Buscando por '${termo}' através da API do Mercado Livre...`);
    
    try {
        const response = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0' } });
        if (!response.ok) throw new Error(`Erro HTTP: ${response.status}`);
        
        const dados = await response.json();
        
        const produtos = dados.results.map(item => ({
            titulo: item.title,
            preco: parseFloat(item.price || 0),
            link: item.permalink
        }));
        
        fs.writeFileSync('produtos.json', JSON.stringify(produtos, null, 4), 'utf-8');
        console.log(`Sucesso! ${produtos.length} produtos foram salvos em 'produtos.json'.`);
        
    } catch (error) {
        console.error("Erro ao acessar a rede:", error.message);
    }
}

buscarMercadoLivre('creatina');
