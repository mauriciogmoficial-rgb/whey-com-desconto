import requests

# === PREENCHA COM OS SEUS DADOS DO MERCADO LIVRE DEVELOPERS ===
CLIENT_ID = "SEU_CLIENT_ID_AQUI"
CLIENT_SECRET = "SEU_CLIENT_SECRET_AQUI"
CODE = "O_CODIGO_DE_AUTORIZACAO_QUE_VOCE_PEGO_NA_URL"
REDIRECT_URI = "A_SUA_URL_DE_REDIRECIONAMENTO_EXATA"

def requisitar_access_token():
    url = "https://mercadolibre.com"
    
    headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded"
    }
    
    payload = {
        "grant_type": "authorization_code",
        "client_id": str(CLIENT_ID),
        "client_secret": str(CLIENT_SECRET),
        "code": str(CODE),
        "redirect_uri": str(REDIRECT_URI)
    }
    
    try:
        response = requests.post(url, data=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            dados = response.json()
            print("\n==================================================")
            print("[SUCESSO] Token obtido com orgulho!")
            print("==================================================")
            print("ACCESS_TOKEN:")
            print(dados.get("access_token"))
            print("\nREFRESH_TOKEN (Guarde para renovar depois):")
            print(dados.get("refresh_token"))
            print("==================================================\n")
        else:
            print(f"\n[Erro da API] Status {response.status_code}: {response.text}\n")
            
    except Exception as e:
        print(f"\n[Erro de Conexao]: {e}\n")

if __name__ == "__main__":
    requisitar_access_token()
