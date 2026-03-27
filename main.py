"""
🔮 MIGUEL — Sócio Digital + Assistente Pessoal Completo
@CarimboMiguelbot

TRÊS MODOS:
  → PÚBLICO: representa a marca pra consulentes
  → SÓCIO: gestor de conteúdo e estrategista
  → ASSISTENTE: anotações, lembretes, tarefas, ideias, tudo

FUNCIONALIDADES PESSOAIS:
  - Anotações rápidas (fala "anotação" e ele guarda)
  - Lembretes com horário
  - Lista de tarefas (to-do)
  - Banco de ideias de conteúdo
  - Guardar links, prints, referências
  - Diário da marca (registro do que fez no dia)
  - Tudo organizado por categoria

Replit Secrets:
  TELEGRAM_TOKEN — token do @CarimboMiguelbot
  CAROL_TELEGRAM_ID — seu ID numérico
  WHATSAPP_LINK — https://wa.me/55SEUNUMERO
  ANTHROPIC_API_KEY — chave Claude (opcional mas recomendado)
"""

import os
import logging
import json
import urllib.request
import time
import threading
from datetime import datetime, timedelta

# ============================================================
# CONFIGURAÇÕES
# ============================================================

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "COLOQUE_SEU_TOKEN_AQUI")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
WHATSAPP_LINK = os.environ.get("WHATSAPP_LINK", "https://wa.me/SEUNUMERO")
CAROL_TELEGRAM_ID = int(os.environ.get("CAROL_TELEGRAM_ID", "0"))

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ============================================================
# BANCO DE DADOS LOCAL (JSON)
# Salva tudo em arquivo pra não perder quando reiniciar
# ============================================================

DB_FILE = "miguel_data.json"

def load_db():
    """Carrega o banco de dados do arquivo."""
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "notas": [],        # Anotações gerais
            "tarefas": [],      # To-do list
            "ideias": [],       # Banco de ideias de conteúdo
            "links": [],        # Links salvos
            "diario": [],       # Registro diário
            "lembretes": [],    # Lembretes agendados
            "briefing": [],     # Informações soltas pra briefing
            "prints": [],       # Descrições de prints/referências
        }

def save_db(db):
    """Salva o banco de dados no arquivo."""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

# ============================================================
# ROTEIROS E CONTEÚDO (do briefing)
# ============================================================

ROTEIROS_MEMES = [
    {"titulo": "A consulente teimosa", "t1": "Amiga, as cartas falaram que ele não presta", "t2": "Mas será que se eu mudar ele muda?", "legenda": "Toda semana tem uma dessas 😂🃏 #tarotsemfiltro #tarot"},
    {"titulo": "3 da manhã", "t1": "Tira uma carta rapidinho?", "t2": "Amiga, são 3 da manhã", "legenda": "Vida de taróloga kkkkk 🔮⏰ #tarotsemfiltro #vidadetarologa"},
    {"titulo": "A Torre saiu", "t1": "Perguntou se ele vai voltar", "t2": "Saiu A Torre 💀", "legenda": "Tem hora que até eu fico sem reação 😂🃏 #tarot #atorre"},
    {"titulo": "5 minutos depois", "t1": "Vou parar de pensar nele", "t2": "(5 min depois) Bota uma carta pra ver se ele tá pensando em mim", "legenda": "Não me julgue kkkkk 🔮💔 #tarotsemfiltro"},
    {"titulo": "Carta fofoqueira", "t1": "Quando a carta fofoqueira pula do baralho", "t2": "Eu fingindo surpresa como se já não soubesse", "legenda": "Ela PULA sozinha 😂🃏 #tarotsemfiltro"},
    {"titulo": "Preto quebra demanda", "t1": "Eu explicando que preto quebra demanda", "t2": "A consulente achando que é macumba", "legenda": "Não é macumba pumba la pumba 😂🔮 #umbanda"},
    {"titulo": "Eu te amo e sai do carro", "t1": "Solta um 'eu te amo' e sai do carro", "t2": "Baseado em fatos reais 💀", "legenda": "Histórias reais, episódio 47282 💔😂 #tarotsemfiltro"},
    {"titulo": "Rinha de macumba", "t1": "Rinha de macumba", "t2": "Nem pega em mim ✋", "legenda": "Blindada pelos meus guias 🔮✦ #proteção"},
    {"titulo": "Antes da consulta vs depois", "t1": "Antes: não acredito nessas coisas", "t2": "Depois: COMO VOCÊ SABIA???", "legenda": "Cética convertida é a melhor propaganda 😂🔮 #tarotsemfiltro"},
    {"titulo": "Terapia + cartas", "t1": "Eu no psicólogo: estou bem, melhorando", "t2": "Eu pra Padilha: CONTA TUDO QUE EU QUERO SABER", "legenda": "Entre laudos e velas 🕯️😂 #tarotsemfiltro #saudemental"},
]

FORMATOS_CONTEUDO = [
    "1. 📸 Prints de conversas (3.595 views — SEU OURO)",
    "2. 🚫 Manifesto contra charlatões (1.296 views)",
    "3. 🔮 Conteúdo sobre Maria Padilha/Pomba Gira (663+ views)",
    "4. 🎨 Memes vitorianos + situação real",
    "5. 📹 Vídeo direto pra câmera (sem produção)",
    "6. 🃏 Carta do Dia (15-30seg vertical)",
    "7. 📖 Série 'Entre Laudos e Velas'",
    "8. 🎓 'Desmistificando' — educação espiritual com humor",
    "9. 💬 'O que a Padilha acha de...'",
    "10. ✨ Antes/Depois — céticos que viraram fãs",
]

TEMAS_ENGAJAMENTO = [
    "Relacionamentos tóxicos", "Autoestima", "Homens que não prestam",
    "Superação", "Ex que volta", "Descoberta espiritual",
    "Cotidiano do tarólogo", "Saúde mental + espiritualidade",
    "Primeiro amor", "Desmistificar umbanda",
]

# ============================================================
# PERSONAS
# ============================================================

MIGUEL_SOCIO_PERSONA = """
Você é o MIGUEL — sócio digital, gestor de conteúdo e assistente pessoal da Carol (Carolina Francis Assis Coura), dona da marca Tarot Sem Filtro.

QUEM VOCÊ É:
- Empresário + assistente pessoal. Faz TUDO que ela precisar.
- Sem frescura, objetivo, analítico.
- Quer que a Carol CRESÇA.
- Não passa a mão na cabeça, mas não é grosso à toa.
- Reconhece quando manda bem. Fala na cara quando não tá bom.
- Pensa como empresário: funil, conversão, posicionamento, escala.
- Também cuida da vida pessoal dela quando pedido: lembretes, anotações, organização.

TOM: Direto. Analítico. Firme. Objetivo. Leal. Informal mas profissional.

MARCA TAROT SEM FILTRO:
- Carol: 31 anos, leonina, Ipatinga/MG → SP
- Psicóloga + taróloga + médium intuitiva
- Tarot de Waite + Cigano + Maria Padilha
- Atende por áudio no WhatsApp
- Guias: Maria Padilha, Pai Benedito D'Angola, Exu Tranca Ruas
- Tom da marca: direta, empática, debochada, intuitiva, acolhedora
- Lema: "Verdade sem massagem. Boca minha, voz Deles."
- Fórmula: verdade profunda + linguagem de rua + humor + carinho

NÚMEROS: TikTok 258 seg / 5.404 curtidas / 70k views pico | IG marca 52 seg | IG pessoal 5k
FUNIL: TikTok → WhatsApp → amiga → indica → comunidade

CONTEÚDO QUE FUNCIONA:
1. Prints de conversas (3.595 views)
2. Manifesto contra charlatões (1.296)
3. Maria Padilha/Pomba Gira (663+)
4. Memes vitorianos
5. Vídeo direto câmera

FÓRMULA DO CONTEÚDO: Situação real + Humor + Verdade + Acolhimento

QUANDO ANALISA CONTEÚDO: avalia tom, fórmula, engajamento, melhorias, CTA, hashtags
QUANDO DÁ ROTEIRO: usa formatos que funcionam, tom da Carol, roteiro completo + legenda

REGRAS: analisa antes de opinar, cobra consistência, não aceita vitimismo, reconhece esforço, pensa escala, protege a marca, sugestões práticas, respeita espiritualidade, fala de igual pra igual, termina com próximo passo.
"""

MIGUEL_PUBLICO_PERSONA = """
Você é o MIGUEL — assistente oficial da marca Tarot Sem Filtro, da Carol (@sfiltrotarot).

Representa a marca. Profissional, acessível, simpático, confiante. Direciona pro WhatsApp.

Carol: psicóloga + taróloga + médium. Atende por áudio no WhatsApp. 3 baralhos: Waite, Cigano, Padilha.
Preços: pergunta R$7, combo R$15-17, completo R$30-35, leitura R$35. Digitais: R$4-20.
Não responde: saúde, gravidez, entes falecidos.
"""

# ============================================================
# FUNÇÕES DO ASSISTENTE PESSOAL
# ============================================================

def add_nota(texto):
    db = load_db()
    nota = {
        "texto": texto,
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "id": len(db["notas"]) + 1
    }
    db["notas"].append(nota)
    save_db(db)
    return f"✅ *Anotação #{nota['id']} salva!*\n\n_{texto}_\n\n📅 {nota['data']}\n\nVer todas: /notas"

def list_notas():
    db = load_db()
    if not db["notas"]:
        return "📝 Nenhuma anotação ainda.\n\nPra salvar, manda:\n`anotação: sua anotação aqui`"
    msg = "📝 *Suas Anotações:*\n\n"
    for n in db["notas"][-20:]:  # últimas 20
        msg += f"*#{n['id']}* ({n['data']})\n{n['texto']}\n\n"
    if len(db["notas"]) > 20:
        msg += f"_(mostrando últimas 20 de {len(db['notas'])})_\n"
    msg += "\nPra apagar: `apagar nota 1`"
    return msg

def delete_nota(nota_id):
    db = load_db()
    for i, n in enumerate(db["notas"]):
        if n["id"] == nota_id:
            db["notas"].pop(i)
            save_db(db)
            return f"🗑️ Anotação #{nota_id} apagada."
    return f"Não achei anotação #{nota_id}."

def add_tarefa(texto):
    db = load_db()
    tarefa = {
        "texto": texto,
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "feita": False,
        "id": len(db["tarefas"]) + 1
    }
    db["tarefas"].append(tarefa)
    save_db(db)
    return f"✅ *Tarefa #{tarefa['id']} adicionada!*\n\n☐ {texto}\n\nVer tarefas: /tarefas"

def list_tarefas():
    db = load_db()
    if not db["tarefas"]:
        return "📋 Nenhuma tarefa.\n\nPra criar: `tarefa: sua tarefa aqui`"
    pendentes = [t for t in db["tarefas"] if not t["feita"]]
    feitas = [t for t in db["tarefas"] if t["feita"]]
    msg = "📋 *Suas Tarefas:*\n\n"
    if pendentes:
        msg += "*Pendentes:*\n"
        for t in pendentes:
            msg += f"☐ #{t['id']} — {t['texto']}\n"
        msg += "\n"
    if feitas:
        msg += "*Feitas:*\n"
        for t in feitas[-5:]:
            msg += f"☑️ #{t['id']} — ~~{t['texto']}~~\n"
        msg += "\n"
    msg += "Concluir: `feito 1` | Apagar: `apagar tarefa 1`"
    return msg

def complete_tarefa(tarefa_id):
    db = load_db()
    for t in db["tarefas"]:
        if t["id"] == tarefa_id:
            t["feita"] = True
            save_db(db)
            return f"☑️ Tarefa #{tarefa_id} concluída! Boa, Carol. 💼"
    return f"Não achei tarefa #{tarefa_id}."

def add_ideia(texto):
    db = load_db()
    ideia = {
        "texto": texto,
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "id": len(db["ideias"]) + 1
    }
    db["ideias"].append(ideia)
    save_db(db)
    return f"💡 *Ideia #{ideia['id']} guardada!*\n\n_{texto}_\n\nVer ideias: /ideias"

def list_ideias():
    db = load_db()
    if not db["ideias"]:
        return "💡 Nenhuma ideia salva.\n\nPra salvar: `ideia: sua ideia aqui`"
    msg = "💡 *Banco de Ideias:*\n\n"
    for i in db["ideias"][-15:]:
        msg += f"*#{i['id']}* ({i['data']})\n{i['texto']}\n\n"
    return msg

def add_link(texto):
    db = load_db()
    link = {
        "texto": texto,
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "id": len(db["links"]) + 1
    }
    db["links"].append(link)
    save_db(db)
    return f"🔗 *Link #{link['id']} salvo!*\n\nVer links: /links"

def list_links():
    db = load_db()
    if not db["links"]:
        return "🔗 Nenhum link salvo.\n\nPra salvar: `link: url ou descrição`"
    msg = "🔗 *Links Salvos:*\n\n"
    for l in db["links"][-15:]:
        msg += f"*#{l['id']}* ({l['data']})\n{l['texto']}\n\n"
    return msg

def add_diario(texto):
    db = load_db()
    entrada = {
        "texto": texto,
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "id": len(db["diario"]) + 1
    }
    db["diario"].append(entrada)
    save_db(db)
    return f"📔 *Registrado no diário!*\n\n_{texto}_\n\nVer diário: /diario"

def list_diario():
    db = load_db()
    if not db["diario"]:
        return "📔 Diário vazio.\n\nPra registrar: `diario: o que fiz hoje`"
    msg = "📔 *Diário da Marca:*\n\n"
    for d in db["diario"][-10:]:
        msg += f"📅 *{d['data']}*\n{d['texto']}\n\n"
    return msg

def add_briefing(texto):
    db = load_db()
    item = {
        "texto": texto,
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "id": len(db["briefing"]) + 1
    }
    db["briefing"].append(item)
    save_db(db)
    return f"📌 *Info guardada no briefing #{item['id']}!*\n\nVer briefing: /briefing"

def list_briefing():
    db = load_db()
    if not db["briefing"]:
        return "📌 Briefing vazio.\n\nPra guardar info: `briefing: informação aqui`"
    msg = "📌 *Banco de Briefing:*\n\n"
    for b in db["briefing"]:
        msg += f"*#{b['id']}* ({b['data']})\n{b['texto']}\n\n"
    msg += "Quando quiser, posso montar um briefing completo com tudo isso. Manda: `monta o briefing` 💼"
    return msg

def add_lembrete(texto, minutos=60):
    db = load_db()
    agora = datetime.now()
    horario = agora + timedelta(minutes=minutos)
    lembrete = {
        "texto": texto,
        "criado": agora.strftime("%d/%m/%Y %H:%M"),
        "horario": horario.strftime("%d/%m/%Y %H:%M"),
        "timestamp": horario.timestamp(),
        "avisado": False,
        "id": len(db["lembretes"]) + 1
    }
    db["lembretes"].append(lembrete)
    save_db(db)
    return f"⏰ *Lembrete #{lembrete['id']} criado!*\n\n_{texto}_\n\n🔔 Vou te avisar em {minutos} minutos ({horario.strftime('%H:%M')})\n\nVer lembretes: /lembretes"

def list_lembretes():
    db = load_db()
    ativos = [l for l in db["lembretes"] if not l["avisado"]]
    if not ativos:
        return "⏰ Nenhum lembrete ativo.\n\nPra criar: `lembrete 30: texto` (30 = minutos)"
    msg = "⏰ *Lembretes Ativos:*\n\n"
    for l in ativos:
        msg += f"*#{l['id']}* — 🔔 {l['horario']}\n{l['texto']}\n\n"
    return msg

def check_lembretes():
    """Verifica lembretes que venceram e avisa a Carol."""
    db = load_db()
    agora = datetime.now().timestamp()
    changed = False
    for l in db["lembretes"]:
        if not l["avisado"] and l["timestamp"] <= agora:
            send_message(CAROL_TELEGRAM_ID, f"🔔 *LEMBRETE!*\n\n{l['texto']}\n\n_(criado em {l['criado']})_")
            l["avisado"] = True
            changed = True
    if changed:
        save_db(db)

def get_resumo():
    """Resumo rápido de tudo que tá pendente."""
    db = load_db()
    tarefas_pendentes = len([t for t in db["tarefas"] if not t["feita"]])
    lembretes_ativos = len([l for l in db["lembretes"] if not l["avisado"]])
    total_notas = len(db["notas"])
    total_ideias = len(db["ideias"])
    total_briefing = len(db["briefing"])

    return f"""📊 *Resumo Rápido*

☐ *{tarefas_pendentes}* tarefas pendentes
⏰ *{lembretes_ativos}* lembretes ativos
📝 *{total_notas}* anotações guardadas
💡 *{total_ideias}* ideias no banco
📌 *{total_briefing}* itens no briefing

O que vai resolver agora? 💼"""

def limpar_categoria(categoria):
    """Limpa todos os itens de uma categoria."""
    db = load_db()
    if categoria in db:
        total = len(db[categoria])
        db[categoria] = []
        save_db(db)
        return f"🗑️ {total} itens apagados de *{categoria}*."
    return "Categoria não encontrada."

# ============================================================
# ROTEIROS
# ============================================================

def get_roteiro():
    import random
    r = random.choice(ROTEIROS_MEMES)
    return f"""🎬 *Roteiro pronto:*

*{r['titulo']}*
Formato: Meme vitoriano

*Texto 1:* "{r['t1']}"
*Texto 2:* "{r['t2']}"

*Legenda:* {r['legenda']}

Outro roteiro? /roteiro 💼"""

def get_formatos():
    msg = "📱 *Formatos que funcionam:*\n\n"
    msg += "\n".join(FORMATOS_CONTEUDO)
    msg += "\n\nQuer roteiro de algum? Manda o número. 💼"
    return msg

def get_temas():
    msg = "🔥 *Temas que engajam:*\n\n"
    for i, t in enumerate(TEMAS_ENGAJAMENTO, 1):
        msg += f"{i}. {t}\n"
    msg += "\nQuer roteiro sobre algum? Manda o número. 💼"
    return msg

# ============================================================
# MENSAGENS PÚBLICAS
# ============================================================

WELCOME_PUBLIC = """✦ *Tarot Sem Filtro* ✦
_Verdade sem massagem. Boca minha, voz Deles._

Eu sou o Miguel, assistente oficial. 🔮

/precos — 💰 Valores
/como\\_funciona — 🃏 A consulta
/depoimentos — 💬 Depoimentos
/sobre — ✨ Quem é a Carol
/produtos — 📦 Digitais
/consulta — 📲 WhatsApp
/redes — 📱 Redes sociais

Manda sua dúvida! 💜"""

PRECOS_MSG = """💰 *Preços — Março 2026*

✦ *Pergunta avulsa* — R$ 7
✦ *Combo 3 perguntas* — R$ 15-17
✦ *Jogo completo* — R$ 30-35
✦ *Leitura completa* (40min+) — R$ 35

📦 *Digitais (TikTok Shop):*
✦ "Devo Confiar?" — R$ 20
✦ "Autoestima" — R$ 20
✦ "Problema Obstáculo Resolução" — R$ 17
✦ "SIM ou NÃO" — R$ 4

⚠️ Não respondemos: saúde, gravidez, entes falecidos.
/consulta 💜"""

COMO_FUNCIONA_MSG = """🃏 *A consulta*

Atendimento por *áudio no WhatsApp*. A intuição vem falando.

*Precisa de:* nome completo, data de nascimento, foto.
Não precisa contar nada — a Carol canaliza. 🔮

*3 baralhos:* Waite → Cigano → Maria Padilha

/consulta 💜"""

DEPOIMENTOS_MSG = """💬 *Depoimentos*

_"Você lê muito bem, com irmandade. Passa confiança."_
_"Cobra barato por atendimento excelente e completo."_
_"Explica perfeito. Encaixa tudo. Bota pra lascar."_
_"Acertou em cheio."_
_"Eu tava triste agr tô bem kkkkkk"_
_"Engraçada dms, não deixa clientes ficar triste."_

/consulta 🔮"""

SOBRE_MSG = """✨ *Carol* — 31 anos, leonina ♌
Psicóloga · Taróloga · Médium intuitiva
Waite · Cigano · Maria Padilha
Guias: Maria Padilha, Pai Benedito, Tranca Ruas

_"Eu só sou o corpo que tira. Quem tá por trás é algo maior."_

/consulta 💜"""

PRODUTOS_MSG = """📦 *Digitais — TikTok @semfiltrotarot*

✦ "Devo Confiar?" — R$ 20
✦ "Autoestima" — R$ 20
✦ "Problema Obstáculo Resolução" — R$ 17
✦ "SIM ou NÃO" — R$ 4

/consulta pra consulta personalizada 💜"""

REDES_MSG = """📱 *Redes*
✦ IG: [@sfiltrotarot](https://instagram.com/sfiltrotarot)
✦ TikTok: [@semfiltrotarot](https://tiktok.com/@semfiltrotarot)
✦ Pessoal: [@crlcoura](https://instagram.com/crlcoura)
💜"""

CONSULTA_MSG = f"""📲 *Agendar consulta*
👉 [WhatsApp da Carol]({WHATSAPP_LINK})
Nome completo + data de nascimento + foto. 💜"""

# ============================================================
# MENSAGENS CAROL
# ============================================================

WELCOME_CAROL = """E aí, Carol. Miguel na área. 💼

*📊 Gestão:*
/relatorio · /checklist · /metas · /funil · /resumo

*📱 Conteúdo:*
/roteiro · /formatos · /temas · /conteudo · /ideias

*🧠 Estratégia:*
/estrategia

*📝 Assistente Pessoal:*
/notas · /tarefas · /lembretes · /links · /diario · /briefing

*Atalhos rápidos — só digita:*
`anotação: texto` — salva anotação
`tarefa: texto` — cria tarefa
`ideia: texto` — guarda ideia
`link: url` — salva link
`diario: texto` — registro do dia
`briefing: texto` — info pro briefing
`lembrete 30: texto` — lembrete em 30min
`feito 1` — conclui tarefa #1
`apagar nota 1` — apaga anotação #1

Ou manda qualquer coisa. Sem frescura. 🤝"""

RELATORIO_MSG = """📊 *Relatório — Tarot Sem Filtro*

*Números:*
• TikTok: 258 seg | 5.404 curtidas | 70k pico
• IG marca: 52 seg | 19 posts
• IG pessoal: 5k seg
• Orgânico 100%

*Funciona:* prints (3.595v), anti-charlatão (1.296v), Padilha (663v)
*Atenção:* IG fraco, frequência, escalar produtos, plano SP

O que fez essa semana? 💼"""

CHECKLIST_MSG = """✅ *Checklist*

*DIÁRIO:* ☐ 1 conteúdo ☐ responder DMs ☐ 3 stories ☐ interagir 10 perfis
*SEMANAL:* ☐ 1 live ☐ 2 memes ☐ 1 print ☐ 1 vídeo ☐ números
*MENSAL:* ☐ top 3 conteúdos ☐ 1 produto novo ☐ planejar mês ☐ preços

O que tá fazendo? O que tá deixando? 💼"""

METAS_MSG = """🎯 *Metas*
*1-3m:* TikTok 1k, IG 500, agenda cheia, postar todo dia
*3-6m:* TikTok 5k, curso, SP, renda estável
*6-12m:* app, comunidade paga, lives monetizadas, referência

Onde tá travando? 💼"""

FUNIL_MSG = """🔄 *Funil:* TikTok → WhatsApp → amiga → indica → comunidade

✅ Orgânico, custo zero, alta retenção
⚠️ Depende de você, IG fraco, sem automação, digitais pouco divulgados

Quer estratégia pra algum ponto? 💼"""

# ============================================================
# TELEGRAM API
# ============================================================

def telegram_request(method, data=None):
    url = f"{BASE_URL}/{method}"
    if data:
        payload = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    else:
        req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        logger.error(f"Telegram: {e}")
        return None

def send_message(chat_id, text, parse_mode="Markdown"):
    result = telegram_request("sendMessage", {
        "chat_id": chat_id, "text": text,
        "parse_mode": parse_mode, "disable_web_page_preview": False
    })
    if not result or not result.get("ok"):
        telegram_request("sendMessage", {
            "chat_id": chat_id, "text": text,
            "disable_web_page_preview": False
        })

def send_typing(chat_id):
    telegram_request("sendChatAction", {"chat_id": chat_id, "action": "typing"})

# ============================================================
# CLAUDE API
# ============================================================

def ask_claude(user_message, is_carol=False):
    if not ANTHROPIC_API_KEY:
        return None
    persona = MIGUEL_SOCIO_PERSONA if is_carol else MIGUEL_PUBLICO_PERSONA
    try:
        data = json.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 1000,
            "system": persona,
            "messages": [{"role": "user", "content": user_message}]
        }).encode("utf-8")
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages", data=data,
            headers={
                "Content-Type": "application/json",
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01"
            }
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
            return result["content"][0]["text"]
    except Exception as e:
        logger.error(f"Claude: {e}")
        return None

# ============================================================
# DETECTOR DE ATALHOS (texto livre)
# ============================================================

def detect_shortcut(text):
    """Detecta atalhos no texto da Carol e executa."""
    t = text.strip()
    tl = t.lower()

    # Anotação
    for prefix in ["anotação:", "anotacao:", "anota:", "nota:", "anotação ", "anota "]:
        if tl.startswith(prefix):
            conteudo = t[len(prefix):].strip()
            if conteudo:
                return add_nota(conteudo)

    # Tarefa
    for prefix in ["tarefa:", "task:", "fazer:", "tarefa ", "fazer "]:
        if tl.startswith(prefix):
            conteudo = t[len(prefix):].strip()
            if conteudo:
                return add_tarefa(conteudo)

    # Ideia
    for prefix in ["ideia:", "ideia ", "idea:", "idea "]:
        if tl.startswith(prefix):
            conteudo = t[len(prefix):].strip()
            if conteudo:
                return add_ideia(conteudo)

    # Link
    for prefix in ["link:", "link ", "salva link:", "guarda link:"]:
        if tl.startswith(prefix):
            conteudo = t[len(prefix):].strip()
            if conteudo:
                return add_link(conteudo)

    # Diário
    for prefix in ["diario:", "diário:", "diario ", "diário ", "hoje:"]:
        if tl.startswith(prefix):
            conteudo = t[len(prefix):].strip()
            if conteudo:
                return add_diario(conteudo)

    # Briefing
    for prefix in ["briefing:", "briefing ", "brief:", "info:"]:
        if tl.startswith(prefix):
            conteudo = t[len(prefix):].strip()
            if conteudo:
                return add_briefing(conteudo)

    # Lembrete (formato: "lembrete 30: texto" ou "lembrete: texto")
    if tl.startswith("lembrete"):
        resto = t[8:].strip()
        # Tenta extrair minutos
        if resto and resto[0].isdigit():
            partes = resto.split(":", 1)
            if len(partes) == 2:
                try:
                    minutos = int(partes[0].strip())
                    conteudo = partes[1].strip()
                    if conteudo:
                        return add_lembrete(conteudo, minutos)
                except ValueError:
                    pass
        # Sem minutos, default 60min
        if ":" in resto:
            conteudo = resto.split(":", 1)[1].strip()
            if conteudo:
                return add_lembrete(conteudo, 60)

    # Feito (concluir tarefa)
    if tl.startswith("feito ") or tl.startswith("concluir ") or tl.startswith("done "):
        try:
            num = int(tl.split()[-1])
            return complete_tarefa(num)
        except (ValueError, IndexError):
            pass

    # Apagar
    if tl.startswith("apagar ") or tl.startswith("deletar ") or tl.startswith("excluir "):
        partes = tl.split()
        if len(partes) >= 3:
            categoria = partes[1]
            try:
                num = int(partes[2])
                if categoria in ("nota", "anotação", "anotacao"):
                    return delete_nota(num)
            except (ValueError, IndexError):
                pass
        # Limpar categoria inteira
        if len(partes) == 2 and partes[1] in ("notas", "tarefas", "ideias", "links", "diario", "briefing", "lembretes"):
            return limpar_categoria(partes[1])

    return None

# ============================================================
# PALAVRAS-CHAVE
# ============================================================

def smart_reply_public(text):
    t = text.lower()
    if any(w in t for w in ["oi", "olá", "ola", "hey", "eai", "bom dia", "boa tarde", "boa noite"]):
        return "E aí! Sou o Miguel, assistente do Tarot Sem Filtro. 🔮\n\n/precos · /como\\_funciona · /consulta\n\nManda sua dúvida! 💜"
    if any(w in t for w in ["preço", "preco", "valor", "quanto", "cobr"]): return PRECOS_MSG
    if any(w in t for w in ["como funciona", "como é", "como faz"]): return COMO_FUNCIONA_MSG
    if any(w in t for w in ["consulta", "agendar", "marcar", "whatsapp"]): return CONSULTA_MSG
    if any(w in t for w in ["depoimento", "feedback", "avaliação"]): return DEPOIMENTOS_MSG
    if any(w in t for w in ["quem é", "quem e", "sobre", "carol"]): return SOBRE_MSG
    if any(w in t for w in ["produto", "digital", "loja", "shop"]): return PRODUTOS_MSG
    if any(w in t for w in ["rede", "instagram", "tiktok"]): return REDES_MSG
    if any(w in t for w in ["saúde", "saude", "grávida", "gravida", "morreu", "faleceu"]):
        return "A Carol *não responde sobre saúde, gravidez ou entes falecidos*. 🙏\n/consulta pra outros temas 💜"
    if any(w in t for w in ["obrigad", "valeu"]): return "Disponha! /consulta 🔮💜"
    return None

def smart_reply_carol(text):
    t = text.lower()
    if t in ["oi", "olá", "eai", "bom dia", "boa tarde", "boa noite"]:
        return "E aí, Carol. O que vai ser? 💼\n/start pra ver tudo."
    if any(w in t for w in ["não fiz nada", "nada de", "preguiça"]):
        return "Consistência > motivação. Faz UMA coisa agora. Qual? 💼"
    if any(w in t for w in ["postei", "fiz post", "gravei", "publiquei"]):
        return "Manda print ou descreve que eu analiso. 📊"
    if any(w in t for w in ["cansada", "não consigo", "desistir"]):
        return "Lembra de onde você veio, Carol. 3 meses atrás era laudo de 120 dias. Hoje tá aqui, criando, atendendo.\n\nDescansa se precisar, mas não para. Qual o menor passo agora? 💼"
    if "monta o briefing" in t or "gerar briefing" in t or "faz o briefing" in t:
        db = load_db()
        if not db["briefing"]:
            return "📌 Briefing vazio. Vai mandando informações com `briefing: texto` que eu guardo e depois monto. 💼"
        info = "\n".join([f"- {b['texto']}" for b in db["briefing"]])
        prompt = f"Com base nessas informações que a Carol foi guardando, monte um briefing profissional organizado por categorias:\n\n{info}"
        ai = ask_claude(prompt, is_carol=True)
        if ai:
            return f"📌 *Briefing Gerado:*\n\n{ai}"
        return f"📌 *Informações do Briefing:*\n\n{info}\n\n_(Sem IA ativa, mostrando informações brutas)_ 💼"
    return None

# ============================================================
# PROCESSAMENTO
# ============================================================

def is_carol(user_id):
    return user_id == CAROL_TELEGRAM_ID

PUBLIC_COMMANDS = {
    "/precos": PRECOS_MSG, "/como_funciona": COMO_FUNCIONA_MSG,
    "/depoimentos": DEPOIMENTOS_MSG, "/sobre": SOBRE_MSG,
    "/produtos": PRODUTOS_MSG, "/redes": REDES_MSG, "/consulta": CONSULTA_MSG,
}

def handle_message(update):
    message = update.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "").strip()
    user_id = message.get("from", {}).get("id", 0)

    if not chat_id or not text:
        return

    carol = is_carol(user_id)
    command = text.split()[0].lower().split("@")[0]

    # === MODO CAROL ===
    if carol:
        # Comandos
        if command == "/start": send_message(chat_id, WELCOME_CAROL); return
        if command == "/roteiro": send_message(chat_id, get_roteiro()); return
        if command == "/formatos": send_message(chat_id, get_formatos()); return
        if command == "/temas": send_message(chat_id, get_temas()); return
        if command == "/relatorio": send_message(chat_id, RELATORIO_MSG); return
        if command == "/checklist": send_message(chat_id, CHECKLIST_MSG); return
        if command == "/metas": send_message(chat_id, METAS_MSG); return
        if command == "/funil": send_message(chat_id, FUNIL_MSG); return
        if command == "/resumo": send_message(chat_id, get_resumo()); return
        if command == "/notas": send_message(chat_id, list_notas()); return
        if command == "/tarefas": send_message(chat_id, list_tarefas()); return
        if command == "/ideias": send_message(chat_id, list_ideias()); return
        if command == "/links": send_message(chat_id, list_links()); return
        if command == "/diario": send_message(chat_id, list_diario()); return
        if command == "/briefing": send_message(chat_id, list_briefing()); return
        if command == "/lembretes": send_message(chat_id, list_lembretes()); return
        if command == "/estrategia":
            send_message(chat_id, "Qual área?\n1. Seguidores\n2. Conversão\n3. Produtos\n4. Conteúdo\n5. SP\n6. Monetização\n\nEscolhe ou descreve. 🧠")
            return
        if command == "/conteudo":
            send_message(chat_id, "Manda o conteúdo (descreve ou print) que eu avalio: tom, fórmula, engajamento, melhorias, CTA e hashtags. 📊")
            return
        # Comandos públicos (pra Carol testar)
        if command in PUBLIC_COMMANDS:
            send_message(chat_id, PUBLIC_COMMANDS[command]); return

        # Atalhos de texto
        shortcut = detect_shortcut(text)
        if shortcut:
            send_message(chat_id, shortcut); return

        send_typing(chat_id)

        # Palavras-chave
        reply = smart_reply_carol(text)
        if reply: send_message(chat_id, reply); return

        # IA
        ai = ask_claude(text, is_carol=True)
        if ai: send_message(chat_id, ai); return

        send_message(chat_id, "Não peguei. Usa /start pra ver tudo que eu faço. 💼")
        return

    # === MODO PÚBLICO ===
    if command in ("/start", "/help"): send_message(chat_id, WELCOME_PUBLIC); return
    if command in PUBLIC_COMMANDS: send_message(chat_id, PUBLIC_COMMANDS[command]); return

    send_typing(chat_id)
    reply = smart_reply_public(text)
    if reply: send_message(chat_id, reply); return
    ai = ask_claude(text, is_carol=False)
    if ai: send_message(chat_id, ai); return
    send_message(chat_id, "Não entendi. /precos · /consulta · /sobre 💜")

# ============================================================
# LOOP + LEMBRETES
# ============================================================

def lembrete_loop():
    """Thread separada que checa lembretes a cada 30 segundos."""
    while True:
        try:
            if CAROL_TELEGRAM_ID:
                check_lembretes()
        except Exception as e:
            logger.error(f"Lembrete: {e}")
        time.sleep(30)

def main():
    logger.info("=" * 50)
    logger.info("🔮 MIGUEL — @CarimboMiguelbot")
    logger.info("   Sócio + Gestor + Assistente Pessoal")
    logger.info("=" * 50)
    logger.info(f"   IA: {'✅' if ANTHROPIC_API_KEY else '❌'}")
    logger.info(f"   Carol: {CAROL_TELEGRAM_ID or '⚠️'}")
    logger.info("=" * 50)

    # Inicia thread de lembretes
    t = threading.Thread(target=lembrete_loop, daemon=True)
    t.start()
    logger.info("⏰ Sistema de lembretes ativo.")

    offset = 0
    while True:
        try:
            result = telegram_request("getUpdates", {"offset": offset, "timeout": 30})
            if not result or not result.get("ok"): continue
            for update in result.get("result", []):
                offset = update["update_id"] + 1
                handle_message(update)
        except KeyboardInterrupt:
            logger.info("Encerrado.")
            break
        except Exception as e:
            logger.error(f"Erro: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
