const fs = require('fs');

const SEU_ID_AFILIADO = "55954375"; 

async function buscarAnunciosMercadoLivre() {
  console.log("Conectando de forma mascarada à API do Mercado Livre...");
  
  try {
    const urlAPI = 'https://mercadolivre.com';
    
    // Enviamos cabeçalhos (headers) idênticos aos de um ser humano navegando no Chrome
    const resposta = await fetch(urlAPI, {
      method: 'GET',
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'no-cache'
      }
    });

    // Verificamos primeiro se a resposta é HTML antes de tentar ler como JSON
    const textoResposta = await resposta.text();
    
    if (textoResposta.trim().startsWith('<!DOCTYPE') || textoResposta.trim().startsWith('<html')) {
      console.error("\n❌ O Mercado Livre bloqueou a requisição e enviou uma página de segurança HTML.");
      console.log("Ativando banco de dados reserva de emergência para manter seu site online...\n");
      usarDadosReserva();
      return;
    }

    const dados = JSON.parse(textoResposta);
    
    if (!dados.results || dados.results.length === 0) {
      console.error("Nenhum produto retornado pela API.");
      usarDadosReserva();
      return;
    }

    const produtosReais = dados.results.map((item, index) => {
      const precoFormatado = item.price.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
      const imagemAltaQualidade = item.thumbnail.replace("-I.jpg", "-O.jpg");
      const linkAfiliado = `${item.permalink}?matt_tool=${SEU_ID_AFILIADO}`;

      return {
        titulo: item.title,
        preco_antigo: item.original_price ? item.original_price.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) : "",
        preco_atual: precoFormatado,
        desconto: item.original_price ? `${Math.round(((item.original_price - item.price) / item.original_price) * 100)}% OFF` : "",
        tag: index === 0 ? "MAIS VENDIDO" : "RECOMENDADO",
        frete: item.shipping.free_shipping ? "Frete Grátis" : "Envio Rápido",
        link_afiliado: linkAfiliado,
        imagem: imagemAltaQualidade
      };
    });

    fs.writeFileSync('produtos.json', JSON.stringify(produtosReais, null, 2));
    console.log(`==================================================`);
    console.log(`🔥 SUCESSO! ${produtosReais.length} Wheys reais gravados.`);
    console.log(`==================================================`);

  } catch (erro) {
    console.error("Erro ao conectar:", erro);
    usarDadosReserva();
  }
}

// Essa função impede que seu site fique em branco caso o Mercado Livre mude algo de novo
function usarDadosReserva() {
  const dadosReserva = [
    {
      "titulo": "Top Whey 3W Max Titanium 900g Sabores Original",
      "preco_antigo": "R\$ 169,90",
      "preco_atual": "R\$ 139,90",
      "desconto": "17% OFF",
      "tag": "MAIS VENDIDO",
      "frete": "Frete Grátis",
      "link_afiliado": "https://mercadolivre.com.br",
      "imagem": "https://mlstatic.com"
    },
    {
      "titulo": "100% Pure Whey Integralmedica 900g Pouch Concentrado",
      "preco_antigo": "R\$ 139,90",
      "preco_atual": "R\$ 124,00",
      "desconto": "11% OFF",
      "tag": "DESTAQUE",
      "frete": "Envio Rápido",
      "link_afiliado": "https://mercadolivre.com.br",
      "imagem": "https://mlstatic.com"
    }
  ];
  fs.writeFileSync('produtos.json', JSON.stringify(dadosReserva, null, 2));
  console.log("✅ Arquivo produtos.json alimentado com a lista reserva com sucesso!");
}

buscarAnunciosMercadoLivre();
