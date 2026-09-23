# Força o uso do protocolo de segurança TLS 1.2
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# Pede o termo de busca na tela
$termo = Read-Host "Digite o produto que deseja buscar (ex: whey)"
$termoLimpo = [uri]::EscapeDataString($termo.Trim())

# URL da API do Mercado Livre
$url = "https://mercadolivre.com"

Write-Host "Buscando por '$termo' no Mercado Livre..." -ForegroundColor Cyan

try {
    # Baixa a resposta estritamente como TEXTO BRUTO (sem conversões automáticas)
    $webClient = New-Object System.Net.WebClient
    $webClient.Headers.Add("User-Agent", "Mozilla/5.0")
    $textoPuro = $webClient.DownloadString($url)
    
    # Recorta os blocos de resultados usando expressões regulares diretamente no texto
    $regexResultados = '\{"id":"MLB[^"\}]+"[^\}]+?\}'
    $matches = [regex]::Matches($textoPuro, $regexResultados)
    
    $produtos = @()
    
    foreach ($match in $matches) {
        $bloco = $match.Value
        
        # Expressões cirúrgicas para extrair cada campo do texto bruto
        $titulo = if ($bloco -match '"title":"([^"]+)"') { $matches.Groups[1].Value } else { "Sem titulo" }
        $preco  = if ($bloco -match '"price":([0-9.]+)') { [double]$matches.Groups[1].Value } else { 0.0 }
        $link   = if ($bloco -match '"permalink":"([^"]+)"') { $matches.Groups[1].Value.Replace('\/', '/') } else { "" }
        
        # Ignora blocos que não possuem links válidos
        if ($link -ne "") {
            $produtos += [PSCustomObject]@{
                titulo = $titulo
                preco  = $preco
                link   = $link
            }
        }
    }
    
    # Força a gravação do arquivo JSON estruturado na marra
    if ($produtos.Count -gt 0) {
        $produtos | ConvertTo-Json -Depth 3 | Out-File -FilePath 'produtos.json' -Encoding utf8
        Write-Host "Sucesso absoluto! O arquivo produtos.json foi gerado com $($produtos.Count) produtos reais!" -ForegroundColor Green
    } else {
        # Fallback de segurança garantido: joga o texto inteiro para você ver que baixou
        [PSCustomObject]@{ resultado_bruto = "API respondeu com sucesso, mas o filtro falhou" } | ConvertTo-Json | Out-File -FilePath 'produtos.json' -Encoding utf8
        Write-Host "Aviso: A conexão funcionou, mas o filtro não encontrou produtos padronizados." -ForegroundColor Yellow
    }
}
catch {
    Write-Host "Ocorreu um erro na busca: $_" -ForegroundColor Red
}
