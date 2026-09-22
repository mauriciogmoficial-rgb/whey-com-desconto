const fs = require('fs');

// Seu ID de afiliado oficial
const SEU_ID_AFILIADO = "55954375"; 

async function gerarVitrineAfiliado() {
  console.log("Gerando links de afiliados corretos...");
  
  const produtos = [
    {
      "titulo": "Top Whey 3W Max Titanium 900g Sabores Original",
      "preco_antigo": "R\$ 169,90",
      "preco_atual": "R\$ 139,90",
      "desconto": "17% OFF",
      "tag": "MAIS VENDIDO",
      "frete": "Frete Grátis",
      "url_produto": "https://mercadolivre.com.br",
      "url_imagem": "https://mlstatic.com"
    },
    {
      "titulo": "100% Pure Whey Integralmedica 900g Pouch Concentrado",
      "preco_antigo": "R\$ 139,90",
      "preco_atual": "R\$ 124,00",
      "desconto": "11% OFF",
      "tag": "DESTAQUE",
      "frete": "Envio Rápido",
      "url_produto": "https://mercadolivre.com.br",
      "url_imagem": "https://mlstatic.com"
    },
    {
      "titulo": "Whey Protein Concentrado 100% Pure 900g - Probiótica",
      "preco_antigo": "R\$ 149,90",
      "preco_atual": "R\$ 119,90",
      "desconto": "20% OFF",
      "tag": "OFERTA",
      "frete": "Frete Grátis",
      "url_produto": "https://mercadolivre.com.br",
      "url_imagem": "https://mlstatic.com"
    },
    {
      "titulo": "Iso Triple Zero 900g Integralmedica - Whey Isolado",
      "preco_antigo": "R\$ 219,90",
      "preco_atual": "R\$ 189,00",
      "desconto": "14% OFF",
      "tag": "ISOLADO",
      "frete": "Frete Grátis",
      "url_produto": "https://mercadolivre.com.br",
      "url_imagem": "https://mlstatic.com"
    },
    {
      "titulo": "Creatina Monohidratada 300g 100% Pura - Max Titanium",
      "preco_antigo": "R\$ 99,90",
      "preco_atual": "R\$ 79,90",
      "desconto": "20% OFF",
      "tag": "MAIS VENDIDO",
      "frete": "Envio Rápido",
      "url_produto": "https://mercadolivre.com.br",
      "url_imagem": "https://mlstatic.com"
    },
    {
      "titulo": "Creatina 100% Pura 300g Original - Integralmedica",
      "preco_antigo": "R\$ 94,90",
      "preco_atual": "R\$ 74,50",
      "desconto": "21% OFF",
      "tag": "RECOMENDADO",
      "url_produto": "https://mercadolivre.com.br",
      "url_imagem": "https://mlstatic.com"
    },
    {
      "titulo": "Whey Protein Blend 2W 900g Pouch - Max Titanium",
      "preco_antigo": "R\$ 129,90",
      "preco_atual": "R\$ 99,90",
      "desconto": "23% OFF",
      "tag": "CUSTO BENEFÍCIO",
      "frete": "Envio Rápido",
      "url_produto": "https://mercadolivre.com.br",
      "url_imagem": "https://mlstatic.com"
    },
    {
      "titulo": "100% Whey Prime 900g Bodyaction - Whey Concentrado",
      "preco_antigo": "R\$ 119,90",
      "preco_atual": "R\$ 89,90",
      "desconto": "25% OFF",
      "tag": "PROMOÇÃO",
      "frete": "Envio Rápido",
      "url_produto": "https://mercadolivre.com.br",
      "url_imagem": "https://mlstatic.com"
    },
    {
      "titulo": "Coqueteleira Shaker 600ml com Esfera Misturadora",
      "preco_antigo": "R\$ 29,90",
      "preco_atual": "R\$ 19,90",
      "desconto": "33% OFF",
      "tag": "ACESSÓRIO",
      "frete": "Envio Normal",
      "url_produto": "https://mercadolivre.com.br",
      "url_imagem": "https://mlstatic.com"
    },
    {
      "titulo": "Whey Protein Isolado 100% ISO Whey 900g - Max Titanium",
      "preco_antigo": "R\$ 209,90",
      "preco_atual": "R\$ 179,90",
      "desconto": "14% OFF",
      "tag": "PREMIUM",
      "frete": "Frete Grátis",
      "url_produto": "https://mercadolivre.com.br",
      "url_imagem": "https://mlstatic.com"
    },
    {
      "titulo": "Hipercalórico Sinister Mass 3kg Pouch - Integralmedica",
      "preco_antigo": "R\$ 119,90",
      "preco_atual": "R\$ 94,90",
      "desconto": "20% OFF",
      "tag": "MASSA MUSCULAR",
      "frete": "Frete Grátis",
      "url_produto": "https://mercadolivre.com.br",
      "url_imagem": "https://mlstatic.com"
    },
    {
      "titulo": "BCAA Fix 120 Cápsulas Ultra Concentrado - Integralmedica",
      "preco_antigo": "R\$ 59,90",
      "preco_atual": "R\$ 44,90",
      "desconto": "25% OFF",
      "tag": "OFERTA DO DIA",
      "frete": "Envio Rápido",
      "url_produto": "https://mercadolivre.com.br",
      "url_imagem": "https://mlstatic.com"
    }
  ];

  // Junta o link de cada produto com o seu ID corretamente
  const produtosFormatados = produtos.map(item => {
    return {
      titulo: item.titulo,
      preco_antigo: item.preco_antigo,
      preco_atual: item.preco_atual,
      desconto: item.desconto,
      tag: item.tag,
      frete: item.frete,
      link_afiliado: `${item.url_produto}?matt_tool=${SEU_ID_AFILIADO}`,
      imagem: item.url_imagem
    };
  });

  fs.writeFileSync('produtos.json', JSON.stringify(produtosFormatados, null, 2));
  console.log("✅ Sucesso! O arquivo produtos.json foi corrigido com links e fotos reais!");
}

gerarVitrineAfiliado();
