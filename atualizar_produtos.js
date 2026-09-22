const fs = require('fs');
const puppeteer = require('puppeteer');

// Seu ID de afiliado real do Mercado Livre extraído do link
const SEU_ID_AFILIADO = "55954375"; 

async function buscarAnunciosMercadoLivre() {
  console.log("Iniciando busca de anúncios reais no Mercado Livre...");
  
  const browser = await puppeteer.launch({ 
    headless: "new",
    args: [
      '--no-sandbox', 
      '--disable-setuid-sandbox',
      '--disable-blink-features=AutomationControlled' // Esconde que é um robô
    ] 
  });
  const page = await browser.newPage();
  
  // Evita bloqueios simulando um navegador real do dia a dia
  await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
  
  // Acessa a listagem limpa de whey protein
  await page.goto('https://mercadolivre.com.br', {
    waitUntil: 'networkidle2'
  });

  // Aguarda a estrutura da lista carregar na tela por segurança
  try {
    await page.waitForSelector('.ui-search-layout__item', { timeout: 7000 });
  } catch (e) {
    console.log("Aviso: Tempo limite de carregamento da estrutura atingido.");
  }

  const produtosReais = await page.evaluate((idAfiliado) => {
    // Seleciona os contêineres de anúncios do Mercado Livre
    const cards = document.querySelectorAll('.ui-search-layout__item');
    const lista = [];

    // Mapeia os 12 primeiros anúncios reais encontrados
    cards.forEach((card, index) => {
      if (lista.length >= 12) return;

      // Puxa o título testando os seletores tradicionais e os novos estruturados (poly)
      const tituloElemento = card.querySelector('.ui-search-item__title') || card.querySelector('[class*="title"]');
      const titulo = tituloElemento ? tituloElemento.innerText.trim() : "";

      // Se não encontrou um título válido no bloco, pula para o próximo card
      if (!titulo) return;

      // Puxa o preço decodificando a estrutura de acessibilidade do ML
      const precoMain = card.querySelector('.andes-money-amount__main-amount');
      let preco = precoMain ? precoMain.innerText.replace('\n', ',').trim() : "";
      
      // Puxa a imagem tratando o carregamento inteligente dinâmico
      const imgElemento = card.querySelector('img');
      let imagem = "";
      if (imgElemento) {
        imagem = imgElemento.getAttribute('data-src') || imgElemento.src || "";
      }

      // Puxa o link original do produto
      const linkElemento = card.querySelector('a.ui-search-link') || card.querySelector('a');
      const linkOriginal = linkElemento ? linkElemento.href : "";

      // Monta a estrutura final idêntica ao seu banco de dados front-end
      if (linkOriginal && imagem) {
        lista.push({
          titulo: titulo,
          preco_antigo: "", 
          preco_atual: preco ? `R$ ${preco}` : "Confira no site",
          desconto: "",
          tag: lista.length === 0 ? "MAIS VENDIDO" : "DESTAQUE",
          frete: card.innerText.toLowerCase().includes("grátis") ? "Frete Grátis" : "Envio Rápido",
          link_afiliado: `${linkOriginal}&matt_tool=${idAfiliado}`, // Injeta o seu link de afiliado oficial
          imagem: imagem
        });
      }
    });

    return lista;
  }, SEU_ID_AFILIADO);

  await browser.close();

  // Proteção: Se a raspagem falhar por completo, mantém o arquivo anterior intacto
  if (produtosReais.length === 0) {
    console.log("Aviso: Nenhum produto extraído nos seletores atuais. Mantendo o arquivo original.");
    return;
  }

  // Grava as informações reais atualizadas por cima do JSON
  fs.writeFileSync('produtos.json', JSON.stringify(produtosReais, null, 2));
  console.log(`Arquivo produtos.json atualizado com sucesso com ${produtosReais.length} anúncios REAIS!`);
}

buscarAnunciosMercadoLivre();
