const fs = require('fs');
const puppeteer = require('puppeteer');

// Substitua pelo seu ID de afiliado real do Mercado Livre
const SEU_ID_AFILIADO = "55954375"; 

async function buscarAnunciosMercadoLivre() {
  console.log("Iniciando busca de anúncios reais no Mercado Livre...");
  
  // Abre um navegador em segundo plano
const browser = await puppeteer.launch({ 
  headless: "new",
  args: ['--no-sandbox', '--disable-setuid-sandbox'] 
});

  const page = await browser.newPage();
  
  // Acessa a página de busca de Whey Protein filtrando pelos mais vendidos
  await page.goto('https://mercadolivre.com.br[A:whey%20protein]', {
    waitUntil: 'networkidle2'
  });

  // Executa um script dentro da página do Mercado Livre para coletar os dados reais
  const produtosReais = await page.evaluate((idAfiliado) => {
    // Seleciona todos os blocos de anúncios da página
    const cards = document.querySelectorAll('.ui-search-result__wrapper');
    const lista = [];

    // Captura apenas os 12 primeiros anúncios reais para o seu site
    for (let i = 0; i < 12; i++) {
      if (!cards[i]) break;
      const card = cards[i];

      const titulo = card.querySelector('.ui-search-item__title')?.innerText || "";
      
      // Captura o preço atual
      const precoElemento = card.querySelector('.andes-money-amount__main-amount');
      const preco = precoElemento ? precoElemento.innerText.replace('\n', ',') : "";

      // Captura a imagem real do anúncio
      const imgElemento = card.querySelector('.ui-search-result-image__element');
      const imagem = imgElemento ? (imgElemento.src || imgElemento.getAttribute('data-src')) : "";

      // Captura o link original do produto
      const linkOriginal = card.querySelector('.ui-search-link')?.href || "";

      // Transforma o link original em um Link de Afiliado estruturado
      // Nota: O Mercado Livre usa criptografia nos links de afiliados da API,
      // mas para links diretos de redirecionamento usa-se o parâmetro mktplace_id
      const linkAfiliado = `${linkOriginal}&mktplace_id=${idAfiliado}`;

      lista.push({
        titulo: titulo,
        preco_antigo: "", // Pode ser mapeado se houver a tag de desconto
        preco_atual: `R$ ${preco}`,
        desconto: "",
        tag: i === 0 ? "MAIS VENDIDO" : "RECOMENDADO",
        frete: card.querySelector('.ui-search-item__shipping--free') ? "Frete Grátis" : "Envio Normal",
        link_afiliado: linkAfiliado,
        imagem: imagem
      });
    }
    return lista;
  }, SEU_ID_AFILIADO);

  await browser.close();

  // Grava os dados REAIS e atualizados diretamente no seu arquivo produtos.json
  fs.writeFileSync('produtos.json', JSON.stringify(produtosReais, null, 2));
  console.log("Arquivo produtos.json atualizado com sucesso com anúncios REAIS!");
}

buscarAnunciosMercadoLivre();
