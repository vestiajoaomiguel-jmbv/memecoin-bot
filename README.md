
# Memecoin Alert Bot (Telegram)

Bot para detectar memecoins promissoras usando:

## Filtros

### DexScreener
- Liquidity > 150k
- MC 90k–5M
- Age < 24h
- Volume 1h > 50k
- Txns 1h > 300

### Solscan
- Top 10 < 25%
- Holders > 300

### Momentum
- Volume 1h crescente
- Traders 1h crescente
- Txns elevadas
- Net Flow positivo

## Classificação
- A+ = alerta imediato
- B = observar
- C = ignorar

---

## Instalação

```bash
pip install -r requirements.txt
```

## Variáveis

Linux/macOS:
```bash
export TELEGRAM_TOKEN="TOKEN"
export CHAT_ID="CHAT_ID"
```

Windows:
```powershell
set TELEGRAM_TOKEN=TOKEN
set CHAT_ID=CHAT_ID
```

## Executar

```bash
python main.py
```

## Criar bot no Telegram

1. Abrir BotFather
2. `/newbot`
3. Copiar TOKEN
4. Obter CHAT_ID:
   https://api.telegram.org/botTOKEN/getUpdates
