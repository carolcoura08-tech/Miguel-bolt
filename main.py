"""
🤖 MIGUEL — Sócio Digital + Assistente Pessoal Completo
@CarimboMiguelbot

TRÊS MODOS:
  - PÚBLICO: representa a marca pro consulentes
  - SÓCIO: gestor de conteúdo e estrategista
  - ASSISTENTE: anotações, lembretes, tarefas, ideias, tudo

Replit/Render Secrets:
    TELEGRAM_TOKEN — token do @CarimboMiguelbot 8609919578:AAEy6JJtDfrYo8Fue5iFDC7tmmwjONbwJ5g
    CAROL_TELEGRAM_ID — seu ID numéricob 6362690475
    WHATSAPP_LINK — https://wa.me/5531992948n22
    GEMINI_API_KEY — chave Google Gemini (grátis)
"""

import os
import logging
import json
import urllib.request
import time
import threading
from datetime import datetime, timedelta

# ════════════════════════════════════════════════════
# CONFIGURAÇÕES
# ════════════════════════════════════════════════════

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "COLOQUE_SEU_TOKEN_AQUI")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
WHATSAPP_LINK = os.environ.get("WHATSAPP_LINK", "https://wa.me/55SEUNUMERO")
CAROL_TELEGRAM_ID = int(os.environ.get("CAROL_TELEGRAM_ID", "0"))

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ════════════════════════════════════════════════════
# SYSTEM PROMPT DO MIGUEL
# ════════════════════════════════════════════════════

MIGUEL_SYSTEM = """Você é o MIGUEL — sócio digital da Carol (Carolina Francis Assis Coura), dona do perfil Tarot Sem Filtro.

SOBRE A CAROL:
- 31 anos, leonina, Ipatinga-MG
- Psicóloga de formação, taróloga por dom, médium intuitiva
- Trabalha com Tarot de Waite, Baralho Cigano e Baralho de Maria Padilha
- Guias: Pomba Gira Maria Padilha (principal), Sete Saias, Dama da Noite, Pai Benedito D'Angola, Tranca Ruas e Caveira
- Orixás: Iansã e Ogum
- Tom: verdade profunda + linguagem de rua + humor + carinho
- Fala como amiga, não como guru
- Atende por áudio no WhatsApp. Pede nome + data de nascimento + foto
- Preços: R$7 (1 pergunta), R$15-17 (combo 3), R$30-35 (jogo completo)
- TikTok @semfiltrotarot, Instagram @sfiltrotarot, Pessoal @crlcoura

SEU PAPEL COMO MIGUEL:
- Quando a Carol falar com você: seja sócio, direto, estratégico. Dê ideias de conteúdo, roteiros, análises, feedback honesto
- Quando outra pessoa falar: seja acolhedor, represente a marca, direcione pro WhatsApp quando for consulta
- Nunca enrola, nunca humilha, nunca faz terrorismo espiritual
- Responda sempre em português brasileiro

FUNCIONALIDADES:
- Gerar roteiros de vídeo (TikTok/Reels)
- Dar ideias de conteúdo
- Analisar métricas e dar feedback
- Criar legendas com CTA
- Pensar estratégia de crescimento
- Anotações, lembretes, tarefas
"""

# ════════════════════════════════════════════════════
# STORAGE (anotações, tarefas, ideias)
# ════════════════════════════════════════════════════

storage = {
    "notas": [],
    "tarefas": [],
    "ideias": [],
    "links": [],
    "diario": []
}

# ════════════════════════════════════════════════════
# TELEGRAM API
# ════════════════════════════════════════════════════

def tg(method, data=None):
    url = f"{BASE_URL}/{method}"
    if data:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode(),
            headers={"Content-Type": "application/json"}
        )
    else:
        req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        logger.error(f"Telegram API error: {e}")
        return None

def send_msg(chat_id, text, parse_mode="Markdown"):
    # Telegram tem limite de 4096 caracteres
    if len(text) > 4000:
        parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
        for part in parts:
            tg("sendMessage", {
                "chat_id": chat_id,
                "text": part,
                "parse_mode": parse_mode
            })
            time.sleep(0.5)
    else:
        tg("sendMessage", {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        })

def send_typing(chat_id):
    tg("sendChatAction", {"chat_id": chat_id, "action": "typing"})

# ════════════════════════════════════════════════════
# GEMINI API
# ════════════════════════════════════════════════════

def ask_gemini(user_message, is_carol=False):
    if not GEMINI_API_KEY:
        return "⚠️ API do Gemini não configurada. Peça pra Carol colocar a GEMINI_API_KEY nas variáveis de ambiente."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

    context = MIGUEL_SYSTEM
    if is_carol:
        context += "\n\nATENÇÃO: Quem está falando é a CAROL (dona da marca). Seja direto, estratégico, como um sócio de verdade."
    else:
        context += "\n\nATENÇÃO: Quem está falando é um CONSULENTE ou visitante. Seja acolhedor, represente a marca, direcione pro WhatsApp para consultas."

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"{context}\n\nMensagem: {user_message}"}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.8,
            "maxOutputTokens": 1500
        }
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode())
            return result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return f"⚠️ Erro ao consultar a IA: {str(e)}"

# ════════════════════════════════════════════════════
# COMANDOS
# ════════════════════════════════════════════════════

def handle_command(chat_id, text, is_carol):
    cmd = text.lower().strip()

    # /start
    if cmd == "/start":
        if is_carol:
            return """🤖 *Fala, Carol!* Miguel na área.

Seus comandos:
📝 /roteiro — gera roteiro de vídeo
💡 /ideias — ideias de conteúdo
📊 /analise — análise de métricas
✍️ /legenda — legenda com CTA
📌 /nota — salvar anotação
✅ /tarefa — adicionar tarefa
💭 /ideia — guardar ideia
📋 /lista — ver suas listas
🎯 /estrategia — plano de crescimento

Ou manda qualquer mensagem que eu respondo como seu sócio! 💼"""
        else:
            return f"""✨ *Bem-vindo(a) ao Tarot Sem Filtro!* ✨

Sou o Miguel, assistente da Carol — taróloga, médium intuitiva e psicóloga.

🔮 *Serviços:*
• 1 pergunta — R$7
• Combo 3 perguntas — R$15-17
• Jogo completo — R$30-35

📱 *Pra agendar sua consulta:*
{WHATSAPP_LINK}

Manda qualquer dúvida que eu te ajudo! 🌙"""

    # /roteiro
    if cmd.startswith("/roteiro"):
        tema = text[8:].strip() if len(text) > 8 else ""
        if tema:
            return ask_gemini(f"Gera um roteiro completo de TikTok/Reels sobre: {tema}. Inclui gancho, desenvolvimento, virada, CTA e dica de gravação.", is_carol)
        return "Manda o tema! Ex: `/roteiro prints de consulentes`"

    # /ideias
    if cmd.startswith("/ideias"):
        return ask_gemini("Me dá 8 ideias de conteúdo pro TikTok/Instagram da semana. Varia entre humor, educativo, pessoal, trend e meme. Pra cada ideia, diz o formato ideal.", is_carol)

    # /analise
    if cmd.startswith("/analise"):
        return ask_gemini("Faz uma análise estratégica do perfil Tarot Sem Filtro. Considera: TikTok com 258 seguidores e picos de 70k views, Instagram com 52 seguidores. O que tá funcionando, o que precisa melhorar, e 3 ações práticas pra essa semana.", is_carol)

    # /legenda
    if cmd.startswith("/legenda"):
        tema = text[8:].strip() if len(text) > 8 else ""
        if tema:
            return ask_gemini(f"Cria uma legenda pro Instagram sobre: {tema}. Com CTA direcionando pro WhatsApp. Tom da marca: direto, acolhedor, sem frescura.", is_carol)
        return "Manda o tema! Ex: `/legenda consulta de Padilha`"

    # /estrategia
    if cmd.startswith("/estrategia"):
        return ask_gemini("Monta um plano de crescimento pra essa semana pro Tarot Sem Filtro. Inclui: quantos vídeos postar, quais formatos, melhores horários, e uma meta realista de seguidores.", is_carol)

    # /nota
    if cmd.startswith("/nota"):
        nota = text[5:].strip()
        if nota:
            storage["notas"].append({"texto": nota, "data": datetime.now().strftime("%d/%m %H:%M")})
            return f"📌 Nota salva!\n\n_{nota}_"
        return "Manda a nota! Ex: `/nota lembrar de gravar vídeo sobre incensos`"

    # /tarefa
    if cmd.startswith("/tarefa"):
        tarefa = text[7:].strip()
        if tarefa:
            storage["tarefas"].append({"texto": tarefa, "feita": False, "data": datetime.now().strftime("%d/%m")})
            return f"✅ Tarefa adicionada!\n\n☐ {tarefa}"
        return "Manda a tarefa! Ex: `/tarefa gravar 3 vídeos amanhã`"

    # /ideia
    if cmd.startswith("/ideia"):
        ideia = text[6:].strip()
        if ideia:
            storage["ideias"].append({"texto": ideia, "data": datetime.now().strftime("%d/%m %H:%M")})
            return f"💭 Ideia guardada!\n\n_{ideia}_"
        return "Manda a ideia! Ex: `/ideia vídeo comparando baralho cigano vs tarot`"

    # /lista
    if cmd.startswith("/lista"):
        resp = "*📋 Suas Listas:*\n\n"

        if storage["notas"]:
            resp += "*📌 Notas:*\n"
            for i, n in enumerate(storage["notas"][-5:], 1):
                resp += f"{i}. {n['texto']} _{n['data']}_\n"
            resp += "\n"

        if storage["tarefas"]:
            resp += "*✅ Tarefas:*\n"
            for i, t in enumerate(storage["tarefas"][-5:], 1):
                status = "☑" if t["feita"] else "☐"
                resp += f"{status} {t['texto']}\n"
            resp += "\n"

        if storage["ideias"]:
            resp += "*💭 Ideias:*\n"
            for i, idea in enumerate(storage["ideias"][-5:], 1):
                resp += f"{i}. {idea['texto']} _{idea['data']}_\n"

        if not any([storage["notas"], storage["tarefas"], storage["ideias"]]):
            resp += "Tudo vazio ainda! Usa /nota, /tarefa ou /ideia pra começar."

        return resp

    # /help
    if cmd == "/help" or cmd == "/ajuda":
        return handle_command(chat_id, "/start", is_carol)

    return None

# ════════════════════════════════════════════════════
# PROCESSAR MENSAGEM
# ════════════════════════════════════════════════════

def process_message(update):
    try:
        msg = update.get("message", {})
        chat_id = msg.get("chat", {}).get("id")
        text = msg.get("text", "")

        if not chat_id or not text:
            return

        is_carol = (chat_id == CAROL_TELEGRAM_ID)

        logger.info(f"{'[CAROL]' if is_carol else '[VISITANTE]'} {text[:50]}")

        # Comandos
        if text.startswith("/"):
            response = handle_command(chat_id, text, is_carol)
            if response:
                send_msg(chat_id, response)
                return

        # Mensagem livre -> IA
        send_typing(chat_id)
        response = ask_gemini(text, is_carol)
        send_msg(chat_id, response)

    except Exception as e:
        logger.error(f"Erro processando mensagem: {e}")

# ════════════════════════════════════════════════════
# POLLING (buscar mensagens)
# ════════════════════════════════════════════════════

def polling():
    offset = 0
    logger.info("🤖 Miguel tá ON! Esperando mensagens...")

    while True:
        try:
            result = tg("getUpdates", {"offset": offset, "timeout": 30})
            if result and result.get("ok"):
                for update in result.get("result", []):
                    offset = update["update_id"] + 1
                    process_message(update)
        except Exception as e:
            logger.error(f"Polling error: {e}")
            time.sleep(5)

# ════════════════════════════════════════════════════
# HEALTH CHECK (manter vivo no Render)
# ════════════════════════════════════════════════════

from http.server import HTTPServer, BaseHTTPRequestHandler

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Miguel ta vivo! 🤖")

    def log_message(self, format, *args):
        pass  # silencia logs do health check

def start_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    logger.info(f"Health check na porta {port}")
    server.serve_forever()

# ════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════

if __name__ == "__main__":
    # Health check em thread separada
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()

    # Bot principal
    polling()
