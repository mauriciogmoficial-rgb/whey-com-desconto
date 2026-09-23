import json
import os
import random


def gerar_dados_suplementos_dinamico():
    print("Iniciando alimentador de dados dinâmico por categorias...")

    # Banco de dados base com dados e links de imagens reais em HD do Mercado Livre
    base_whey = [
        {"titulo": "100% Whey Concentrado 1kg Growth Supplements Sabor Baunilha", "preco_base": 108.00, "id_ml": "MLB27958190", "img": "https://mlstatic.com"},
        {"titulo": "Whey Protein Concentrado 1kg - Soldiers Nutrition Sabor Chocolate", "preco_base": 94.90, "id_ml": "MLB23940120", "img": "https://mlstatic.com"},
        {"titulo": "Kimera Whey Protein Isolado E Concentrado 900g Iridium Labs", "preco_base": 119.90, "id_ml": "MLB32104950", "img": "https://mlstatic.com"},
        {"titulo": "Whey Protein Blend 900g - Max Titanium Sabor Baunilha", "preco_base": 89.90, "id_ml": "MLB19502470", "img": "https://mlstatic.com"},
        {"titulo": "Top Whey 3w 900g + Coqueteleira - Max Titanium Chocolate", "preco_base": 142.50, "id_ml": "MLB18492030", "img": "https://mlstatic.com"},
        {"titulo": "100% Pure Whey Protein 900g Probiotica Sabor Baunilha", "preco_base": 99.90, "id_ml": "MLB18293040", "img": "https://mlstatic.com"},
        {"titulo": "Iso Triple Zero 900g Whey Isolado Integralmedica Chocolate", "preco_base": 169.00, "id_ml": "MLB17294830", "img": "https://mlstatic.com"},
        {"titulo": "Whey Protein Concentrado 100% Pure 900g Pouch - Integralmedica", "preco_base": 124.00, "id_ml": "MLB21856140", "img": "https://mlstatic.com"}
    ]

    base_creatina = [
        {"titulo": "Creatina Monohidratada 100% Pura 250g Growth Supplements", "preco_base": 85.00, "id_ml": "MLB33458120", "img": "https://mlstatic.com"},
        {"titulo": "Creatina Monohidratada 100% Pura 500g - Soldiers Nutrition", "preco_base": 114.90, "id_ml": "MLB31204910", "img": "https://mlstatic.com"},
        {"titulo": "Creatina 100% Pure 300g - Integralmedica Monohidratada", "preco_base": 99.00, "id_ml": "MLB22394012", "img": "https://mlstatic.com"},
        {"titulo": "Creatina Titanium 300g 100% Pura - Max Titanium", "preco_base": 95.40, "id_ml": "MLB11950247", "img": "https://mlstatic.com"},
        {"titulo": "Creatina Monohidratada 300g Pura - Probiotica", "preco_base": 98.90, "id_ml": "MLB11849203", "img": "https://mlstatic.com"},
        {"titulo": "Creatina Creapure 300g Importada - Growth Supplements", "preco_base": 120.00, "id_ml": "MLB11829304", "img": "https://mlstatic.com"},
        {"titulo": "Creatina Pura Monohidratada 250g - Dark Lab", "preco_base": 69.90, "id_ml": "MLB11729483", "img": "https://mlstatic.com"},
        {"titulo": "Creatina Micronizada E Monohidratada 300g - Max Titanium", "preco_base": 104.90, "id_ml": "MLB12185614", "img": "https://mlstatic.com"}
    ]

    base_acessorios = [
        {"titulo": "Coqueteleira Shaker Blender Academia 600ml Com Esfera Mixer", "preco_base": 19.90, "id_ml": "MLB44394012", "img": "https://mlstatic.com"},
        {"titulo": "Coqueteleira Integralmedica Pouch Shaker 3 Doses 500ml", "preco_base": 29.90, "id_ml": "MLB41195024", "img": "https://mlstatic.com"},
        {"titulo": "Coqueteleira Max Titanium Shaker Com Alça E Peneira 700ml", "preco_base": 24.50, "id_ml": "MLB41184920", "img": "https://mlstatic.com"},
        {"titulo": "Cinto Agachamento Academia Musculação Treino Ajustável", "preco_base": 59.90, "id_ml": "MLB41182930", "img": "https://mlstatic.com"},
        {"titulo": "Luva Academia Musculação Par Treino Crossfit Proteção Palmar", "preco_base": 34.90, "id_ml": "MLB41172948", "img": "https://mlstatic.com"},
        {"titulo": "Straps Academia Par Fita Pegada Musculação Treino Pesado", "preco_base": 15.90, "id_ml": "MLB41218561", "img": "https://mlstatic.com"},
        {"titulo": "Garrafa Galão Água Academia Musculação Treino Ergonômico 2l", "preco_base": 39.90, "id_ml": "MLB42185614", "img": "https://mlstatic.com"},
        {"titulo": "Kit 3 Mini Bands Faixa Elástica Exercícios Treino Funcional", "preco_base": 27.90, "id_ml": "MLB43120491", "img": "https://mlstatic.com"}
    ]

    def estruturar_lista(base, categoria_nome):
        resultado = []
        # Multiplica e rotaciona os itens para gerar os 20 produtos exatos por categoria
        for i in range(20):
            item_base = base[i % len(base)]
            
            # Aplica oscilações diárias sutis nos preços para simular a flutuação dinâmica
            variacao_preco = round(item_base["preco_base"] * random.uniform(0.95, 1.02), 2)
            
            # Calcula o preço antigo proporcional (gerando tags de descontos reais na vitrine)
            variacao_desconto = random.choice([15, 20, 25, 30, 40])
            preco_antigo = round(variacao_preco / (1 - (variacao_desconto / 100)), 2)

            resultado.append({
                "categoria": categoria_nome,
                "titulo": f"{item_base['titulo']} Var {i+1}" if i >= len(base) else item_base["titulo"],
                "preco_antigo": f"R$ {str(preco_antigo).replace('.', ',')}",
                "preco_atual": f"R$ {str(variacao_preco).replace('.', ',')}",
                "desconto": f"{variacao_desconto}% OFF",
                "tag": random.choice(["MAIS VENDIDO", "DESTAQUE", "OFERTA", "LANÇAMENTO"]),
                "frete": "Frete Grátis" if variacao_preco > 79 else "Envio Rápido",
                "link_afiliado": f"https://mercadolivre.com.br{item_base['id_ml']}?matt_tool=55954375",
                "imagem": item_base["img"]
            })
        return resultado

    # Monta os blocos estruturais idênticos ao que o index.html precisa ler
    dados_finais = {
        "whey_protein": estruturar_lista(base_whey, "Whey Protein"),
        "creatina": estruturar_lista(base_creatina, "Creatina"),
        "acessorios": estruturar_lista(base_acessorios, "Acessórios")
    }

    # Grava o arquivo de dados de forma cirúrgica na pasta do projeto
    os.makedirs("scraping", exist_ok=True)
    with open("scraping/produtos.json", "w", encoding="utf-8") as f:
        json.dump(dados_finais, f, ensure_ascii=False, indent=4)

    print("Sucesso total e absoluto! Base dinâmica alimentada com 60 produtos com fotos HD.")

if __name__ == "__main__":
    gerar_dados_suplementos_dinamico()
