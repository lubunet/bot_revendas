import telebot
from telebot import types
import subprocess
import random
import re
import ast
import os
import json
import html
import threading
import time
import shlex
import tempfile
import pytz
import json
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import revenda
import sub
import zipfile
import shutil
import socket
import telebot.apihelper as apihelper

# =========================================================
# CONFIGURAÇÕES PRINCIPAIS
# =========================================================
TOKEN = "8536673527:AAHj1PyF2cCEYVepxg3RrafGm4ewF41QnfU"
ADMIN_ID = 843005386
PREVIEW_URL = "https://a.imagem.app/GBaprX.png"
PREVIEW_URL_REVENDAS = "https://a.imagem.app/GG1sGX.png"

# Arquivo onde os testes temporários ficarão salvos
TESTES_FILE = "/root/revenda/testes.txt"

# Arquivo que salva se o modo UUID está ativo ou não e o bakupe
UUID_MODE_FILE = "/root/revenda/uuid_mode.txt"
UUID_EXPIRED_MODE_FILE = "/root/revenda/uuid_exp_mode.txt"
UUID_EXPIRED_FILE = "/root/revenda/uuid_exp.txt"
AUTO_BACKUP_FILE = "/root/revenda/auto_backup.txt"
# Tempo de checagem dos testes expirados
CHECK_INTERVAL = 60
UUID_EXPIRED_MONITOR_INTERVAL = 30

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# Guarda dados temporários do fluxo
user_data = {}

# Controle de ações em andamento por usuário
list_users_busy = {}

# Lock para leitura/escrita segura do arquivo de testes
testes_lock = threading.Lock()
uuid_exp_lock = threading.Lock()
xray_config_lock = threading.Lock()
uuid_monitor_lock = threading.Lock()

#puxar a lista de usuarios
USUARIOS_DB = "/root/usuarios.db"
SENHAS_DIR = "/etc/SSHPlus/senha"
XRAY_CONFIG_FILE = "/usr/local/etc/xray/config.json"

# DADOS DE REVENDAS e subs
REV_DIR = "/root/revenda/dados_rev"
SUB_DIR = "/root/revenda/dados_sub"

SP_TZ = pytz.timezone("America/Sao_Paulo")
# =========================================================
# FUNÇÕES BÁSICAS
# =========================================================
def eh_admin(user_id):
    return user_id == ADMIN_ID


def limpar_fluxo(user_id):
    if user_id in user_data:
        del user_data[user_id]


def senha_aleatoria():
    return f"{random.randint(1000, 9999)}"


def senha_valida(senha):
    return re.fullmatch(r"[A-Za-z0-9]{4,8}", senha) is not None


def username_valido(username):
    return re.fullmatch(r"[A-Za-z0-9]{4,8}", username) is not None

def username_apenas_numeros(username):
    return str(username).isdigit()

def esc(texto):
    return html.escape(str(texto))


# =========================================================
# CONTROLE DO MODO UUID
# =========================================================

def extrair_uuid_vless(v2ray_link):
    if not v2ray_link:
        return None

    match = re.search(r"vless://([0-9a-fA-F-]+)@", str(v2ray_link))
    if match:
        return match.group(1)

    return None


def garantir_arquivo_uuid_mode():
    pasta = os.path.dirname(UUID_MODE_FILE)
    if pasta:
        os.makedirs(pasta, exist_ok=True)

    if not os.path.exists(UUID_MODE_FILE):
        with open(UUID_MODE_FILE, "w", encoding="utf-8") as f:
            f.write("0")

# =========================================================
# CONTROLE DO AUTO BACKUP
# =========================================================
def garantir_arquivo_auto_backup():
    pasta = os.path.dirname(AUTO_BACKUP_FILE)
    if pasta:
        os.makedirs(pasta, exist_ok=True)

    if not os.path.exists(AUTO_BACKUP_FILE):
        with open(AUTO_BACKUP_FILE, "w", encoding="utf-8") as f:
            f.write("0")


def auto_backup_ativo():
    garantir_arquivo_auto_backup()
    try:
        with open(AUTO_BACKUP_FILE, "r", encoding="utf-8") as f:
            return f.read().strip() == "1"
    except:
        return False


def definir_auto_backup(ativo):
    garantir_arquivo_auto_backup()
    with open(AUTO_BACKUP_FILE, "w", encoding="utf-8") as f:
        f.write("1" if ativo else "0")


def texto_botao_auto_backup():
    return "Desativar Auto backup" if auto_backup_ativo() else "Ativar Auto backup"

def uuid_mode_ativo():
    garantir_arquivo_uuid_mode()
    try:
        with open(UUID_MODE_FILE, "r", encoding="utf-8") as f:
            return f.read().strip() == "1"
    except:
        return False


def definir_uuid_mode(ativo):
    garantir_arquivo_uuid_mode()
    with open(UUID_MODE_FILE, "w", encoding="utf-8") as f:
        f.write("1" if ativo else "0")


def texto_botao_uuid():
    return "Desativar usuários UUID" if uuid_mode_ativo() else "Ativar usuários UUID"


# =========================================================
# MARKUPS DO PAINEL
# =========================================================
def painel_markup():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("Criar usuário", callback_data="criar_usuario"),
        types.InlineKeyboardButton("Criar teste", callback_data="criar_teste")
    )   
    kb.add(
        types.InlineKeyboardButton("Criar usuário automático", callback_data="criar_usuario_auto")
    )
    kb.add(
        types.InlineKeyboardButton("Alterar Limite", callback_data="alterar_limite"),
        types.InlineKeyboardButton("Alterar Senha", callback_data="alterar_senha")
    )     
    kb.add(
        types.InlineKeyboardButton("Alterar Data", callback_data="alterar_data"),
        types.InlineKeyboardButton("Renovar", callback_data="renovar_usuario")
    )
    kb.add(
        types.InlineKeyboardButton("Deletar usuário", callback_data="deletar_usuario"),
        types.InlineKeyboardButton("Apagar expirados", callback_data="apagar_expirados")
    )    
    kb.add(
        types.InlineKeyboardButton("Listar usuários", callback_data="listar_usuarios_painel"),
        types.InlineKeyboardButton("Usuários Online", callback_data="usuarios_online_menu")
    )   
    kb.add(
        types.InlineKeyboardButton("Consultar usuário", callback_data="consultar_usuario_individual")
    )     
    kb.add(
        types.InlineKeyboardButton("REVENDAS", callback_data="painel_revendas")
    )
    kb.add(
        types.InlineKeyboardButton("Mais funções", callback_data="mais_funcoes_admin")
    )
    return kb


def painel_usuario_auto_markup():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("📅 1 mês", callback_data="auto_mes_1"))
    kb.add(types.InlineKeyboardButton("📅 2 meses", callback_data="auto_mes_2"))
    kb.add(types.InlineKeyboardButton("📅 3 meses", callback_data="auto_mes_3"))
    return kb


def painel_usuario_auto_tipo_markup():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("XRay", callback_data="auto_tipo_xray"),
        types.InlineKeyboardButton("Nenhum", callback_data="auto_tipo_nenhum")
    )
    return kb


def teclado_tipo_manual():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.row(types.KeyboardButton("XRay"), types.KeyboardButton("Nenhum"))
    return kb


# =========================================================
# FUNÇÕES DE USUÁRIOS DO SISTEMA
# =========================================================
def listar_usuarios():
    comando = ["/opt/sshplus/plugin-sync", "-h", "--list-users"]
    resultado = subprocess.run(
        comando,
        capture_output=True,
        text=True,
        timeout=20
    )

    if resultado.returncode != 0:
        erro = (resultado.stderr or resultado.stdout or "Erro ao listar usuários").strip()
        raise Exception(erro)

    saida = (resultado.stdout or "").strip()

    try:
        lista = ast.literal_eval(saida)
        if isinstance(lista, list):
            return [str(x) for x in lista]
        return []
    except Exception:
        raise Exception(f"Saída inválida ao listar usuários: {saida}")


def usuario_existe(username):
    usuarios_existentes = listar_usuarios()
    username_lower = username.lower()
    usuarios_existentes_lower = {u.lower() for u in usuarios_existentes}
    return username_lower in usuarios_existentes_lower


def criar_usuario_sistema(username, senha, limite, dias, usar_v2ray=False):
    comando = [
        "/opt/sshplus/plugin-sync",
        "-h",
        "--create-user",
        username,
        senha,
        str(limite),
        str(dias)
    ]

    if usar_v2ray:
        comando.append("--v2ray")

    resultado = subprocess.run(
        comando,
        capture_output=True,
        text=True,
        timeout=20
    )

    if resultado.returncode != 0:
        erro = (resultado.stderr or resultado.stdout or "Erro ao criar usuário").strip()
        raise Exception(erro)

    if usar_v2ray:
        saida = (resultado.stdout or "").strip()
        try:
            return json.loads(saida)
        except Exception:
            raise Exception(f"Saída inválida do modo UUID/XRay: {saida}")

    return None

def alterar_limite_usuario_sistema(username, limite):
    comando = [
        "/opt/sshplus/plugin-sync",
        "-h",
        "--limit-user",
        username,
        str(limite)
    ]

    resultado = subprocess.run(
        comando,
        capture_output=True,
        text=True,
        timeout=20
    )

    if resultado.returncode != 0:
        erro = (resultado.stderr or resultado.stdout or "Erro ao alterar limite").strip()
        raise Exception(erro)

def deletar_usuario_sistema(username):
    comando = [
        "/opt/sshplus/plugin-sync",
        "-h",
        "--del-user",
        username
    ]

    resultado = subprocess.run(
        comando,
        capture_output=True,
        text=True,
        timeout=20
    )

    if resultado.returncode != 0:
        erro = (resultado.stderr or resultado.stdout or "Erro ao deletar usuário").strip()
        raise Exception(erro)


# =========================================================
# FUNÇÕES DO ARQUIVO DE TESTES
# Formato:
# usuario|horas|timestamp_expiracao
# =========================================================
def garantir_arquivo_testes():
    pasta = os.path.dirname(TESTES_FILE)
    if pasta:
        os.makedirs(pasta, exist_ok=True)

    if not os.path.exists(TESTES_FILE):
        with open(TESTES_FILE, "w", encoding="utf-8") as f:
            pass


def ler_testes():
    garantir_arquivo_testes()

    testes = []
    with testes_lock:
        with open(TESTES_FILE, "r", encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                if not linha:
                    continue

                partes = linha.split("|")
                if len(partes) != 3:
                    continue

                username, horas, expires_at = partes
                try:
                    horas_int = int(horas)
                    expira_em = datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")
                    testes.append({
                        "username": username,
                        "horas": horas_int,
                        "expires_at": expira_em
                    })
                except:
                    continue

    return testes


def salvar_testes(testes):
    garantir_arquivo_testes()

    with testes_lock:
        with open(TESTES_FILE, "w", encoding="utf-8") as f:
            for teste in testes:
                linha = f"{teste['username']}|{teste['horas']}|{teste['expires_at'].strftime('%Y-%m-%d %H:%M:%S')}\n"
                f.write(linha)


def adicionar_teste_arquivo(username, horas, expires_at):
    garantir_arquivo_testes()

    with testes_lock:
        with open(TESTES_FILE, "a", encoding="utf-8") as f:
            f.write(f"{username}|{horas}|{expires_at.strftime('%Y-%m-%d %H:%M:%S')}\n")


# =========================================================
# GERAÇÃO DE NOMES AUTOMÁTICOS
# =========================================================
def gerar_username_teste():
    return f"teste{random.randint(100, 999)}"


def gerar_username_auto():
    return f"app{random.randint(100, 999)}"


def gerar_username_disponivel(prefixo, max_tentativas=3):
    for _ in range(max_tentativas):
        if prefixo == "teste":
            username = gerar_username_teste()
        elif prefixo == "app":
            username = gerar_username_auto()
        else:
            return None

        try:
            if not usuario_existe(username):
                return username
        except Exception:
            raise

    return None


# =========================================================
# CÁLCULO PRECISO DE VENCIMENTO MENSAL
# =========================================================
def calcular_vencimento_mensal(meses):
    hoje = datetime.now().date()
    vencimento = hoje + relativedelta(months=+meses)
    return vencimento

def calcular_dias_ate_vencimento(vencimento):
    hoje = datetime.now().date()
    dias = (vencimento - hoje).days

    if dias <= 0:
        dias = 1

    return dias


# =========================================================
# MENSAGENS FORMATADAS
# =========================================================
def montar_msg_usuario(username, senha, limite, vencimento_formatado, uuid_code=None):
    texto = (
        "✅ <b>Usuário criado com sucesso!</b>\n\n"
        f"👤 <b>Usuário:</b> <code>{esc(username)}</code>\n"
        f"🔑 <b>Senha:</b> <code>{esc(senha)}</code>\n"
        f"👥 <b>Limite:</b> {esc(limite)}\n"
        f"📅 <b>Vencimento:</b> {esc(vencimento_formatado)}"
    )

    if uuid_code:
        texto += f"\n\n🆔 <b>UUID:</b> <code>{esc(uuid_code)}</code>"

    return texto


def montar_msg_teste(username, senha, horas, uuid_code=None):
    texto = (
        "✅ <b>Teste criado</b>\n\n"
        f"👤 <b>Usuário:</b> <code>{esc(username)}</code>\n"
        f"🔑 <b>Senha:</b> <code>{esc(senha)}</code>\n"
        f"⏰ <b>Tempo:</b> {esc(horas)} hora(s)"
    )

    if uuid_code:
        texto += f"\n\n🆔 <b>UUID:</b> <code>{esc(uuid_code)}</code>"

    return texto


# =========================================================
# ROTINA AUTOMÁTICA PARA APAGAR TESTES EXPIRADOS
# Agora devolve automaticamente o crédito da revenda OU sub-revenda
# =========================================================
def processar_testes_expirados():
    try:
        testes = ler_testes()
        agora = datetime.now()

        restantes = []

        for teste in testes:
            username = teste["username"]
            expires_at = teste["expires_at"]

            if agora >= expires_at:
                try:
                    deletar_usuario_sistema(username)

                    # -------------------------------------------------
                    # Primeiro tenta como SUB-REVENDA
                    # -------------------------------------------------
                    telegram_sub = encontrar_subrevenda_do_usuario(username)
                    if telegram_sub:
                        try:
                            remover_usuario_sub_arquivo(telegram_sub, username)
                        except:
                            pass

                        try:
                            dados_sub = ler_dados_subrevenda(telegram_sub)
                            dono = str(dados_sub.get("dono", "")).strip()
                            limite_total = int(str(dados_sub.get("limite_total", "0")).strip())
                            vencimento = str(dados_sub.get("vencimento", "")).strip()

                            usado = calcular_limite_usado_real_subrevenda(telegram_sub)
                            novo_limite_restante = limite_total - usado
                            if novo_limite_restante < 0:
                                novo_limite_restante = 0

                            salvar_subrevenda(
                                dono=dono,
                                telegram_user=telegram_sub,
                                limite_total=limite_total,
                                limite_restante=novo_limite_restante,
                                vencimento_formatado=vencimento
                            )
                        except:
                            pass

                        # já tratou como sub, vai para o próximo teste
                        continue

                    # -------------------------------------------------
                    # Se não for sub, tenta como REVENDA
                    # -------------------------------------------------
                    telegram_user = encontrar_revenda_do_usuario(username)
                    if telegram_user:
                        try:
                            remover_usuario_revenda_arquivo(telegram_user, username)
                        except:
                            pass

                        try:
                            recalcular_limite_restante_revenda(telegram_user)
                        except:
                            pass

                except Exception:
                    restantes.append(teste)
            else:
                restantes.append(teste)

        salvar_testes(restantes)

    except Exception as e:
        print(f"[ERRO TESTES] {e}")


def loop_testes_expirados():
    while True:
        processar_testes_expirados()
        time.sleep(CHECK_INTERVAL)


def iniciar_monitor_testes():
    garantir_arquivo_testes()
    garantir_arquivo_uuid_mode()
    processar_testes_expirados()
    t = threading.Thread(target=loop_testes_expirados, daemon=True)
    t.start()

# =========================================================
# MONITOR DE VENCIMENTO DAS REVENDAS
# 09:00 -> avisa quem vence no dia
# 23:59 -> suspende automaticamente quem venceu
# =========================================================
def monitor_revendas():
    while True:
        try:
            agora = datetime.now(SP_TZ)
            hoje_str = agora.strftime("%d/%m/%Y")
            hora_minuto = agora.strftime("%H:%M")

            for telegram_user in listar_todas_revendas():
                try:
                    dados = ler_dados_revenda(telegram_user)
                    ultimo_aviso = str(dados.get("ultimo_aviso", "")).strip()
                    ultima_suspensao = str(dados.get("ultima_suspensao", "")).strip()

                    # Aviso às 09:00 no dia do vencimento
                    if hora_minuto == "09:00":
                        if revenda_vence_hoje(telegram_user) and ultimo_aviso != hoje_str:
                            enviado = enviar_msg_revenda(
                                telegram_user,
                                "⚠️ Sua revenda vence hoje.\n\nFaça a renovação para não ficar sem acesso."
                            )

                            if enviado:
                                salvar_campo_revenda(telegram_user, "ultimo_aviso", hoje_str)

                    # Suspensão automática às 23:59 do dia do vencimento
                    if revenda_deve_ser_suspensa_hoje(telegram_user, hora=23, minuto=59):
                        if not revenda_suspensa(telegram_user) and ultima_suspensao != hoje_str:
                            suspender_revenda_automaticamente(telegram_user)

                except Exception as e:
                    try:
                        bot.send_message(
                            ADMIN_ID,
                            f"❌ Erro ao processar revenda automática.\n\n"
                            f"👤 <b>Revenda:</b> <code>{esc(telegram_user)}</code>\n"
                            f"<code>{esc(e)}</code>"
                        )
                    except:
                        pass

            time.sleep(50)

        except Exception as e:
            try:
                bot.send_message(
                    ADMIN_ID,
                    f"❌ Erro no monitor de revendas.\n<code>{esc(e)}</code>"
                )
            except:
                pass

            time.sleep(60)

# =========================================================
# MONITOR DE VENCIMENTO DAS SUB-REVENDAS
# 09:00 -> avisa quem vence no dia
# 23:59 -> suspende automaticamente quem venceu
# =========================================================
def monitor_subrevendas():
    while True:
        try:
            agora = datetime.now(SP_TZ)
            hoje_str = agora.strftime("%d/%m/%Y")
            hora_minuto = agora.strftime("%H:%M")

            for telegram_user in listar_todas_subrevendas():
                try:
                    dados = ler_dados_subrevenda(telegram_user)
                    ultimo_aviso = str(dados.get("ultimo_aviso", "")).strip()
                    ultima_suspensao = str(dados.get("ultima_suspensao", "")).strip()
                    dono = str(dados.get("dono", "")).strip()

                    # Aviso às 09:00 no dia do vencimento
                    if hora_minuto == "09:00":
                        if subrevenda_vence_hoje(telegram_user) and ultimo_aviso != hoje_str:
                            enviado = enviar_msg_subrevenda(
                                telegram_user,
                                "⚠️ Seu acesso vence hoje.\n\nEsse é o último dia do painel. Renove para não ficar sem acesso."
                            )

                            if enviado:
                                salvar_campo_subrevenda(telegram_user, "ultimo_aviso", hoje_str)

                    # Suspensão automática às 23:59 do dia do vencimento
                    if subrevenda_deve_ser_suspensa_hoje(telegram_user, hora=23, minuto=59):
                        if not subrevenda_suspensa(telegram_user) and ultima_suspensao != hoje_str:
                            suspender_subrevenda_automaticamente(telegram_user)

                except Exception as e:
                    try:
                        bot.send_message(
                            ADMIN_ID,
                            f"❌ Erro ao processar sub-revenda automática.\n\n"
                            f"👤 <b>Sub-revenda:</b> <code>{esc(telegram_user)}</code>\n"
                            f"<code>{esc(e)}</code>"
                        )
                    except:
                        pass

            time.sleep(50)

        except Exception as e:
            try:
                bot.send_message(
                    ADMIN_ID,
                    f"❌ Erro no monitor de sub-revendas.\n<code>{esc(e)}</code>"
                )
            except:
                pass

            time.sleep(60)


def iniciar_monitor_subrevendas():
    t = threading.Thread(target=monitor_subrevendas, daemon=True)
    t.start()

def iniciar_monitor_revendas():
    t = threading.Thread(target=monitor_revendas, daemon=True)
    t.start()

# =========================================================
# AUTO BACKUP
# 11:00 / 18:00 / 00:05
# =========================================================
def monitor_auto_backup():
    ultimo_envio = None

    while True:
        try:
            if auto_backup_ativo():
                agora = datetime.now(SP_TZ)
                hoje_str = agora.strftime("%d/%m/%Y")
                hora_minuto = agora.strftime("%H:%M")

                horarios = {"11:00", "18:00", "00:05"}

                chave = f"{hoje_str} {hora_minuto}"

                if hora_minuto in horarios and ultimo_envio != chave:
                    enviar_backup_automatico()
                    ultimo_envio = chave

            time.sleep(40)

        except Exception as e:
            try:
                bot.send_message(
                    ADMIN_ID,
                    f"❌ Erro no monitor de auto backup.\n<code>{esc(e)}</code>"
                )
            except:
                pass

            time.sleep(60)


def iniciar_monitor_auto_backup():
    garantir_arquivo_auto_backup()
    t = threading.Thread(target=monitor_auto_backup, daemon=True)
    t.start()

# =========================================================
# VERIFICAR REVENDAS VENCIDAS NA INICIALIZAÇÃO
# Se o bot ficou offline, ao voltar ele suspende tudo
# que já estiver vencido no diretório /root/revenda/dados_rev
# =========================================================
def verificar_revendas_vencidas_ao_iniciar():
    processadas = 0
    suspensas = 0
    ja_suspensas = 0
    erros = []

    try:
        for telegram_user in listar_todas_revendas():
            processadas += 1

            try:
                # Se já está suspensa, não faz de novo
                if revenda_suspensa(telegram_user):
                    ja_suspensas += 1
                    continue

                # Se venceu e ainda não foi suspensa, suspende agora
                if revenda_deve_ser_suspensa_hoje(telegram_user):
                    suspender_revenda_automaticamente(telegram_user)
                    suspensas += 1

            except Exception as e:
                erros.append(f"{telegram_user}: {e}")

        # Só avisa o admin se realmente houve alguma suspensão
        if suspensas > 0:
            resumo = (
                f"🔍 <b>Verificação de revendas ao iniciar concluída</b>\n\n"
                f"📦 <b>Revendas analisadas:</b> <code>{esc(processadas)}</code>\n"
                f"⛔ <b>Suspensas agora:</b> <code>{esc(suspensas)}</code>\n"
                f"🔒 <b>Já estavam suspensas:</b> <code>{esc(ja_suspensas)}</code>\n"
                f"⚠️ <b>Erros:</b> <code>{esc(len(erros))}</code>"
            )

            bot.send_message(ADMIN_ID, resumo)

        # Se houve erro, aí sim avisa também
        if erros:
            bot.send_message(
                ADMIN_ID,
                "❌ <b>Erros na verificação inicial de revendas</b>\n\n"
                + "\n".join(f"<code>{esc(x)}</code>" for x in erros[:20])
            )

    except Exception as e:
        try:
            bot.send_message(
                ADMIN_ID,
                f"❌ Erro geral ao verificar revendas vencidas na inicialização.\n"
                f"<code>{esc(e)}</code>"
            )
        except:
            pass
        
# =========================================================
# VERIFICAR SUB-REVENDAS VENCIDAS NA INICIALIZAÇÃO
# =========================================================
def verificar_subrevendas_vencidas_ao_iniciar():
    processadas = 0
    suspensas = 0
    ja_suspensas = 0
    erros = []

    try:
        for telegram_user in listar_todas_subrevendas():
            processadas += 1

            try:
                if subrevenda_suspensa(telegram_user):
                    ja_suspensas += 1
                    continue

                if subrevenda_deve_ser_suspensa_hoje(telegram_user):
                    suspender_subrevenda_automaticamente(telegram_user)
                    suspensas += 1

            except Exception as e:
                erros.append(f"{telegram_user}: {e}")

        print(
            "[SUBREVENDAS VENCIDAS AO INICIAR] "
            f"processadas={processadas} | "
            f"suspensas={suspensas} | "
            f"ja_suspensas={ja_suspensas} | "
            f"erros={len(erros)}"
        )

        if erros:
            bot.send_message(
                ADMIN_ID,
                "❌ <b>Erros ao verificar sub-revendas vencidas na inicialização</b>\n\n"
                + "\n".join(f"<code>{esc(x)}</code>" for x in erros[:20])
            )

    except Exception as e:
        print(f"[ERRO SUBREVENDAS AO INICIAR] {e}")

        try:
            bot.send_message(
                ADMIN_ID,
                f"❌ Erro na verificação inicial das sub-revendas.\n<code>{esc(e)}</code>"
            )
        except:
            pass
        
# =========================================================
# COMANDOS DO BOT
# =========================================================
@bot.message_handler(commands=["start"])
def start(message):
    texto = (
        "<b>Bot de gerenciamento de logins</b>\n\n"
        "Use /menu para abrir o painel."
    )
    bot.send_message(message.chat.id, texto)


@bot.message_handler(commands=["menu"])
def menu(message):
    if eh_admin(message.from_user.id):
        nome = esc(message.from_user.first_name or "Usuário")
        texto = f"🚀 <b>{nome}</b>, Bem Vindoª Ao Painel LUBU NET"

        preview = types.LinkPreviewOptions(
            is_disabled=False,
            url=PREVIEW_URL,
            show_above_text=True,
            prefer_large_media=True
        )

        bot.send_message(
            message.chat.id,
            texto,
            reply_markup=painel_markup(),
            link_preview_options=preview
        )
        return

    tg = obter_telegram_atual(message)

    if tg and usuario_eh_revenda(message):
        if revenda_suspensa(tg):
            bot.reply_to(message, "❌ Você está suspenso.")
            return
    
        salvar_chat_id_revenda(tg, message.chat.id)
        revenda.abrir_menu_revenda(message)
        return
    
    if tg and usuario_eh_subrevenda(message):
        salvar_chat_id_subrevenda(tg, message.chat.id)
    
        if subrevenda_suspensa(tg):
            bot.reply_to(message, "❌ Você está suspenso.")
            return
    
        sub.abrir_menu_subrevenda(message)
        return
    
    bot.reply_to(message, "❌ Acesso negado!")


# =========================================================
# CALLBACK DOS BOTÕES
# =========================================================
@bot.callback_query_handler(func=lambda c: True)
def callback(c):
    tg = obter_telegram_atual(c)

    if tg and usuario_eh_revenda(c):
        if revenda_suspensa(tg):
            bot.answer_callback_query(c.id, "❌ Você está suspenso.", show_alert=True)
            return
    
        if revenda.handle_callback_revenda(c):
            return
    
        bot.answer_callback_query(c.id, "❌ Sem permissão.", show_alert=True)
        return
    
    if tg and usuario_eh_subrevenda(c):
        if subrevenda_suspensa(tg):
            bot.answer_callback_query(c.id, "❌ Você está suspenso.", show_alert=True)
            return
    
        if sub.handle_callback_subrevenda(c):
            return
    
        bot.answer_callback_query(c.id, "❌ Sem permissão.", show_alert=True)
        return
    
    if not eh_admin(c.from_user.id):
        bot.answer_callback_query(c.id, "❌ Sem permissão.", show_alert=True)
        return
    # -----------------------------------------------------
    # LISTAR USUÁRIOS
    # -----------------------------------------------------
    if c.data == "listar_usuarios_painel":
        bot.answer_callback_query(c.id, "Abrindo...")
    
        try:
            bot.edit_message_text(
                chat_id=c.message.chat.id,
                message_id=c.message.message_id,
                text="<b>LISTAR USUÁRIOS</b>\n\nEscolha uma opção:",
                reply_markup=painel_listar_usuarios_admin_markup()
            )
        except Exception as e:
            bot.send_message(
                c.message.chat.id,
                f"❌ Erro ao abrir menu de listagem.\n<code>{esc(e)}</code>"
            )
    
        return
    
    # -----------------------------------------------------
    # LISTAR USUÁRIOS - TODOS
    # -----------------------------------------------------
    if c.data == "listar_usuarios_todos":
        if list_users_busy.get(c.from_user.id):
            bot.answer_callback_query(
                c.id,
                "Aguarde, a lista já está sendo gerada.",
                show_alert=True
            )
            return

        list_users_busy[c.from_user.id] = True
        bot.answer_callback_query(c.id, "Buscando usuários.")

        try:
            # o próprio painel vira "consultando"
            bot.edit_message_text(
                chat_id=c.message.chat.id,
                message_id=c.message.message_id,
                text="<b>Consultando usuários...</b>"
            )

            usuarios = obter_lista_completa_usuarios()
            texto = montar_texto_lista_usuarios(usuarios)

            if len(texto) <= 3500:
                bot.edit_message_text(
                    chat_id=c.message.chat.id,
                    message_id=c.message.message_id,
                    text=texto,
                    reply_markup=painel_voltar_markup()
                )
            else:
                pdf_path = gerar_pdf_usuarios(usuarios)
                try:
                    with open(pdf_path, "rb") as pdf_file:
                        # apaga o consultando antes de mandar o pdf
                        try:
                            bot.delete_message(c.message.chat.id, c.message.message_id)
                        except:
                            pass

                        bot.send_document(
                            c.message.chat.id,
                            pdf_file,
                            caption=f"Lista de usuários ({len(usuarios)} no total)"
                        )
                finally:
                    if os.path.exists(pdf_path):
                        os.remove(pdf_path)

        except Exception as e:
            bot.send_message(
                c.message.chat.id,
                f"❌ Erro ao listar usuários.\n<code>{esc(e)}</code>"
            )
        finally:
            list_users_busy.pop(c.from_user.id, None)

        return
    
    
    # -----------------------------------------------------
    # LISTAR USUÁRIOS - MEUS
    # -----------------------------------------------------
    if c.data == "listar_usuarios_meus":
        if list_users_busy.get(c.from_user.id):
            bot.answer_callback_query(
                c.id,
                "Aguarde, a lista já está sendo gerada.",
                show_alert=True
            )
            return

        list_users_busy[c.from_user.id] = True
        bot.answer_callback_query(c.id, "Buscando usuários.")

        try:
            # o próprio painel vira "consultando"
            bot.edit_message_text(
                chat_id=c.message.chat.id,
                message_id=c.message.message_id,
                text="<b>Consultando usuários...</b>"
            )

            usuarios = obter_lista_completa_usuarios_meus()
            texto = montar_texto_lista_usuarios(usuarios)

            if len(texto) <= 3500:
                bot.edit_message_text(
                    chat_id=c.message.chat.id,
                    message_id=c.message.message_id,
                    text=texto,
                    reply_markup=painel_voltar_markup()
                )
            else:
                pdf_path = gerar_pdf_usuarios(usuarios)
                try:
                    with open(pdf_path, "rb") as pdf_file:
                        # apaga o consultando antes de mandar o pdf
                        try:
                            bot.delete_message(c.message.chat.id, c.message.message_id)
                        except:
                            pass

                        bot.send_document(
                            c.message.chat.id,
                            pdf_file,
                            caption=f"Lista de usuários ({len(usuarios)} no total)"
                        )
                finally:
                    if os.path.exists(pdf_path):
                        os.remove(pdf_path)

        except Exception as e:
            bot.send_message(
                c.message.chat.id,
                f"❌ Erro ao listar usuários.\n<code>{esc(e)}</code>"
            )
        finally:
            list_users_busy.pop(c.from_user.id, None)

        return
    
    # -----------------------------------------------------
    # VOLTAR PARA O PAINEL
    # -----------------------------------------------------
    if c.data == "voltar_painel":
        bot.answer_callback_query(c.id, "Voltando...")

        try:
            preview = types.LinkPreviewOptions(
                is_disabled=False,
                url=PREVIEW_URL,
                show_above_text=True,
                prefer_large_media=True
            )

            nome = esc(c.from_user.first_name or "Usuário")
            texto = f"🚀 <b>{nome}</b>, Bem Vindoª Ao Painel LUBU NET"

            bot.edit_message_text(
                chat_id=c.message.chat.id,
                message_id=c.message.message_id,
                text=texto,
                reply_markup=painel_markup(),
                link_preview_options=preview
            )
        except Exception as e:
            bot.send_message(
                c.message.chat.id,
                f"❌ Erro ao voltar para o painel.\n<code>{esc(e)}</code>"
            )
        return
        
    # -----------------------------------------------------
    # PAINEL REVENDAS
    # -----------------------------------------------------
    if c.data == "painel_revendas":
        bot.answer_callback_query(c.id, "Abrindo...")
    
        try:
            preview = types.LinkPreviewOptions(
                is_disabled=False,
                url=PREVIEW_URL_REVENDAS,
                show_above_text=True,
                prefer_large_media=True
            )
    
            bot.edit_message_text(
                chat_id=c.message.chat.id,
                message_id=c.message.message_id,
                text="<b>PAINEL REVENDAS</b>\n\nEscolha uma opção:",
                reply_markup=painel_revendas_markup(),
                link_preview_options=preview
            )
        except Exception as e:
            bot.send_message(
                c.message.chat.id,
                f"❌ Erro ao abrir painel de revendas.\n<code>{esc(e)}</code>"
            )
        return
    
    # -----------------------------------------------------
    # ADICIONAR REVENDA
    # -----------------------------------------------------
    if c.data == "add_revenda":
        bot.answer_callback_query(c.id, "Abrindo...")

        try:
            bot.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        limpar_fluxo(c.from_user.id)
        user_data[c.from_user.id] = {"acao": "add_revenda"}

        msg = bot.send_message(
            c.message.chat.id,
            "Envie o @ da revenda."
        )
        bot.register_next_step_handler(msg, receber_telegram_revenda)
        return
    
    # -----------------------------------------------------
    # DELETAR REVENDA
    # -----------------------------------------------------
    if c.data == "del_revenda":
        bot.answer_callback_query(c.id, "Abrindo...")

        try:
            bot.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        limpar_fluxo(c.from_user.id)
        user_data[c.from_user.id] = {"acao": "del_revenda"}

        msg = bot.send_message(
            c.message.chat.id,
            "Envie o @ da revenda para deletar."
        )
        bot.register_next_step_handler(msg, receber_telegram_del_revenda)
        return
    
    # -----------------------------------------------------
    # TOGGLE DO CONTROLE DE UUIDS VENCIDOS
    # -----------------------------------------------------
    if c.data == "toggle_uuid_expired_mode":
        try:
            if uuid_expired_mode_ativo():
                resumo = restaurar_todos_uuid_suspensos_xray()
                definir_uuid_expired_mode(False)
                mensagem = (
                    "Controle de UUID vencidos desativado.\n"
                    f"UUIDs restaurados: {resumo['restaurados']}"
                )
            else:
                definir_uuid_expired_mode(True)
                resumo_sync = sincronizar_uuid_vencidos_xray_agora()
                resumo_exp = resumo_sync["expirados"]
                resumo_paineis = resumo_sync["paineis_suspensos"]
                resumo_rea = resumo_sync["reativacao"]
                mensagem = (
                    "Controle de UUID vencidos ativado.\n"
                    f"Removidos agora: {resumo_exp['removidos_xray'] + resumo_paineis['removidos_xray']} | "
                    f"Reativados agora: {resumo_rea['reativados']}"
                )

            try:
                bot.edit_message_reply_markup(
                    chat_id=c.message.chat.id,
                    message_id=c.message.message_id,
                    reply_markup=painel_mais_funcoes_markup()
                )
            except:
                pass

            bot.answer_callback_query(c.id, mensagem, show_alert=True)

        except Exception as e:
            bot.answer_callback_query(
                c.id,
                f"Erro ao alterar controle de UUID vencidos: {e}",
                show_alert=True
            )
        return

    # -----------------------------------------------------
    # TOGGLE DO MODO UUID
    # -----------------------------------------------------
    if c.data == "toggle_uuid_mode":
        novo_estado = not uuid_mode_ativo()
        definir_uuid_mode(novo_estado)
    
        try:
            bot.edit_message_reply_markup(
                chat_id=c.message.chat.id,
                message_id=c.message.message_id,
                reply_markup=painel_mais_funcoes_markup()
            )
        except:
            pass
    
        bot.answer_callback_query(
            c.id,
            "Modo UUID ativado." if novo_estado else "Modo UUID desativado.",
            show_alert=True
        )
        return

    # -----------------------------------------------------
    # CRIAR USUÁRIO NORMAL
    # -----------------------------------------------------
    if c.data == "criar_usuario":
        bot.answer_callback_query(c.id, "Abrindo...")

        try:
            bot.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        limpar_fluxo(c.from_user.id)
        user_data[c.from_user.id] = {"acao": "criar_usuario"}

        msg = bot.send_message(c.message.chat.id, "Envie o nome do usuário.")
        bot.register_next_step_handler(msg, receber_usuario)
        return

    # -----------------------------------------------------
    # CRIAR TESTE
    # -----------------------------------------------------
    if c.data == "criar_teste":
        bot.answer_callback_query(c.id, "Abrindo...")

        try:
            bot.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        limpar_fluxo(c.from_user.id)
        user_data[c.from_user.id] = {"acao": "criar_teste"}

        msg = bot.send_message(
            c.message.chat.id,
            "Envie a quantidade de horas do teste. Máximo: 24"
        )
        bot.register_next_step_handler(msg, receber_horas_teste)
        return

    # -----------------------------------------------------
    # ABRIR MINI PAINEL DE USUÁRIO AUTOMÁTICO
    # -----------------------------------------------------
    if c.data == "criar_usuario_auto":
        bot.answer_callback_query(c.id, "Abrindo...")

        limpar_fluxo(c.from_user.id)
        user_data[c.from_user.id] = {"acao": "criar_usuario_auto"}

        try:
            bot.edit_message_text(
                chat_id=c.message.chat.id,
                message_id=c.message.message_id,
                text=(
                    "<b>Criar usuário automático</b>\n\n"
                    "Escolha abaixo a validade do usuário:"
                ),
                reply_markup=painel_usuario_auto_markup()
            )
        except Exception as e:
            bot.send_message(c.message.chat.id, f"❌ Erro ao abrir painel.\n<code>{esc(e)}</code>")
        return

    # -----------------------------------------------------
    # ESCOLHA DE 1, 2 OU 3 MESES DO AUTO
    # -----------------------------------------------------
    if c.data in ["auto_mes_1", "auto_mes_2", "auto_mes_3"]:
        bot.answer_callback_query(c.id, "Continuando...")

        mapa_meses = {
            "auto_mes_1": 1,
            "auto_mes_2": 2,
            "auto_mes_3": 3
        }
        meses = mapa_meses[c.data]

        if uuid_mode_ativo():
            user_data[c.from_user.id] = {
                "acao": "criar_usuario_auto",
                "meses": meses
            }

            try:
                bot.edit_message_text(
                    chat_id=c.message.chat.id,
                    message_id=c.message.message_id,
                    text=(
                        "<b>Criar usuário automático</b>\n\n"
                        "Escolha o tipo da configuração:"
                    ),
                    reply_markup=painel_usuario_auto_tipo_markup()
                )
            except Exception as e:
                limpar_fluxo(c.from_user.id)
                bot.send_message(c.message.chat.id, f"❌ Erro ao abrir opções.\n<code>{esc(e)}</code>")
            return

        try:
            bot.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        try:
            username = gerar_username_disponivel("app", max_tentativas=3)

            if not username:
                limpar_fluxo(c.from_user.id)
                bot.send_message(
                    c.message.chat.id,
                    "❌ Não foi possível gerar um usuário disponível. Digite /menu para tentar novamente."
                )
                return

            senha = senha_aleatoria()
            limite = 1
            vencimento = calcular_vencimento_mensal(meses)
            vencimento_formatado = vencimento.strftime("%d/%m/%Y")
            dias_para_plugin = calcular_dias_ate_vencimento(vencimento)

            criar_usuario_sistema(username, senha, limite, dias_para_plugin, usar_v2ray=False)

            bot.send_message(
                c.message.chat.id,
                montar_msg_usuario(username, senha, limite, vencimento_formatado)
            )

        except subprocess.TimeoutExpired:
            bot.send_message(c.message.chat.id, "❌ O comando demorou demais.")
        except Exception as e:
            bot.send_message(
                c.message.chat.id,
                f"❌ Falha ao criar usuário automático.\n<code>{esc(e)}</code>"
            )
        finally:
            limpar_fluxo(c.from_user.id)
        return

    # -----------------------------------------------------
    # ESCOLHA DO TIPO DO AUTO QUANDO UUID ESTÁ ATIVO
    # -----------------------------------------------------
    if c.data in ["auto_tipo_xray", "auto_tipo_nenhum"]:
        bot.answer_callback_query(c.id, "Criando...")

        dados = user_data.get(c.from_user.id)
        if not dados or dados.get("acao") != "criar_usuario_auto" or "meses" not in dados:
            limpar_fluxo(c.from_user.id)
            bot.send_message(c.message.chat.id, "❌ Fluxo inválido. Digite /menu para tentar novamente.")
            return

        meses = dados["meses"]
        usar_v2ray = c.data == "auto_tipo_xray"

        try:
            bot.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        try:
            username = gerar_username_disponivel("app", max_tentativas=3)

            if not username:
                limpar_fluxo(c.from_user.id)
                bot.send_message(
                    c.message.chat.id,
                    "❌ Não foi possível gerar um usuário disponível. Digite /menu para tentar novamente."
                )
                return

            senha = senha_aleatoria()
            limite = 1
            vencimento = calcular_vencimento_mensal(meses)
            vencimento_formatado = vencimento.strftime("%d/%m/%Y")
            dias_para_plugin = calcular_dias_ate_vencimento(vencimento)

            retorno_v2ray = criar_usuario_sistema(
                username, senha, limite, dias_para_plugin, usar_v2ray=usar_v2ray
            )

            uuid_code = None
            if usar_v2ray and retorno_v2ray:
                uuid_code = extrair_uuid_vless(retorno_v2ray.get("v2ray"))
            
            bot.send_message(
                c.message.chat.id,
                montar_msg_usuario(username, senha, limite, vencimento_formatado, uuid_code)
            )

        except subprocess.TimeoutExpired:
            bot.send_message(c.message.chat.id, "❌ O comando demorou demais.")
        except Exception as e:
            bot.send_message(
                c.message.chat.id,
                f"❌ Falha ao criar usuário automático.\n<code>{esc(e)}</code>"
            )
        finally:
            limpar_fluxo(c.from_user.id)
        return

    # ----------------
    # ALTERAR LIMITE
    # ----------------
    if c.data == "alterar_limite":
        bot.answer_callback_query(c.id, "Abrindo...")
    
        try:
            bot.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass
    
        limpar_fluxo(c.from_user.id)
        user_data[c.from_user.id] = {"acao": "alterar_limite"}
    
        msg = bot.send_message(
            c.message.chat.id,
            "Envie o nome do usuário."
        )
        bot.register_next_step_handler(msg, receber_usuario_alterar_limite)
        return

    # ----------------
    # ALTERAR SENHA
    # ----------------
    if c.data == "alterar_senha":
        bot.answer_callback_query(c.id, "Abrindo...")
    
        try:
            bot.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass
    
        limpar_fluxo(c.from_user.id)
        user_data[c.from_user.id] = {"acao": "alterar_senha"}
    
        msg = bot.send_message(
            c.message.chat.id,
            "Envie o nome do usuário."
        )
        bot.register_next_step_handler(msg, receber_usuario_alterar_senha)
        return

    # ----------------
    # ALTERAR DATA
    # ----------------
    if c.data == "alterar_data":
        bot.answer_callback_query(c.id, "Abrindo...")
    
        try:
            bot.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass
    
        limpar_fluxo(c.from_user.id)
        user_data[c.from_user.id] = {"acao": "alterar_data"}
    
        msg = bot.send_message(
            c.message.chat.id,
            "Envie o nome do usuário."
        )
        bot.register_next_step_handler(msg, receber_usuario_alterar_data)
        return
    
    
    # ----------------
    # RENOVAR USUÁRIO
    # ----------------
    if c.data == "renovar_usuario":
        bot.answer_callback_query(
            c.id,
            "Este usuário será renovado em 1 mês a partir da data de vencimento atual.",
            show_alert=True
        )
    
        try:
            bot.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass
    
        limpar_fluxo(c.from_user.id)
        user_data[c.from_user.id] = {"acao": "renovar_usuario"}
    
        msg = bot.send_message(
            c.message.chat.id,
            "Envie o nome do usuário."
        )
        bot.register_next_step_handler(msg, receber_usuario_renovar)
        return
    
    # -----------------------------------------------------
    # DELETAR USUÁRIO
    # -----------------------------------------------------
    if c.data == "deletar_usuario":
        bot.answer_callback_query(c.id, "Abrindo...")

        try:
            bot.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        limpar_fluxo(c.from_user.id)
        user_data[c.from_user.id] = {"acao": "deletar_usuario"}

        msg = bot.send_message(
            c.message.chat.id,
            "Envie o nome do usuário."
        )
        bot.register_next_step_handler(msg, receber_usuario_deletar)
        return

    # -----------------------------------------------------
    # VERIFICAR USUÁRIOS EXPIRADOS
    # -----------------------------------------------------
    if c.data == "apagar_expirados":
        bot.answer_callback_query(c.id, "Verificando...")

        try:
            bot.edit_message_text(
                chat_id=c.message.chat.id,
                message_id=c.message.message_id,
                text="⏳ <b>Verificando expirados...</b>"
            )

            expirados = obter_usuarios_expirados_meus()

            # guarda temporariamente para usar no botão deletar
            user_data[c.from_user.id] = {
                "acao": "apagar_expirados",
                "expirados": expirados
            }

            if expirados:
                bot.edit_message_text(
                    chat_id=c.message.chat.id,
                    message_id=c.message.message_id,
                    text=montar_texto_expirados(expirados),
                    reply_markup=painel_expirados_markup(tem_expirados=True)
                )
            else:
                bot.edit_message_text(
                    chat_id=c.message.chat.id,
                    message_id=c.message.message_id,
                    text="🗑️ <b>Nenhum usuário expirado.</b>",
                    reply_markup=painel_expirados_markup(tem_expirados=False)
                )

        except Exception as e:
            bot.send_message(
                c.message.chat.id,
                f"❌ Erro ao verificar expirados.\n<code>{esc(e)}</code>"
            )
        return
    
    # -----------------------------------------------------
    # DELETAR USUÁRIOS EXPIRADOS
    # -----------------------------------------------------
    if c.data == "confirmar_deletar_expirados":
        bot.answer_callback_query(c.id, "Apagando...")

        dados = user_data.get(c.from_user.id)
        if not dados or dados.get("acao") != "apagar_expirados":
            limpar_fluxo(c.from_user.id)
            bot.send_message(
                c.message.chat.id,
                "❌ Fluxo inválido. Digite /menu para tentar novamente."
            )
            return

        expirados = dados.get("expirados", [])
        apagados = 0

        try:
            bot.edit_message_text(
                chat_id=c.message.chat.id,
                message_id=c.message.message_id,
                text="⏳ <b>Apagando usuários expirados...</b>"
            )

            for username in expirados:
                try:
                    deletar_usuario_sistema(username)
                    apagados += 1
                except Exception:
                    continue

            limpar_fluxo(c.from_user.id)

            bot.edit_message_text(
                chat_id=c.message.chat.id,
                message_id=c.message.message_id,
                text=f"✅ <b>{apagados} usuário{'s' if apagados != 1 else ''} apagado{'s' if apagados != 1 else ''} com sucesso!</b>"
            )

        except Exception as e:
            limpar_fluxo(c.from_user.id)
            bot.send_message(
                c.message.chat.id,
                f"❌ Erro ao apagar expirados.\n<code>{esc(e)}</code>"
            )
        return

    # -----------------------------------------------------
    # ALTERAR DATA DA REVENDA
    # -----------------------------------------------------
    if c.data == "alt_data_revenda":
        bot.answer_callback_query(c.id, "Abrindo...")

        try:
            bot.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        limpar_fluxo(c.from_user.id)
        user_data[c.from_user.id] = {"acao": "alt_data_revenda"}

        msg = bot.send_message(
            c.message.chat.id,
            "Envie o @ da revenda."
        )
        bot.register_next_step_handler(msg, receber_telegram_alt_data_revenda)
        return
    
    # -----------------------------------------------------
    # ALTERAR LIMITE DA REVENDA
    # -----------------------------------------------------
    if c.data == "alt_limite_revenda":
        bot.answer_callback_query(c.id, "Abrindo...")

        try:
            bot.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        limpar_fluxo(c.from_user.id)
        user_data[c.from_user.id] = {"acao": "alt_limite_revenda"}

        msg = bot.send_message(
            c.message.chat.id,
            "Envie o @ da revenda."
        )
        bot.register_next_step_handler(msg, receber_telegram_alt_limite_revenda)
        return
    
    # -----------------------------------------------------
    # SUSPENDER REVENDA
    # -----------------------------------------------------
    if c.data == "suspender_revenda":
        bot.answer_callback_query(c.id, "Abrindo...")

        try:
            bot.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        limpar_fluxo(c.from_user.id)
        user_data[c.from_user.id] = {"acao": "suspender_revenda"}

        msg = bot.send_message(
            c.message.chat.id,
            "Envie o @ da revenda."
        )
        bot.register_next_step_handler(msg, receber_telegram_suspender_revenda)
        return    
    
    # -----------------------------------------------------
    # RENOVAR REVENDA
    # -----------------------------------------------------
    if c.data == "renovar_revenda":
        bot.answer_callback_query(
            c.id,
            (
                "Se a revenda estiver ativa, será renovada em 1 mês a partir "
                "da data de vencimento atual.\n\n"
                "Se estiver suspensa, será renovada em 1 mês a partir de hoje "
                "e todos os usuários dela serão desbloqueados."
            ),
            show_alert=True
        )

        try:
            bot.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        limpar_fluxo(c.from_user.id)
        user_data[c.from_user.id] = {"acao": "renovar_revenda"}

        msg = bot.send_message(
            c.message.chat.id,
            "Envie o @ da revenda."
        )
        bot.register_next_step_handler(msg, receber_telegram_renovar_revenda)
        return
    
    # -----------------------------------------------------
    # MENU USUÁRIOS ONLINE
    # -----------------------------------------------------
    if c.data == "usuarios_online_menu":
        bot.answer_callback_query(c.id, "Abrindo...")

        try:
            bot.edit_message_text(
                chat_id=c.message.chat.id,
                message_id=c.message.message_id,
                text="<b>MONITOR DE USUÁRIOS ONLINE</b>\n\nEscolha uma opção:",
                reply_markup=painel_usuarios_online_menu_markup()
            )
        except Exception as e:
            bot.send_message(
                c.message.chat.id,
                f"❌ Erro ao abrir menu de usuários online.\n<code>{esc(e)}</code>"
            )
        return
    
    # -----------------------------------------------------
    # USUÁRIOS ONLINE - MEUS
    # -----------------------------------------------------
    if c.data == "usuarios_online_meus":
        if list_users_busy.get(c.from_user.id):
            bot.answer_callback_query(
                c.id,
                "Aguarde, já existe uma consulta em andamento.",
                show_alert=True
            )
            return

        list_users_busy[c.from_user.id] = True
        bot.answer_callback_query(c.id, "Consultando...")

        try:
            bot.edit_message_text(
                chat_id=c.message.chat.id,
                message_id=c.message.message_id,
                text="<b>Consultando...</b>"
            )

            usuarios_online = obter_lista_usuarios_online_meus()
            total_online = total_conexoes_online(usuarios_online)
            texto = montar_texto_usuarios_online(usuarios_online)

            if len(texto) <= 3500:
                bot.edit_message_text(
                    chat_id=c.message.chat.id,
                    message_id=c.message.message_id,
                    text=texto,
                    reply_markup=painel_usuarios_online_voltar_markup()
                )
            else:
                pdf_path = gerar_pdf_usuarios_online(usuarios_online)

                try:
                    preview = types.LinkPreviewOptions(
                        is_disabled=False,
                        url=PREVIEW_URL,
                        show_above_text=True,
                        prefer_large_media=True
                    )

                    nome = esc(c.from_user.first_name or "Usuário")
                    texto_painel = f"🚀 <b>{nome}</b>, Bem Vindoª Ao Painel LUBU NET"

                    bot.edit_message_text(
                        chat_id=c.message.chat.id,
                        message_id=c.message.message_id,
                        text=texto_painel,
                        reply_markup=painel_markup(),
                        link_preview_options=preview
                    )

                    with open(pdf_path, "rb") as pdf_file:
                        bot.send_document(
                            c.message.chat.id,
                            pdf_file,
                            caption=f"Usuários online (meus) ({total_online} no total)"
                        )
                finally:
                    if os.path.exists(pdf_path):
                        os.remove(pdf_path)

        except Exception as e:
            bot.send_message(
                c.message.chat.id,
                f"❌ Erro ao consultar usuários online (meus).\n<code>{esc(e)}</code>"
            )
        finally:
            list_users_busy.pop(c.from_user.id, None)

        return
    # -----------------------------------------------------
    # USUÁRIOS ONLINE - TODOS
    # -----------------------------------------------------
    if c.data == "usuarios_online_todos":
        if list_users_busy.get(c.from_user.id):
            bot.answer_callback_query(
                c.id,
                "Aguarde, já existe uma consulta em andamento.",
                show_alert=True
            )
            return

        list_users_busy[c.from_user.id] = True
        bot.answer_callback_query(c.id, "Consultando...")

        try:
            bot.edit_message_text(
                chat_id=c.message.chat.id,
                message_id=c.message.message_id,
                text="<b>Consultando...</b>"
            )

            usuarios_online = obter_lista_usuarios_online_todos()
            total_online = total_conexoes_online(usuarios_online)
            texto = montar_texto_usuarios_online(usuarios_online)

            # margem de segurança para mensagem HTML no Telegram
            if len(texto) <= 3500:
                bot.edit_message_text(
                    chat_id=c.message.chat.id,
                    message_id=c.message.message_id,
                    text=texto,
                    reply_markup=painel_usuarios_online_voltar_markup()
                )
            else:
                pdf_path = gerar_pdf_usuarios_online(usuarios_online)

                try:
                    # apaga o "Consultando..." e volta para o painel principal
                    preview = types.LinkPreviewOptions(
                        is_disabled=False,
                        url=PREVIEW_URL,
                        show_above_text=True,
                        prefer_large_media=True
                    )

                    nome = esc(c.from_user.first_name or "Usuário")
                    texto_painel = f"🚀 <b>{nome}</b>, Bem Vindoª Ao Painel LUBU NET"

                    bot.edit_message_text(
                        chat_id=c.message.chat.id,
                        message_id=c.message.message_id,
                        text=texto_painel,
                        reply_markup=painel_markup(),
                        link_preview_options=preview
                    )

                    with open(pdf_path, "rb") as pdf_file:
                        bot.send_document(
                            c.message.chat.id,
                            pdf_file,
                            caption=f"Usuários online ({total_online} no total)"
                        )
                finally:
                    if os.path.exists(pdf_path):
                        os.remove(pdf_path)

        except Exception as e:
            bot.send_message(
                c.message.chat.id,
                f"❌ Erro ao consultar usuários online.\n<code>{esc(e)}</code>"
            )
        finally:
            list_users_busy.pop(c.from_user.id, None)

        return

    # -----------------------------------------------------
    # RELATÓRIO GERAL DAS REVENDAS
    # -----------------------------------------------------
    if c.data == "relatorio_revendas":
        if list_users_busy.get(c.from_user.id):
            bot.answer_callback_query(
                c.id,
                "Aguarde, já existe uma consulta em andamento.",
                show_alert=True
            )
            return

        list_users_busy[c.from_user.id] = True
        bot.answer_callback_query(c.id, "Consultando...")

        msg_consultando = None

        try:
            # Mantém o painel atual e envia a msg abaixo
            msg_consultando = bot.send_message(
                c.message.chat.id,
                "<b>Consultando...</b>"
            )

            # -------------------------------------------------
            # 1) SINCRONIZA SILENCIOSAMENTE TODAS AS REVENDAS
            #    SEM EXIBIR NADA AO USUÁRIO
            # -------------------------------------------------
            try:
                sincronizar_todas_revendas()
            
                for telegram_user in listar_todas_revendas():
                    try:
                        recalcular_limite_restante_revenda(telegram_user)
                    except:
                        pass
            except:
                pass

            # -------------------------------------------------
            # 2) AGORA PEGA A LISTA JÁ CORRIGIDA
            # -------------------------------------------------
            revendas = obter_lista_relatorio_revendas()

            # -------------------------------------------------
            # 3) GERA O PDF
            # -------------------------------------------------
            pdf_path = gerar_pdf_relatorio_revendas(revendas)

            try:
                # Apaga a msg "Consultando..."
                if msg_consultando:
                    try:
                        bot.delete_message(
                            msg_consultando.chat.id,
                            msg_consultando.message_id
                        )
                    except:
                        pass

                with open(pdf_path, "rb") as pdf_file:
                    bot.send_document(
                        c.message.chat.id,
                        pdf_file,
                        caption=f"Relatório de revendas ({len(revendas)} no total)"
                    )
            finally:
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)

        except Exception as e:
            try:
                if msg_consultando:
                    bot.delete_message(
                        msg_consultando.chat.id,
                        msg_consultando.message_id
                    )
            except:
                pass

            bot.send_message(
                c.message.chat.id,
                f"❌ Erro ao gerar relatório das revendas.\n<code>{esc(e)}</code>"
            )
        finally:
            list_users_busy.pop(c.from_user.id, None)

        return
    
    # -----------------------------------------------------
    # RELATÓRIO INDIVIDUAL DA REVENDA
    # -----------------------------------------------------
    if c.data == "relatorio_individual_revenda":
        bot.answer_callback_query(c.id, "Abrindo...")

        try:
            bot.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        limpar_fluxo(c.from_user.id)
        user_data[c.from_user.id] = {"acao": "relatorio_individual_revenda"}

        msg = bot.send_message(
            c.message.chat.id,
            "Envie o @ da revenda."
        )
        bot.register_next_step_handler(msg, receber_telegram_relatorio_individual_revenda)
        return
    
    # -----------------------------------------------------
    # RELATORIO SUB-REVENDAS (ADMIN)
    # -----------------------------------------------------
    if c.data == "relatorio_subrevendas_revendas":
        bot.answer_callback_query(c.id, "Consultando...")

        revendas_com_subs = listar_revendas_com_subrevendas()

        if not revendas_com_subs:
            bot.send_message(
                c.message.chat.id,
                "❌ Nenhum revenda possui sub-revendas no momento."
            )
            return

        try:
            bot.edit_message_text(
                chat_id=c.message.chat.id,
                message_id=c.message.message_id,
                text="<b>RELATORIO SUB-REVENDAS</b>\n\nEscolha a revenda:",
                reply_markup=painel_admin_relatorio_subrevendas_markup(revendas_com_subs)
            )
        except Exception as e:
            bot.send_message(
                c.message.chat.id,
                f"❌ Erro ao abrir menu de sub-revendas.\n<code>{esc(e)}</code>"
            )
        return
    
    # -----------------------------------------------------
    # RELATORIO DAS SUB-REVENDAS DE UMA REVENDA ESPECÍFICA
    # -----------------------------------------------------
    if c.data.startswith("admin_rel_subs:"):
        bot.answer_callback_query(c.id, "Consultando...")

        telegram_revenda = "@" + c.data.split(":", 1)[1].strip()

        try:
            exibir_relatorios_subrevendas_da_revenda_admin(
                c.message.chat.id,
                c.message.message_id,
                telegram_revenda
            )
        except Exception as e:
            bot.send_message(
                c.message.chat.id,
                f"❌ Erro ao exibir relatório das sub-revendas.\n<code>{esc(e)}</code>"
            )
        return
    
    # -----------------------------------------------------
    # ALTERAR NOME DE USUARIO DA REVENDA
    # -----------------------------------------------------
    if c.data == "alt_nome_usuario_revenda":
        bot.answer_callback_query(c.id, "Abrindo...")

        try:
            bot.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        limpar_fluxo(c.from_user.id)
        user_data[c.from_user.id] = {"acao": "alt_nome_usuario_revenda"}

        msg = bot.send_message(
            c.message.chat.id,
            "Envie o @ da revenda que deseja alterar."
        )
        bot.register_next_step_handler(msg, receber_telegram_revenda_alterar_nome)
        return
    
    # -----------------------------------------------------
    # CONSULTAR USUÁRIO INDIVIDUAL
    # -----------------------------------------------------
    if c.data == "consultar_usuario_individual":
        bot.answer_callback_query(c.id, "Abrindo...")

        try:
            bot.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        limpar_fluxo(c.from_user.id)
        user_data[c.from_user.id] = {"acao": "consultar_usuario_individual"}

        msg = bot.send_message(
            c.message.chat.id,
            "Envie o nome do usuário ou UUID."
        )
        bot.register_next_step_handler(msg, receber_consulta_usuario_individual)
        return
    
    # -----------------------------------------------------
    # MAIS FUNÇÕES (ADMIN)
    # -----------------------------------------------------
    if c.data == "mais_funcoes_admin":
        bot.answer_callback_query(c.id, "Abrindo...")

        try:
            bot.edit_message_text(
                chat_id=c.message.chat.id,
                message_id=c.message.message_id,
                text="<b>⚙️ INFORMAÇÕES E AJUSTES</b>\n\nEscolha uma opção:",
                reply_markup=painel_mais_funcoes_markup()
            )
        except Exception as e:
            bot.send_message(
                c.message.chat.id,
                f"❌ Erro ao abrir mais funções.\n<code>{esc(e)}</code>"
            )
        return


    # -----------------------------------------------------
    # CRIAR BACKUP (ADMIN)
    # -----------------------------------------------------
    if c.data == "criar_backup_admin":
        bot.answer_callback_query(c.id, "Gerando backup.")

        msg_status = None

        try:
            # manda apenas uma msg abaixo, sem mexer no painel oficial
            msg_status = bot.send_message(
                c.message.chat.id,
                "<b>Gerando backup.</b>"
            )

            try:
                sincronizar_revendas_ao_iniciar()
            except:
                pass

            try:
                sincronizar_subrevendas_ao_iniciar()
            except:
                pass

            zip_path, payload, xray_entries = gerar_backup_zip()

            try:
                with open(zip_path, "rb") as f:
                    bot.send_document(
                        c.message.chat.id,
                        f,
                        caption=(
                            "✅ <b>Backup gerado com sucesso!</b>\n\n"
                            f"👤 <b>Usuários admin:</b> <code>{esc(len(payload['admin_users']))}</code>\n"
                            f"🏪 <b>Revendas:</b> <code>{esc(len(payload['resellers']))}</code>\n"
                            f"🏷️ <b>Sub-revendas:</b> <code>{esc(len(payload['subresellers']))}</code>\n"
                            f"🧪 <b>Testes:</b> <code>{esc(len(payload.get('tests', [])))}</code>\n"
                            f"🆔 <b>Usuários XRay:</b> <code>{esc(len(xray_entries))}</code>"
                        )
                    )
            finally:
                if os.path.exists(zip_path):
                    os.remove(zip_path)

            if msg_status:
                try:
                    bot.delete_message(msg_status.chat.id, msg_status.message_id)
                except:
                    pass

        except Exception as e:
            if msg_status:
                try:
                    bot.edit_message_text(
                        f"❌ <b>Erro ao gerar backup.</b>\n\n<code>{esc(e)}</code>",
                        chat_id=msg_status.chat.id,
                        message_id=msg_status.message_id
                    )
                except:
                    bot.send_message(
                        c.message.chat.id,
                        f"❌ Erro ao gerar backup.\n<code>{esc(e)}</code>"
                    )
            else:
                bot.send_message(
                    c.message.chat.id,
                    f"❌ Erro ao gerar backup.\n<code>{esc(e)}</code>"
                )

        return
    
    # -----------------------------------------------------
    # CONFIRMAR RESTAURAÇÃO DE BACKUP
    # -----------------------------------------------------
    if c.data == "confirmar_restore_backup":
        bot.answer_callback_query(c.id, "Restaurando.")

        dados = user_data.get(c.from_user.id, {})
        if dados.get("acao") != "restore_backup":
            bot.send_message(c.message.chat.id, "❌ Nenhum backup pendente para restaurar.")
            return

        try:
            payload = dados["payload"]
            xray_entries = dados["xray_entries"]

            ultimo_status = {"texto": ""}

            def atualizar_status(texto):
                if texto == ultimo_status["texto"]:
                    return

                ultimo_status["texto"] = texto

                try:
                    bot.edit_message_text(
                        text=texto,
                        chat_id=c.message.chat.id,
                        message_id=c.message.message_id
                    )
                except:
                    pass

            atualizar_status("⏳ <b>Estruturando backup...</b>")

            resumo = restaurar_backup_payload(
                payload,
                xray_entries,
                atualizar_status=atualizar_status
            )

            if resumo["xray_error"]:
                erro_xray_curto = esc(resumo["xray_error"][:1500]) if resumo["xray_error"] else ""

                bot.edit_message_text(
                    (
                        "⚠️ <b>Restauração concluída com falhas.</b>\n\n"
                        f"👤 <b>Usuários restaurados:</b> <code>{esc(resumo['users_ok'])}</code>\n"
                        f"🏪 <b>Revendas:</b> <code>{esc(resumo['resellers'])}</code>\n"
                        f"🏷️ <b>Sub-revendas:</b> <code>{esc(resumo['subresellers'])}</code>\n"
                        f"🧪 <b>Testes restaurados:</b> <code>{esc(resumo.get('tests_restored', 0))}</code>\n"
                        f"🔒 <b>Painéis suspensos reaplicados:</b> <code>{esc(resumo.get('suspensos_reaplicados', 0))}</code>\n"
                        f"🏗️ <b>Falhas de estrutura:</b> <code>{esc(len(resumo['structure_fail']))}</code>\n"
                        f"⚠️ <b>Falhas de usuários:</b> <code>{esc(len(resumo['users_fail']))}</code>\n\n"
                        f"<b>Erro real do XRay:</b>\n<code>{erro_xray_curto}</code>"
                    ),
                    chat_id=c.message.chat.id,
                    message_id=c.message.message_id
                )
            else:
                bot.edit_message_text(
                    (
                        "✅ <b>Backup restaurado com sucesso!</b>\n\n"
                        f"👤 <b>Usuários restaurados:</b> <code>{esc(resumo['users_ok'])}</code>\n"
                        f"🏪 <b>Revendas:</b> <code>{esc(resumo['resellers'])}</code>\n"
                        f"🏷️ <b>Sub-revendas:</b> <code>{esc(resumo['subresellers'])}</code>\n"
                        f"🧪 <b>Testes restaurados:</b> <code>{esc(resumo.get('tests_restored', 0))}</code>\n"
                        f"🔒 <b>Painéis suspensos reaplicados:</b> <code>{esc(resumo.get('suspensos_reaplicados', 0))}</code>\n"
                        f"🆔 <b>UUID corrigidos no XRay:</b> <code>{esc(resumo['xray_updated'])}</code>\n"
                        f"🏗️ <b>Falhas de estrutura:</b> <code>{esc(len(resumo['structure_fail']))}</code>\n"
                        f"⚠️ <b>Falhas de usuários:</b> <code>{esc(len(resumo['users_fail']))}</code>"
                    ),
                    chat_id=c.message.chat.id,
                    message_id=c.message.message_id
                )

            if resumo["structure_fail"]:
                bot.send_message(
                    c.message.chat.id,
                    "⚠️ <b>Falhas na estrutura da restauração:</b>\n\n"
                    + "\n".join(f"<code>{esc(x)}</code>" for x in resumo["structure_fail"][:30])
                )

            if resumo["users_fail"]:
                bot.send_message(
                    c.message.chat.id,
                    "⚠️ <b>Falhas na restauração de alguns usuários:</b>\n\n"
                    + "\n".join(f"<code>{esc(x)}</code>" for x in resumo["users_fail"][:30])
                )

        except Exception as e:
            bot.edit_message_text(
                f"❌ <b>Erro ao restaurar backup.</b>\n\n<code>{esc(e)}</code>",
                chat_id=c.message.chat.id,
                message_id=c.message.message_id
            )
        finally:
            try:
                zip_path = dados.get("zip_path", "")
                if zip_path and os.path.exists(zip_path):
                    os.remove(zip_path)
            except:
                pass

            limpar_fluxo(c.from_user.id)

        return


    # -----------------------------------------------------
    # CANCELAR RESTAURAÇÃO DE BACKUP
    # -----------------------------------------------------
    if c.data == "cancelar_restore_backup":
        bot.answer_callback_query(c.id, "Cancelado.")
        dados = user_data.get(c.from_user.id, {})

        try:
            zip_path = dados.get("zip_path", "")
            if zip_path and os.path.exists(zip_path):
                os.remove(zip_path)
        except:
            pass

        limpar_fluxo(c.from_user.id)

        preview = types.LinkPreviewOptions(
            is_disabled=False,
            url=PREVIEW_URL,
            show_above_text=True,
            prefer_large_media=True
        )

        nome = esc(c.from_user.first_name or "Usuário")
        texto = f"🚀 <b>{nome}</b>, Bem Vindoª Ao Painel LUBU NET"

        bot.edit_message_text(
            chat_id=c.message.chat.id,
            message_id=c.message.message_id,
            text=texto,
            reply_markup=painel_markup(),
            link_preview_options=preview
        )
        return
    
    # -----------------------------------------------------
    # TESTE DE VELOCIDADE
    # -----------------------------------------------------
    if c.data == "teste_velocidade_admin":
        bot.answer_callback_query(c.id, "Executando teste.")

        try:
            msg_status = bot.send_message(
                c.message.chat.id,
                "<b>Executando teste de velocidade.</b>\n\nAguarde..."
            )

            saida = executar_speedtest()
            dados = parsear_speedtest(saida)
            texto = montar_msg_speedtest(dados)

            # mesma mensagem, preview embaixo
            if dados.get("result_url"):
                preview = types.LinkPreviewOptions(
                    is_disabled=False,
                    url=dados["result_url"],
                    show_above_text=False,
                    prefer_large_media=True
                )

                bot.edit_message_text(
                    texto,
                    chat_id=msg_status.chat.id,
                    message_id=msg_status.message_id,
                    link_preview_options=preview
                )
            else:
                bot.edit_message_text(
                    texto,
                    chat_id=msg_status.chat.id,
                    message_id=msg_status.message_id
                )

        except Exception as e:
            try:
                bot.edit_message_text(
                    f"❌ <b>Erro ao executar teste de velocidade.</b>\n\n{esc(e)}",
                    chat_id=msg_status.chat.id,
                    message_id=msg_status.message_id
                )
            except:
                bot.send_message(
                    c.message.chat.id,
                    f"❌ Erro ao executar teste de velocidade.\n{esc(e)}"
                )

        return
    
    # -----------------------------------------------------
    # CALCULAR LIMITE REVENDA
    # -----------------------------------------------------
    if c.data == "calcular_limite_revenda":
        bot.answer_callback_query(c.id, "Abrindo...")

        try:
            bot.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        limpar_fluxo(c.from_user.id)
        user_data[c.from_user.id] = {"acao": "calcular_limite_revenda"}

        msg = bot.send_message(
            c.message.chat.id,
            "Envie o @ da revenda."
        )
        bot.register_next_step_handler(msg, receber_telegram_calcular_limite_revenda)
        return
    
    # -----------------------------------------------------
    # TOGGLE DO AUTO BACKUP
    # -----------------------------------------------------
    if c.data == "toggle_auto_backup":
        novo_estado = not auto_backup_ativo()
        definir_auto_backup(novo_estado)

        try:
            bot.edit_message_reply_markup(
                chat_id=c.message.chat.id,
                message_id=c.message.message_id,
                reply_markup=painel_mais_funcoes_markup()
            )
        except:
            pass

        if novo_estado:
            bot.answer_callback_query(
                c.id,
                "♻️ Auto backup ativado!\n\n"
                "Horários:\n"
                "11:00\n"
                "18:00\n"
                "00:05",
                show_alert=True
            )
        else:
            bot.answer_callback_query(
                c.id,
                "♻️ Auto backup desativado!",
                show_alert=True
            )

        return
    
    # -----------------------------------------------------
    # VOLTAR AO MENU DE REVENDAS
    # -----------------------------------------------------
    if c.data == "voltar_menu_revendas":
        bot.answer_callback_query(c.id, "Voltando...")

        try:
            preview = types.LinkPreviewOptions(
                is_disabled=False,
                url=PREVIEW_URL_REVENDAS,
                show_above_text=True,
                prefer_large_media=True
            )

            bot.edit_message_text(
                chat_id=c.message.chat.id,
                message_id=c.message.message_id,
                text="<b>PAINEL REVENDAS</b>\n\nEscolha uma opção:",
                reply_markup=painel_revendas_markup(),
                link_preview_options=preview
            )
        except Exception as e:
            bot.send_message(
                c.message.chat.id,
                f"❌ Erro ao voltar para o painel de revendas.\n<code>{esc(e)}</code>"
            )
        return
# =========================================================
# FLUXO DE CRIAR USUÁRIO NORMAL
# =========================================================
def receber_usuario(message):
    if not eh_admin(message.from_user.id):
        return

    if not message.text:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Usuário inválido. Digite /menu para tentar novamente."
        )
        return

    username = message.text.strip()

    if not username_valido(username):
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Nome inválido. Use 4 a 8 caracteres com apenas letras e números.\nDigite /menu para tentar novamente."
        )
        return

    if username_apenas_numeros(username):
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Nome inválido. Não pode ser apenas números.\nDigite /menu para tentar novamente."
        )
        return

    try:
        if usuario_existe(username):
            limpar_fluxo(message.from_user.id)
            bot.send_message(
                message.chat.id,
                "❌ Usuário já existe. Digite /menu para tentar novamente."
            )
            return
    except Exception as e:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            f"❌ Erro ao verificar usuários.\n<code>{esc(e)}</code>"
        )
        return

    user_data[message.from_user.id]["username"] = username

    msg = bot.send_message(
        message.chat.id,
        "Envie o limite. Ex: 1"
    )
    bot.register_next_step_handler(msg, receber_limite)


def receber_limite(message):
    if not eh_admin(message.from_user.id):
        return

    if not message.text:
        limpar_fluxo(message.from_user.id)
        bot.send_message(message.chat.id, "❌ Limite inválido. Digite /menu para tentar novamente.")
        return

    texto = message.text.strip()

    if not texto.isdigit() or int(texto) <= 0:
        limpar_fluxo(message.from_user.id)
        bot.send_message(message.chat.id, "❌ Limite inválido. Digite /menu para tentar novamente.")
        return

    user_data[message.from_user.id]["limite"] = int(texto)

    msg = bot.send_message(message.chat.id, "Envie a quantidade de dias. Ex: 30")
    bot.register_next_step_handler(msg, receber_dias)


def receber_dias(message):
    if not eh_admin(message.from_user.id):
        return

    if not message.text:
        limpar_fluxo(message.from_user.id)
        bot.send_message(message.chat.id, "❌ Quantidade inválida. Digite /menu para tentar novamente.")
        return

    texto = message.text.strip()

    if not texto.isdigit() or int(texto) <= 0:
        limpar_fluxo(message.from_user.id)
        bot.send_message(message.chat.id, "❌ Quantidade inválida. Digite /menu para tentar novamente.")
        return

    dias = int(texto)
    user_data[message.from_user.id]["dias"] = dias

    if uuid_mode_ativo():
        msg = bot.send_message(
            message.chat.id,
            "Qual config deseja gerar?",
            reply_markup=teclado_tipo_manual()
        )
        bot.register_next_step_handler(msg, receber_tipo_manual)
        return

    criar_usuario_manual_final(message, usar_v2ray=False)


def receber_tipo_manual(message):
    if not eh_admin(message.from_user.id):
        return

    if not message.text:
        criar_usuario_manual_final(message, usar_v2ray=False)
        return

    texto = message.text.strip().lower()

    if texto == "xray":
        criar_usuario_manual_final(message, usar_v2ray=True)
        return

    # qualquer outra coisa vira "Nenhum"
    criar_usuario_manual_final(message, usar_v2ray=False)


def criar_usuario_manual_final(message, usar_v2ray):
    try:
        dados = user_data.get(message.from_user.id)
        if not dados:
            bot.send_message(
                message.chat.id,
                "❌ Fluxo inválido. Digite /menu para tentar novamente.",
                reply_markup=types.ReplyKeyboardRemove()
            )
            return

        username = dados["username"]
        limite = dados["limite"]
        dias = dados["dias"]
        senha = senha_aleatoria()

        data_vencimento = datetime.now() + timedelta(days=dias)
        vencimento_formatado = data_vencimento.strftime("%d/%m/%Y")

        retorno_v2ray = criar_usuario_sistema(
            username, senha, limite, dias, usar_v2ray=usar_v2ray
        )

        uuid_code = None
        if usar_v2ray and retorno_v2ray:
            uuid_code = extrair_uuid_vless(retorno_v2ray.get("v2ray"))
        
        bot.send_message(
            message.chat.id,
            montar_msg_usuario(username, senha, limite, vencimento_formatado, uuid_code),
            reply_markup=types.ReplyKeyboardRemove()
        )

    except subprocess.TimeoutExpired:
        bot.send_message(
            message.chat.id,
            "❌ O comando demorou demais.",
            reply_markup=types.ReplyKeyboardRemove()
        )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Falha ao criar usuário.\n<code>{esc(e)}</code>",
            reply_markup=types.ReplyKeyboardRemove()
        )
    finally:
        limpar_fluxo(message.from_user.id)


# =========================================================
# FLUXO DE CRIAR TESTE
# =========================================================
def receber_horas_teste(message):
    if not eh_admin(message.from_user.id):
        return

    if not message.text:
        limpar_fluxo(message.from_user.id)
        bot.send_message(message.chat.id, "❌ Horas inválidas. Digite /menu para tentar novamente.")
        return

    texto = message.text.strip()

    if not texto.isdigit():
        limpar_fluxo(message.from_user.id)
        bot.send_message(message.chat.id, "❌ Horas inválidas. Digite /menu para tentar novamente.")
        return

    horas = int(texto)

    if horas <= 0 or horas > 24:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ O teste deve ter entre 1 e 24 horas.\nDigite /menu para tentar novamente."
        )
        return

    try:
        username = gerar_username_disponivel("teste", max_tentativas=3)

        if not username:
            limpar_fluxo(message.from_user.id)
            bot.send_message(
                message.chat.id,
                "❌ Não foi possível gerar um teste disponível. Digite /menu e tente novamente."
            )
            return

        senha = senha_aleatoria()
        limite = 1
        dias_sistema = 2
        expira_em = datetime.now() + timedelta(hours=horas)

        usar_v2ray = uuid_mode_ativo()

        retorno_v2ray = criar_usuario_sistema(
            username, senha, limite, dias_sistema, usar_v2ray=usar_v2ray
        )

        adicionar_teste_arquivo(username, horas, expira_em)

        uuid_code = None
        if usar_v2ray and retorno_v2ray:
            uuid_code = extrair_uuid_vless(retorno_v2ray.get("v2ray"))
        
        bot.send_message(
            message.chat.id,
            montar_msg_teste(username, senha, horas, uuid_code)
        )

    except subprocess.TimeoutExpired:
        bot.send_message(message.chat.id, "❌ O comando demorou demais.")
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Falha ao criar teste.\n<code>{esc(e)}</code>"
        )
    finally:
        limpar_fluxo(message.from_user.id)

# =========================================================
# ALTERAR LIMITE
# =========================================================
def receber_usuario_alterar_limite(message):
    if not eh_admin(message.from_user.id):
        return

    if not message.text:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Usuário não encontrado. Digite /menu para tentar novamente."
        )
        return

    username_digitado = message.text.strip()

    try:
        usuarios_existentes = listar_usuarios()
    except Exception as e:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            f"❌ Erro ao verificar usuários.\n<code>{esc(e)}</code>"
        )
        return

    # Comparação exata, respeitando maiúsculas e minúsculas
    if username_digitado not in usuarios_existentes:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Usuário não encontrado. Digite /menu para tentar novamente."
        )
        return

    user_data[message.from_user.id]["username"] = username_digitado

    msg = bot.send_message(
        message.chat.id,
        "Informe o novo limite."
    )
    bot.register_next_step_handler(msg, receber_novo_limite)    

def receber_novo_limite(message):
    if not eh_admin(message.from_user.id):
        return

    if not message.text:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Limite inválido. Digite /menu para tentar novamente."
        )
        return

    texto = message.text.strip()

    if not texto.isdigit() or int(texto) <= 0:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Limite inválido. Digite /menu para tentar novamente."
        )
        return

    novo_limite = int(texto)
    username = user_data[message.from_user.id]["username"]

    try:
        alterar_limite_usuario_sistema(username, novo_limite)

        bot.send_message(
            message.chat.id,
            "✅ <b>Limite alterado!</b>\n\n"
            f"👤 <b>Usuário:</b> {esc(username)}\n"
            f"👥 <b>Novo limite:</b> {esc(novo_limite)}"
        )

    except subprocess.TimeoutExpired:
        bot.send_message(
            message.chat.id,
            "❌ O comando demorou demais."
        )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Falha ao alterar limite.\n<code>{esc(e)}</code>"
        )
    finally:
        limpar_fluxo(message.from_user.id)

# alterar senha 
def alterar_senha_usuario_sistema(username, nova_senha):
    comando = [
        "/opt/sshplus/plugin-sync",
        "-h",
        "--pass-user",
        username,
        nova_senha
    ]

    resultado = subprocess.run(
        comando,
        capture_output=True,
        text=True,
        timeout=20
    )

    if resultado.returncode != 0:
        erro = (resultado.stderr or resultado.stdout or "Erro ao alterar senha").strip()
        raise Exception(erro)
    
def receber_usuario_alterar_senha(message):
    if not eh_admin(message.from_user.id):
        return

    if not message.text:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Usuário não encontrado. Digite /menu para tentar novamente."
        )
        return

    username_digitado = message.text.strip()

    try:
        usuarios_existentes = listar_usuarios()
    except Exception as e:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            f"❌ Erro ao verificar usuários.\n<code>{esc(e)}</code>"
        )
        return

    # Comparação exata
    if username_digitado not in usuarios_existentes:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Usuário não encontrado. Digite /menu para tentar novamente."
        )
        return

    user_data[message.from_user.id]["username"] = username_digitado

    msg = bot.send_message(
        message.chat.id,
        "Informe a nova senha."
    )
    bot.register_next_step_handler(msg, receber_nova_senha)

def receber_nova_senha(message):
    if not eh_admin(message.from_user.id):
        return

    if not message.text:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Senha inválida. Use 4 a 8 caracteres com apenas letras e números.\nDigite /menu para tentar novamente."
        )
        return

    nova_senha = message.text.strip()

    if not senha_valida(nova_senha):
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Senha inválida. Use 4 a 8 caracteres com apenas letras e números.\nDigite /menu para tentar novamente."
        )
        return

    username = user_data[message.from_user.id]["username"]

    try:
        alterar_senha_usuario_sistema(username, nova_senha)

        bot.send_message(
            message.chat.id,
            "✅ <b>Senha alterada com sucesso!</b>\n\n"
            f"👤 <b>Usuário:</b> <code>{esc(username)}</code>\n"
            f"🔑 <b>Nova senha:</b> <code>{esc(nova_senha)}</code>"
        )

    except subprocess.TimeoutExpired:
        bot.send_message(
            message.chat.id,
            "❌ O comando demorou demais."
        )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Falha ao alterar senha.\n<code>{esc(e)}</code>"
        )
    finally:
        limpar_fluxo(message.from_user.id)


# ----------------
# ALTERAR DATA
# ----------------
def receber_usuario_alterar_data(message):
    if not eh_admin(message.from_user.id):
        return

    if not message.text:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Usuário não encontrado. Digite /menu para tentar novamente."
        )
        return

    username_digitado = message.text.strip()

    try:
        usuarios_existentes = listar_usuarios()
    except Exception as e:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            f"❌ Erro ao verificar usuários.\n<code>{esc(e)}</code>"
        )
        return

    # comparação exata
    if username_digitado not in usuarios_existentes:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Usuário não encontrado. Digite /menu para tentar novamente."
        )
        return

    user_data[message.from_user.id]["username"] = username_digitado

    msg = bot.send_message(
        message.chat.id,
        "Informe a nova quantidade de dias."
    )
    bot.register_next_step_handler(msg, receber_nova_data_usuario)


def receber_nova_data_usuario(message):
    if not eh_admin(message.from_user.id):
        return

    if not message.text:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Data inválida. Digite /menu para tentar novamente."
        )
        return

    texto = message.text.strip()

    if not texto.isdigit() or int(texto) <= 0:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Data inválida. Digite /menu para tentar novamente."
        )
        return

    dias = int(texto)
    username = user_data[message.from_user.id]["username"]

    try:
        alterar_data_usuario_sistema(username, dias)

        nova_data = datetime.now() + timedelta(days=dias)
        nova_data_formatada = nova_data.strftime("%d/%m/%Y")

        bot.send_message(
            message.chat.id,
            "✅ <b>Data alterada!</b>\n\n"
            f"👤 <b>Usuário:</b> <code>{esc(username)}</code>\n"
            f"📅 <b>Nova Data:</b> {esc(nova_data_formatada)}"
        )

    except subprocess.TimeoutExpired:
        bot.send_message(message.chat.id, "❌ O comando demorou demais.")
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Falha ao alterar data.\n<code>{esc(e)}</code>"
        )
    finally:
        limpar_fluxo(message.from_user.id)

# ----------------
# RENOVAR USUÁRIO
# ----------------
def receber_usuario_renovar(message):
    if not eh_admin(message.from_user.id):
        return

    if not message.text:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Usuário não encontrado. Digite /menu para tentar novamente."
        )
        return

    username_digitado = message.text.strip()

    try:
        usuarios_existentes = listar_usuarios()
    except Exception as e:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            f"❌ Erro ao verificar usuários.\n<code>{esc(e)}</code>"
        )
        return

    if username_digitado not in usuarios_existentes:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Usuário não encontrado. Digite /menu para tentar novamente."
        )
        return

    try:
        vencimento_atual = obter_data_vencimento_usuario(username_digitado)
        hoje = datetime.now()

        if vencimento_atual.date() >= hoje.date():
            data_base = vencimento_atual
        else:
            data_base = hoje

        novo_vencimento = calcular_renovacao_mais_um_mes(data_base)
        dias_para_novo_vencimento = calcular_dias_ate_data_futura(novo_vencimento)

        alterar_data_usuario_sistema(username_digitado, dias_para_novo_vencimento)

        vencimento_formatado = novo_vencimento.strftime("%d/%m/%Y")

        bot.send_message(
            message.chat.id,
            "✅ <b>Usuário renovado!</b>\n\n"
            f"👤 <b>Usuário:</b> <code>{esc(username_digitado)}</code>\n"
            f"📅 <b>Nova Data:</b> {esc(vencimento_formatado)}"
        )

    except subprocess.TimeoutExpired:
        bot.send_message(
            message.chat.id,
            "❌ O comando demorou demais."
        )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Falha ao renovar usuário.\n<code>{esc(e)}</code>"
        )
    finally:
        limpar_fluxo(message.from_user.id)
        
# ----------------
# ALTERAR DATA NO SISTEMA
# ----------------
def alterar_data_usuario_sistema(username, dias):
    comando = [
        "/opt/sshplus/plugin-sync",
        "-h",
        "--date-user",
        username,
        str(dias)
    ]

    resultado = subprocess.run(
        comando,
        capture_output=True,
        text=True,
        timeout=20
    )

    if resultado.returncode != 0:
        erro = (resultado.stderr or resultado.stdout or "Erro ao alterar data").strip()
        raise Exception(erro)


# ----------------
# CONSULTAR DATA DE VENCIMENTO ATUAL DO USUÁRIO
# ----------------
def obter_data_vencimento_usuario(username):
    comando = (
        f"LC_ALL=C chage -l {shlex.quote(username)} | "
        "grep 'Account expires' | awk -F ': ' '{print $2}'"
    )

    resultado = subprocess.run(
        ["bash", "-lc", comando],
        capture_output=True,
        text=True,
        timeout=20
    )

    if resultado.returncode != 0:
        erro = (resultado.stderr or resultado.stdout or "Erro ao consultar vencimento").strip()
        raise Exception(erro)

    saida = (resultado.stdout or "").strip()

    if not saida or saida.lower() == "never":
        raise Exception("Usuário sem data de expiração válida.")

    try:
        # Exemplo esperado: Jul 01, 2026
        return datetime.strptime(saida, "%b %d, %Y")
    except Exception:
        raise Exception(f"Data inválida retornada pelo chage: {saida}")


# ----------------
# CALCULAR DIAS RESTANTES PARA A VARREDURA DA REVENDA
# Usa a data real do sistema e devolve:
# - "0" se já venceu
# - "1", "2", "3"... se ainda está válido
# ----------------
def calcular_dias_restantes_revenda_sync(data_vencimento):
    if not data_vencimento:
        return "0"

    hoje = datetime.now().date()
    data_final = data_vencimento.date()

    dias = (data_final - hoje).days

    if dias < 0:
        return "0"

    return str(dias)

# ----------------
# SOMAR 1 MÊS EXATO NA DATA DE VENCIMENTO
# ----------------
def calcular_renovacao_mais_um_mes(data_atual_vencimento):
    return data_atual_vencimento + relativedelta(months=+1)


# ----------------
# CALCULAR DIAS A PARTIR DE AGORA ATÉ A NOVA DATA
# ----------------
def calcular_dias_ate_data_futura(data_futura):
    agora = datetime.now()
    alvo = datetime(
        year=data_futura.year,
        month=data_futura.month,
        day=data_futura.day,
        hour=23,
        minute=59,
        second=59
    )

    diferenca = alvo - agora
    dias = diferenca.days

    if diferenca.total_seconds() > 0 and dias <= 0:
        dias = 1

    if dias <= 0:
        dias = 1

    return dias


# =========================================================
# MARKUP DE VOLTAR
# =========================================================
def painel_voltar_markup():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("⬅️ Voltar", callback_data="voltar_painel"))
    return kb

# =========================================================
# MARKUP DO MENU DE USUÁRIOS ONLINE
# =========================================================
def painel_usuarios_online_menu_markup():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("Todos", callback_data="usuarios_online_todos"),
        types.InlineKeyboardButton("Meus", callback_data="usuarios_online_meus")
    )
    kb.add(types.InlineKeyboardButton("⬅️ Voltar", callback_data="voltar_painel"))
    return kb


# =========================================================
# MARKUP DE VOLTAR DA LISTA DE USUÁRIOS ONLINE
# =========================================================
def painel_usuarios_online_voltar_markup():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("⬅️ Voltar", callback_data="voltar_painel"))
    return kb

# =========================================================
# TEXTO DA LISTA DE USUÁRIOS DO ADMIN
# Mesmo formato da revenda
# =========================================================
def montar_texto_lista_usuarios(usuarios):
    linhas = []
    linhas.append("<b>⚠️ LISTA DE USUÁRIOS ⚠️</b>")
    linhas.append("")
    linhas.append(f"<b>Total usuários:</b> <code>{esc(len(usuarios))}</code>")
    linhas.append("")
    linhas.append("<b>USUÁRIO | SENHA | LIMITE | DATA</b>")

    for item in usuarios:
        try:
            dias_int = int(str(item.get("dias", "0")).strip())
        except:
            dias_int = 0

        if dias_int <= 0:
            data_txt = "Venceu"
        else:
            data_txt = f"{dias_int} DIAS"

        linha = f"{item['username']} • {item['senha']} • {item['limite']} • {data_txt}"
        linhas.append(f"<blockquote>{esc(linha)}</blockquote>")

    uuids = [u for u in usuarios if str(u.get("uuid", "")).strip()]

    if uuids:
        linhas.append("")
        linhas.append("<b>XRAY DISPONÍVEL:</b>")
        linhas.append("")

        for item in uuids:
            linhas.append(
                f"<blockquote>Usuário: {esc(item['username'])}\nUUID: {esc(item['uuid'])}</blockquote>"
            )

    return "\n".join(linhas)

# =========================================================
# GERAR PDF DA LISTA DE USUÁRIOS DO ADMIN
# Mesmo estilo da revenda
# =========================================================
def gerar_pdf_usuarios(usuarios):
    nome_pdf = f"usuarios_adm{random.randint(100, 999)}.pdf"
    pdf_path = os.path.join(tempfile.gettempdir(), nome_pdf)

    c = canvas.Canvas(pdf_path, pagesize=A4)
    largura, altura = A4

    margem = 26
    topo = altura - 40
    rodape = 35

    colunas = [
        ("USUARIO", 105),
        ("SENHA", 85),
        ("LIMITE", 55),
        ("EXPIRACAO", 85),
        ("UUID", 210),
    ]

    def cortar_texto(texto, fonte="Helvetica", tamanho=10, largura_max=100):
        texto = str(texto or "")
        while stringWidth(texto, fonte, tamanho) > largura_max - 8 and len(texto) > 1:
            texto = texto[:-1]
        return texto

    def desenhar_primeira_pagina():
        c.setFont("Helvetica-Bold", 16)
        titulo = "LISTA DE USUARIOS LUBU NET"
        largura_t = stringWidth(titulo, "Helvetica-Bold", 16)
        c.drawString((largura - largura_t) / 2, altura - 28, titulo)

        y = altura - 58
        x = margem

        c.setFont("Helvetica-Bold", 11)
        for titulo_col, largura_col in colunas:
            c.rect(x, y, largura_col, 22)
            c.drawString(x + 6, y + 7, titulo_col)
            x += largura_col

        return y - 22

    def nova_pagina_sem_cabecalho():
        c.showPage()
        c.setFont("Helvetica", 10)
        return altura - 35

    y = desenhar_primeira_pagina()
    c.setFont("Helvetica", 10)

    for item in usuarios:
        try:
            dias_int = int(str(item.get("dias", "0")).strip())
        except:
            dias_int = 0

        if dias_int <= 0:
            data_txt = "VENCEU"
        else:
            data_txt = f"{dias_int} DIAS"

        uuid_txt = str(item.get("uuid", "")).strip() or "-"

        dados = [
            cortar_texto(item.get("username", ""), largura_max=colunas[0][1]),
            cortar_texto(item.get("senha", ""), largura_max=colunas[1][1]),
            cortar_texto(item.get("limite", ""), largura_max=colunas[2][1]),
            cortar_texto(data_txt, largura_max=colunas[3][1]),
            cortar_texto(uuid_txt, largura_max=colunas[4][1]),
        ]

        altura_linha = 22

        if y < rodape:
            y = nova_pagina_sem_cabecalho()

        x = margem
        for i, (_, largura_col) in enumerate(colunas):
            c.rect(x, y, largura_col, altura_linha)
            c.drawString(x + 6, y + 7, dados[i])
            x += largura_col

        y -= altura_linha

    c.save()
    return pdf_path

# =========================================================
# MONITOR DIÁRIO DE SINCRONIZAÇÃO DAS REVENDAS
# Roda todo dia às 23:00 horário de São Paulo
# Sucesso -> só terminal
# Erro -> Telegram
# =========================================================
def monitor_sincronizacao_revendas():
    ultimo_sync = ""

    while True:
        try:
            agora = datetime.now(SP_TZ)
            data_hora = agora.strftime("%d/%m/%Y %H:%M")
            data_chave = agora.strftime("%d/%m/%Y")
            hora_minuto = agora.strftime("%H:%M")

            if hora_minuto == "00:01" and ultimo_sync != data_chave:
                resultados, erros = sincronizar_todas_revendas()

                total_revendas = len(resultados)
                total_analisados = sum(x["analisados"] for x in resultados)
                total_removidos = sum(x["removidos"] for x in resultados)
                total_atualizados = sum(x["atualizados"] for x in resultados)

                print(
                    "[SYNC REVENDAS - DIARIA] "
                    f"executado_em={data_hora} | "
                    f"revendas={total_revendas} | "
                    f"usuarios={total_analisados} | "
                    f"removidos={total_removidos} | "
                    f"atualizados={total_atualizados} | "
                    f"erros={len(erros)}"
                )

                if erros:
                    bot.send_message(
                        ADMIN_ID,
                        "❌ <b>Erros na sincronização diária das revendas</b>\n\n"
                        + "\n".join(f"<code>{esc(x)}</code>" for x in erros[:20])
                    )

                ultimo_sync = data_chave

            time.sleep(50)

        except Exception as e:
            print(f"[ERRO MONITOR SYNC REVENDAS] {e}")

            try:
                bot.send_message(
                    ADMIN_ID,
                    f"❌ Erro no monitor de sincronização das revendas.\n<code>{esc(e)}</code>"
                )
            except:
                pass

            time.sleep(60)


def iniciar_monitor_sincronizacao_revendas():
    t = threading.Thread(target=monitor_sincronizacao_revendas, daemon=True)
    t.start()

# =========================================================
# MONITOR DIÁRIO DE SINCRONIZAÇÃO DAS SUB REVENDA
# Roda todo dia às 00:01 horário de São Paulo
# Sucesso -> só terminal
# Erro -> Telegram
# =========================================================
def monitor_sincronizacao_subrevendas():
    ultimo_sync = ""

    while True:
        try:
            agora = datetime.now(SP_TZ)
            data_hora = agora.strftime("%d/%m/%Y %H:%M")
            data_chave = agora.strftime("%d/%m/%Y")
            hora_minuto = agora.strftime("%H:%M")

            if hora_minuto == "00:01" and ultimo_sync != data_chave:
                resultados, erros = sincronizar_todas_subrevendas()

                total_subs = len(resultados)
                total_analisados = sum(x["analisados"] for x in resultados)
                total_removidos = sum(x["removidos"] for x in resultados)
                total_atualizados = sum(x["atualizados"] for x in resultados)

                print(
                    "[SYNC SUBREVENDAS - DIARIA] "
                    f"executado_em={data_hora} | "
                    f"subrevendas={total_subs} | "
                    f"usuarios={total_analisados} | "
                    f"removidos={total_removidos} | "
                    f"atualizados={total_atualizados} | "
                    f"erros={len(erros)}"
                )

                if erros:
                    bot.send_message(
                        ADMIN_ID,
                        "❌ <b>Erros na sincronização diária das sub-revendas</b>\n\n"
                        + "\n".join(f"<code>{esc(x)}</code>" for x in erros[:20])
                    )

                ultimo_sync = data_chave

            time.sleep(50)

        except Exception as e:
            print(f"[ERRO MONITOR SYNC SUBREVENDAS] {e}")

            try:
                bot.send_message(
                    ADMIN_ID,
                    f"❌ Erro no monitor de sincronização das sub-revendas.\n<code>{esc(e)}</code>"
                )
            except:
                pass

            time.sleep(60)


def iniciar_monitor_sincronizacao_subrevendas():
    t = threading.Thread(target=monitor_sincronizacao_subrevendas, daemon=True)
    t.start()

# =========================================================
# SINCRONIZAR REVENDAS AO INICIAR
# =========================================================
def sincronizar_revendas_ao_iniciar():
    try:
        resultados, erros = sincronizar_todas_revendas()

        total_revendas = len(resultados)
        total_analisados = sum(x["analisados"] for x in resultados)
        total_removidos = sum(x["removidos"] for x in resultados)
        total_atualizados = sum(x["atualizados"] for x in resultados)

        print(
            "[SYNC REVENDAS - INICIAL] "
            f"revendas={total_revendas} | "
            f"usuarios={total_analisados} | "
            f"removidos={total_removidos} | "
            f"atualizados={total_atualizados} | "
            f"erros={len(erros)}"
        )

        if erros:
            bot.send_message(
                ADMIN_ID,
                "❌ <b>Erros na sincronização inicial das revendas</b>\n\n"
                + "\n".join(f"<code>{esc(x)}</code>" for x in erros[:20])
            )

    except Exception as e:
        print(f"[ERRO SYNC REVENDAS - INICIAL] {e}")

        try:
            bot.send_message(
                ADMIN_ID,
                f"❌ Erro ao sincronizar revendas ao iniciar.\n<code>{esc(e)}</code>"
            )
        except:
            pass
        
# =========================================================
# SINCRONIZAR SUB-REVENDAS AO INICIAR
# =========================================================
def sincronizar_subrevendas_ao_iniciar():
    try:
        resultados, erros = sincronizar_todas_subrevendas()

        total_subs = len(resultados)
        total_analisados = sum(x["analisados"] for x in resultados)
        total_removidos = sum(x["removidos"] for x in resultados)
        total_atualizados = sum(x["atualizados"] for x in resultados)

        print(
            "[SYNC SUBREVENDAS - INICIAL] "
            f"subrevendas={total_subs} | "
            f"usuarios={total_analisados} | "
            f"removidos={total_removidos} | "
            f"atualizados={total_atualizados} | "
            f"erros={len(erros)}"
        )

        if erros:
            bot.send_message(
                ADMIN_ID,
                "❌ <b>Erros na sincronização inicial das sub-revendas</b>\n\n"
                + "\n".join(f"<code>{esc(x)}</code>" for x in erros[:20])
            )

    except Exception as e:
        print(f"[ERRO SYNC INICIAL SUBREVENDAS] {e}")

        try:
            bot.send_message(
                ADMIN_ID,
                f"❌ Erro na sincronização inicial das sub-revendas.\n<code>{esc(e)}</code>"
            )
        except:
            pass
        
# =========================================================
# SINCRONIZAR TODAS AS REVENDAS
# =========================================================
def sincronizar_todas_revendas():
    resultados = []
    erros = []

    for telegram_user in listar_todas_revendas():
        try:
            resultado = sincronizar_arquivo_revenda(telegram_user)

            try:
                recalcular_limite_restante_revenda(telegram_user)
            except:
                pass

            resultados.append(resultado)
        except Exception as e:
            erros.append(f"{telegram_user}: {e}")

    return resultados, erros

# =========================================================
# SINCRONIZAR UMA REVENDA INTEIRA
# Regras:
# - se usuário não existe no list-users, remove da revenda
# - se existe, atualiza senha, limite, data e uuid
# - se uuid não existir no Xray, remove o uuid da linha
# =========================================================
def sincronizar_arquivo_revenda(telegram_user):
    usuarios_arquivo = ler_usuarios_revenda_completos(telegram_user)
    if not usuarios_arquivo:
        return {
            "telegram_user": telegram_user,
            "analisados": 0,
            "removidos": 0,
            "atualizados": 0
        }

    usuarios_sistema = set(listar_usuarios())
    mapa_uuids = obter_mapa_uuids_disponiveis()
    mapa_limites = obter_mapa_limites_sistema()

    novos_usuarios = []
    removidos = 0
    atualizados = 0
    usuarios_orfaos_uuid = set()

    for item in usuarios_arquivo:
        username = str(item["username"]).strip()

        # ---------------------------------------------
        # Se não existe mais no sistema, remove
        # ---------------------------------------------
        if username not in usuarios_sistema:
            removidos += 1
            usuarios_orfaos_uuid.add(username)
            continue

        # ---------------------------------------------
        # SENHA REAL DA VPS
        # ---------------------------------------------
        try:
            senha_real = str(obter_senha_usuario(username)).strip()
            if not senha_real:
                senha_real = str(item["senha"]).strip()
        except:
            senha_real = str(item["senha"]).strip()

        # ---------------------------------------------
        # LIMITE REAL DA VPS
        # Lendo diretamente do mapa montado do usuarios.db
        # ---------------------------------------------
        limite_real = str(mapa_limites.get(username, "")).strip()
        if not limite_real:
            limite_real = str(item["limite"]).strip()

        # ---------------------------------------------
        # DATA REAL DA VPS -> salva em "dias"
        # ---------------------------------------------
        try:
            data_venc = obter_data_vencimento_usuario(username)
            dias_txt = calcular_dias_restantes_revenda_sync(data_venc)
        except:
            dias_txt = str(item["dias"]).strip()

        # ---------------------------------------------
        # UUID REAL DO XRAY
        # ---------------------------------------------
        try:
            uuid_real = str(obter_uuid_disponivel_usuario(username, mapa_uuids)).strip()
        except:
            uuid_real = str(item.get("uuid", "")).strip()

        senha_antiga = str(item["senha"]).strip()
        limite_antigo = str(item["limite"]).strip()
        dias_antigo = str(item["dias"]).strip()
        uuid_antigo = str(item.get("uuid", "")).strip()

        mudou = (
            senha_antiga != senha_real or
            limite_antigo != limite_real or
            dias_antigo != dias_txt or
            uuid_antigo != uuid_real
        )

        if mudou:
            atualizados += 1

        novos_usuarios.append({
            "username": username,
            "senha": senha_real,
            "limite": limite_real,
            "dias": dias_txt,
            "uuid": uuid_real
        })

    if usuarios_orfaos_uuid:
        try:
            remover_usuarios_uuid_expirados(usuarios_orfaos_uuid)
        except:
            pass

    reescrever_arquivo_revenda(telegram_user, novos_usuarios)

    return {
        "telegram_user": telegram_user,
        "analisados": len(usuarios_arquivo),
        "removidos": removidos,
        "atualizados": atualizados
    }

# =========================================================
# REESCREVER ARQUIVO DA REVENDA
# Mantém os cabeçalhos e recria o bloco de usuários
# sem linhas sobrando
# =========================================================
def reescrever_arquivo_revenda(telegram_user, usuarios_atualizados):
    caminho = caminho_arquivo_revenda(telegram_user)

    if not os.path.exists(caminho):
        return False

    cabecalhos = []

    with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
        for linha in f:
            linha_limpa = linha.rstrip("\n")
            if not linha_limpa.strip():
                continue
            if "=" in linha_limpa:
                cabecalhos.append(linha_limpa)

    with open(caminho, "w", encoding="utf-8") as f:
        for linha in cabecalhos:
            f.write(linha + "\n")

        if usuarios_atualizados:
            f.write("\n")
            for item in usuarios_atualizados:
                linha = (
                    f"{item['username']} "
                    f"{item['senha']} "
                    f"{item['limite']} "
                    f"{item['dias']}"
                )

                uuid = str(item.get("uuid", "")).strip()
                if uuid:
                    linha += f" {uuid}"

                f.write(linha + "\n")

    return True

# =========================================================
# MONTAR TEXTO DO RELATÓRIO INDIVIDUAL DA REVENDA
# =========================================================
def montar_texto_relatorio_individual_revenda(telegram_user):
    dados = ler_dados_revenda(telegram_user)

    vencimento = str(dados.get("vencimento", "")).strip()
    limite_total = int(dados.get("limite_total", "0"))
    limite_restante = int(dados.get("limite_restante", "0"))
    status = "suspenso" if revenda_suspensa(telegram_user) else "ativo"

    usuarios = ler_usuarios_revenda_completos(telegram_user)

    linhas = []
    linhas.append("⚠️ <b>DADOS DO REVENDA ⚠️</b>")
    linhas.append("")
    linhas.append(f"<b>Usuário:</b> {esc(telegram_user)}")
    linhas.append(f"<b>Data de vencimento:</b> {esc(vencimento)}")
    linhas.append(f"<b>Limite atual:</b> {esc(limite_total)}")
    linhas.append(f"<b>Limite restante:</b> {esc(limite_restante)}")
    linhas.append(f"<b>Status:</b> {esc(status)}")
    linhas.append("")
    linhas.append("<b>USUÁRIO | SENHA | LIMITE | DATA</b>")

    for item in usuarios:
        try:
            dias_int = int(str(item["dias"]).strip())
        except:
            dias_int = 0

        if dias_int <= 0:
            data_txt = "Venceu"
        else:
            data_txt = f"{dias_int} DIAS"

        linha = f"{item['username']} • {item['senha']} • {item['limite']} • {data_txt}"
        linhas.append(f"<blockquote>{esc(linha)}</blockquote>")

    uuids = [u for u in usuarios if str(u.get("uuid", "")).strip()]

    if uuids:
        linhas.append("")
        linhas.append("<b>XRAY DISPONÍVEL:</b>")
        linhas.append("")

        for item in uuids:
            linhas.append(
                f"<blockquote>Usuário: {esc(item['username'])}\nUUID: {esc(item['uuid'])}</blockquote>"
            )

    texto = "\n".join(linhas)
    return texto, usuarios


# =========================================================
# GERAR PDF DO RELATÓRIO INDIVIDUAL DA REVENDA
# =========================================================
def gerar_pdf_relatorio_individual_revenda(telegram_user):
    dados = ler_dados_revenda(telegram_user)

    vencimento = str(dados.get("vencimento", "")).strip()
    limite_total = int(dados.get("limite_total", "0"))
    limite_restante = int(dados.get("limite_restante", "0"))
    status = "suspenso" if revenda_suspensa(telegram_user) else "ativo"
    usuarios = ler_usuarios_revenda_completos(telegram_user)

    nome_pdf = f"relatorio_individual_revenda_{random.randint(100,999)}.pdf"
    pdf_path = os.path.join(tempfile.gettempdir(), nome_pdf)

    c = canvas.Canvas(pdf_path, pagesize=A4)
    largura_pagina, altura_pagina = A4

    rodape = 35
    margem_lateral = 25

    colunas = [
        ("USUARIO", 110),
        ("SENHA", 90),
        ("LIMITE", 70),
        ("DATA", 80),
        ("UUID", 190),
    ]

    largura_tabela = sum(l for _, l in colunas)
    x_inicial = (largura_pagina - largura_tabela) / 2

    def cortar_texto(texto, fonte="Helvetica", tamanho=9, largura_max=100):
        texto = str(texto)
        while stringWidth(texto, fonte, tamanho) > largura_max - 8 and len(texto) > 1:
            texto = texto[:-1]
        return texto

    def desenhar_topo():
        c.setFont("Helvetica-Bold", 16)
        titulo = "RELATÓRIO INDIVIDUAL DA REVENDA"
        largura_titulo = stringWidth(titulo, "Helvetica-Bold", 16)
        c.drawString((largura_pagina - largura_titulo) / 2, altura_pagina - 35, titulo)

        c.setFont("Helvetica", 10)
        y = altura_pagina - 62

        c.drawString(margem_lateral, y, f"Usuário: {telegram_user}")
        y -= 16
        c.drawString(margem_lateral, y, f"Data de vencimento: {vencimento}")
        y -= 16
        c.drawString(margem_lateral, y, f"Limite atual: {limite_total}")
        y -= 16
        c.drawString(margem_lateral, y, f"Limite restante: {limite_restante}")
        y -= 16
        c.drawString(margem_lateral, y, f"Status: {status}")
        y -= 24

        x = x_inicial
        c.setFont("Helvetica-Bold", 9)
        altura_cab = 22

        for titulo_coluna, largura_coluna in colunas:
            c.rect(x, y, largura_coluna, altura_cab)
            c.drawString(x + 6, y + 7, titulo_coluna)
            x += largura_coluna

        return y - altura_cab

    def nova_pagina():
        c.showPage()
        return desenhar_topo()

    y = desenhar_topo()
    c.setFont("Helvetica", 9)

    for item in usuarios:
        if y < rodape:
            y = nova_pagina()
            c.setFont("Helvetica", 9)

        try:
            dias_int = int(str(item["dias"]).strip())
        except:
            dias_int = 0

        if dias_int <= 0:
            data_txt = "Venceu"
        else:
            data_txt = f"{dias_int} DIAS"

        linha = [
            cortar_texto(item["username"], largura_max=colunas[0][1]),
            cortar_texto(item["senha"], largura_max=colunas[1][1]),
            cortar_texto(item["limite"], largura_max=colunas[2][1]),
            cortar_texto(data_txt, largura_max=colunas[3][1]),
            cortar_texto(item.get("uuid", ""), largura_max=colunas[4][1]),
        ]

        x = x_inicial
        altura_linha = 22

        for i, valor in enumerate(linha):
            largura_coluna = colunas[i][1]
            c.rect(x, y, largura_coluna, altura_linha)
            c.drawString(x + 6, y + 7, str(valor))
            x += largura_coluna

        y -= altura_linha

    c.save()
    return pdf_path


# =========================================================
# LER USUÁRIOS COMPLETOS DA REVENDA
# Formato da linha:
# usuario senha limite dias
# usuario senha limite dias uuid
# =========================================================
def ler_usuarios_revenda_completos(telegram_user):
    caminho = caminho_arquivo_revenda(telegram_user)

    if not os.path.exists(caminho):
        return []

    usuarios = []

    with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
        for linha in f:
            linha = linha.strip()

            if not linha:
                continue

            if "=" in linha:
                continue

            partes = linha.split()
            if len(partes) < 4:
                continue

            username = partes[0].strip()
            senha = partes[1].strip()
            limite = partes[2].strip()
            dias = partes[3].strip()
            uuid = partes[4].strip() if len(partes) >= 5 else ""

            usuarios.append({
                "username": username,
                "senha": senha,
                "limite": limite,
                "dias": dias,
                "uuid": uuid
            })

    return usuarios

# =========================================================
# LER UUIDS DO XRAY PELO config.json
# Mapeia:
# email -> id
# =========================================================
def obter_mapa_uuids_xray():
    mapa = {}

    try:
        if not os.path.exists(XRAY_CONFIG_FILE):
            return mapa

        with open(XRAY_CONFIG_FILE, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)

        inbounds = data.get("inbounds", [])
        if not isinstance(inbounds, list):
            return mapa

        for inbound in inbounds:
            settings = inbound.get("settings", {})
            clients = settings.get("clients", [])

            if not isinstance(clients, list):
                continue

            for client in clients:
                if not isinstance(client, dict):
                    continue

                email = str(client.get("email", "")).strip()
                uuid = str(client.get("id", "")).strip()

                if email:
                    mapa[email] = uuid

    except Exception:
        return {}

    return mapa

def obter_uuid_usuario_xray(username, mapa_uuids=None):
    try:
        if mapa_uuids is None:
            mapa_uuids = obter_mapa_uuids_xray()

        return str(mapa_uuids.get(username, "")).strip()
    except:
        return ""
    
# =========================================================
# LISTAR USUÁRIOS PELO ARQUIVO /root/usuarios.db
# =========================================================
def obter_usuarios_do_banco():
    if not os.path.exists(USUARIOS_DB):
        raise Exception(f"Arquivo não encontrado: {USUARIOS_DB}")

    usuarios = []

    with open(USUARIOS_DB, "r", encoding="utf-8", errors="ignore") as f:
        for linha in f:
            linha = linha.strip()

            if not linha:
                continue

            partes = linha.split()

            # precisa ter pelo menos 2 partes: usuario e limite
            if len(partes) < 2:
                continue

            username = partes[0].strip()
            limite_txt = partes[1].strip()

            if not username:
                continue

            if not limite_txt.isdigit():
                raise Exception(f"Limite inválido no arquivo {USUARIOS_DB}: {linha}")

            usuarios.append({
                "username": username,
                "limit": int(limite_txt)
            })

    usuarios.sort(key=lambda x: x["username"].lower())
    return usuarios

def obter_mapa_limites_sistema():
    usuarios = obter_usuarios_do_banco()
    return {str(item["username"]).strip(): str(item["limit"]).strip() for item in usuarios}

# =========================================================
# LER SENHA DO USUÁRIO EM /etc/SSHPlus/senha/NOME
# =========================================================
def obter_senha_usuario(username):
    caminho = os.path.join(SENHAS_DIR, username)

    if not os.path.exists(caminho):
        raise Exception(f"Senha não encontrada para o usuário: {username}")

    with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
        senha = f.read().strip()

    if not senha:
        raise Exception(f"Senha vazia para o usuário: {username}")

    return senha


# =========================================================
# PEGAR DATA DE EXPIRAÇÃO PELO CHAGE
# Retorna datetime ou None se falhar
# =========================================================
def obter_data_expiracao_usuario(username):
    comando = (
        f"LC_ALL=C chage -l {shlex.quote(username)} | "
        "grep 'Account expires' | awk -F ': ' '{print $2}'"
    )

    resultado = subprocess.run(
        ["bash", "-lc", comando],
        capture_output=True,
        text=True,
        timeout=20
    )

    if resultado.returncode != 0:
        erro = (resultado.stderr or resultado.stdout or "Erro ao consultar expiração").strip()
        raise Exception(f"Erro ao consultar expiração de {username}: {erro}")

    saida = (resultado.stdout or "").strip()

    if not saida or saida.lower() == "never":
        return None

    try:
        return datetime.strptime(saida, "%b %d, %Y")
    except Exception:
        raise Exception(f"Data inválida do chage para {username}: {saida}")


# =========================================================
# CALCULAR STATUS DE EXPIRAÇÃO
# Retorna:
# - "Venceu" se 0 ou menos
# - "X DIAS" se maior que 0
# =========================================================
def calcular_status_expiracao(username):
    data_exp = obter_data_expiracao_usuario(username)

    if data_exp is None:
        return "Venceu"

    hoje = datetime.now().date()
    data_final = data_exp.date()
    dias_restantes = (data_final - hoje).days

    if dias_restantes <= 0:
        return "Venceu"

    return f"{dias_restantes} DIAS"


# =========================================================
# OBTER LISTA COMPLETA DOS USUÁRIOS "MEUS" DO ADMIN
# Exclui usuários de TODAS as revendas e TODAS as sub-revendas
# =========================================================
def obter_lista_completa_usuarios_meus():
    usuarios_todos = obter_lista_completa_usuarios()
    bloqueados = obter_usuarios_bloqueados_admin()

    resultado = []
    for item in usuarios_todos:
        username = str(item.get("username", "")).strip()
        if username in bloqueados:
            continue
        resultado.append(item)

    return resultado


# =========================================================
# CONVERTER ETIME PARA SEGUNDOS
# Formatos aceitos do ps:
# MM:SS
# HH:MM:SS
# DD-HH:MM:SS
# =========================================================
def etime_para_segundos(etime):
    etime = str(etime).strip()

    if not etime:
        return 0

    dias = 0

    if "-" in etime:
        parte_dias, parte_tempo = etime.split("-", 1)
        if parte_dias.isdigit():
            dias = int(parte_dias)
        etime = parte_tempo

    partes = etime.split(":")

    try:
        if len(partes) == 2:
            horas = 0
            minutos = int(partes[0])
            segundos = int(partes[1])
        elif len(partes) == 3:
            horas = int(partes[0])
            minutos = int(partes[1])
            segundos = int(partes[2])
        else:
            return 0

        return dias * 86400 + horas * 3600 + minutos * 60 + segundos
    except:
        return 0


# =========================================================
# CONSULTAR USUÁRIOS ONLINE NO PLUGIN-SYNC
# Retorna dict no formato:
# {
#   "Lekinho": 1,
#   "Messias": 2
# }
# =========================================================
def obter_usuarios_online_plugin():
    comando = ["/opt/sshplus/plugin-sync", "-h", "--monitor-users"]

    resultado = subprocess.run(
        comando,
        capture_output=True,
        text=True,
        timeout=20
    )

    if resultado.returncode != 0:
        erro = (resultado.stderr or resultado.stdout or "Erro ao consultar usuários online").strip()
        raise Exception(erro)

    saida = (resultado.stdout or "").strip()

    if not saida:
        return {}

    try:
        dados = ast.literal_eval(saida)

        if not isinstance(dados, dict):
            raise Exception("Saída do monitor não é um dicionário válido.")

        saida_final = {}
        for username, conectados in dados.items():
            nome = str(username).strip()
            if not nome:
                continue

            try:
                qtd = int(conectados)
            except:
                qtd = 0

            if qtd > 0:
                saida_final[nome] = qtd

        return saida_final

    except Exception:
        raise Exception(f"Saída inválida do monitor de usuários: {saida}")


# =========================================================
# PEGAR MAPA username -> limit DO /root/usuarios.db
# =========================================================
def obter_mapa_limites_usuarios():
    usuarios = obter_usuarios_do_banco()
    return {item["username"]: int(item["limit"]) for item in usuarios}


# =========================================================
# PEGAR O MAIOR TEMPO ONLINE DE UM USUÁRIO
# Usa:
# ps -u USUARIO -o etime,cmd | grep ssh
# Se der erro, retorna ----
# =========================================================
def obter_maior_tempo_online_usuario(username):
    try:
        comando = (
            f"ps -u {shlex.quote(username)} -o etime=,cmd= | "
            "grep ssh || true"
        )

        resultado = subprocess.run(
            ["bash", "-lc", comando],
            capture_output=True,
            text=True,
            timeout=20
        )

        saida = (resultado.stdout or "").strip()

        if not saida:
            return "----", 0

        maior_etime = "----"
        maior_segundos = 0
        encontrou_algum = False

        for linha in saida.splitlines():
            linha = linha.strip()
            if not linha:
                continue

            partes = linha.split(None, 1)
            if not partes:
                continue

            etime = partes[0].strip()
            segundos = etime_para_segundos(etime)

            if not encontrou_algum or segundos > maior_segundos:
                encontrou_algum = True
                maior_segundos = segundos
                maior_etime = etime if etime else "----"

        if not encontrou_algum:
            return "----", 0

        return maior_etime, maior_segundos

    except Exception:
        return "----", 0


# =========================================================
# JUNTAR DADOS DOS USUÁRIOS ONLINE
# Retorna lista:
# [
#   {
#     "username": "fabio",
#     "online": 1,
#     "limit": 1,
#     "tempo": "01:58:15",
#     "tempo_segundos": 7095
#   }
# ]
# =========================================================
def obter_lista_usuarios_online_todos():
    online_dict = obter_usuarios_online_plugin()

    if not online_dict:
        return []

    mapa_limites = obter_mapa_limites_usuarios()
    resultado = []

    for username in sorted(online_dict.keys(), key=lambda x: x.lower()):
        qtd_online = int(online_dict.get(username, 0))
        limit = int(mapa_limites.get(username, 0))
        tempo, tempo_segundos = obter_maior_tempo_online_usuario(username)

        resultado.append({
            "username": username,
            "online": qtd_online,
            "limit": limit,
            "tempo": tempo,
            "tempo_segundos": tempo_segundos
        })

    return resultado

# =========================================================
# PEGAR TODOS OS USUÁRIOS DE TODAS AS REVENDAS
# Lê /root/revenda/dados_rev e monta um set com os usernames
# =========================================================
def obter_usuarios_de_todas_revendas():
    usuarios_revendas = set()

    for telegram_user in listar_todas_revendas():
        try:
            usuarios = ler_usuarios_revenda_completos(telegram_user)

            for item in usuarios:
                username = str(item.get("username", "")).strip()
                if username:
                    usuarios_revendas.add(username)

        except Exception:
            continue

    return usuarios_revendas

# =========================================================
# JUNTAR DADOS DOS USUÁRIOS ONLINE - SOMENTE MEUS
# Remove da lista todos os usuários pertencentes às revendas
# e às sub-revendas
# =========================================================
def obter_lista_usuarios_online_meus():
    online_dict = obter_usuarios_online_plugin()

    if not online_dict:
        return []

    bloqueados = obter_usuarios_bloqueados_admin()

    mapa_limites = obter_mapa_limites_usuarios()
    resultado = []

    for username in sorted(online_dict.keys(), key=lambda x: x.lower()):
        if username in bloqueados:
            continue

        qtd_online = int(online_dict.get(username, 0))
        limit = int(mapa_limites.get(username, 0))
        tempo, tempo_segundos = obter_maior_tempo_online_usuario(username)

        resultado.append({
            "username": username,
            "online": qtd_online,
            "limit": limit,
            "tempo": tempo,
            "tempo_segundos": tempo_segundos
        })

    return resultado

def total_conexoes_online(usuarios_online):
    total = 0

    for item in usuarios_online or []:
        try:
            total += int(str(item.get("online", 0)).strip() or "0")
        except:
            continue

    return total
# =========================================================
# MONTAR TEXTO DOS USUÁRIOS ONLINE PARA O TELEGRAM
# Cada usuário vai em uma citação separada
# Formato:
# usuario online/limite tempo
# =========================================================
def montar_texto_usuarios_online(usuarios_online):
    if not usuarios_online:
        return (
            "<b>MONITOR USUARIOS ONLINES</b>\n\n"
            "⚠️ Exibe no formato abaixo:\n"
            "<blockquote>USUÁRIO ONLINE/LIMITE TEMPO</blockquote>\n\n"
            "Nenhum usuário online no momento."
        )

    linhas = [
        "<b>MONITOR USUARIOS ONLINES</b>",
        "",
        "⚠️ Exibe no formato abaixo:",
        "<blockquote>USUÁRIO ONLINE/LIMITE TEMPO</blockquote>",
        ""
    ]

    for item in usuarios_online:
        linha = f"🟢 {item['username']} {item['online']}/{item['limit']} ⏳{item['tempo']}"
        linhas.append(f"<blockquote>{esc(linha)}</blockquote>")

    linhas.append("")
    linhas.append(f"<b><i>Total Usuários: {total_conexoes_online(usuarios_online)} onlines</i></b>")

    return "\n".join(linhas)


# =========================================================
# GERAR PDF TEMPORÁRIO DE USUÁRIOS ONLINE
# =========================================================
def gerar_pdf_usuarios_online(usuarios_online):
    nome_pdf = f"usuarios_online_adm{random.randint(100, 999)}.pdf"
    pdf_path = os.path.join(tempfile.gettempdir(), nome_pdf)

    c = canvas.Canvas(pdf_path, pagesize=A4)
    largura, altura = A4

    margem = 50
    rodape = 50

    colunas = [
        ("USUARIO", 200),
        ("ONLINE", 80),
        ("LIMITE", 80),
        ("TEMPO", 130),
    ]

    def desenhar_primeira_pagina():
        c.setFont("Helvetica-Bold", 16)
        titulo1 = "LUBU NET - Internet Ilimitada"
        largura_t1 = stringWidth(titulo1, "Helvetica-Bold", 16)
        c.drawString((largura - largura_t1) / 2, altura - 45, titulo1)

        c.setFont("Helvetica-Bold", 13)
        titulo2 = "USUARIOS ONLINE"
        largura_t2 = stringWidth(titulo2, "Helvetica-Bold", 13)
        c.drawString((largura - largura_t2) / 2, altura - 65, titulo2)

        y = altura - 95
        x = margem

        c.setFont("Helvetica-Bold", 11)
        for titulo, largura_col in colunas:
            c.rect(x, y, largura_col, 22)
            c.drawString(x + 6, y + 7, titulo)
            x += largura_col

        return y - 22

    def nova_pagina_sem_cabecalho():
        c.showPage()
        c.setFont("Helvetica", 10)
        return altura - 40

    def cortar_texto(texto, fonte="Helvetica", tamanho=10, largura_max=100):
        texto = str(texto)
        while stringWidth(texto, fonte, tamanho) > largura_max - 8 and len(texto) > 1:
            texto = texto[:-1]
        return texto

    y = desenhar_primeira_pagina()
    c.setFont("Helvetica", 10)

    for item in usuarios_online:
        if y < rodape:
            y = nova_pagina_sem_cabecalho()

        dados = [
            cortar_texto(item["username"], largura_max=colunas[0][1]),
            cortar_texto(item["online"], largura_max=colunas[1][1]),
            cortar_texto(item["limit"], largura_max=colunas[2][1]),
            cortar_texto(item["tempo"], largura_max=colunas[3][1]),
        ]

        x = margem
        altura_linha = 22

        for i, valor in enumerate(dados):
            largura_col = colunas[i][1]
            c.rect(x, y, largura_col, altura_linha)
            c.drawString(x + 6, y + 7, str(valor))
            x += largura_col

        y -= altura_linha

    c.save()
    return pdf_path


# ----------------
# DELETAR USUÁRIO
# ----------------
def receber_usuario_deletar(message):
    if not eh_admin(message.from_user.id):
        return

    if not message.text:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Usuário não encontrado. Digite /menu para tentar novamente."
        )
        return

    username_digitado = message.text.strip()

    try:
        usuarios_existentes = listar_usuarios()
    except Exception as e:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            f"❌ Erro ao verificar usuários.\n<code>{esc(e)}</code>"
        )
        return

    # comparação exata
    if username_digitado not in usuarios_existentes:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Usuário não encontrado. Digite /menu para tentar novamente."
        )
        return

    try:
        deletar_usuario_sistema(username_digitado)

        bot.send_message(
            message.chat.id,
            f"🗑️ Usuário <b>{esc(username_digitado)}</b> deletado com sucesso!"
        )

    except subprocess.TimeoutExpired:
        bot.send_message(
            message.chat.id,
            "❌ O comando demorou demais."
        )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Falha ao deletar usuário.\n<code>{esc(e)}</code>"
        )
    finally:
        limpar_fluxo(message.from_user.id)

# =========================================================
# MARKUP DOS EXPIRADOS
# =========================================================
def painel_expirados_markup(tem_expirados=True):
    kb = types.InlineKeyboardMarkup(row_width=1)

    if tem_expirados:
        kb.add(types.InlineKeyboardButton("🗑️ Deletar expirados", callback_data="confirmar_deletar_expirados"))

    kb.add(types.InlineKeyboardButton("⬅️ Voltar", callback_data="voltar_painel"))
    return kb

# =========================================================
# VERIFICAR SE USUÁRIO ESTÁ EXPIRADO
# Expirado = data de expiração é hoje ou anterior
# =========================================================
def usuario_esta_expirado(username):
    data_exp = obter_data_expiracao_usuario(username)

    if data_exp is None:
        return True

    hoje = datetime.now().date()
    data_final = data_exp.date()

    return data_final <= hoje

# =========================================================
# LISTAR USUÁRIOS EXPIRADOS - SOMENTE MEUS
# Exclui usuários de todas as revendas e sub-revendas
# =========================================================
def obter_usuarios_expirados_meus():
    usuarios = listar_usuarios()
    expirados = []

    bloqueados = obter_usuarios_bloqueados_admin()

    for username in usuarios:
        try:
            if username in bloqueados:
                continue

            if usuario_esta_expirado(username):
                expirados.append(username)
        except Exception:
            continue

    return expirados

# =========================================================
# MONTAR TEXTO DOS USUÁRIOS EXPIRADOS
# =========================================================
def montar_texto_expirados(expirados):
    linhas = ["🗑️ <b>USUÁRIOS EXPIRADOS</b>", ""]

    if expirados:
        for username in expirados:
            linhas.append(f"👤 <b>Usuário:</b> <code>{esc(username)}</code>")
    else:
        linhas.append("Nenhum usuário expirado encontrado.")

    linhas.append("")
    linhas.append(f"📊 <b>Total:</b> {len(expirados)} usuário{'s' if len(expirados) != 1 else ''}")

    return "\n".join(linhas)


# =========================================================
# FUNÇÕES DE REVENDAS
# =========================================================
def garantir_pasta_revendas():
    os.makedirs(REV_DIR, exist_ok=True)


def telegram_revenda_valido(telegram_user):
    return isinstance(telegram_user, str) and telegram_user.startswith("@") and len(telegram_user.strip()) > 1


def nome_arquivo_revenda(telegram_user):
    tg = normalizar_telegram_user(telegram_user)
    return tg.lstrip("@") + ".txt"


def caminho_arquivo_revenda(telegram_user):
    return os.path.join(REV_DIR, nome_arquivo_revenda(telegram_user))


def revenda_existe(telegram_user):
    tg = normalizar_telegram_user(telegram_user)
    if not tg:
        return False

    try:
        for rev in listar_todas_revendas():
            if normalizar_telegram_user(rev) == tg:
                return True
    except:
        pass

    return False


# =========================================================
# SUSPENDER REVENDA
# Bloqueia todos os usuários dela e bloqueia o acesso ao bot
# =========================================================
def receber_telegram_suspender_revenda(message):
    if not eh_admin(message.from_user.id):
        return

    if not message.text:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ @ inválido. Digite /menu para tentar novamente."
        )
        return

    telegram_user = message.text.strip()

    if not telegram_revenda_valido(telegram_user):
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ @ inválido. O @ precisa começar com @.\nDigite /menu para tentar novamente."
        )
        return

    if not revenda_existe(telegram_user):
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Revenda não encontrada. Digite /menu para tentar novamente."
        )
        return

    if revenda_suspensa(telegram_user):
        bot.send_message(
            message.chat.id,
            f"⚠️ A revenda {esc(telegram_user)} já está suspensa."
        )
        limpar_fluxo(message.from_user.id)
        return
    
    try:
        bloqueados, falharam = bloquear_todos_usuarios_da_revenda(telegram_user)

        if falharam:
            bot.send_message(
                message.chat.id,
                "❌ Não foi possível bloquear todos os usuários da revenda.\n\n"
                f"⚠️ Falharam: <code>{esc(', '.join(falharam))}</code>"
            )
            limpar_fluxo(message.from_user.id)
            return

        definir_suspensao_revenda(telegram_user, True)
        hoje_str = datetime.now(SP_TZ).strftime("%d/%m/%Y")
        salvar_campo_revenda(telegram_user, "ultima_suspensao", hoje_str)

        resultado_subs = suspender_subrevendas_da_revenda(telegram_user)

        enviar_msg_revenda(
            telegram_user,
            "⛔ Seu acesso foi suspenso.\n\nEntre em contato com o administrador para mais informações."
        
        )

        texto_admin = (
            "⛔ <b>Revenda suspensa com sucesso!</b>\n\n"
            f"👤 <b>Telegram:</b> {esc(telegram_user)}\n"
            f"🔒 <b>Usuários da revenda bloqueados:</b> {esc(len(bloqueados))}"
        )
        
        if resultado_subs["suspensas_agora"] or resultado_subs["ja_estavam_suspensas"]:
            texto_admin += f"\n📦 <b>Sub-revendas suspensas agora:</b> {esc(len(resultado_subs['suspensas_agora']))}"
        
        bot.send_message(message.chat.id, texto_admin)

    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Erro ao suspender revenda.\n<code>{esc(e)}</code>"
        )
    finally:
        limpar_fluxo(message.from_user.id)
        

# =========================================================
# RENOVAR REVENDA
# =========================================================
def receber_telegram_renovar_revenda(message):
    if not eh_admin(message.from_user.id):
        return

    if not message.text:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ @ inválido. Digite /menu para tentar novamente."
        )
        return

    telegram_user = message.text.strip()

    if not telegram_revenda_valido(telegram_user):
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ @ inválido. O @ precisa começar com @.\nDigite /menu para tentar novamente."
        )
        return

    if not revenda_existe(telegram_user):
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Revenda não encontrada.\nDigite /menu para tentar novamente."
        )
        return

    try:
        resultado = renovar_revenda(telegram_user)

        # -------------------------------------------------
        # MENSAGEM PRINCIPAL DO ADMIN
        # Sempre curta, sem mostrar vencimento anterior
        # e sem usar <code> no @
        # -------------------------------------------------
        bot.send_message(
            message.chat.id,
            "✅ <b>Revenda renovada com sucesso!</b>\n\n"
            f"👤 <b>Telegram:</b> {esc(telegram_user)}\n"
            f"📆 <b>Novo vencimento:</b> {esc(resultado['novo_vencimento'])}"
        )

        # -------------------------------------------------
        # MENSAGEM PARA A REVENDA
        # Só quando a renovação foi feita por esta opção
        # -------------------------------------------------
        if resultado["estava_suspensa"]:
            enviar_msg_revenda(telegram_user, "✅ Seu acesso foi reativado!")
        else:
            enviar_msg_revenda(telegram_user, "✅ Seu acesso foi renovado")

        # -------------------------------------------------
        # SE ESTAVA SUSPENSA, ENVIA OUTRA MSG SEPARADA
        # INFORMANDO QUANTOS USUÁRIOS FORAM REATIVADOS
        # -------------------------------------------------
        if resultado["estava_suspensa"]:
            texto_reativacao = (
                "✅ <b>Reativação concluída com sucesso!</b>\n\n"
                f"👥 <b>Usuários da revenda reativados:</b> {esc(len(resultado['desbloqueados']))}"
            )
        
            if resultado.get("subs_reativadas"):
                texto_reativacao += f"\n📦 <b>Sub-revendas reativadas:</b> {esc(len(resultado['subs_reativadas']))}"
        
            bot.send_message(message.chat.id, texto_reativacao)

    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Erro ao renovar revenda.\n<code>{esc(e)}</code>"
        )
    finally:
        limpar_fluxo(message.from_user.id)

        
# =========================================================
# SALVAR REVENDA
# Preserva status, chat_id, avisos e usuários já salvos
# =========================================================
def salvar_revenda(telegram_user, limite_total, limite_restante, vencimento_formatado):
    garantir_pasta_revendas()

    caminho = caminho_arquivo_revenda(telegram_user)

    linhas_usuarios = []
    suspenso = "0"
    chat_id = ""
    ultimo_aviso = ""
    ultima_suspensao = ""

    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
            for linha in f:
                linha_limpa = linha.rstrip("\n")

                if not linha_limpa.strip():
                    continue

                if "=" in linha_limpa:
                    chave, valor = linha_limpa.split("=", 1)
                    chave = chave.strip()
                    valor = valor.strip()

                    if chave == "suspenso":
                        suspenso = valor or "0"
                    elif chave == "chat_id":
                        chat_id = valor
                    elif chave == "ultimo_aviso":
                        ultimo_aviso = valor
                    elif chave == "ultima_suspensao":
                        ultima_suspensao = valor
                    continue

                partes = linha_limpa.split()
                if len(partes) >= 4:
                    linhas_usuarios.append(linha_limpa)

    with open(caminho, "w", encoding="utf-8") as f:
        f.write(f"telegram={telegram_user}\n")
        f.write(f"limite_total={limite_total}\n")
        f.write(f"limite_restante={limite_restante}\n")
        f.write(f"vencimento={vencimento_formatado}\n")
        f.write(f"suspenso={suspenso}\n")
        f.write(f"chat_id={chat_id}\n")
        f.write(f"ultimo_aviso={ultimo_aviso}\n")
        f.write(f"ultima_suspensao={ultima_suspensao}\n")

        if linhas_usuarios:
            f.write("\n")
            for linha in linhas_usuarios:
                f.write(linha + "\n")

def deletar_revenda(telegram_user):
    caminho = caminho_arquivo_revenda(telegram_user)
    if not os.path.exists(caminho):
        raise Exception("Revenda não encontrada.")
    os.remove(caminho)


# =========================================================
# ALTERAR @ DA REVENDA
# Renomeia o arquivo da revenda, atualiza a linha telegram=
# e atualiza o campo dono= das sub-revendas vinculadas
# =========================================================
def alterar_nome_usuario_revenda(telegram_antigo, telegram_novo):
    if not revenda_existe(telegram_antigo):
        raise Exception("Revenda não encontrada.")

    if revenda_existe(telegram_novo):
        raise Exception("O novo @ já está em uso por outra revenda.")

    if subrevenda_existe(telegram_novo):
        raise Exception("O novo @ já está em uso por uma sub-revenda.")

    caminho_antigo = caminho_arquivo_revenda(telegram_antigo)
    caminho_novo = caminho_arquivo_revenda(telegram_novo)

    linhas = []

    with open(caminho_antigo, "r", encoding="utf-8", errors="ignore") as f:
        for linha in f:
            linha_sem_quebra = linha.rstrip("\n")

            if linha_sem_quebra.startswith("telegram="):
                linhas.append(f"telegram={telegram_novo}")
            else:
                linhas.append(linha_sem_quebra)

    with open(caminho_antigo, "w", encoding="utf-8") as f:
        for linha in linhas:
            f.write(linha + "\n")

    os.rename(caminho_antigo, caminho_novo)

    atualizadas, falharam = atualizar_dono_subrevendas_da_revenda(telegram_antigo, telegram_novo)

    if falharam:
        raise Exception("Erro ao atualizar dono das sub-revendas: " + " | ".join(falharam))

    return {
        "subrevendas_atualizadas": atualizadas
    }

def obter_telegram_atual(message_or_callback):
    username = getattr(message_or_callback.from_user, "username", None)
    if not username:
        return None
    return normalizar_telegram_user("@" + username)

# =========================================================
# VERIFICAR SE É SUB REVENDA
# =========================================================
def usuario_eh_subrevenda(message_or_callback):
    tg = obter_telegram_atual(message_or_callback)
    if not tg:
        return False
    return subrevenda_existe(tg)

def usuario_eh_revenda(message_or_callback):
    tg = obter_telegram_atual(message_or_callback)
    if not tg:
        return False
    return revenda_existe(tg)


# =========================================================
# BLOQUEAR USUÁRIO NO SISTEMA
# =========================================================
def bloquear_usuario_sistema(username):
    comando = [
        "/opt/sshplus/plugin-sync",
        "-h",
        "--lock-user",
        username
    ]

    resultado = subprocess.run(
        comando,
        capture_output=True,
        text=True,
        timeout=20
    )

    if resultado.returncode != 0:
        erro = (resultado.stderr or resultado.stdout or "Erro ao bloquear usuário").strip()
        raise Exception(erro)


# =========================================================
# DESBLOQUEAR USUÁRIO NO SISTEMA
# =========================================================
def desbloquear_usuario_sistema(username):
    comando = [
        "/opt/sshplus/plugin-sync",
        "-h",
        "--unlock-user",
        username
    ]

    resultado = subprocess.run(
        comando,
        capture_output=True,
        text=True,
        timeout=20
    )

    if resultado.returncode != 0:
        erro = (resultado.stderr or resultado.stdout or "Erro ao desbloquear usuário").strip()
        raise Exception(erro)
    
# =========================================================
# STATUS DE SUSPENSÃO DA REVENDA
# =========================================================
def revenda_suspensa(telegram_user):
    try:
        dados = ler_dados_revenda(telegram_user)
        return str(dados.get("suspenso", "0")).strip() == "1"
    except:
        return False


def definir_suspensao_revenda(telegram_user, suspenso=True):
    caminho = caminho_arquivo_revenda(telegram_user)
    if not os.path.exists(caminho):
        raise Exception("Revenda não encontrada.")

    linhas = []
    achou_suspenso = False

    with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
        for linha in f:
            linha_sem_quebra = linha.rstrip("\n")

            if linha_sem_quebra.startswith("suspenso="):
                linhas.append(f"suspenso={'1' if suspenso else '0'}")
                achou_suspenso = True
            else:
                linhas.append(linha_sem_quebra)

    if not achou_suspenso:
        novas_linhas = []
        inserido = False
        for linha in linhas:
            novas_linhas.append(linha)
            if linha.startswith("vencimento=") and not inserido:
                novas_linhas.append(f"suspenso={'1' if suspenso else '0'}")
                inserido = True
        linhas = novas_linhas

    with open(caminho, "w", encoding="utf-8") as f:
        for linha in linhas:
            f.write(linha + "\n")


# =========================================================
# BLOQUEAR TODOS OS USUÁRIOS DA REVENDA
# =========================================================
def bloquear_todos_usuarios_da_revenda(telegram_user):
    usuarios = listar_usuarios_da_revenda(telegram_user)
    bloqueados = []
    falharam = []

    for username in usuarios:
        try:
            bloquear_usuario_sistema(username)
            bloqueados.append(username)
        except Exception:
            falharam.append(username)

    return bloqueados, falharam

# =========================================================
# DESBLOQUEAR TODOS OS USUÁRIOS DA REVENDA
# =========================================================
def desbloquear_todos_usuarios_da_revenda(telegram_user):
    usuarios = listar_usuarios_da_revenda(telegram_user)
    desbloqueados = []
    falharam = []

    for username in usuarios:
        try:
            desbloquear_usuario_sistema(username)
            desbloqueados.append(username)
        except Exception:
            falharam.append(username)

    return desbloqueados, falharam

# =========================================================
# STATUS DE SUSPENSÃO DA SUB REVENDA
# =========================================================
def subrevenda_suspensa(telegram_user):
    try:
        dados = ler_dados_subrevenda(telegram_user)
        return str(dados.get("suspenso", "0")).strip() == "1"
    except:
        return False


def definir_suspensao_subrevenda(telegram_user, suspenso=True):
    caminho = caminho_arquivo_subrevenda(telegram_user)
    if not os.path.exists(caminho):
        raise Exception("Sub revenda não encontrada.")

    linhas = []
    achou_suspenso = False

    with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
        for linha in f:
            linha_sem_quebra = linha.rstrip("\n")

            if linha_sem_quebra.startswith("suspenso="):
                linhas.append(f"suspenso={'1' if suspenso else '0'}")
                achou_suspenso = True
            else:
                linhas.append(linha_sem_quebra)

    if not achou_suspenso:
        novas_linhas = []
        inserido = False
        for linha in linhas:
            novas_linhas.append(linha)
            if linha.startswith("vencimento=") and not inserido:
                novas_linhas.append(f"suspenso={'1' if suspenso else '0'}")
                inserido = True
        linhas = novas_linhas

    with open(caminho, "w", encoding="utf-8") as f:
        for linha in linhas:
            f.write(linha + "\n")


# =========================================================
# ENVIAR MENSAGEM PARA SUB REVENDA
# =========================================================
def enviar_msg_subrevenda(telegram_user, texto):
    try:
        dados = ler_dados_subrevenda(telegram_user)
        chat_id = str(dados.get("chat_id", "")).strip()

        if not chat_id:
            return False

        bot.send_message(int(chat_id), texto)
        return True

    except Exception as e:
        print(f"[SUB MSG ERRO] {telegram_user}: {e}")
        return False


# =========================================================
# VERIFICAR SE A SUB REVENDA VENCE HOJE
# =========================================================
def subrevenda_vence_hoje(telegram_user):
    try:
        dados = ler_dados_subrevenda(telegram_user)
        vencimento = dados.get("vencimento", "").strip()
        if not vencimento:
            return False

        data_venc = datetime.strptime(vencimento, "%d/%m/%Y").date()
        hoje = datetime.now(SP_TZ).date()
        return data_venc == hoje
    except:
        return False


# =========================================================
# VERIFICAR SE A SUB REVENDA DEVE SER SUSPENSA
# Suspende no próprio dia, no horário configurado
# =========================================================
def subrevenda_deve_ser_suspensa_hoje(telegram_user, hora=23, minuto=59):
    try:
        dados = ler_dados_subrevenda(telegram_user)
        vencimento = str(dados.get("vencimento", "")).strip()
        if not vencimento:
            return False

        data_venc = datetime.strptime(vencimento, "%d/%m/%Y").date()
        agora = datetime.now(SP_TZ)

        momento_suspensao = SP_TZ.localize(
            datetime(
                year=data_venc.year,
                month=data_venc.month,
                day=data_venc.day,
                hour=hora,
                minute=minuto,
                second=0,
                microsecond=0
            )
        )

        return agora >= momento_suspensao
    except:
        return False


# =========================================================
# LISTAR USUÁRIOS DA SUB REVENDA
# =========================================================
def listar_usuarios_da_subrevenda(telegram_user):
    caminho = caminho_arquivo_subrevenda(telegram_user)
    if not os.path.exists(caminho):
        return []

    usuarios = []

    with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
        for linha in f:
            texto = linha.strip()
            if not texto or "=" in texto:
                continue

            partes = texto.split()
            if partes:
                usuarios.append(partes[0])

    return usuarios


# =========================================================
# BLOQUEAR TODOS OS USUÁRIOS DA SUB REVENDA
# =========================================================
def bloquear_todos_usuarios_da_subrevenda(telegram_user):
    usuarios = listar_usuarios_da_subrevenda(telegram_user)
    bloqueados = []
    falharam = []

    for username in usuarios:
        try:
            bloquear_usuario_sistema(username)
            bloqueados.append(username)
        except Exception:
            falharam.append(username)

    return bloqueados, falharam


# =========================================================
# DESBLOQUEAR TODOS OS USUÁRIOS DA SUB REVENDA
# =========================================================
def desbloquear_todos_usuarios_da_subrevenda(telegram_user):
    usuarios = listar_usuarios_da_subrevenda(telegram_user)
    desbloqueados = []
    falharam = []

    for username in usuarios:
        try:
            desbloquear_usuario_sistema(username)
            desbloqueados.append(username)
        except Exception:
            falharam.append(username)

    return desbloqueados, falharam


# =========================================================
# SUSPENDER SUB REVENDA AUTOMATICAMENTE
# =========================================================
def suspender_subrevenda_automaticamente(telegram_user):
    if subrevenda_suspensa(telegram_user):
        return False

    bloqueados, falharam = bloquear_todos_usuarios_da_subrevenda(telegram_user)

    if falharam:
        raise Exception(f"Falha ao bloquear usuários: {', '.join(falharam)}")

    definir_suspensao_subrevenda(telegram_user, True)

    hoje_str = datetime.now(SP_TZ).strftime("%d/%m/%Y")
    salvar_campo_subrevenda(telegram_user, "ultima_suspensao", hoje_str)

    enviar_msg_subrevenda(
        telegram_user,
        "⛔ Seu acesso foi suspenso por vencimento.\n\nRenove para voltar a usar o painel."
    )

    try:
        dados = ler_dados_subrevenda(telegram_user)
        dono = str(dados.get("dono", "")).strip()
        if dono:
            enviar_msg_revenda(
                dono,
                f"⛔ A sub-revenda {telegram_user} foi suspensa por vencimento."
            )
    except:
        pass

    return True

# =========================================================
# SUSPENDER SUB REVENDA MANUALMENTE
# Quando a suspensão vier do botão da revenda,
# envia ao sub o nome do fornecedor
# =========================================================
def suspender_subrevenda_manualmente(telegram_user):
    if subrevenda_suspensa(telegram_user):
        return False

    bloqueados, falharam = bloquear_todos_usuarios_da_subrevenda(telegram_user)

    if falharam:
        raise Exception(f"Falha ao bloquear usuários: {', '.join(falharam)}")

    definir_suspensao_subrevenda(telegram_user, True)

    hoje_str = datetime.now(SP_TZ).strftime("%d/%m/%Y")
    salvar_campo_subrevenda(telegram_user, "ultima_suspensao", hoje_str)

    # -----------------------------------------------------
    # DESCOBRIR O DONO DA SUB PARA MONTAR A MENSAGEM
    # -----------------------------------------------------
    nome_revenda = ""

    try:
        dados = ler_dados_subrevenda(telegram_user)
        nome_revenda = str(dados.get("dono", "")).strip()
    except:
        nome_revenda = ""

    # -----------------------------------------------------
    # MENSAGEM PERSONALIZADA PARA A SUB-REVENDA
    # -----------------------------------------------------
    if nome_revenda:
        enviar_msg_subrevenda(
            telegram_user,
            "⛔️ Seu painel foi suspenso pelo seu fornecedor!\n\n"
            f"Entre em contato para mais informações: {nome_revenda}"
        )
    else:
        enviar_msg_subrevenda(
            telegram_user,
            "⛔️ Seu painel foi suspenso pelo seu fornecedor!\n\n"
            "Entre em contato para mais informações."
        )

    return True

# =========================================================
# REATIVAR SUB REVENDA
# Remove suspensão e desbloqueia todos os usuários
# =========================================================
def reativar_subrevenda(telegram_user):
    if not subrevenda_suspensa(telegram_user):
        return {
            "estava_suspensa": False,
            "desbloqueados": []
        }

    desbloqueados, falharam = desbloquear_todos_usuarios_da_subrevenda(telegram_user)

    if falharam:
        raise Exception(f"Falha ao desbloquear usuários: {', '.join(falharam)}")

    definir_suspensao_subrevenda(telegram_user, False)
    salvar_campo_subrevenda(telegram_user, "ultima_suspensao", "")

    enviar_msg_subrevenda(
        telegram_user,
        "✅ Seu painel foi reativado!"
    )

    return {
        "estava_suspensa": True,
        "desbloqueados": desbloqueados
    }

# =========================================================
# ALTERAR DATA DA REVENDA
# Mantém os usuários salvos no mesmo arquivo
# =========================================================
def alterar_data_revenda(telegram_user, dias):
    dados = ler_dados_revenda(telegram_user)

    limite_total = int(dados.get("limite_total", "0"))
    limite_restante = int(dados.get("limite_restante", "0"))
    estava_suspensa = revenda_suspensa(telegram_user)

    nova_data = datetime.now() + timedelta(days=dias)
    nova_data_formatada = nova_data.strftime("%d/%m/%Y")

    salvar_revenda(
        telegram_user=telegram_user,
        limite_total=limite_total,
        limite_restante=limite_restante,
        vencimento_formatado=nova_data_formatada
    )

    desbloqueados = []
    falharam = []
    resultado_subs = {
        "reativadas": [],
        "ignoradas": [],
        "falharam": []
    }

    if estava_suspensa:
        desbloqueados, falharam = desbloquear_todos_usuarios_da_revenda(telegram_user)

        if falharam:
            raise Exception(f"Falha ao desbloquear usuários da revenda: {', '.join(falharam)}")

        definir_suspensao_revenda(telegram_user, False)
        salvar_campo_revenda(telegram_user, "ultima_suspensao", "")

        resultado_subs = reativar_subrevendas_da_revenda(telegram_user)

    return {
        "nova_data": nova_data_formatada,
        "estava_suspensa": estava_suspensa,
        "desbloqueados": desbloqueados,
        "subs_reativadas": resultado_subs["reativadas"]
    }


# =========================================================
# RENOVAR REVENDA
#
# REGRA:
# - Se NÃO está suspensa:
#       renova 1 mês a partir do vencimento atual
#       Ex: 22/10 -> 22/11
#
# - Se ESTÁ suspensa:
#       renova 1 mês a partir de hoje
#       Ex: hoje 31/10 -> 30/11
#       e também remove a suspensão dos usuários
#
# Tudo feito só com DATA, sem hora, para não perder 1 dia.
# =========================================================
def renovar_revenda(telegram_user):
    dados = ler_dados_revenda(telegram_user)

    vencimento_str = str(dados.get("vencimento", "")).strip()
    if not vencimento_str:
        raise Exception("Vencimento da revenda não encontrado.")

    esta_suspensa = revenda_suspensa(telegram_user)

    try:
        data_venc_atual = datetime.strptime(vencimento_str, "%d/%m/%Y").date()
    except:
        raise Exception("Data de vencimento inválida da revenda.")

    hoje = datetime.now(SP_TZ).date()

    if esta_suspensa:
        data_base = hoje
    else:
        data_base = data_venc_atual

    novo_vencimento = data_base + relativedelta(months=+1)
    novo_vencimento_str = novo_vencimento.strftime("%d/%m/%Y")

    salvar_campo_revenda(telegram_user, "vencimento", novo_vencimento_str)

    desbloqueados = []
    falharam = []

    resultado_subs = {
        "reativadas": [],
        "ignoradas": [],
        "falharam": []
    }

    if esta_suspensa:
        desbloqueados, falharam = desbloquear_todos_usuarios_da_revenda(telegram_user)

        if falharam:
            raise Exception(f"Falha ao desbloquear usuários: {', '.join(falharam)}")

        definir_suspensao_revenda(telegram_user, False)
        salvar_campo_revenda(telegram_user, "ultima_suspensao", "")
        resultado_subs = reativar_subrevendas_da_revenda(telegram_user)

    return {
        "vencimento_anterior": vencimento_str,
        "novo_vencimento": novo_vencimento_str,
        "estava_suspensa": esta_suspensa,
        "desbloqueados": desbloqueados,
        "subs_reativadas": resultado_subs["reativadas"]
    }

# =========================================================
# RENOVAR SUB-REVENDA 1 mes
# =========================================================
def renovar_subrevenda(telegram_user):
    dados = ler_dados_subrevenda(telegram_user)

    vencimento_str = str(dados.get("vencimento", "")).strip()
    if not vencimento_str:
        raise Exception("Vencimento da sub-revenda não encontrado.")

    esta_suspensa = subrevenda_suspensa(telegram_user)

    try:
        data_venc_atual = datetime.strptime(vencimento_str, "%d/%m/%Y").date()
    except:
        raise Exception("Data de vencimento inválida da sub-revenda.")

    hoje = datetime.now(SP_TZ).date()

    # -----------------------------------------------------
    # BASE DA RENOVAÇÃO
    # -----------------------------------------------------
    if esta_suspensa:
        data_base = hoje
    else:
        data_base = data_venc_atual

    novo_vencimento = data_base + relativedelta(months=+1)
    novo_vencimento_str = novo_vencimento.strftime("%d/%m/%Y")

    # Atualiza apenas o vencimento
    salvar_campo_subrevenda(telegram_user, "vencimento", novo_vencimento_str)

    # Se estava suspensa, remove a suspensão da sub-revenda e dos usuários
    desbloqueados = []
    falharam = []

    if esta_suspensa:
        desbloqueados, falharam = desbloquear_todos_usuarios_da_subrevenda(telegram_user)

        if falharam:
            raise Exception(f"Falha ao desbloquear usuários: {', '.join(falharam)}")

        definir_suspensao_subrevenda(telegram_user, False)
        salvar_campo_subrevenda(telegram_user, "ultima_suspensao", "")

        enviar_msg_subrevenda(
            telegram_user,
            "✅ Seu painel foi renovado e reativado."
        )
    else:
        enviar_msg_subrevenda(
            telegram_user,
            "✅ Seu painel foi renovado."
        )

    return {
        "vencimento_anterior": vencimento_str,
        "novo_vencimento": novo_vencimento_str,
        "estava_suspensa": esta_suspensa,
        "desbloqueados": desbloqueados
    }

def ler_dados_revenda(telegram_user):
    caminho = caminho_arquivo_revenda(telegram_user)
    if not os.path.exists(caminho):
        raise Exception("Revenda não encontrada.")

    dados = {}
    with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
        for linha in f:
            linha = linha.strip()
            if not linha:
                continue
            if "=" not in linha:
                continue
            k, v = linha.split("=", 1)
            dados[k.strip()] = v.strip()

    return dados

# =========================================================
# ALTERAR LIMITE DA REVENDA
# Mantém a data e recalcula o limite restante corretamente
# =========================================================
def alterar_limite_revenda(telegram_user, novo_limite):
    dados = ler_dados_revenda(telegram_user)
    vencimento = dados.get("vencimento", "-")

    usado = calcular_limite_usado_real_revenda(telegram_user)
    limite_restante = int(novo_limite) - int(usado)

    if limite_restante < 0:
        limite_restante = 0

    salvar_revenda(
        telegram_user=telegram_user,
        limite_total=novo_limite,
        limite_restante=limite_restante,
        vencimento_formatado=vencimento
    )

    return {
        "novo_limite": int(novo_limite),
        "usado": int(usado),
        "limite_restante": int(limite_restante)
    }

# =========================================================
# LER USUÁRIOS CRIADOS PELA REVENDA NO MESMO ARQUIVO
# Linhas esperadas:
# usuario senha limite dias
# usuario senha limite dias uuid
# =========================================================
def listar_usuarios_da_revenda(telegram_user):
    caminho = caminho_arquivo_revenda(telegram_user)
    if not os.path.exists(caminho):
        raise Exception("Revenda não encontrada.")

    usuarios = []

    with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
        for linha in f:
            linha = linha.strip()

            if not linha:
                continue

            if "=" in linha:
                continue

            partes = linha.split()
            if len(partes) < 4:
                continue

            username = partes[0].strip()
            if username:
                usuarios.append(username)

    return usuarios


# =========================================================
# APAGAR TODOS OS USUÁRIOS DA REVENDA
# =========================================================
def apagar_todos_usuarios_da_revenda(telegram_user):
    usuarios = listar_usuarios_da_revenda(telegram_user)
    apagados = []
    falharam = []

    for username in usuarios:
        try:
            deletar_usuario_sistema(username)
            apagados.append(username)
        except Exception:
            falharam.append(username)

    return apagados, falharam

# =========================================================
# ADICIONAR REVENDA
# =========================================================
def receber_telegram_revenda(message):
    if not eh_admin(message.from_user.id):
        return

    if not message.text:
        limpar_fluxo(message.from_user.id)
        bot.send_message(message.chat.id, "❌ @ inválido. Digite /menu para tentar novamente.")
        return

    telegram_user = normalizar_telegram_user(message.text)
    
    if not telegram_revenda_valido(telegram_user):
        limpar_fluxo(message.from_user.id)
        bot.send_message(message.chat.id, "❌ @ inválido. O @ precisa começar com @.\nDigite /menu para tentar novamente.")
        return
    
    if telegram_ja_existe_global(telegram_user):
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Esse usuário já existe em nosso banco de dados.\nDigite /menu para tentar novamente."
        )
        return

    user_data[message.from_user.id]["telegram_revenda"] = telegram_user

    msg = bot.send_message(message.chat.id, "Informe o limite da revenda.")
    bot.register_next_step_handler(msg, receber_limite_revenda)


def receber_limite_revenda(message):
    if not eh_admin(message.from_user.id):
        return

    if not message.text:
        limpar_fluxo(message.from_user.id)
        bot.send_message(message.chat.id, "❌ Limite inválido. Digite /menu para tentar novamente.")
        return

    texto = message.text.strip()
    if not texto.isdigit() or int(texto) <= 0:
        limpar_fluxo(message.from_user.id)
        bot.send_message(message.chat.id, "❌ Limite inválido. Digite /menu para tentar novamente.")
        return

    user_data[message.from_user.id]["limite_revenda"] = int(texto)

    msg = bot.send_message(message.chat.id, "Informe a quantidade de dias da revenda.")
    bot.register_next_step_handler(msg, receber_dias_revenda)


def receber_dias_revenda(message):
    if not eh_admin(message.from_user.id):
        return

    if not message.text:
        limpar_fluxo(message.from_user.id)
        bot.send_message(message.chat.id, "❌ Data inválida. Digite /menu para tentar novamente.")
        return

    texto = message.text.strip()
    if not texto.isdigit() or int(texto) <= 0:
        limpar_fluxo(message.from_user.id)
        bot.send_message(message.chat.id, "❌ Data inválida. Digite /menu para tentar novamente.")
        return

    if message.from_user.id not in user_data:
        limpar_fluxo(message.from_user.id)
        bot.send_message(message.chat.id, "❌ Sessão expirada. Digite /menu para tentar novamente.")
        return

    dias = int(texto)

    try:
        telegram_user = normalizar_telegram_user(
            user_data[message.from_user.id]["telegram_revenda"]
        )
        limite = user_data[message.from_user.id]["limite_revenda"]

        # trava final antes de salvar
        if telegram_ja_existe_global(telegram_user):
            bot.send_message(
                message.chat.id,
                "❌ Esse usuário já existe em nosso banco de dados.\nDigite /menu para tentar novamente."
            )
            return

        data_vencimento = datetime.now() + timedelta(days=dias)
        vencimento_formatado = data_vencimento.strftime("%d/%m/%Y")

        salvar_revenda(
            telegram_user=telegram_user,
            limite_total=limite,
            limite_restante=limite,
            vencimento_formatado=vencimento_formatado
        )

        try:
            username_bot = f"@{bot.get_me().username}"
        except:
            username_bot = "@do_bot_usado"

        bot.send_message(
            message.chat.id,
            "✅ <b>Revenda cadastrada!</b>\n\n"
            f"<b>Revendedorª:</b> {esc(telegram_user)}\n"
            f"<b>Limite De Logins:</b> {esc(limite)}\n"
            f"<b>Validade:</b> {esc(vencimento_formatado)}\n\n"
            f"<b>Bot (Painel) :</b> {esc(username_bot)}"
        )

    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Erro ao cadastrar revenda.\n<code>{esc(e)}</code>"
        )
    finally:
        limpar_fluxo(message.from_user.id)

# =========================================================
# ALTERAR DATA DA REVENDA
# =========================================================
def receber_telegram_alt_data_revenda(message):
    if not eh_admin(message.from_user.id):
        return

    if not message.text:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ @ inválido. Digite /menu para tentar novamente."
        )
        return

    telegram_user = message.text.strip()

    if not telegram_revenda_valido(telegram_user):
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ @ inválido. O @ precisa começar com @.\nDigite /menu para tentar novamente."
        )
        return

    if not revenda_existe(telegram_user):
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Revenda não encontrada. Digite /menu para tentar novamente."
        )
        return

    try:
        dados = ler_dados_revenda(telegram_user)
        vencimento_atual = dados.get("vencimento", "-")
    except Exception as e:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            f"❌ Erro ao ler dados da revenda.\n<code>{esc(e)}</code>"
        )
        return

    user_data[message.from_user.id]["telegram_revenda"] = telegram_user

    msg = bot.send_message(
        message.chat.id,
        f"📅 Data atual da revenda: <code>{esc(vencimento_atual)}</code>\n\nInforme a nova quantidade de dias."
    )
    bot.register_next_step_handler(msg, receber_nova_data_revenda)


# =========================================================
# ALTERAR LIMITE DA REVENDA
# Primeiro sincroniza a revenda e recalcula o restante
# Depois mostra o limite atual e pede o novo limite
# =========================================================
def receber_telegram_alt_limite_revenda(message):
    if not eh_admin(message.from_user.id):
        return

    if not message.text:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ @ inválido. Digite /menu para tentar novamente."
        )
        return

    telegram_user = message.text.strip()

    if not telegram_revenda_valido(telegram_user):
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ @ inválido. O @ precisa começar com @.\nDigite /menu para tentar novamente."
        )
        return

    if not revenda_existe(telegram_user):
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Revenda não encontrada. Digite /menu para tentar novamente."
        )
        return

    try:
        # -------------------------------------------------
        # SINCRONIZA PRIMEIRO ESSA REVENDA
        # -------------------------------------------------
        sincronizar_arquivo_revenda(telegram_user)
        recalcular_limite_restante_revenda(telegram_user)

        dados = ler_dados_revenda(telegram_user)
        limite_atual = int(dados.get("limite_total", "0"))
        usado_atual = calcular_limite_usado_real_revenda(telegram_user)
        reservado_sub = calcular_limite_reservado_subrevendas(telegram_user)

    except Exception as e:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            f"❌ Erro ao ler dados da revenda.\n<code>{esc(e)}</code>"
        )
        return

    user_data[message.from_user.id]["telegram_revenda"] = telegram_user
    user_data[message.from_user.id]["limite_usado_revenda"] = usado_atual
    user_data[message.from_user.id]["limite_reservado_subrevendas"] = reservado_sub

    msg = bot.send_message(
        message.chat.id,
        f"👥 Limite atual da revenda: <code>{esc(limite_atual)}</code>\n\nInforme o novo limite."
    )
    bot.register_next_step_handler(msg, receber_novo_limite_revenda)


# =========================================================
# ALTERAR NOME DE USUARIO DA REVENDA
# PASSO 1: RECEBER @ ATUAL
# =========================================================
def receber_telegram_revenda_alterar_nome(message):
    if not eh_admin(message.from_user.id):
        return

    if not message.text:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ @ inválido. Digite /menu para tentar novamente."
        )
        return

    telegram_antigo = message.text.strip()

    if not telegram_revenda_valido(telegram_antigo):
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ @ inválido. O @ precisa começar com @.\nDigite /menu para tentar novamente."
        )
        return

    if not revenda_existe(telegram_antigo):
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Revenda não encontrada."
        )
        return

    user_data[message.from_user.id]["telegram_revenda_antigo"] = telegram_antigo

    msg = bot.send_message(
        message.chat.id,
        "Envie o novo @ da revenda."
    )
    bot.register_next_step_handler(msg, receber_novo_nome_usuario_revenda)

# =========================================================
# ALTERAR NOME DE USUARIO DA REVENDA
# PASSO 2: RECEBER NOVO @ E ATUALIZAR TUDO
# =========================================================
def receber_novo_nome_usuario_revenda(message):
    if not eh_admin(message.from_user.id):
        return

    if not message.text:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ @ inválido. Digite /menu para tentar novamente."
        )
        return

    dados_fluxo = user_data.get(message.from_user.id, {})
    telegram_antigo = dados_fluxo.get("telegram_revenda_antigo")

    if not telegram_antigo:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Fluxo inválido. Digite /menu para tentar novamente."
        )
        return

    telegram_antigo = normalizar_telegram_user(telegram_antigo)
    telegram_novo = normalizar_telegram_user(message.text)

    if not telegram_revenda_valido(telegram_novo):
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ @ inválido. O @ precisa começar com @.\nDigite /menu para tentar novamente."
        )
        return

    if telegram_novo == telegram_antigo:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ O novo @ é igual ao atual.\nDigite /menu para tentar novamente."
        )
        return

    if telegram_ja_existe_global(telegram_novo, ignorar_telegram=telegram_antigo):
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Esse novo @ já está em uso em nosso banco de dados.\nDigite /menu para tentar novamente."
        )
        return

    try:
        alterar_nome_usuario_revenda(telegram_antigo, telegram_novo)

        bot.send_message(
            message.chat.id,
            "✅ <b>Nome de usuário da revenda alterado com sucesso!</b>\n\n"
            f"👤 <b>Telegram antigo:</b> {esc(telegram_antigo)}\n"
            f"🆕 <b>Novo Telegram:</b> {esc(telegram_novo)}"
        )

    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Erro ao alterar nome de usuário da revenda.\n<code>{esc(e)}</code>"
        )
    finally:
        limpar_fluxo(message.from_user.id)

        
# =========================================================
# RECALCULAR LIMITE_RESTANTE DA REVENDA
# Agora considera:
# - uso real dos usuários da revenda
# - limite reservado para subrevendas dessa revenda
# =========================================================
def recalcular_limite_restante_revenda(telegram_user):
    dados = ler_dados_revenda(telegram_user)

    limite_total = int(dados.get("limite_total", "0"))
    vencimento = str(dados.get("vencimento", "")).strip()

    usado = calcular_limite_usado_real_revenda(telegram_user)
    reservado_sub = calcular_limite_reservado_subrevendas(telegram_user)

    limite_restante = limite_total - usado - reservado_sub

    if limite_restante < 0:
        limite_restante = 0

    salvar_revenda(
        telegram_user=telegram_user,
        limite_total=limite_total,
        limite_restante=limite_restante,
        vencimento_formatado=vencimento
    )

    return {
        "limite_total": limite_total,
        "usado": usado,
        "reservado_sub": reservado_sub,
        "limite_restante": limite_restante
    }

# =========================================================
# BOTÃO DE VOLTAR DO RELATÓRIO INDIVIDUAL DA REVENDA
# =========================================================
def painel_voltar_relatorio_individual_revenda():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("⬅️ Voltar", callback_data="voltar_menu_revendas"))
    return kb

# =========================================================
# PEGAR DADOS RESUMIDOS DE UMA REVENDA PARA O RELATÓRIO
# =========================================================
def obter_dados_relatorio_revenda(telegram_user):
    dados = ler_dados_revenda(telegram_user)

    limite_total = int(dados.get("limite_total", "0"))
    vencimento = str(dados.get("vencimento", "")).strip()
    status = "suspenso" if revenda_suspensa(telegram_user) else "ativo"

    # USO REAL vindo das linhas dos usuários da revenda
    usado = calcular_limite_usado_real_revenda(telegram_user)

    if usado < 0:
        usado = 0

    return {
        "telegram_user": telegram_user,
        "usado": usado,
        "limite_total": limite_total,
        "vencimento": vencimento,
        "status": status
    }

# =========================================================
# LISTA COMPLETA DE DADOS PARA O RELATÓRIO DAS REVENDAS
# =========================================================
def obter_lista_relatorio_revendas():
    resultado = []

    for telegram_user in listar_todas_revendas():
        try:
            item = obter_dados_relatorio_revenda(telegram_user)
            resultado.append(item)
        except:
            continue

    resultado.sort(key=lambda x: x["telegram_user"].lower())
    return resultado

# =========================================================
# SOMAR O LIMITE USADO REAL DA REVENDA
# =========================================================
def calcular_limite_usado_real_revenda(telegram_user):
    caminho = caminho_arquivo_revenda(telegram_user)

    if not os.path.exists(caminho):
        raise Exception("Revenda não encontrada.")

    usado = 0

    with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
        for linha in f:
            linha = linha.strip()

            if not linha:
                continue

            if "=" in linha:
                continue

            partes = linha.split()
            if len(partes) < 4:
                continue

            try:
                limite_usuario = int(partes[2])
            except:
                limite_usuario = 0

            usado += limite_usuario

    return usado

# =========================================================
# GERAR PDF TEMPORÁRIO DO RELATÓRIO DE REVENDAS
# =========================================================
def gerar_pdf_relatorio_revendas(revendas):
    nome_pdf = f"relatorio_revendas_{random.randint(100, 999)}.pdf"
    pdf_path = os.path.join(tempfile.gettempdir(), nome_pdf)

    c = canvas.Canvas(pdf_path, pagesize=A4)
    largura_pagina, altura_pagina = A4

    rodape = 40

    # Total = 510, cabe no A4 e centraliza direito
    colunas = [
        ("USUARIO", 160),
        ("USO/LIMITE", 105),
        ("EXPIRACAO", 145),
        ("STATUS", 100),
    ]

    largura_tabela = sum(largura for _, largura in colunas)
    x_inicial = (largura_pagina - largura_tabela) / 2

    def cortar_texto(texto, fonte="Helvetica", tamanho=10, largura_max=100):
        texto = str(texto)
        while stringWidth(texto, fonte, tamanho) > largura_max - 10 and len(texto) > 1:
            texto = texto[:-1]
        return texto

    def desenhar_topo():
        c.setFont("Helvetica-Bold", 17)
        titulo = "REVENDAS LUBU NET"
        largura_titulo = stringWidth(titulo, "Helvetica-Bold", 17)
        c.drawString((largura_pagina - largura_titulo) / 2, altura_pagina - 42, titulo)

        y = altura_pagina - 78
        x = x_inicial

        c.setFont("Helvetica", 10)
        altura_cab = 23

        for titulo_coluna, largura_coluna in colunas:
            c.rect(x, y, largura_coluna, altura_cab)
            c.drawString(x + 8, y + 7, titulo_coluna)
            x += largura_coluna

        return y - altura_cab

    def nova_pagina():
        c.showPage()
        return desenhar_topo()

    y = desenhar_topo()
    c.setFont("Helvetica", 10)

    for item in revendas:
        if y < rodape:
            y = nova_pagina()
            c.setFont("Helvetica", 10)

        usuario = cortar_texto(item["telegram_user"], largura_max=colunas[0][1])
        uso_limite = cortar_texto(f"{item['usado']}/{item['limite_total']}", largura_max=colunas[1][1])
        expiracao = cortar_texto(item["vencimento"], largura_max=colunas[2][1])
        status = cortar_texto(item["status"], largura_max=colunas[3][1])

        linha = [usuario, uso_limite, expiracao, status]

        x = x_inicial
        altura_linha = 23

        for i, valor in enumerate(linha):
            largura_coluna = colunas[i][1]
            c.rect(x, y, largura_coluna, altura_linha)
            c.drawString(x + 8, y + 7, str(valor))
            x += largura_coluna

        y -= altura_linha

    c.save()
    return pdf_path


# =========================================================
# RECEBER NOVO LIMITE DA REVENDA
# Não permite limite novo abaixo do uso atual
# nem abaixo do reservado para subrevendas
# =========================================================
def receber_novo_limite_revenda(message):
    if not eh_admin(message.from_user.id):
        return

    if not message.text:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Limite inválido. Digite /menu para tentar novamente."
        )
        return

    texto = message.text.strip()

    if not texto.isdigit() or int(texto) <= 0:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Limite inválido. Digite /menu para tentar novamente."
        )
        return

    novo_limite = int(texto)

    dados_fluxo = user_data.get(message.from_user.id, {})
    telegram_user = dados_fluxo.get("telegram_revenda")
    usado_atual = int(dados_fluxo.get("limite_usado_revenda", 0))
    reservado_sub = int(dados_fluxo.get("limite_reservado_subrevendas", 0))

    if not telegram_user:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Fluxo inválido. Digite /menu para tentar novamente."
        )
        return

    minimo_permitido = usado_atual + reservado_sub

    if novo_limite < minimo_permitido:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            f"❌ Revenda com limite acima de {esc(novo_limite)} usados.\n\n"
            "Execute /menu e tente dnv"
        )
        return

    try:
        alterar_limite_revenda(telegram_user, novo_limite)

        bot.send_message(
            message.chat.id,
            "✅ <b>Limite da revenda alterado com sucesso!</b>\n\n"
            f"👤 <b>Telegram:</b> <code>{esc(telegram_user)}</code>\n"
            f"👥 <b>Novo limite:</b> <code>{esc(novo_limite)}</code>"
        )

    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Erro ao alterar limite da revenda.\n<code>{esc(e)}</code>"
        )
    finally:
        limpar_fluxo(message.from_user.id)

def receber_nova_data_revenda(message):
    if not eh_admin(message.from_user.id):
        return

    if not message.text:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Data inválida. Digite /menu para tentar novamente."
        )
        return

    texto = message.text.strip()

    if not texto.isdigit() or int(texto) <= 0:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Data inválida. Digite /menu para tentar novamente."
        )
        return

    dias = int(texto)
    telegram_user = user_data[message.from_user.id]["telegram_revenda"]

    try:
        resultado = alterar_data_revenda(telegram_user, dias)

        if resultado["estava_suspensa"]:
            bot.send_message(
                message.chat.id,
                "✅ <b>Revenda suspensa reativada com sucesso!</b>"
            )

            enviar_msg_revenda(
                telegram_user,
                f"✅ Seu acesso foi reativado!\n\n📅 Novo vencimento: {resultado['nova_data']}"
            )

        bot.send_message(
            message.chat.id,
            "✅ <b>Data da revenda alterada com sucesso!</b>\n\n"
            f"👤 <b>Telegram:</b> {esc(telegram_user)}\n"
            f"📅 <b>Novo vencimento:</b> {esc(resultado['nova_data'])}"
        )

    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Erro ao alterar data da revenda.\n<code>{esc(e)}</code>"
        )
    finally:
        limpar_fluxo(message.from_user.id)


# =========================================================
# RELATÓRIO INDIVIDUAL DA REVENDA
# =========================================================
def receber_telegram_relatorio_individual_revenda(message):
    if not eh_admin(message.from_user.id):
        return

    if not message.text:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ @ inválido. Digite /menu para tentar novamente."
        )
        return

    telegram_user = message.text.strip()

    if not telegram_revenda_valido(telegram_user):
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ @ inválido. O @ precisa começar com @.\nDigite /menu para tentar novamente."
        )
        return

    if not revenda_existe(telegram_user):
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Revenda não encontrada.\nDigite /menu para tentar novamente."
        )
        return

    msg_consultando = None

    try:
        msg_consultando = bot.send_message(
            message.chat.id,
            "<b>Consultando...</b>"
        )

        # -------------------------------------------------
        # VARREDURA SILENCIOSA APENAS DESTA REVENDA
        # -------------------------------------------------
        try:
            sincronizar_arquivo_revenda(telegram_user)
            recalcular_limite_restante_revenda(telegram_user)
        except:
            pass

        texto, usuarios = montar_texto_relatorio_individual_revenda(telegram_user)

        if msg_consultando:
            try:
                bot.delete_message(message.chat.id, msg_consultando.message_id)
            except:
                pass

        if len(texto) <= 3500:
            bot.send_message(
                message.chat.id,
                texto,
                reply_markup=painel_voltar_relatorio_individual_revenda()
            )
        else:
            pdf_path = gerar_pdf_relatorio_individual_revenda(telegram_user)

            try:
                with open(pdf_path, "rb") as pdf_file:
                    bot.send_document(
                        message.chat.id,
                        pdf_file,
                        caption=f"Relatório individual da revenda {telegram_user}"
                    )
            finally:
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)

    except Exception as e:
        try:
            if msg_consultando:
                bot.delete_message(message.chat.id, msg_consultando.message_id)
        except:
            pass

        bot.send_message(
            message.chat.id,
            f"❌ Erro ao gerar relatório individual da revenda.\n<code>{esc(e)}</code>"
        )
    finally:
        limpar_fluxo(message.from_user.id)

# =========================================================
# DELETAR REVENDA
# Primeiro apaga todos os usuários dela
# Depois apaga o cadastro da revenda
# =========================================================
def receber_telegram_del_revenda(message):
    if not eh_admin(message.from_user.id):
        return

    if not message.text:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ @ inválido. Digite /menu para tentar novamente."
        )
        return

    telegram_user = normalizar_telegram_user(message.text)

    if not telegram_revenda_valido(telegram_user):
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ @ inválido. O @ precisa começar com @.\nDigite /menu para tentar novamente."
        )
        return

    if not revenda_existe(telegram_user):
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Revenda não encontrada.\nDigite /menu para tentar novamente."
        )
        return

    try:
        # -------------------------------------------------
        # 0) SINCRONIZA A REVENDA ANTES DE APAGAR
        # -------------------------------------------------
        try:
            sincronizar_arquivo_revenda(telegram_user)
        except:
            pass

        # -------------------------------------------------
        # 1) DELETA PRIMEIRO AS SUB-REVENDAS DESTA REVENDA
        # -------------------------------------------------
        subs_apagadas, subs_falharam = deletar_subrevendas_da_revenda(telegram_user)

        if subs_falharam:
            bot.send_message(
                message.chat.id,
                "❌ Não foi possível apagar todas as sub-revendas desta revenda.\n\n"
                f"⚠️ Falharam: <code>{esc(' | '.join(subs_falharam))}</code>"
            )
            limpar_fluxo(message.from_user.id)
            return

        # -------------------------------------------------
        # 2) APAGA OS USUÁRIOS DA REVENDA
        # -------------------------------------------------
        apagados, falharam = apagar_todos_usuarios_da_revenda(telegram_user)

        if falharam:
            bot.send_message(
                message.chat.id,
                "❌ Não foi possível apagar todos os usuários da revenda.\n\n"
                f"⚠️ Falharam: <code>{esc(', '.join(falharam))}</code>"
            )
            limpar_fluxo(message.from_user.id)
            return

        # -------------------------------------------------
        # 3) REMOVE O CADASTRO DA REVENDA
        # -------------------------------------------------
        deletar_revenda(telegram_user)

        texto = (
            "🗑️ <b>Revenda deletada com sucesso!</b>\n\n"
            f"👤 <b>Telegram:</b> {esc(telegram_user)}\n"
            f"📊 <b>Usuários da revenda apagados:</b> {esc(len(apagados))}"
        )

        if subs_apagadas:
            texto += f"\n📦 <b>Sub-revendas apagadas:</b> {esc(len(subs_apagadas))}"

        bot.send_message(message.chat.id, texto)

    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Erro ao deletar revenda.\n<code>{esc(e)}</code>"
        )
    finally:
        limpar_fluxo(message.from_user.id)
# =========================================================
# PAINEL DE REVENDAS (ADMIN)
# =========================================================
def painel_revendas_markup():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton("Adicionar revenda", callback_data="add_revenda"))
    kb.add(types.InlineKeyboardButton("Deletar revenda", callback_data="del_revenda"))
    kb.add(types.InlineKeyboardButton("Alterar data revenda", callback_data="alt_data_revenda"))
    kb.add(types.InlineKeyboardButton("Alterar limite revenda", callback_data="alt_limite_revenda"))
    kb.add(types.InlineKeyboardButton("Relatório revendas", callback_data="relatorio_revendas"))
    kb.add(types.InlineKeyboardButton("Relatório individual revenda", callback_data="relatorio_individual_revenda"))
    kb.add(types.InlineKeyboardButton("Relatório sub-revendas", callback_data="relatorio_subrevendas_revendas"))
    kb.add(types.InlineKeyboardButton("Alterar @ do revenda", callback_data="alt_nome_usuario_revenda"))
    kb.add(
        types.InlineKeyboardButton("Suspender", callback_data="suspender_revenda"),
        types.InlineKeyboardButton("Renovar", callback_data="renovar_revenda")
    )
    kb.add(types.InlineKeyboardButton("⬅️ Voltar", callback_data="voltar_painel"))
    return kb


# =========================================================
# LISTAR TODAS AS REVENDAS
# =========================================================
def listar_todas_revendas():
    garantir_pasta_revendas()
    revendas = []

    for nome in os.listdir(REV_DIR):
        if not nome.endswith(".txt"):
            continue

        caminho = os.path.join(REV_DIR, nome)
        if not os.path.isfile(caminho):
            continue

        try:
            with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
                primeira_linha = f.readline().strip()

            if primeira_linha.startswith("telegram=@"):
                telegram_user = primeira_linha.split("=", 1)[1].strip()
                if telegram_user:
                    revendas.append(telegram_user)
        except:
            continue

    return revendas


# =========================================================
# SALVAR CHAT_ID DA REVENDA
# =========================================================
def salvar_chat_id_revenda(telegram_user, chat_id):
    caminho = caminho_arquivo_revenda(telegram_user)
    if not os.path.exists(caminho):
        return

    with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
        linhas = [linha.rstrip("\n") for linha in f]

    # se já está salvo igual, não faz nada
    for linha in linhas:
        if linha == f"chat_id={chat_id}":
            return

    novas_linhas = []
    achou = False

    for linha in linhas:
        if linha.startswith("chat_id="):
            novas_linhas.append(f"chat_id={chat_id}")
            achou = True
        else:
            novas_linhas.append(linha)

    if not achou:
        inserido = False
        resultado = []

        for linha in novas_linhas:
            resultado.append(linha)
            if linha.startswith("suspenso=") and not inserido:
                resultado.append(f"chat_id={chat_id}")
                inserido = True

        if not inserido:
            resultado.append(f"chat_id={chat_id}")

        novas_linhas = resultado

    with open(caminho, "w", encoding="utf-8") as f:
        for linha in novas_linhas:
            f.write(linha + "\n")

# =========================================================
# SALVAR CHAT_ID DA SUB REVENDA
# =========================================================
def salvar_chat_id_subrevenda(telegram_user, chat_id):
    caminho = caminho_arquivo_subrevenda(telegram_user)
    if not os.path.exists(caminho):
        return

    linhas = []
    achou = False

    with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
        for linha in f:
            linha_sem_quebra = linha.rstrip("\n")

            if linha_sem_quebra.startswith("chat_id="):
                linhas.append(f"chat_id={chat_id}")
                achou = True
            else:
                linhas.append(linha_sem_quebra)

    if not achou:
        novas_linhas = []
        inserido = False

        for linha in linhas:
            novas_linhas.append(linha)
            if linha.startswith("suspenso=") and not inserido:
                novas_linhas.append(f"chat_id={chat_id}")
                inserido = True

        if not inserido:
            novas_linhas.append(f"chat_id={chat_id}")

        linhas = novas_linhas

    with open(caminho, "w", encoding="utf-8") as f:
        for linha in linhas:
            f.write(linha + "\n")


# =========================================================
# SALVAR MARCADOR DE AVISO/SUSPENSÃO DA SUB REVENDA
# =========================================================
def salvar_campo_subrevenda(telegram_user, campo, valor):
    caminho = caminho_arquivo_subrevenda(telegram_user)
    if not os.path.exists(caminho):
        return

    linhas = []
    achou = False

    with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
        for linha in f:
            linha_sem_quebra = linha.rstrip("\n")

            if linha_sem_quebra.startswith(f"{campo}="):
                linhas.append(f"{campo}={valor}")
                achou = True
            else:
                linhas.append(linha_sem_quebra)

    if not achou:
        novas_linhas = []
        inserido = False

        for linha in linhas:
            novas_linhas.append(linha)
            if linha.startswith("chat_id=") and not inserido:
                novas_linhas.append(f"{campo}={valor}")
                inserido = True

        if not inserido:
            novas_linhas.append(f"{campo}={valor}")

        linhas = novas_linhas

    with open(caminho, "w", encoding="utf-8") as f:
        for linha in linhas:
            f.write(linha + "\n")


# =========================================================
# SALVAR MARCADOR DE AVISO/SUSPENSÃO DA REVENDA
# =========================================================
def salvar_campo_revenda(telegram_user, campo, valor):
    caminho = caminho_arquivo_revenda(telegram_user)
    if not os.path.exists(caminho):
        return

    linhas = []
    achou = False

    with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
        for linha in f:
            linha_sem_quebra = linha.rstrip("\n")

            if linha_sem_quebra.startswith(f"{campo}="):
                linhas.append(f"{campo}={valor}")
                achou = True
            else:
                linhas.append(linha_sem_quebra)

    if not achou:
        novas_linhas = []
        inserido = False

        for linha in linhas:
            novas_linhas.append(linha)
            if linha.startswith("chat_id=") and not inserido:
                novas_linhas.append(f"{campo}={valor}")
                inserido = True

        if not inserido:
            novas_linhas.append(f"{campo}={valor}")

        linhas = novas_linhas

    with open(caminho, "w", encoding="utf-8") as f:
        for linha in linhas:
            f.write(linha + "\n")


# =========================================================
# ENVIAR MENSAGEM PARA REVENDA
# Só funciona se ela já tiver falado com o bot e tivermos chat_id
# =========================================================
def enviar_msg_revenda(telegram_user, texto):
    try:
        dados = ler_dados_revenda(telegram_user)
        chat_id = str(dados.get("chat_id", "")).strip()
        if not chat_id:
            return False

        bot.send_message(int(chat_id), texto)
        return True
    except:
        return False


# =========================================================
# VERIFICAR SE A REVENDA VENCE HOJE
# =========================================================
def revenda_vence_hoje(telegram_user):
    try:
        dados = ler_dados_revenda(telegram_user)
        vencimento = dados.get("vencimento", "").strip()
        if not vencimento:
            return False

        data_venc = datetime.strptime(vencimento, "%d/%m/%Y").date()
        hoje = datetime.now(SP_TZ).date()
        return data_venc == hoje
    except:
        return False


# =========================================================
# VERIFICAR SE A REVENDA DEVE SER SUSPENSA
# Suspende no próprio dia, no horário configurado
# =========================================================
def revenda_deve_ser_suspensa_hoje(telegram_user, hora=23, minuto=59):
    try:
        dados = ler_dados_revenda(telegram_user)
        vencimento = str(dados.get("vencimento", "")).strip()
        if not vencimento:
            return False

        data_venc = datetime.strptime(vencimento, "%d/%m/%Y").date()
        agora = datetime.now(SP_TZ)

        momento_suspensao = SP_TZ.localize(
            datetime(
                year=data_venc.year,
                month=data_venc.month,
                day=data_venc.day,
                hour=hora,
                minute=minuto,
                second=0,
                microsecond=0
            )
        )

        return agora >= momento_suspensao
    except:
        return False
    
# =========================================================
# SUSPENDER REVENDA AUTOMATICAMENTE
# =========================================================
def suspender_revenda_automaticamente(telegram_user):
    if revenda_suspensa(telegram_user):
        return False

    bloqueados, falharam = bloquear_todos_usuarios_da_revenda(telegram_user)

    if falharam:
        raise Exception(f"Falha ao bloquear usuários: {', '.join(falharam)}")

    definir_suspensao_revenda(telegram_user, True)

    hoje_str = datetime.now(SP_TZ).strftime("%d/%m/%Y")
    salvar_campo_revenda(telegram_user, "ultima_suspensao", hoje_str)
    resultado_subs = suspender_subrevendas_da_revenda(telegram_user)
    
    enviar_msg_revenda(
        telegram_user,
        "⛔ Sua revenda foi suspensa por vencimento.\n\nRenove para voltar a usar o painel."
    )
    
    texto_admin = (
        "⛔ <b>Revenda suspensa por vencimento</b>\n\n"
        f"👤 <b>Revenda:</b> {esc(telegram_user)}\n"
        f"🔒 <b>Usuários bloqueados:</b> {esc(len(bloqueados))}"
    )
    
    if resultado_subs["suspensas_agora"] or resultado_subs["ja_estavam_suspensas"]:
        texto_admin += f"\n📦 <b>Sub-revendas suspensas agora:</b> {esc(len(resultado_subs['suspensas_agora']))}"
    
    bot.send_message(ADMIN_ID, texto_admin)

    try:
        if resultado_subs["suspensas_agora"]:
            bot.send_message(
                ADMIN_ID,
                "⛔ <b>Sub-revendas suspensas junto com a revenda</b>\n\n"
                f"👤 <b>Revenda:</b> <code>{esc(telegram_user)}</code>\n"
                f"📦 <b>Subs suspensas agora:</b> <code>{esc(len(resultado_subs['suspensas_agora']))}</code>"
            )
    except:
        pass
    
    return True
# =========================================================
# ARQUIVO DE USUÁRIOS DA REVENDA
# =========================================================
def adicionar_usuario_revenda_arquivo(telegram_user, username, senha, limite, dias_restantes, uuid_code=None):
    caminho = caminho_arquivo_revenda(telegram_user)

    linha = f"{username} {senha} {limite} {dias_restantes}"
    if uuid_code:
        linha += f" {uuid_code}"

    with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
        conteudo = f.read()

    if "\n\n" not in conteudo:
        with open(caminho, "a", encoding="utf-8") as f:
            if not conteudo.endswith("\n"):
                f.write("\n")
            f.write("\n")

    with open(caminho, "a", encoding="utf-8") as f:
        f.write(linha + "\n")

# =========================================================
# ARQUIVO DE USUÁRIOS DA SUB REVENDA
# =========================================================
def adicionar_usuario_sub_arquivo(telegram_user, username, senha, limite, dias_restantes, uuid_code=None):
    caminho = caminho_arquivo_subrevenda(telegram_user)

    linha = f"{username} {senha} {limite} {dias_restantes}"
    if uuid_code:
        linha += f" {uuid_code}"

    with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
        conteudo = f.read()

    if "\n\n" not in conteudo:
        with open(caminho, "a", encoding="utf-8") as f:
            if not conteudo.endswith("\n"):
                f.write("\n")
            f.write("\n")

    with open(caminho, "a", encoding="utf-8") as f:
        f.write(linha + "\n")


# =========================================================
# ADICIONAR TESTE NO MESMO ARQUIVO DA SUB REVENDA
# =========================================================
def adicionar_teste_sub_arquivo(telegram_user, username, senha, limite, dias_restantes, uuid_code=None):
    caminho = caminho_arquivo_subrevenda(telegram_user)

    linha = f"{username} {senha} {limite} {dias_restantes}"
    if uuid_code:
        linha += f" {uuid_code}"

    with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
        conteudo = f.read()

    if "\n\n" not in conteudo:
        with open(caminho, "a", encoding="utf-8") as f:
            if not conteudo.endswith("\n"):
                f.write("\n")
            f.write("\n")

    with open(caminho, "a", encoding="utf-8") as f:
        f.write(linha + "\n")

# =========================================================
# ADICIONAR TESTE NO MESMO ARQUIVO DA REVENDA
# Formato:
# usuario senha limite horas uuid_opcional
# =========================================================
def adicionar_teste_revenda_arquivo(telegram_user, username, senha, limite, horas, uuid_code=None):
    caminho = caminho_arquivo_revenda(telegram_user)

    linha = f"{username} {senha} {limite} {horas}"
    if uuid_code:
        linha += f" {uuid_code}"

    with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
        conteudo = f.read()

    if "\n\n" not in conteudo:
        with open(caminho, "a", encoding="utf-8") as f:
            if not conteudo.endswith("\n"):
                f.write("\n")
            f.write("\n")

    with open(caminho, "a", encoding="utf-8") as f:
        f.write(linha + "\n")

# =========================================================
# REMOVER USUÁRIO/TESTE DO ARQUIVO DA REVENDA
# =========================================================
def remover_usuario_revenda_arquivo(telegram_user, username):
    caminho = caminho_arquivo_revenda(telegram_user)
    if not os.path.exists(caminho):
        return False

    novas_linhas = []
    removeu = False

    with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
        for linha in f:
            linha_limpa = linha.rstrip("\n")
            texto = linha_limpa.strip()

            if not texto:
                continue

            if "=" in texto:
                novas_linhas.append(linha_limpa)
                continue

            partes = texto.split()
            if len(partes) >= 1 and partes[0] == username:
                removeu = True
                continue

            novas_linhas.append(linha_limpa)

    with open(caminho, "w", encoding="utf-8") as f:
        for i, linha in enumerate(novas_linhas):
            f.write(linha + "\n")

    return removeu

# =========================================================
# REMOVER USUÁRIO/TESTE DO ARQUIVO DA SUB REVENDA
# =========================================================
def remover_usuario_sub_arquivo(telegram_user, username):
    caminho = caminho_arquivo_subrevenda(telegram_user)
    if not os.path.exists(caminho):
        return False

    novas_linhas = []
    removeu = False

    with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
        for linha in f:
            linha_limpa = linha.rstrip("\n")
            texto = linha_limpa.strip()

            if not texto:
                continue

            if "=" in texto:
                novas_linhas.append(linha_limpa)
                continue

            partes = texto.split()
            if len(partes) >= 1 and partes[0] == username:
                removeu = True
                continue

            novas_linhas.append(linha_limpa)

    with open(caminho, "w", encoding="utf-8") as f:
        for linha in novas_linhas:
            f.write(linha + "\n")

    return removeu

# =========================================================
# PASTA / ARQUIVO DAS SUB REVENDA
# =========================================================
def garantir_pasta_subrevendas():
    os.makedirs(SUB_DIR, exist_ok=True)


def caminho_arquivo_subrevenda(telegram_user):
    garantir_pasta_subrevendas()
    tg = normalizar_telegram_user(telegram_user)
    return os.path.join(SUB_DIR, f"{tg.lstrip('@')}.txt")

# =========================================================
# SALVAR SUB REVENDA
# Mantém os usuários/testes no mesmo arquivo
# Preserva suspenso/chat_id/ultimo_aviso/ultima_suspensao
# =========================================================
def salvar_subrevenda(dono, telegram_user, limite_total, limite_restante, vencimento_formatado):
    garantir_pasta_subrevendas()

    dono = normalizar_telegram_user(dono)
    telegram_user = normalizar_telegram_user(telegram_user)

    caminho = caminho_arquivo_subrevenda(telegram_user)

    # -----------------------------------------------------
    # PRESERVAR CAMPOS JÁ EXISTENTES DO CABEÇALHO
    # -----------------------------------------------------
    dados_antigos = {}
    linhas_usuarios = []

    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
            for linha in f:
                linha_limpa = linha.rstrip("\n")
                texto = linha_limpa.strip()

                if not texto:
                    continue

                if "=" in texto:
                    chave, valor = texto.split("=", 1)
                    dados_antigos[chave.strip()] = valor.strip()
                else:
                    linhas_usuarios.append(linha_limpa)

    # -----------------------------------------------------
    # CAMPOS PRINCIPAIS ATUALIZADOS
    # -----------------------------------------------------
    dados_antigos["dono"] = dono
    dados_antigos["telegram"] = telegram_user
    dados_antigos["limite_total"] = str(limite_total)
    dados_antigos["limite_restante"] = str(limite_restante)
    dados_antigos["vencimento"] = str(vencimento_formatado)

    # -----------------------------------------------------
    # REESCREVER O ARQUIVO PRESERVANDO METADADOS
    # -----------------------------------------------------
    ordem_campos = [
        "dono",
        "telegram",
        "limite_total",
        "limite_restante",
        "vencimento",
        "suspenso",
        "chat_id",
        "ultimo_aviso",
        "ultima_suspensao",
        "suspenso_por_fornecedor"
    ]

    with open(caminho, "w", encoding="utf-8") as f:
        for campo in ordem_campos:
            if campo in dados_antigos and str(dados_antigos[campo]).strip() != "":
                f.write(f"{campo}={dados_antigos[campo]}\n")

        # grava quaisquer outros campos extras que existirem
        for campo, valor in dados_antigos.items():
            if campo not in ordem_campos and str(valor).strip() != "":
                f.write(f"{campo}={valor}\n")

        if linhas_usuarios:
            f.write("\n")
            for linha in linhas_usuarios:
                f.write(linha + "\n")


# =========================================================
# LER DADOS DA SUB REVENDA
# =========================================================
def ler_dados_subrevenda(telegram_user):
    caminho = caminho_arquivo_subrevenda(telegram_user)
    if not os.path.exists(caminho):
        raise Exception("Sub revenda não encontrada.")

    dados = {}
    with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
        for linha in f:
            linha = linha.strip()
            if not linha:
                continue
            if "=" not in linha:
                continue
            k, v = linha.split("=", 1)
            dados[k.strip()] = v.strip()

    return dados

# =========================================================
# ATUALIZAR DONO DAS SUB-REVENDAS QUANDO A REVENDA MUDA DE @
# =========================================================
def atualizar_dono_subrevendas_da_revenda(telegram_antigo, telegram_novo):
    subs = listar_subrevendas_da_revenda(telegram_antigo)
    atualizadas = []
    falharam = []

    for telegram_sub in subs:
        try:
            caminho = caminho_arquivo_subrevenda(telegram_sub)
            if not os.path.exists(caminho):
                continue

            linhas = []
            alterou = False

            with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
                for linha in f:
                    linha_sem_quebra = linha.rstrip("\n")

                    if linha_sem_quebra.startswith("dono="):
                        linhas.append(f"dono={telegram_novo}")
                        alterou = True
                    else:
                        linhas.append(linha_sem_quebra)

            if not alterou:
                novas_linhas = [f"dono={telegram_novo}"]
                novas_linhas.extend(linhas)
                linhas = novas_linhas

            with open(caminho, "w", encoding="utf-8") as f:
                for linha in linhas:
                    f.write(linha + "\n")

            atualizadas.append(telegram_sub)

        except Exception as e:
            falharam.append(f"{telegram_sub}: {e}")

    return atualizadas, falharam

# =========================================================
# SUB-REVENDAS DE UMA REVENDA
# =========================================================
def listar_subrevendas_da_revenda(telegram_revenda):
    resultado = []

    for telegram_sub in listar_todas_subrevendas():
        try:
            dados = ler_dados_subrevenda(telegram_sub)
            dono = str(dados.get("dono", "")).strip()

            if dono == telegram_revenda:
                resultado.append(telegram_sub)
        except:
            continue

    return resultado


def subrevenda_suspensa_por_fornecedor(telegram_user):
    try:
        dados = ler_dados_subrevenda(telegram_user)
        return str(dados.get("suspenso_por_fornecedor", "0")).strip() == "1"
    except:
        return False


def definir_suspensao_por_fornecedor_subrevenda(telegram_user, suspenso=True):
    salvar_campo_subrevenda(
        telegram_user,
        "suspenso_por_fornecedor",
        "1" if suspenso else "0"
    )

# =========================================================
# SUSPENDER SUB-REVENDAS VINCULADAS À REVENDA
# Suspende apenas as que NÃO estavam suspensas antes
# e marca no arquivo quais foram suspensas por herança
# =========================================================
def suspender_subrevendas_da_revenda(telegram_revenda):
    suspensas_agora = []
    ja_estavam_suspensas = []
    falharam = []

    subs = listar_subrevendas_da_revenda(telegram_revenda)

    for telegram_sub in subs:
        try:
            if subrevenda_suspensa(telegram_sub):
                ja_estavam_suspensas.append(telegram_sub)
                continue

            bloqueados, falharam_users = bloquear_todos_usuarios_da_subrevenda(telegram_sub)
            if falharam_users:
                raise Exception(f"Falha ao bloquear usuários da sub {telegram_sub}: {', '.join(falharam_users)}")

            definir_suspensao_subrevenda(telegram_sub, True)

            hoje_str = datetime.now(SP_TZ).strftime("%d/%m/%Y")
            salvar_campo_subrevenda(telegram_sub, "ultima_suspensao", hoje_str)
            definir_suspensao_por_fornecedor_subrevenda(telegram_sub, True)

            dados_sub = ler_dados_subrevenda(telegram_sub)
            dono_sub = str(dados_sub.get("dono", "")).strip()

            if not dono_sub:
                dono_sub = telegram_revenda

            enviar_msg_subrevenda(
                telegram_sub,
                f"⛔ Seu fornecedor foi suspenso!\n\nEntre em contato para mais informações {dono_sub}."
            )

            suspensas_agora.append(telegram_sub)

        except Exception as e:
            falharam.append(f"{telegram_sub}: {e}")

    return {
        "suspensas_agora": suspensas_agora,
        "ja_estavam_suspensas": ja_estavam_suspensas,
        "falharam": falharam
    }

# =========================================================
# REATIVAR SUB-REVENDAS SUSPENSAS POR HERANÇA DA REVENDA
# Só reativa as que foram suspensas junto com a revenda
# =========================================================
def reativar_subrevendas_da_revenda(telegram_revenda):
    reativadas = []
    ignoradas = []
    falharam = []

    subs = listar_subrevendas_da_revenda(telegram_revenda)

    for telegram_sub in subs:
        try:
            if not subrevenda_suspensa(telegram_sub):
                ignoradas.append(telegram_sub)
                continue

            if not subrevenda_suspensa_por_fornecedor(telegram_sub):
                ignoradas.append(telegram_sub)
                continue

            desbloqueados, falharam_users = desbloquear_todos_usuarios_da_subrevenda(telegram_sub)
            if falharam_users:
                raise Exception(f"Falha ao desbloquear usuários da sub {telegram_sub}: {', '.join(falharam_users)}")

            definir_suspensao_subrevenda(telegram_sub, False)
            salvar_campo_subrevenda(telegram_sub, "ultima_suspensao", "")
            definir_suspensao_por_fornecedor_subrevenda(telegram_sub, False)

            enviar_msg_subrevenda(
                telegram_sub,
                "✅ Seu painel foi reativado!"
            )

            reativadas.append(telegram_sub)

        except Exception as e:
            falharam.append(f"{telegram_sub}: {e}")

    return {
        "reativadas": reativadas,
        "ignoradas": ignoradas,
        "falharam": falharam
    }


# =========================================================
# SOMAR O LIMITE USADO REAL DA SUB REVENDA
# =========================================================
def calcular_limite_usado_real_subrevenda(telegram_sub):
    caminho = caminho_arquivo_subrevenda(telegram_sub)

    if not os.path.exists(caminho):
        raise Exception("Sub revenda não encontrada.")

    usado = 0

    with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
        for linha in f:
            linha = linha.strip()

            if not linha:
                continue

            if "=" in linha:
                continue

            partes = linha.split()
            if len(partes) < 4:
                continue

            try:
                limite_usuario = int(partes[2])
            except:
                limite_usuario = 0

            usado += limite_usuario

    return usado

# =========================================================
# LER USUÁRIOS COMPLETOS DA SUB REVENDA
# =========================================================
def ler_usuarios_subrevenda_completos(telegram_sub):
    caminho = caminho_arquivo_subrevenda(telegram_sub)

    if not os.path.exists(caminho):
        raise Exception("Sub revenda não encontrada.")

    usuarios = []

    with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
        for linha in f:
            linha = linha.strip()

            if not linha:
                continue

            if "=" in linha:
                continue

            partes = linha.split()
            if len(partes) < 4:
                continue

            username = partes[0].strip()
            senha = partes[1].strip()
            limite = partes[2].strip()
            dias = partes[3].strip()
            uuid = partes[4].strip() if len(partes) >= 5 else ""

            usuarios.append({
                "username": username,
                "senha": senha,
                "limite": limite,
                "dias": dias,
                "uuid": uuid
            })

    return usuarios

# =========================================================
# REESCREVER ARQUIVO DA SUB REVENDA
# Mantém os cabeçalhos e recria o bloco de usuários
# =========================================================
def reescrever_arquivo_subrevenda(telegram_sub, usuarios_atualizados):
    caminho = caminho_arquivo_subrevenda(telegram_sub)

    if not os.path.exists(caminho):
        return False

    cabecalhos = []

    with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
        for linha in f:
            linha_limpa = linha.rstrip("\n")
            if not linha_limpa.strip():
                continue
            if "=" in linha_limpa:
                cabecalhos.append(linha_limpa)

    with open(caminho, "w", encoding="utf-8") as f:
        for linha in cabecalhos:
            f.write(linha + "\n")

        if usuarios_atualizados:
            f.write("\n")
            for item in usuarios_atualizados:
                linha = (
                    f"{item['username']} "
                    f"{item['senha']} "
                    f"{item['limite']} "
                    f"{item['dias']}"
                )

                uuid = str(item.get("uuid", "")).strip()
                if uuid:
                    linha += f" {uuid}"

                f.write(linha + "\n")

    return True

# =========================================================
# SINCRONIZAR ARQUIVO DA SUB REVENDA
# Regras:
# - se usuário não existe no list-users, remove da sub
# - se existe, atualiza senha, limite, data e uuid
# - ao final, recalcula e salva o limite_restante da sub
# =========================================================
def sincronizar_arquivo_subrevenda(telegram_sub):
    usuarios_arquivo = ler_usuarios_subrevenda_completos(telegram_sub)
    if not usuarios_arquivo:
        try:
            dados_sub = ler_dados_subrevenda(telegram_sub)
            dono = str(dados_sub.get("dono", "")).strip()
            limite_total = int(str(dados_sub.get("limite_total", "0")).strip())
            vencimento = str(dados_sub.get("vencimento", "")).strip()

            salvar_subrevenda(
                dono=dono,
                telegram_user=telegram_sub,
                limite_total=limite_total,
                limite_restante=limite_total,
                vencimento_formatado=vencimento
            )
        except:
            pass

        return {
            "telegram_user": telegram_sub,
            "analisados": 0,
            "removidos": 0,
            "atualizados": 0
        }

    usuarios_sistema = set(listar_usuarios())
    mapa_uuids = obter_mapa_uuids_disponiveis()
    mapa_limites = obter_mapa_limites_sistema()

    novos_usuarios = []
    removidos = 0
    atualizados = 0
    usuarios_orfaos_uuid = set()

    for item in usuarios_arquivo:
        username = str(item["username"]).strip()

        # ---------------------------------------------
        # Se não existe mais no sistema, remove
        # ---------------------------------------------
        if username not in usuarios_sistema:
            removidos += 1
            usuarios_orfaos_uuid.add(username)
            continue

        # ---------------------------------------------
        # SENHA REAL DA VPS
        # ---------------------------------------------
        try:
            senha_real = str(obter_senha_usuario(username)).strip()
            if not senha_real:
                senha_real = str(item["senha"]).strip()
        except:
            senha_real = str(item["senha"]).strip()

        # ---------------------------------------------
        # LIMITE REAL DA VPS
        # Lendo diretamente do mapa montado do usuarios.db
        # ---------------------------------------------
        limite_real = str(mapa_limites.get(username, "")).strip()
        if not limite_real:
            limite_real = str(item["limite"]).strip()

        # ---------------------------------------------
        # DATA REAL DA VPS -> salva em "dias"
        # ---------------------------------------------
        try:
            data_venc = obter_data_vencimento_usuario(username)
            dias_txt = calcular_dias_restantes_revenda_sync(data_venc)
        except:
            dias_txt = str(item["dias"]).strip()

        # ---------------------------------------------
        # UUID REAL DO XRAY
        # ---------------------------------------------
        try:
            uuid_real = str(obter_uuid_disponivel_usuario(username, mapa_uuids)).strip()
        except:
            uuid_real = str(item.get("uuid", "")).strip()

        senha_antiga = str(item["senha"]).strip()
        limite_antigo = str(item["limite"]).strip()
        dias_antigo = str(item["dias"]).strip()
        uuid_antigo = str(item.get("uuid", "")).strip()

        mudou = (
            senha_antiga != senha_real or
            limite_antigo != limite_real or
            dias_antigo != dias_txt or
            uuid_antigo != uuid_real
        )

        if mudou:
            atualizados += 1

        novos_usuarios.append({
            "username": username,
            "senha": senha_real,
            "limite": limite_real,
            "dias": dias_txt,
            "uuid": uuid_real
        })

    if usuarios_orfaos_uuid:
        try:
            remover_usuarios_uuid_expirados(usuarios_orfaos_uuid)
        except:
            pass

    reescrever_arquivo_subrevenda(telegram_sub, novos_usuarios)

    # ---------------------------------------------
    # RECALCULAR E SALVAR O CABEÇALHO DA SUB
    # ---------------------------------------------
    try:
        dados_sub = ler_dados_subrevenda(telegram_sub)
        dono = str(dados_sub.get("dono", "")).strip()
        limite_total = int(str(dados_sub.get("limite_total", "0")).strip())
        vencimento = str(dados_sub.get("vencimento", "")).strip()

        usado = 0
        for item in novos_usuarios:
            try:
                usado += int(str(item["limite"]).strip())
            except:
                pass

        limite_restante = limite_total - usado
        if limite_restante < 0:
            limite_restante = 0

        salvar_subrevenda(
            dono=dono,
            telegram_user=telegram_sub,
            limite_total=limite_total,
            limite_restante=limite_restante,
            vencimento_formatado=vencimento
        )
    except:
        pass

    return {
        "telegram_user": telegram_sub,
        "analisados": len(usuarios_arquivo),
        "removidos": removidos,
        "atualizados": atualizados
    }

# =========================================================
# SINCRONIZAR TODAS AS SUB REVENDA
# =========================================================
def sincronizar_todas_subrevendas():
    resultados = []
    erros = []

    for telegram_sub in listar_todas_subrevendas():
        try:
            resultado = sincronizar_arquivo_subrevenda(telegram_sub)
            resultados.append(resultado)
        except Exception as e:
            erros.append(f"{telegram_sub}: {e}")

    return resultados, erros

# =========================================================
# DELETAR SUB REVENDA
# Apaga os usuários dela, remove o arquivo e devolve o limite à revenda dona
# =========================================================
def deletar_subrevenda(telegram_user):
    try:
        if sincronizar_arquivo_subrevenda:
            sincronizar_arquivo_subrevenda(telegram_user)
    except:
        pass

    caminho = caminho_arquivo_subrevenda(telegram_user)
    if not os.path.exists(caminho):
        raise Exception("Sub revenda não encontrada.")

    dados_sub = ler_dados_subrevenda(telegram_user)
    dono = str(dados_sub.get("dono", "")).strip()

    usuarios_para_apagar = []

    with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
        for linha in f:
            texto = linha.strip()

            if not texto:
                continue

            if "=" in texto:
                continue

            partes = texto.split()
            if len(partes) < 4:
                continue

            username = partes[0].strip()
            if username:
                usuarios_para_apagar.append(username)

    for username in usuarios_para_apagar:
        try:
            if usuario_existe(username):
                deletar_usuario_sistema(username)
        except:
            pass

    os.remove(caminho)

    if dono:
        try:
            recalcular_limite_restante_revenda(dono)
        except:
            pass

# =========================================================
# DELETAR TODAS AS SUB-REVENDAS DE UMA REVENDA
# Apaga o cadastro e todos os usuários das subs vinculadas
# =========================================================
def deletar_subrevendas_da_revenda(telegram_revenda):
    subs = listar_subrevendas_da_revenda(telegram_revenda)

    apagadas = []
    falharam = []

    for telegram_sub in subs:
        try:
            deletar_subrevenda(telegram_sub)
            apagadas.append(telegram_sub)
        except Exception as e:
            falharam.append(f"{telegram_sub}: {e}")

    return apagadas, falharam

# =========================================================
# VERIFICAR SE SUB REVENDA EXISTE
# =========================================================
def subrevenda_existe(telegram_user):
    tg = normalizar_telegram_user(telegram_user)
    if not tg:
        return False

    try:
        for sub_tg in listar_todas_subrevendas():
            if normalizar_telegram_user(sub_tg) == tg:
                return True
    except:
        pass

    return False


# =========================================================
# LISTAR TODAS AS SUB REVENDA
# =========================================================
def listar_todas_subrevendas():
    garantir_pasta_subrevendas()
    resultado = []

    for nome in os.listdir(SUB_DIR):
        if not nome.endswith(".txt"):
            continue

        caminho = os.path.join(SUB_DIR, nome)
        try:
            dados = ler_dados_subrevenda("@" + nome[:-4])
            telegram_user = str(dados.get("telegram", "")).strip()
            if telegram_user:
                resultado.append(telegram_user)
        except:
            continue

    return sorted(set(resultado), key=lambda x: x.lower())

# =========================================================
# LISTAR SUBREVENDAS DE UMA REVENDA
# Usa comparação normalizada do campo dono
# =========================================================
def listar_subrevendas_da_revenda(dono_telegram):
    garantir_pasta_subrevendas()
    resultado = []

    dono_telegram = normalizar_telegram_user(dono_telegram)

    for nome in os.listdir(SUB_DIR):
        if not nome.endswith(".txt"):
            continue

        telegram_sub = "@" + nome[:-4]

        try:
            dados = ler_dados_subrevenda(telegram_sub)
            dono = normalizar_telegram_user(str(dados.get("dono", "")).strip())

            if dono == dono_telegram:
                resultado.append(telegram_sub)
        except:
            continue

    return sorted(resultado, key=lambda x: x.lower())

# =========================================================
# SOMAR LIMITE RESERVADO NAS SUBREVENDAS DA REVENDA
# Usa o limite_total de cada sub como crédito reservado
# =========================================================
def calcular_limite_reservado_subrevendas(dono_telegram):
    total = 0

    for telegram_sub in listar_subrevendas_da_revenda(dono_telegram):
        try:
            dados = ler_dados_subrevenda(telegram_sub)
            limite_sub = int(str(dados.get("limite_total", "0")).strip())
            if limite_sub > 0:
                total += limite_sub
        except:
            continue

    return total

# =========================================================
# ENCONTRAR DE QUAL REVENDA É UM USUÁRIO/TESTE
# =========================================================
def encontrar_revenda_do_usuario(username):
    for telegram_user in listar_todas_revendas():
        try:
            caminho = caminho_arquivo_revenda(telegram_user)
            if not os.path.exists(caminho):
                continue

            with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
                for linha in f:
                    texto = linha.strip()
                    if not texto or "=" in texto:
                        continue

                    partes = texto.split()
                    if partes and partes[0] == username:
                        return telegram_user
        except:
            pass

    return None

# =========================================================
# LISTAR REVENDAS QUE POSSUEM SUB-REVENDAS
# =========================================================
def listar_revendas_com_subrevendas():
    resultado = []

    for telegram_revenda in listar_todas_revendas():
        try:
            subs = listar_subrevendas_da_revenda(telegram_revenda)
            if subs:
                resultado.append(telegram_revenda)
        except:
            continue

    return sorted(resultado, key=lambda x: x.lower())


# =========================================================
# MENU ADMIN: ESCOLHER REVENDA COM SUB-REVENDAS
# =========================================================
def painel_admin_relatorio_subrevendas_markup(revendas):
    kb = types.InlineKeyboardMarkup(row_width=1)

    for telegram_revenda in revendas:
        callback = f"admin_rel_subs:{telegram_revenda.lstrip('@')}"
        kb.add(types.InlineKeyboardButton(telegram_revenda, callback_data=callback))

    kb.add(types.InlineKeyboardButton("⬅️ Voltar", callback_data="voltar_menu_revendas"))
    return kb


# =========================================================
# CONTAR USUÁRIOS DE UMA SUB-REVENDA APÓS VARREDURA
# =========================================================
def contar_usuarios_subrevenda_atualizados(telegram_sub):
    try:
        if sincronizar_arquivo_subrevenda:
            sincronizar_arquivo_subrevenda(telegram_sub)
    except:
        pass

    try:
        usuarios = ler_usuarios_subrevenda_completos(telegram_sub)
        return len(usuarios)
    except:
        return 0


# =========================================================
# ORDENAR SUB-REVENDAS DA REVENDA PELO TOTAL DE USUÁRIOS
# =========================================================
def listar_subrevendas_ordenadas_por_usuarios(telegram_revenda):
    resultado = []

    for telegram_sub in listar_subrevendas_da_revenda(telegram_revenda):
        total_usuarios = contar_usuarios_subrevenda_atualizados(telegram_sub)
        resultado.append({
            "telegram_sub": telegram_sub,
            "total_usuarios": total_usuarios
        })

    resultado.sort(key=lambda x: (-x["total_usuarios"], x["telegram_sub"].lower()))
    return resultado

# =========================================================
# EXIBIR RELATÓRIOS DAS SUB-REVENDAS DE UMA REVENDA NO ADMIN
# Reaproveita o estilo do relatório individual já existente
# =========================================================
def exibir_relatorios_subrevendas_da_revenda_admin(chat_id, message_id, telegram_revenda):
    ordenadas = listar_subrevendas_ordenadas_por_usuarios(telegram_revenda)

    if not ordenadas:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"❌ A revenda {esc(telegram_revenda)} não possui sub-revendas.",
            reply_markup=painel_admin_relatorio_subrevendas_markup(listar_revendas_com_subrevendas())
        )
        return

    total = len(ordenadas)

    for idx, item in enumerate(ordenadas):
        telegram_sub = item["telegram_sub"]

        try:
            # varredura antes de gerar o relatório, como você pediu
            if sincronizar_arquivo_subrevenda:
                sincronizar_arquivo_subrevenda(telegram_sub)
        except:
            pass

        texto, usuarios = revenda.montar_texto_relatorio_individual_subrevenda(telegram_sub)

        ultimo = (idx == total - 1)

        if len(texto) <= 3500:
            if idx == 0:
                # substitui o mini painel pelo primeiro relatório
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=texto,
                    reply_markup=painel_voltar_relatorio_subrevendas_admin() if ultimo else None
                )
            else:
                bot.send_message(
                    chat_id,
                    texto,
                    reply_markup=painel_voltar_relatorio_subrevendas_admin() if ultimo else None
                )
        else:
            pdf_path = revenda.gerar_pdf_relatorio_individual_subrevenda(telegram_sub)

            try:
                if idx == 0:
                    try:
                        bot.delete_message(chat_id, message_id)
                    except:
                        pass

                with open(pdf_path, "rb") as pdf_file:
                    bot.send_document(
                        chat_id,
                        pdf_file,
                        caption=f"Relatório individual da sub-revenda ({len(usuarios)} usuário(s))"
                    )
            finally:
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)

# =========================================================
# BOTÃO DE VOLTAR DO RELATÓRIO DE SUB-REVENDAS NO ADMIN
# =========================================================
def painel_voltar_relatorio_subrevendas_admin():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("⬅️ Voltar", callback_data="voltar_menu_revendas"))
    return kb

# =========================================================
# LOCALIZAR USUÁRIO NO BANCO DAS REVENDAS POR USERNAME OU UUID
# =========================================================
def localizar_usuario_nas_revendas(termo):
    termo = str(termo or "").strip()
    if not termo:
        return None, None

    termo_lower = termo.lower()

    for telegram_revenda in listar_todas_revendas():
        try:
            usuarios = ler_usuarios_revenda_completos(telegram_revenda)
            for item in usuarios:
                username = str(item.get("username", "")).strip()
                uuid = str(item.get("uuid", "")).strip()

                if username == termo:
                    return item, telegram_revenda

                if uuid and uuid.lower() == termo_lower:
                    return item, telegram_revenda
        except:
            continue

    return None, None


# =========================================================
# LOCALIZAR USUÁRIO NO BANCO DAS SUB-REVENDAS POR USERNAME OU UUID
# =========================================================
def localizar_usuario_nas_subrevendas(termo):
    termo = str(termo or "").strip()
    if not termo:
        return None, None, None

    termo_lower = termo.lower()

    for telegram_sub in listar_todas_subrevendas():
        try:
            usuarios = ler_usuarios_subrevenda_completos(telegram_sub)
            dados_sub = ler_dados_subrevenda(telegram_sub)
            dono = str(dados_sub.get("dono", "")).strip()

            for item in usuarios:
                username = str(item.get("username", "")).strip()
                uuid = str(item.get("uuid", "")).strip()

                if username == termo:
                    return item, telegram_sub, dono

                if uuid and uuid.lower() == termo_lower:
                    return item, telegram_sub, dono
        except:
            continue

    return None, None, None


# =========================================================
# LOCALIZAR USUÁRIO NO SISTEMA GERAL POR USERNAME OU UUID
# =========================================================
def localizar_usuario_geral_por_username_ou_uuid(termo):
    termo = str(termo or "").strip()
    if not termo:
        return None

    termo_lower = termo.lower()

    # 1) tenta por username diretamente nos usuários do sistema
    try:
        usuarios_banco = obter_usuarios_do_banco()
    except:
        usuarios_banco = []

    for item in usuarios_banco:
        username = str(item.get("username", "")).strip()
        if username == termo:
            uuid_code = obter_uuid_disponivel_usuario_exato(username)
            return obter_dados_base_usuario(username, uuid_code=uuid_code)

    # 2) se não achou por username, tenta interpretar como UUID
    try:
        mapa_uuids = obter_mapa_uuids_disponiveis()
    except:
        mapa_uuids = {}

    for username, uuid_code in mapa_uuids.items():
        if str(uuid_code).strip().lower() == termo_lower:
            return obter_dados_base_usuario(username, uuid_code=uuid_code)

    correspondencias = []
    for item in usuarios_banco:
        username = str(item.get("username", "")).strip()
        if username.lower() == termo_lower:
            correspondencias.append(username)

    if len(correspondencias) == 1:
        username = correspondencias[0]
        uuid_code = obter_uuid_disponivel_usuario_exato(username)
        return obter_dados_base_usuario(username, uuid_code=uuid_code)

    if len(correspondencias) > 1:
        return {
            "_erro_busca": (
                "Existe mais de um usuario com esse nome variando maiusculas e minusculas. "
                "Digite exatamente como ele esta cadastrado."
            )
        }

    return None

# =========================================================
# TEXTO DA CONSULTA INDIVIDUAL DO ADMIN
# =========================================================
def montar_texto_consulta_usuario_admin(item, revenda_encontrada=None, sub_encontrada=None, dono_sub=None):
    username = str(item.get("username", "")).strip()
    senha = str(item.get("senha", "")).strip()
    limite = str(item.get("limite", "")).strip()
    uuid = str(item.get("uuid", "")).strip()
    expira_txt = str(item.get("expira_txt", "")).strip() or "Venceu"
    restam_txt = str(item.get("restam_txt", "")).strip() or "0 dias"

    linhas = [
        "📋 <b>Dados Do Usuário</b>",
        "",
        f"• Usuário: <code>{esc(username)}</code>",
        f"• Senha: <code>{esc(senha)}</code>",
        f"• Limite: <code>{esc(limite)}</code>",
        f"• Expira em: <code>{esc(expira_txt)}</code>",
        f"<blockquote>• Restam: {esc(restam_txt)}</blockquote>",
    ]

    if uuid:
        linhas.extend([
            "",
            "UUID:",
            f"<code>{esc(uuid)}</code>"
        ])

    info_extra = []

    if revenda_encontrada:
        info_extra.append(f"Revendedor encontrado: {esc(revenda_encontrada)}")

    if sub_encontrada:
        info_extra.append(f"Sub-revenda encontrada: {esc(sub_encontrada)}")

    if dono_sub:
        info_extra.append(f"Revenda da sub - {esc(dono_sub)}")

    if info_extra:
        linhas.append("")
        linhas.extend(info_extra)

    return "\n".join(linhas)

# =========================================================
# CONSULTA INDIVIDUAL DO ADMIN
# Primeiro puxa dados do sistema, depois descobre se é de revenda/sub
# =========================================================
def receber_consulta_usuario_individual(message):
    if not eh_admin(message.from_user.id):
        return

    if not message.text:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Usuário não encontrado. Digite /menu para tentar novamente."
        )
        return

    termo = message.text.strip()

    try:
        # 1) pega dados reais do sistema primeiro
        item_final = localizar_usuario_geral_por_username_ou_uuid(termo)

        if not item_final:
            bot.send_message(
                message.chat.id,
                "❌ Usuário não encontrado. Digite /menu para tentar novamente."
            )
            return

        if item_final.get("_erro_busca"):
            bot.send_message(
                message.chat.id,
                f"❌ {esc(item_final['_erro_busca'])}"
            )
            return

        username_real = str(item_final.get("username", "")).strip()
        uuid_real = str(item_final.get("uuid", "")).strip()
        consulta_por_uuid = bool(uuid_real) and termo.lower() == uuid_real.lower()

        # 2) agora verifica se ele pertence a revenda/sub
        item_rev, revenda_encontrada = localizar_usuario_nas_revendas(username_real)
        if not item_rev and consulta_por_uuid:
            item_rev, revenda_encontrada = localizar_usuario_nas_revendas(uuid_real)

        item_sub, sub_encontrada, dono_sub = localizar_usuario_nas_subrevendas(username_real)
        if not item_sub and consulta_por_uuid:
            item_sub, sub_encontrada, dono_sub = localizar_usuario_nas_subrevendas(uuid_real)

        texto = montar_texto_consulta_usuario_admin(
            item=item_final,
            revenda_encontrada=revenda_encontrada,
            sub_encontrada=sub_encontrada,
            dono_sub=dono_sub
        )

        bot.send_message(message.chat.id, texto)

    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Erro ao consultar usuário.\n<code>{esc(e)}</code>"
        )
    finally:
        limpar_fluxo(message.from_user.id)

# =========================================================
# OBTER SENHA REAL DO USUÁRIO PELO ARQUIVO DO SISTEMA
# =========================================================
def obter_senha_usuario(username):
    try:
        caminho = os.path.join(SENHAS_DIR, username)
        if not os.path.exists(caminho):
            return ""

        with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()
    except:
        return ""
    
# =========================================================
# OBTER DADOS BASE DO USUÁRIO PELO SISTEMA
# Sempre tenta puxar do sistema primeiro
# =========================================================
def obter_dados_base_usuario(username, uuid_code=""):
    username = str(username or "").strip()

    if not username:
        return None

    try:
        mapa_limites = obter_mapa_limites_sistema()
    except:
        mapa_limites = {}

    limite_txt = str(mapa_limites.get(username, "")).strip()

    try:
        if not limite_txt:
            # fallback case-insensitive
            usuarios_banco = obter_usuarios_do_banco()
            for item in usuarios_banco:
                if str(item.get("username", "")).strip().lower() == username.lower():
                    limite_txt = str(item.get("limit", "")).strip()
                    break
    except:
        pass

    try:
        senha = obter_senha_usuario(username)
    except:
        senha = ""

    try:
        data_expiracao = obter_data_expiracao_usuario(username)
        if data_expiracao:
            expira_txt = data_expiracao.strftime("%d/%m/%Y")
            dias_restantes = (data_expiracao.date() - datetime.now().date()).days
        else:
            expira_txt = "Venceu"
            dias_restantes = 0
    except:
        expira_txt = "Venceu"
        dias_restantes = 0

    if dias_restantes <= 0:
        restam_txt = "0 dias"
    elif dias_restantes == 1:
        restam_txt = "1 dia"
    else:
        restam_txt = f"{dias_restantes} dias"

    return {
        "username": username,
        "senha": senha,
        "limite": limite_txt,
        "expira_txt": expira_txt,
        "restam_txt": restam_txt,
        "uuid": str(uuid_code or "").strip()
    }

# =========================================================
# MINI MENU LISTAR USUÁRIOS (ADMIN)
# =========================================================
def painel_listar_usuarios_admin_markup():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("Meus", callback_data="listar_usuarios_meus"),
        types.InlineKeyboardButton("Todos", callback_data="listar_usuarios_todos")
    )
    kb.add(
        types.InlineKeyboardButton("⬅️ Voltar", callback_data="voltar_painel")
    )
    return kb

# =========================================================
# PEGAR TODOS OS USUÁRIOS DE TODAS AS SUB-REVENDAS
# Lê /root/revenda/dados_sub e monta um set com os usernames
# =========================================================
def obter_usuarios_de_todas_subrevendas():
    usuarios_subrevendas = set()

    for telegram_user in listar_todas_subrevendas():
        try:
            usuarios = ler_usuarios_subrevenda_completos(telegram_user)

            for item in usuarios:
                username = str(item.get("username", "")).strip()
                if username:
                    usuarios_subrevendas.add(username)

        except Exception:
            continue

    return usuarios_subrevendas


def obter_usuarios_bloqueados_admin():
    return obter_usuarios_de_todas_revendas() | obter_usuarios_de_todas_subrevendas()


def obter_uuid_disponivel_usuario_exato(username, mapa_uuids=None):
    username = str(username or "").strip()
    if not username:
        return ""

    try:
        if mapa_uuids is None:
            mapa_uuids = obter_mapa_uuids_disponiveis()

        return str(mapa_uuids.get(username, "")).strip()
    except:
        return ""

# =========================================================
# JUNTAR TODOS OS DADOS DOS USUÁRIOS
# Retorna:
# [
#   {
#     "username": ".",
#     "senha": ".",
#     "limite": "1",
#     "dias": "10",
#     "uuid": "..."
#   }
# ]
# =========================================================
def obter_lista_completa_usuarios():
    usuarios_base = obter_usuarios_do_banco()
    resultado = []
    mapa_uuids = obter_mapa_uuids_disponiveis()

    for item in usuarios_base:
        username = str(item["username"]).strip()
        limite = str(item["limit"]).strip()

        senha = obter_senha_usuario(username)
        expira = calcular_status_expiracao(username)

        if expira == "Venceu":
            dias_txt = "0"
        else:
            dias_txt = expira.replace(" DIAS", "").strip()

        uuid_code = obter_uuid_disponivel_usuario_exato(username, mapa_uuids)

        resultado.append({
            "username": username,
            "senha": senha,
            "limite": limite,
            "dias": dias_txt,
            "uuid": uuid_code
        })

    return resultado

# =========================================================
# PAINEL MAIS FUNÇÕES (ADMIN)
# =========================================================
def painel_mais_funcoes_markup():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("CRIAR BACKUP", callback_data="criar_backup_admin")
    )
    kb.add(
        types.InlineKeyboardButton(texto_botao_auto_backup(), callback_data="toggle_auto_backup")
    )
    kb.add(
        types.InlineKeyboardButton("Teste de velocidade", callback_data="teste_velocidade_admin")
    )
    kb.add(
        types.InlineKeyboardButton("Calcular limite revenda", callback_data="calcular_limite_revenda")
    )
    kb.add(
        types.InlineKeyboardButton(texto_botao_uuid_vencidos(), callback_data="toggle_uuid_expired_mode")
    )
    kb.add(
        types.InlineKeyboardButton(texto_botao_uuid(), callback_data="toggle_uuid_mode")
    )
    kb.add(
        types.InlineKeyboardButton("⬅️ Voltar", callback_data="voltar_painel")
    )
    return kb

# =========================================================
# BACKUP / RESTORE
# =========================================================
BACKUP_ZIP_NAME = "backup_lubu.zip"


def data_futura_para_backup(data_exp):
    if not data_exp:
        return False
    hoje = datetime.now(SP_TZ).date()
    return data_exp.date() > hoje


def dias_ate_data_str(data_str):
    try:
        data = datetime.strptime(str(data_str).strip(), "%d/%m/%Y").date()
        hoje = datetime.now(SP_TZ).date()
        dias = (data - hoje).days
        return dias if dias > 0 else 1
    except:
        return 1


def coletar_usuario_do_sistema_para_backup(username, limite_hint=None, senha_hint=None, uuid_hint=None):
    username = str(username or "").strip()
    if not username:
        return None

    try:
        data_exp = obter_data_expiracao_usuario(username)
    except:
        data_exp = None

    if not data_futura_para_backup(data_exp):
        return None

    try:
        senha = senha_hint if senha_hint else obter_senha_usuario(username)
    except:
        senha = ""

    try:
        if limite_hint is None or str(limite_hint).strip() == "":
            mapa_limites = obter_mapa_limites_sistema()
            limite = str(mapa_limites.get(username, "")).strip()
        else:
            limite = str(limite_hint).strip()
    except:
        limite = str(limite_hint or "").strip()

    try:
        mapa_uuids = obter_mapa_uuids_disponiveis()
        uuid_code = str(uuid_hint).strip() if uuid_hint else obter_uuid_disponivel_usuario_exato(username, mapa_uuids)
    except:
        uuid_code = str(uuid_hint or "").strip()

    expires_at = data_exp.strftime("%d/%m/%Y")
    days = (data_exp.date() - datetime.now(SP_TZ).date()).days
    if days <= 0:
        return None

    return {
        "username": username,
        "password": senha,
        "limit": int(str(limite or "0")),
        "days": int(days),
        "expires_at": expires_at,
        "uuid": uuid_code
    }


def coletar_admin_users_backup():
    usuarios = []
    meus = obter_lista_completa_usuarios_meus()

    for item in meus:
        user = coletar_usuario_do_sistema_para_backup(
            username=item.get("username", ""),
            limite_hint=item.get("limite", ""),
            senha_hint=item.get("senha", ""),
            uuid_hint=item.get("uuid", "")
        )
        if user:
            usuarios.append(user)

    return usuarios


def coletar_revendas_backup():
    resultado = []

    for telegram_rev in listar_todas_revendas():
        try:
            dados = ler_dados_revenda(telegram_rev)

            limit_total = int(str(dados.get("limite_total", "0")).strip() or "0")
            
            registro = {
                "telegram": telegram_rev,
                "limit_total": limit_total,
                "limit_restante": 0,
                "vencimento": str(dados.get("vencimento", "")).strip(),
                "suspenso": bool(revenda_suspensa(telegram_rev)),
                "users": []
            }

            try:
                usuarios_rev = ler_usuarios_revenda_completos(telegram_rev)
            except:
                usuarios_rev = []

            for item in usuarios_rev:
                user = coletar_usuario_do_sistema_para_backup(
                    username=item.get("username", ""),
                    limite_hint=item.get("limite", ""),
                    senha_hint=item.get("senha", ""),
                    uuid_hint=item.get("uuid", "")
                )
                if user:
                    registro["users"].append(user)

            usado_real_backup = sum(int(str(u.get("limit", 0))) for u in registro["users"])
            reservado_sub = calcular_limite_reservado_subrevendas(telegram_rev)
            novo_restante = limit_total - usado_real_backup - reservado_sub
            if novo_restante < 0:
                novo_restante = 0
            registro["limit_restante"] = novo_restante

            resultado.append(registro)

        except:
            continue

    return resultado

def painel_confirmar_restore_backup_markup():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("✅ Confirmar restauração", callback_data="confirmar_restore_backup"))
    kb.add(types.InlineKeyboardButton("⬅️ Cancelar", callback_data="cancelar_restore_backup"))
    return kb

def coletar_subrevendas_backup():
    resultado = []

    for telegram_sub in listar_todas_subrevendas():
        try:
            dados = ler_dados_subrevenda(telegram_sub)

            limit_total = int(str(dados.get("limite_total", "0")).strip() or "0")

            registro = {
                "telegram": telegram_sub,
                "owner": str(dados.get("dono", "")).strip(),
                "limit_total": limit_total,
                "limit_restante": 0,
                "vencimento": str(dados.get("vencimento", "")).strip(),
                "suspenso": bool(subrevenda_suspensa(telegram_sub)),
                "suspenso_por_fornecedor": bool(subrevenda_suspensa_por_fornecedor(telegram_sub)),
                "users": []
            }

            try:
                usuarios_sub = ler_usuarios_subrevenda_completos(telegram_sub)
            except:
                usuarios_sub = []

            for item in usuarios_sub:
                user = coletar_usuario_do_sistema_para_backup(
                    username=item.get("username", ""),
                    limite_hint=item.get("limite", ""),
                    senha_hint=item.get("senha", ""),
                    uuid_hint=item.get("uuid", "")
                )
                if user:
                    registro["users"].append(user)

            usado_real_backup = sum(int(str(u.get("limit", 0))) for u in registro["users"])
            novo_restante = limit_total - usado_real_backup
            if novo_restante < 0:
                novo_restante = 0

            registro["limit_restante"] = novo_restante

            resultado.append(registro)

        except:
            continue

    return resultado


def coletar_xray_clients_backup(payload):
    entries = []

    for item in payload.get("admin_users", []):
        if str(item.get("uuid", "")).strip():
            entries.append({"username": item["username"], "uuid": item["uuid"]})

    for rev in payload.get("resellers", []):
        for item in rev.get("users", []):
            if str(item.get("uuid", "")).strip():
                entries.append({"username": item["username"], "uuid": item["uuid"]})

    for sub_item in payload.get("subresellers", []):
        for item in sub_item.get("users", []):
            if str(item.get("uuid", "")).strip():
                entries.append({"username": item["username"], "uuid": item["uuid"]})

    # remove duplicados
    unico = {}
    for item in entries:
        unico[item["username"]] = item["uuid"]

    return [{"username": k, "uuid": v} for k, v in sorted(unico.items(), key=lambda x: x[0].lower())]


def gerar_backup_payload():
    payload = {
        "created_at": datetime.now(SP_TZ).strftime("%d/%m/%Y %H:%M:%S"),
        "admin_users": coletar_admin_users_backup(),
        "resellers": coletar_revendas_backup(),
        "subresellers": coletar_subrevendas_backup(),
        "tests": coletar_testes_backup()
    }

    return payload


def gerar_backup_zip():
    payload = gerar_backup_payload()
    xray_entries = coletar_xray_clients_backup(payload)

    meta = {
        "backup_name": BACKUP_ZIP_NAME,
        "generated_at": payload["created_at"],
        "counts": {
            "admin_users": len(payload["admin_users"]),
            "resellers": len(payload["resellers"]),
            "subresellers": len(payload["subresellers"]),
            "xray_users": len(xray_entries)
        }
    }

    zip_path = os.path.join(tempfile.gettempdir(), BACKUP_ZIP_NAME)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("backup.json", json.dumps(payload, ensure_ascii=False, indent=2))
        zf.writestr("xray_clients.json", json.dumps(xray_entries, ensure_ascii=False, indent=2))
        zf.writestr("meta.json", json.dumps(meta, ensure_ascii=False, indent=2))

    return zip_path, payload, xray_entries

#bakupe automatico 
def enviar_backup_automatico():
    try:
        if not auto_backup_ativo():
            return

        try:
            sincronizar_revendas_ao_iniciar()
        except:
            pass

        try:
            sincronizar_subrevendas_ao_iniciar()
        except:
            pass

        zip_path, payload, xray_entries = gerar_backup_zip()

        try:
            with open(zip_path, "rb") as f:
                bot.send_document(
                    ADMIN_ID,
                    f,
                    caption=(
                        "♻️ <b>Backup automatico</b>"
                    )
                )
        finally:
            if os.path.exists(zip_path):
                os.remove(zip_path)

    except Exception as e:
        try:
            bot.send_message(
                ADMIN_ID,
                f"❌ Erro no backup automático.\n<code>{esc(e)}</code>"
            )
        except:
            pass
        
def arquivo_parece_backup(file_name):
    return str(file_name or "").strip().lower() == BACKUP_ZIP_NAME.lower()


def carregar_backup_zip(zip_path):
    with zipfile.ZipFile(zip_path, "r") as zf:
        nomes = set(zf.namelist())

        if "backup.json" not in nomes:
            raise Exception("backup.json não encontrado no ZIP.")

        payload = json.loads(zf.read("backup.json").decode("utf-8"))

        if "xray_clients.json" in nomes:
            xray_entries = json.loads(zf.read("xray_clients.json").decode("utf-8"))
        else:
            xray_entries = []

    if not isinstance(payload, dict):
        raise Exception("backup.json inválido.")

    if "admin_users" not in payload or "resellers" not in payload or "subresellers" not in payload:
        raise Exception("Estrutura do backup inválida.")

    return payload, xray_entries


# =========================================================
# CRIAR OU ATUALIZAR USUÁRIO DO BACKUP
# Se o username estiver em xray_entries, cria com --v2ray
# =========================================================
def criar_ou_atualizar_usuario_do_backup(item, mapa_xray=None):
    mapa_xray = mapa_xray or {}

    username = str(item.get("username", "")).strip()
    password = str(item.get("password", "")).strip()
    limit = int(str(item.get("limit", "0")).strip() or "0")
    expires_at = str(item.get("expires_at", "")).strip()

    if not username:
        return {"status": "ignorado", "reason": "username vazio"}

    dias = dias_ate_data_str(expires_at)

    # -----------------------------------------------------
    # O BACKUP DE XRAY É A FONTE DE VERDADE
    # -----------------------------------------------------
    uuid_code = mapa_xray.get(username, "").strip()

    # fallback se por acaso também vier no payload
    if not uuid_code:
        uuid_code = str(item.get("uuid", "")).strip()

    usar_v2ray = bool(uuid_code)

    if not usuario_existe(username):
        criar_usuario_sistema(
            username,
            password,
            limit,
            dias,
            usar_v2ray=usar_v2ray
        )
    else:
        alterar_senha_usuario_sistema(username, password)
        alterar_limite_usuario_sistema(username, limit)
        alterar_data_usuario_sistema(username, dias)

    return {
        "status": "ok",
        "username": username,
        "usar_v2ray": usar_v2ray
    }


def recriar_revenda_do_backup(item):
    telegram_user = str(item.get("telegram", "")).strip()
    if not telegram_user:
        return

    try:
        if revenda_existe(telegram_user):
            try:
                os.remove(caminho_arquivo_revenda(telegram_user))
            except:
                pass
    except:
        pass

    salvar_revenda(
        telegram_user=telegram_user,
        limite_total=int(str(item.get("limit_total", "0")).strip() or "0"),
        limite_restante=int(str(item.get("limit_restante", "0")).strip() or "0"),
        vencimento_formatado=str(item.get("vencimento", "")).strip()
    )

    salvar_campo_revenda(telegram_user, "suspenso", "1" if item.get("suspenso") else "0")


def recriar_subrevenda_do_backup(item):
    telegram_user = str(item.get("telegram", "")).strip()
    dono = str(item.get("owner", "")).strip()
    if not telegram_user:
        return

    try:
        if subrevenda_existe(telegram_user):
            try:
                os.remove(caminho_arquivo_subrevenda(telegram_user))
            except:
                pass
    except:
        pass

    salvar_subrevenda(
        dono=dono,
        telegram_user=telegram_user,
        limite_total=int(str(item.get("limit_total", "0")).strip() or "0"),
        limite_restante=int(str(item.get("limit_restante", "0")).strip() or "0"),
        vencimento_formatado=str(item.get("vencimento", "")).strip()
    )

    salvar_campo_subrevenda(telegram_user, "suspenso", "1" if item.get("suspenso") else "0")
    salvar_campo_subrevenda(
        telegram_user,
        "suspenso_por_fornecedor",
        "1" if item.get("suspenso_por_fornecedor") else "0"
    )


def repopular_usuarios_revenda_do_backup(item):
    telegram_user = str(item.get("telegram", "")).strip()
    for user in item.get("users", []):
        dias = dias_ate_data_str(user.get("expires_at", ""))
        adicionar_usuario_revenda_arquivo(
            telegram_user=telegram_user,
            username=user.get("username", ""),
            senha=user.get("password", ""),
            limite=int(str(user.get("limit", "0")).strip() or "0"),
            dias_restantes=dias,
            uuid_code=user.get("uuid", "")
        )


def repopular_usuarios_subrevenda_do_backup(item):
    telegram_user = str(item.get("telegram", "")).strip()
    for user in item.get("users", []):
        dias = dias_ate_data_str(user.get("expires_at", ""))
        adicionar_usuario_sub_arquivo(
            telegram_user=telegram_user,
            username=user.get("username", ""),
            senha=user.get("password", ""),
            limite=int(str(user.get("limit", "0")).strip() or "0"),
            dias_restantes=dias,
            uuid_code=user.get("uuid", "")
        )


def reiniciar_xray():
    resultado = subprocess.run(
        ["service", "xray", "restart"],
        capture_output=True,
        text=True,
        timeout=25
    )

    if resultado.returncode != 0:
        raise Exception(
            f"service xray restart falhou | "
            f"code={resultado.returncode} | "
            f"stdout={resultado.stdout.strip()} | "
            f"stderr={resultado.stderr.strip()}"
        )


# =========================================================
# CONTROLE DE UUIDS VENCIDOS NO XRAY
# Tudo relacionado a remover/restaurar UUIDs vencidos
# fica centralizado aqui para facilitar manutenção.
# =========================================================
def garantir_arquivo_uuid_exp_mode():
    pasta = os.path.dirname(UUID_EXPIRED_MODE_FILE)
    if pasta:
        os.makedirs(pasta, exist_ok=True)

    if not os.path.exists(UUID_EXPIRED_MODE_FILE):
        with open(UUID_EXPIRED_MODE_FILE, "w", encoding="utf-8") as f:
            f.write("0")


def garantir_arquivo_uuid_exp():
    pasta = os.path.dirname(UUID_EXPIRED_FILE)
    if pasta:
        os.makedirs(pasta, exist_ok=True)

    if not os.path.exists(UUID_EXPIRED_FILE):
        with open(UUID_EXPIRED_FILE, "w", encoding="utf-8") as f:
            pass


def uuid_expired_mode_ativo():
    garantir_arquivo_uuid_exp_mode()
    try:
        with open(UUID_EXPIRED_MODE_FILE, "r", encoding="utf-8") as f:
            return f.read().strip() == "1"
    except:
        return False


def definir_uuid_expired_mode(ativo):
    garantir_arquivo_uuid_exp_mode()
    with open(UUID_EXPIRED_MODE_FILE, "w", encoding="utf-8") as f:
        f.write("1" if ativo else "0")


def texto_botao_uuid_vencidos():
    return "Desativar UUID vencidos" if uuid_expired_mode_ativo() else "Ativar UUID vencidos"


def ler_uuid_expirados():
    garantir_arquivo_uuid_exp()
    registros = {}

    with uuid_exp_lock:
        with open(UUID_EXPIRED_FILE, "r", encoding="utf-8", errors="ignore") as f:
            for linha in f:
                linha = linha.strip()
                if not linha:
                    continue

                partes = linha.split("|")
                if len(partes) < 2:
                    continue

                username = partes[0].strip()
                uuid_code = partes[1].strip()

                if username and uuid_code:
                    registros[username.lower()] = {
                        "username": username,
                        "uuid": uuid_code
                    }

    return sorted(registros.values(), key=lambda x: x["username"].lower())


def salvar_uuid_expirados(registros):
    garantir_arquivo_uuid_exp()
    unicos = {}

    for item in registros or []:
        username = str(item.get("username", "")).strip()
        uuid_code = str(item.get("uuid", "")).strip()

        if username and uuid_code:
            unicos[username.lower()] = {
                "username": username,
                "uuid": uuid_code
            }

    ordenados = sorted(unicos.values(), key=lambda x: x["username"].lower())

    with uuid_exp_lock:
        with open(UUID_EXPIRED_FILE, "w", encoding="utf-8") as f:
            for item in ordenados:
                f.write(f"{item['username']}|{item['uuid']}\n")

    return ordenados


def remover_usuarios_uuid_expirados(usernames):
    usernames_validos = {
        str(username).strip().lower()
        for username in (usernames or [])
        if str(username).strip()
    }
    if not usernames_validos:
        return 0

    registros_atuais = ler_uuid_expirados()
    if not registros_atuais:
        return 0

    registros_filtrados = [
        item for item in registros_atuais
        if str(item.get("username", "")).strip().lower() not in usernames_validos
    ]

    removidos = len(registros_atuais) - len(registros_filtrados)
    if removidos > 0:
        salvar_uuid_expirados(registros_filtrados)

    return removidos


def remover_usuario_uuid_expirado(username):
    return remover_usuarios_uuid_expirados([username])


# Mantem a limpeza do uuid_exp.txt junto da central de UUIDs vencidos,
# para valer automaticamente no admin, revenda e sub.
def deletar_usuario_sistema(username):
    comando = [
        "/opt/sshplus/plugin-sync",
        "-h",
        "--del-user",
        username
    ]

    resultado = subprocess.run(
        comando,
        capture_output=True,
        text=True,
        timeout=20
    )

    if resultado.returncode != 0:
        erro = (resultado.stderr or resultado.stdout or "Erro ao deletar usuÃ¡rio").strip()
        raise Exception(erro)

    try:
        remover_usuarios_uuid_expirados([username])
    except:
        pass


def obter_mapa_uuids_suspensos():
    return {
        str(item.get("username", "")).strip(): str(item.get("uuid", "")).strip()
        for item in ler_uuid_expirados()
        if str(item.get("username", "")).strip() and str(item.get("uuid", "")).strip()
    }


def obter_mapa_uuids_disponiveis():
    mapa = {}

    for username, uuid_code in obter_mapa_uuids_suspensos().items():
        mapa[username] = uuid_code

    for username, uuid_code in obter_mapa_uuids_xray().items():
        mapa[username] = uuid_code

    return mapa


def obter_uuid_disponivel_usuario(username, mapa_uuids=None):
    username = str(username or "").strip()
    if not username:
        return ""

    try:
        if mapa_uuids is None:
            mapa_uuids = obter_mapa_uuids_disponiveis()

        uuid_code = str(mapa_uuids.get(username, "")).strip()
        if uuid_code:
            return uuid_code

        username_lower = username.lower()
        for email, uuid_code in mapa_uuids.items():
            if str(email).strip().lower() == username_lower:
                return str(uuid_code).strip()
    except:
        pass

    return ""


def obter_inbounds_xray_compativeis(data):
    inbounds = data.get("inbounds", [])
    if not isinstance(inbounds, list):
        raise Exception("config.json inválido: inbounds ausente.")

    target_inbounds = [
        x for x in inbounds
        if str(x.get("tag", "")).strip() == "inbound-sshplus"
    ]

    if not target_inbounds:
        target_inbounds = [
            x for x in inbounds
            if isinstance(x.get("settings", {}).get("clients", None), list)
        ]

    if not target_inbounds:
        raise Exception("Nenhum inbound compatível com clients foi encontrado no config.json.")

    return target_inbounds


def salvar_config_xray(data):
    with open(XRAY_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def sincronizar_clientes_xray(remover_usernames=None, upsert_entries=None):
    remover_set = {
        str(username).strip()
        for username in (remover_usernames or [])
        if str(username).strip()
    }

    upsert_map = {}
    for item in upsert_entries or []:
        username = str(item.get("username", "")).strip()
        uuid_code = str(item.get("uuid", "")).strip()
        if username and uuid_code:
            upsert_map[username] = uuid_code

    if not remover_set and not upsert_map:
        return {"removed": 0, "updated": 0, "added": 0, "changed": False}

    if not os.path.exists(XRAY_CONFIG_FILE):
        raise Exception(f"Arquivo não encontrado: {XRAY_CONFIG_FILE}")

    backup_cfg = XRAY_CONFIG_FILE + ".bak_uuid_monitor"

    with xray_config_lock:
        shutil.copy2(XRAY_CONFIG_FILE, backup_cfg)

        try:
            with open(XRAY_CONFIG_FILE, "r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)

            target_inbounds = obter_inbounds_xray_compativeis(data)

            def remover_usuario_dos_clients(username):
                removeu = False

                for inbound in target_inbounds:
                    settings = inbound.get("settings", {})
                    clients = settings.get("clients", [])
                    if not isinstance(clients, list):
                        continue

                    novos_clients = []
                    for client in clients:
                        if not isinstance(client, dict):
                            novos_clients.append(client)
                            continue

                        email = str(client.get("email", "")).strip()
                        if email == username:
                            removeu = True
                            continue

                        novos_clients.append(client)

                    settings["clients"] = novos_clients

                return removeu

            def localizar_ocorrencias(username):
                ocorrencias = []

                for inbound in target_inbounds:
                    settings = inbound.get("settings", {})
                    clients = settings.get("clients", [])
                    if not isinstance(clients, list):
                        continue

                    for client in clients:
                        if not isinstance(client, dict):
                            continue

                        email = str(client.get("email", "")).strip()
                        if email == username:
                            ocorrencias.append(client)

                return ocorrencias

            removed = 0
            updated = 0
            added = 0

            for username in sorted(remover_set):
                if remover_usuario_dos_clients(username):
                    removed += 1

            for username, uuid_code in sorted(upsert_map.items(), key=lambda x: x[0].lower()):
                ocorrencias = localizar_ocorrencias(username)

                if len(ocorrencias) == 1:
                    client = ocorrencias[0]
                    uuid_atual = str(client.get("id", "")).strip()
                    try:
                        level_atual = int(str(client.get("level", 0)).strip())
                    except:
                        level_atual = client.get("level", 0)

                    if uuid_atual == uuid_code and level_atual == 0:
                        continue

                existed_before = bool(ocorrencias)

                if existed_before:
                    remover_usuario_dos_clients(username)

                settings_alvo = target_inbounds[0].setdefault("settings", {})
                clients_alvo = settings_alvo.get("clients")

                if not isinstance(clients_alvo, list):
                    raise Exception("Inbound alvo do XRay sem lista válida de clients.")

                clients_alvo.append({
                    "email": username,
                    "id": uuid_code,
                    "level": 0
                })

                if existed_before:
                    updated += 1
                else:
                    added += 1

            changed = bool(removed or updated or added)

            if changed:
                salvar_config_xray(data)
                reiniciar_xray()

            return {
                "removed": removed,
                "updated": updated,
                "added": added,
                "changed": changed
            }

        except Exception:
            shutil.copy2(backup_cfg, XRAY_CONFIG_FILE)
            try:
                reiniciar_xray()
            except:
                pass
            raise
        finally:
            try:
                if os.path.exists(backup_cfg):
                    os.remove(backup_cfg)
            except:
                pass


def remover_uuids_xray(usernames):
    return sincronizar_clientes_xray(remover_usernames=usernames)


def upsert_uuids_xray(entries):
    return sincronizar_clientes_xray(upsert_entries=entries)


def adicionar_usuario_uuid_monitorado(destino, username, uuid_code, origem):
    username = str(username or "").strip()
    uuid_code = str(uuid_code or "").strip()

    if not username or not uuid_code:
        return

    chave = username.lower()
    if chave not in destino:
        destino[chave] = {
            "username": username,
            "uuid": uuid_code,
            "origem": origem
        }


def coletar_usuarios_uuid_monitorados():
    usuarios = {}
    mapa_uuids = obter_mapa_uuids_disponiveis()
    usernames_revendas = set()
    usernames_subrevendas = set()

    try:
        for telegram_revenda in listar_todas_revendas():
            try:
                usuarios_rev = ler_usuarios_revenda_completos(telegram_revenda)
            except:
                usuarios_rev = []

            for item in usuarios_rev:
                username = str(item.get("username", "")).strip()
                uuid_code = str(item.get("uuid", "")).strip() or obter_uuid_disponivel_usuario(username, mapa_uuids)

                if username:
                    usernames_revendas.add(username.lower())

                adicionar_usuario_uuid_monitorado(usuarios, username, uuid_code, "revenda")
    except:
        pass

    try:
        for telegram_sub in listar_todas_subrevendas():
            try:
                usuarios_sub = ler_usuarios_subrevenda_completos(telegram_sub)
            except:
                usuarios_sub = []

            for item in usuarios_sub:
                username = str(item.get("username", "")).strip()
                uuid_code = str(item.get("uuid", "")).strip() or obter_uuid_disponivel_usuario(username, mapa_uuids)

                if username:
                    usernames_subrevendas.add(username.lower())

                adicionar_usuario_uuid_monitorado(usuarios, username, uuid_code, "subrevenda")
    except:
        pass

    bloqueados = usernames_revendas | usernames_subrevendas

    try:
        for item in obter_usuarios_do_banco():
            username = str(item.get("username", "")).strip()
            if not username or username.lower() in bloqueados:
                continue

            uuid_code = obter_uuid_disponivel_usuario(username, mapa_uuids)
            adicionar_usuario_uuid_monitorado(usuarios, username, uuid_code, "admin")
    except:
        pass

    return sorted(usuarios.values(), key=lambda x: x["username"].lower())


def coletar_usuarios_uuid_paineis_suspensos():
    usuarios = {}
    mapa_uuids = obter_mapa_uuids_disponiveis()

    try:
        for telegram_revenda in listar_todas_revendas():
            try:
                if not revenda_suspensa(telegram_revenda):
                    continue

                usuarios_rev = ler_usuarios_revenda_completos(telegram_revenda)
            except:
                usuarios_rev = []

            for item in usuarios_rev:
                username = str(item.get("username", "")).strip()
                uuid_code = str(item.get("uuid", "")).strip() or obter_uuid_disponivel_usuario(username, mapa_uuids)
                adicionar_usuario_uuid_monitorado(usuarios, username, uuid_code, "revenda_suspensa")
    except:
        pass

    try:
        for telegram_sub in listar_todas_subrevendas():
            try:
                if not subrevenda_suspensa(telegram_sub):
                    continue

                usuarios_sub = ler_usuarios_subrevenda_completos(telegram_sub)
            except:
                usuarios_sub = []

            for item in usuarios_sub:
                username = str(item.get("username", "")).strip()
                uuid_code = str(item.get("uuid", "")).strip() or obter_uuid_disponivel_usuario(username, mapa_uuids)
                adicionar_usuario_uuid_monitorado(usuarios, username, uuid_code, "subrevenda_suspensa")
    except:
        pass

    return sorted(usuarios.values(), key=lambda x: x["username"].lower())


def obter_set_usernames_paineis_suspensos():
    return {
        str(item.get("username", "")).strip().lower()
        for item in coletar_usuarios_uuid_paineis_suspensos()
        if str(item.get("username", "")).strip()
    }


def obter_set_usuarios_existentes():
    return {str(username).strip().lower() for username in listar_usuarios() if str(username).strip()}


def processar_uuid_vencidos_xray():
    with uuid_monitor_lock:
        if not uuid_expired_mode_ativo():
            return {
                "analisados": 0,
                "expirados": 0,
                "novos_txt": 0,
                "removidos_xray": 0,
                "mudou": False
            }

        hoje = datetime.now(SP_TZ).date()
        usuarios = coletar_usuarios_uuid_monitorados()
        expirados = []

        for item in usuarios:
            username = str(item.get("username", "")).strip()
            uuid_code = str(item.get("uuid", "")).strip()

            if not username or not uuid_code:
                continue

            try:
                data_exp = obter_data_expiracao_usuario(username)
            except Exception:
                continue

            if not data_exp or data_exp.date() <= hoje:
                expirados.append({
                    "username": username,
                    "uuid": uuid_code
                })

        if not expirados:
            return {
                "analisados": len(usuarios),
                "expirados": 0,
                "novos_txt": 0,
                "removidos_xray": 0,
                "mudou": False
            }

        registros_atuais = ler_uuid_expirados()
        mapa_registros = {
            str(item.get("username", "")).strip().lower(): {
                "username": str(item.get("username", "")).strip(),
                "uuid": str(item.get("uuid", "")).strip()
            }
            for item in registros_atuais
            if str(item.get("username", "")).strip() and str(item.get("uuid", "")).strip()
        }

        novos_txt = 0
        for item in expirados:
            chave = item["username"].lower()
            anterior = mapa_registros.get(chave)
            if not anterior or anterior.get("uuid") != item["uuid"]:
                novos_txt += 1
            mapa_registros[chave] = item

        resumo_xray = remover_uuids_xray([item["username"] for item in expirados])

        try:
            salvar_uuid_expirados(list(mapa_registros.values()))
        except Exception:
            try:
                upsert_uuids_xray(expirados)
            except:
                pass
            raise

        return {
            "analisados": len(usuarios),
            "expirados": len(expirados),
            "novos_txt": novos_txt,
            "removidos_xray": resumo_xray["removed"],
            "mudou": bool(novos_txt or resumo_xray["changed"])
        }


def processar_uuid_paineis_suspensos_xray():
    with uuid_monitor_lock:
        if not uuid_expired_mode_ativo():
            return {
                "analisados": 0,
                "suspensos": 0,
                "novos_txt": 0,
                "removidos_xray": 0,
                "mudou": False
            }

        usuarios_suspensos = coletar_usuarios_uuid_paineis_suspensos()
        if not usuarios_suspensos:
            return {
                "analisados": 0,
                "suspensos": 0,
                "novos_txt": 0,
                "removidos_xray": 0,
                "mudou": False
            }

        registros_atuais = ler_uuid_expirados()
        mapa_registros = {
            str(item.get("username", "")).strip().lower(): {
                "username": str(item.get("username", "")).strip(),
                "uuid": str(item.get("uuid", "")).strip()
            }
            for item in registros_atuais
            if str(item.get("username", "")).strip() and str(item.get("uuid", "")).strip()
        }

        novos_txt = 0
        for item in usuarios_suspensos:
            chave = item["username"].lower()
            anterior = mapa_registros.get(chave)
            if not anterior or anterior.get("uuid") != item["uuid"]:
                novos_txt += 1
            mapa_registros[chave] = {
                "username": item["username"],
                "uuid": item["uuid"]
            }

        resumo_xray = remover_uuids_xray([item["username"] for item in usuarios_suspensos])

        try:
            salvar_uuid_expirados(list(mapa_registros.values()))
        except Exception:
            try:
                upsert_uuids_xray(usuarios_suspensos)
            except:
                pass
            raise

        return {
            "analisados": len(usuarios_suspensos),
            "suspensos": len(usuarios_suspensos),
            "novos_txt": novos_txt,
            "removidos_xray": resumo_xray["removed"],
            "mudou": bool(novos_txt or resumo_xray["changed"])
        }


def processar_reativacao_uuid_suspensos_xray():
    with uuid_monitor_lock:
        registros = ler_uuid_expirados()
        if not registros:
            return {
                "analisados": 0,
                "reativados": 0,
                "removidos_txt": 0,
                "mudou": False
            }

        hoje = datetime.now(SP_TZ).date()
        manter = []
        reativar = []

        try:
            usuarios_existentes = obter_set_usuarios_existentes()
        except Exception:
            usuarios_existentes = None

        try:
            usuarios_paineis_suspensos = obter_set_usernames_paineis_suspensos()
        except Exception:
            usuarios_paineis_suspensos = set()

        for item in registros:
            username = str(item.get("username", "")).strip()
            uuid_code = str(item.get("uuid", "")).strip()

            if not username or not uuid_code:
                continue

            if usuarios_existentes is None:
                manter.append(item)
                continue

            if username.lower() not in usuarios_existentes:
                continue

            if username.lower() in usuarios_paineis_suspensos:
                manter.append(item)
                continue

            try:
                data_exp = obter_data_expiracao_usuario(username)
            except Exception:
                manter.append(item)
                continue

            if data_exp and data_exp.date() > hoje:
                reativar.append({
                    "username": username,
                    "uuid": uuid_code
                })
            else:
                manter.append(item)

        if reativar:
            upsert_uuids_xray(reativar)

        removidos_txt = len(registros) - len(manter)
        if removidos_txt > 0:
            salvar_uuid_expirados(manter)

        return {
            "analisados": len(registros),
            "reativados": len(reativar),
            "removidos_txt": removidos_txt,
            "mudou": bool(reativar or removidos_txt)
        }


def restaurar_todos_uuid_suspensos_xray():
    with uuid_monitor_lock:
        registros = ler_uuid_expirados()
        if not registros:
            return {"restaurados": 0, "limpos_txt": 0}

        try:
            usuarios_existentes = obter_set_usuarios_existentes()
        except Exception:
            usuarios_existentes = None

        candidatos = []
        for item in registros:
            username = str(item.get("username", "")).strip()
            if not username:
                continue

            if usuarios_existentes is None or username.lower() in usuarios_existentes:
                candidatos.append(item)

        if candidatos:
            upsert_uuids_xray(candidatos)

        salvar_uuid_expirados([])
        return {
            "restaurados": len(candidatos),
            "limpos_txt": len(registros)
        }


def sincronizar_uuid_vencidos_xray_agora():
    return {
        "expirados": processar_uuid_vencidos_xray(),
        "paineis_suspensos": processar_uuid_paineis_suspensos_xray(),
        "reativacao": processar_reativacao_uuid_suspensos_xray()
    }


def monitor_uuid_vencidos_xray():
    ultimo_processamento_diario = ""

    while True:
        try:
            garantir_arquivo_uuid_exp_mode()
            garantir_arquivo_uuid_exp()

            if uuid_expired_mode_ativo():
                agora = datetime.now(SP_TZ)
                data_chave = agora.strftime("%d/%m/%Y")
                hora_minuto = agora.strftime("%H:%M")

                if hora_minuto == "00:10" and ultimo_processamento_diario != data_chave:
                    resumo_expirados = processar_uuid_vencidos_xray()
                    ultimo_processamento_diario = data_chave

                    print(
                        "[UUID XRAY - DIARIO] "
                        f"executado_em={agora.strftime('%d/%m/%Y %H:%M:%S')} | "
                        f"analisados={resumo_expirados['analisados']} | "
                        f"expirados={resumo_expirados['expirados']} | "
                        f"removidos_xray={resumo_expirados['removidos_xray']} | "
                        f"novos_txt={resumo_expirados['novos_txt']}"
                    )

                resumo_paineis = processar_uuid_paineis_suspensos_xray()
                if resumo_paineis["mudou"]:
                    print(
                        "[UUID XRAY - PAINEIS SUSPENSOS] "
                        f"executado_em={datetime.now(SP_TZ).strftime('%d/%m/%Y %H:%M:%S')} | "
                        f"suspensos={resumo_paineis['suspensos']} | "
                        f"removidos_xray={resumo_paineis['removidos_xray']} | "
                        f"novos_txt={resumo_paineis['novos_txt']}"
                    )

                resumo_reativacao = processar_reativacao_uuid_suspensos_xray()
                if resumo_reativacao["mudou"]:
                    print(
                        "[UUID XRAY - REATIVACAO] "
                        f"executado_em={datetime.now(SP_TZ).strftime('%d/%m/%Y %H:%M:%S')} | "
                        f"analisados={resumo_reativacao['analisados']} | "
                        f"reativados={resumo_reativacao['reativados']} | "
                        f"removidos_txt={resumo_reativacao['removidos_txt']}"
                    )

            time.sleep(UUID_EXPIRED_MONITOR_INTERVAL)

        except Exception as e:
            print(f"[ERRO MONITOR UUID XRAY] {e}")

            try:
                bot.send_message(
                    ADMIN_ID,
                    f"❌ Erro no monitor de UUID vencidos do XRay.\n<code>{esc(e)}</code>"
                )
            except:
                pass

            time.sleep(60)


def iniciar_monitor_uuid_vencidos_xray():
    garantir_arquivo_uuid_exp_mode()
    garantir_arquivo_uuid_exp()

    if uuid_expired_mode_ativo():
        try:
            sincronizar_uuid_vencidos_xray_agora()
        except Exception as e:
            print(f"[ERRO UUID XRAY AO INICIAR] {e}")
            try:
                bot.send_message(
                    ADMIN_ID,
                    f"❌ Erro ao sincronizar UUID vencidos na inicialização.\n<code>{esc(e)}</code>"
                )
            except:
                pass

    t = threading.Thread(target=monitor_uuid_vencidos_xray, daemon=True)
    t.start()


def _aplicar_uuids_backup_no_xray_legado(xray_entries):
    if not xray_entries:
        return {"updated": 0, "added": 0}

    if not os.path.exists(XRAY_CONFIG_FILE):
        raise Exception(f"Arquivo não encontrado: {XRAY_CONFIG_FILE}")

    backup_cfg = XRAY_CONFIG_FILE + ".bak_before_restore"
    shutil.copy2(XRAY_CONFIG_FILE, backup_cfg)

    try:
        with open(XRAY_CONFIG_FILE, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)

        inbounds = data.get("inbounds", [])
        if not isinstance(inbounds, list):
            raise Exception("config.json inválido: inbounds ausente.")

        target_inbounds = [
            x for x in inbounds
            if str(x.get("tag", "")).strip() == "inbound-sshplus"
        ]
        if not target_inbounds:
            target_inbounds = [
                x for x in inbounds
                if isinstance(x.get("settings", {}).get("clients", None), list)
            ]

        if not target_inbounds:
            raise Exception("Nenhum inbound compatível com clients foi encontrado no config.json.")

        # remove duplicatas dos usuários presentes no backup
        backup_usernames = {
            str(x.get("username", "")).strip()
            for x in xray_entries
            if str(x.get("username", "")).strip()
        }

        for inbound in target_inbounds:
            settings = inbound.get("settings", {})
            clients = settings.get("clients", [])

            if not isinstance(clients, list):
                continue

            novos_clients = []
            vistos = set()

            for client in clients:
                if not isinstance(client, dict):
                    continue

                email = str(client.get("email", "")).strip()

                if email in backup_usernames:
                    if email in vistos:
                        continue
                    vistos.add(email)
                    novos_clients.append(client)
                else:
                    novos_clients.append(client)

            settings["clients"] = novos_clients

        updated = 0
        added = 0

        for entry in xray_entries:
            username = str(entry.get("username", "")).strip()
            uuid_code = str(entry.get("uuid", "")).strip()

            if not username or not uuid_code:
                continue

            achou = False

            for inbound in target_inbounds:
                settings = inbound.get("settings", {})
                clients = settings.get("clients", [])

                if not isinstance(clients, list):
                    continue

                for client in clients:
                    if not isinstance(client, dict):
                        continue

                    if str(client.get("email", "")).strip() == username:
                        client["id"] = uuid_code
                        achou = True
                        updated += 1
                        break

                if achou:
                    break

            if not achou:
                inseriu = False

                for inbound in target_inbounds:
                    settings = inbound.get("settings", {})
                    clients = settings.get("clients", [])

                    if isinstance(clients, list):
                        clients.append({
                            "id": uuid_code,
                            "email": username,
                            "level": 0
                        })
                        inseriu = True
                        added += 1
                        break

                if not inseriu:
                    raise Exception("Nenhum inbound compatível com clients foi encontrado no config.json.")

        with open(XRAY_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        reiniciar_xray()
        return {"updated": updated, "added": added}

    except Exception:
        shutil.copy2(backup_cfg, XRAY_CONFIG_FILE)
        try:
            reiniciar_xray()
        except:
            pass
        raise

def aplicar_uuids_backup_no_xray(xray_entries):
    if not xray_entries:
        return {"updated": 0, "added": 0, "applied": 0, "changed": False}

    resumo = upsert_uuids_xray(xray_entries)
    total_aplicado = resumo["updated"] + resumo["added"]
    return {
        "updated": total_aplicado,
        "added": resumo["added"],
        "applied": total_aplicado,
        "changed": resumo["changed"]
    }

# =========================================================
# MAPA DE USUÁRIOS XRAY DO BACKUP
# username -> uuid
# =========================================================
def montar_mapa_xray_backup(xray_entries):
    mapa = {}

    for item in xray_entries or []:
        username = str(item.get("username", "")).strip()
        uuid_code = str(item.get("uuid", "")).strip()

        if username and uuid_code:
            mapa[username] = uuid_code

    return mapa

def restaurar_backup_payload(payload, xray_entries, atualizar_status=None):
    garantir_pasta_revendas()
    garantir_pasta_subrevendas()

    resumo = {
        "users_ok": 0,
        "users_fail": [],
        "structure_fail": [],
        "resellers": 0,
        "subresellers": 0,
        "xray_updated": 0,
        "xray_added": 0,
        "xray_applied": 0,
        "xray_removed_policy": 0,
        "xray_error": "",
        "tests_restored": 0,
        "suspensos_reaplicados": 0
    }

    def status(texto):
        if atualizar_status:
            try:
                atualizar_status(texto)
            except:
                pass

    # -----------------------------------------------------
    # 0) MAPA XRAY
    # -----------------------------------------------------
    mapa_xray = montar_mapa_xray_backup(xray_entries)

    # -----------------------------------------------------
    # 1) ESTRUTURA
    # -----------------------------------------------------
    status("⏳ <b>Estruturando backup...</b>")

    for item in payload.get("resellers", []):
        try:
            recriar_revenda_do_backup(item)
            resumo["resellers"] += 1
        except Exception as e:
            resumo["structure_fail"].append(f"Revenda {item.get('telegram', '')}: {e}")

    for item in payload.get("subresellers", []):
        try:
            recriar_subrevenda_do_backup(item)
            resumo["subresellers"] += 1
        except Exception as e:
            resumo["structure_fail"].append(f"Sub-revenda {item.get('telegram', '')}: {e}")

    # -----------------------------------------------------
    # 2) REUNIR USUÁRIOS
    # -----------------------------------------------------
    todos = []
    todos.extend(payload.get("admin_users", []))

    for item in payload.get("resellers", []):
        todos.extend(item.get("users", []))

    for item in payload.get("subresellers", []):
        todos.extend(item.get("users", []))

    unicos = {}
    for item in todos:
        username = str(item.get("username", "")).strip()
        if username:
            unicos[username] = item

    lista_usuarios = list(unicos.values())
    total_usuarios = len(lista_usuarios)

    # -----------------------------------------------------
    # 3) CRIAR/ATUALIZAR USUÁRIOS
    # -----------------------------------------------------
    ultimo_update = 0

    for i, item in enumerate(lista_usuarios, start=1):
        try:
            criar_ou_atualizar_usuario_do_backup(item, mapa_xray=mapa_xray)
            resumo["users_ok"] += 1
        except Exception as e:
            resumo["users_fail"].append(f"{item.get('username', '')}: {e}")

        if total_usuarios > 0:
            percentual = int((i / total_usuarios) * 100)

            if percentual >= ultimo_update + 3 or i == 1 or i == total_usuarios:
                ultimo_update = percentual
                status(
                    "👤 <b>Criando usuários...</b>\n\n"
                    f"<b>Progresso:</b> {percentual}%\n"
                    f"<b>Processados:</b> {i}/{total_usuarios}"
                )

    # -----------------------------------------------------
    # 4) BANCO LOCAL
    # -----------------------------------------------------
    status("📦 <b>Organizando bancos locais...</b>")

    for item in payload.get("resellers", []):
        try:
            repopular_usuarios_revenda_do_backup(item)
        except Exception as e:
            resumo["structure_fail"].append(f"Usuários revenda {item.get('telegram', '')}: {e}")

    for item in payload.get("subresellers", []):
        try:
            repopular_usuarios_subrevenda_do_backup(item)
        except Exception as e:
            resumo["structure_fail"].append(f"Usuários sub-revenda {item.get('telegram', '')}: {e}")

    try:
        testes = payload.get("tests", [])
        if isinstance(testes, list):
            resumo["tests_restored"] = restaurar_testes_do_backup(testes)
    except Exception as e:
        resumo["structure_fail"].append(f"Testes: {e}")

    try:
        resumo["suspensos_reaplicados"] = reaplicar_suspensoes_do_backup(payload)
    except Exception as e:
        resumo["structure_fail"].append(f"Suspensões: {e}")

    # -----------------------------------------------------
    # 5) UUID / XRAY
    # -----------------------------------------------------
    try:
        status("🆔 <b>Organizando UUID...</b>")
        xr = aplicar_uuids_backup_no_xray(xray_entries)
        resumo["xray_updated"] = xr.get("updated", 0)
        resumo["xray_added"] = xr.get("added", 0)

        status("🔄 <b>Reiniciando Xray...</b>")
        reiniciar_xray()

    except Exception as e:
        resumo["xray_error"] = str(e)

    return resumo

    # -----------------------------------------------------
    # 4) REPOVOA OS ARQUIVOS LOCAIS
    # -----------------------------------------------------
    status("📦 <b>Organizando bancos locais...</b>")

    for item in payload.get("resellers", []):
        try:
            repopular_usuarios_revenda_do_backup(item)
        except Exception as e:
            resumo["structure_fail"].append(f"Usuários revenda {item.get('telegram', '')}: {e}")

    for item in payload.get("subresellers", []):
        try:
            repopular_usuarios_subrevenda_do_backup(item)
        except Exception as e:
            resumo["structure_fail"].append(f"Usuários sub-revenda {item.get('telegram', '')}: {e}")

    # -----------------------------------------------------
    # 5) RESTAURA TESTES
    # -----------------------------------------------------
    try:
        testes = payload.get("tests", [])
        if isinstance(testes, list):
            resumo["tests_restored"] = restaurar_testes_do_backup(testes)
    except Exception as e:
        resumo["structure_fail"].append(f"Testes: {e}")

    # -----------------------------------------------------
    # 6) REAPLICA SUSPENSÕES DE PAINEL
    # -----------------------------------------------------
    try:
        resumo["suspensos_reaplicados"] = reaplicar_suspensoes_do_backup(payload)
    except Exception as e:
        resumo["structure_fail"].append(f"Suspensões: {e}")

    # -----------------------------------------------------
    # 7) CORRIGE UUIDS NO XRAY
    # -----------------------------------------------------
    try:
        status("🆔 <b>Organizando UUID...</b>")
        xr = aplicar_uuids_backup_no_xray(xray_entries)
        resumo["xray_updated"] = xr.get("updated", 0)
        resumo["xray_added"] = xr.get("added", 0)

        status("🔄 <b>Reiniciando Xray...</b>")
        reiniciar_xray()

    except Exception as e:
        resumo["xray_error"] = str(e)

    return resumo

# =========================================================
# RESTAURAÇÃO DE BACKUP VIA DOCUMENTO
# Só admin pode usar
# =========================================================
def restaurar_backup_payload(payload, xray_entries, atualizar_status=None):
    garantir_pasta_revendas()
    garantir_pasta_subrevendas()

    resumo = {
        "users_ok": 0,
        "users_fail": [],
        "structure_fail": [],
        "resellers": 0,
        "subresellers": 0,
        "xray_updated": 0,
        "xray_added": 0,
        "xray_applied": 0,
        "xray_removed_policy": 0,
        "xray_error": "",
        "tests_restored": 0,
        "suspensos_reaplicados": 0
    }

    def status(texto):
        if atualizar_status:
            try:
                atualizar_status(texto)
            except:
                pass

    mapa_xray = montar_mapa_xray_backup(xray_entries)

    status("⏳ <b>Estruturando backup...</b>")

    for item in payload.get("resellers", []):
        try:
            recriar_revenda_do_backup(item)
            resumo["resellers"] += 1
        except Exception as e:
            resumo["structure_fail"].append(f"Revenda {item.get('telegram', '')}: {e}")

    for item in payload.get("subresellers", []):
        try:
            recriar_subrevenda_do_backup(item)
            resumo["subresellers"] += 1
        except Exception as e:
            resumo["structure_fail"].append(f"Sub-revenda {item.get('telegram', '')}: {e}")

    todos = []
    todos.extend(payload.get("admin_users", []))

    for item in payload.get("resellers", []):
        todos.extend(item.get("users", []))

    for item in payload.get("subresellers", []):
        todos.extend(item.get("users", []))

    unicos = {}
    for item in todos:
        username = str(item.get("username", "")).strip()
        if username:
            unicos[username] = item

    lista_usuarios = list(unicos.values())
    total_usuarios = len(lista_usuarios)
    ultimo_update = 0

    for i, item in enumerate(lista_usuarios, start=1):
        try:
            criar_ou_atualizar_usuario_do_backup(item, mapa_xray=mapa_xray)
            resumo["users_ok"] += 1
        except Exception as e:
            resumo["users_fail"].append(f"{item.get('username', '')}: {e}")

        if total_usuarios > 0:
            percentual = int((i / total_usuarios) * 100)

            if percentual >= ultimo_update + 3 or i == 1 or i == total_usuarios:
                ultimo_update = percentual
                status(
                    "👤 <b>Criando usuários...</b>\n\n"
                    f"<b>Progresso:</b> {percentual}%\n"
                    f"<b>Processados:</b> {i}/{total_usuarios}"
                )

    status("📦 <b>Organizando bancos locais...</b>")

    for item in payload.get("resellers", []):
        try:
            repopular_usuarios_revenda_do_backup(item)
        except Exception as e:
            resumo["structure_fail"].append(f"Usuários revenda {item.get('telegram', '')}: {e}")

    for item in payload.get("subresellers", []):
        try:
            repopular_usuarios_subrevenda_do_backup(item)
        except Exception as e:
            resumo["structure_fail"].append(f"Usuários sub-revenda {item.get('telegram', '')}: {e}")

    try:
        testes = payload.get("tests", [])
        if isinstance(testes, list):
            resumo["tests_restored"] = restaurar_testes_do_backup(testes)
    except Exception as e:
        resumo["structure_fail"].append(f"Testes: {e}")

    try:
        resumo["suspensos_reaplicados"] = reaplicar_suspensoes_do_backup(payload)
    except Exception as e:
        resumo["structure_fail"].append(f"Suspensões: {e}")

    try:
        status("🆔 <b>Organizando UUID...</b>")
        xr = aplicar_uuids_backup_no_xray(xray_entries)
        resumo["xray_updated"] = xr.get("updated", 0)
        resumo["xray_added"] = xr.get("added", 0)
        resumo["xray_applied"] = xr.get("applied", resumo["xray_updated"] + resumo["xray_added"])

        if uuid_expired_mode_ativo():
            status("🔒 <b>Aplicando regras de UUID...</b>")
            resumo_uuid = sincronizar_uuid_vencidos_xray_agora()
            resumo["xray_removed_policy"] = (
                resumo_uuid["expirados"]["removidos_xray"] +
                resumo_uuid["paineis_suspensos"]["removidos_xray"]
            )

    except Exception as e:
        resumo["xray_error"] = str(e)

    return resumo

@bot.message_handler(content_types=["document"])
def receber_documento_backup(message):
    if not eh_admin(message.from_user.id):
        return

    doc = message.document
    if not doc:
        return

    file_name = str(doc.file_name or "").strip()

    if not arquivo_parece_backup(file_name):
        return

    msg_status = bot.send_message(
        message.chat.id,
        "<b>Backup detectado.</b>\n\nValidando arquivo..."
    )

    temp_zip = os.path.join(tempfile.gettempdir(), BACKUP_ZIP_NAME)

    try:
        file_info = bot.get_file(doc.file_id)
        downloaded = bot.download_file(file_info.file_path)

        with open(temp_zip, "wb") as f:
            f.write(downloaded)

        payload, xray_entries = carregar_backup_zip(temp_zip)

        user_data[message.from_user.id] = {
            "acao": "restore_backup",
            "zip_path": temp_zip,
            "payload": payload,
            "xray_entries": xray_entries
        }

        bot.edit_message_text(
            (
                "<b>Backup detectado.</b>\n\n"
                f"👤 Usuários admin: <code>{len(payload.get('admin_users', []))}</code>\n"
                f"🏪 Revendas: <code>{len(payload.get('resellers', []))}</code>\n"
                f"🏷️ Sub-revendas: <code>{len(payload.get('subresellers', []))}</code>\n"
                f"🆔 XRay: <code>{len(xray_entries)}</code>\n\n"
                "Deseja restaurar este backup?"
            ),
            chat_id=msg_status.chat.id,
            message_id=msg_status.message_id,
            reply_markup=painel_confirmar_restore_backup_markup()
        )

    except Exception as e:
        bot.edit_message_text(
            f"❌ <b>Erro ao validar backup.</b>\n\n<code>{esc(e)}</code>",
            chat_id=msg_status.chat.id,
            message_id=msg_status.message_id
        )

        try:
            if os.path.exists(temp_zip):
                os.remove(temp_zip)
        except:
            pass
        
def coletar_testes_backup():
    resultado = []
    agora = datetime.now()

    for teste in ler_testes():
        try:
            username = str(teste.get("username", "")).strip()
            horas = int(teste.get("horas", 0))
            expires_at = teste.get("expires_at")

            if not username or not isinstance(expires_at, datetime):
                continue

            # só guarda testes ainda válidos
            if expires_at <= agora:
                continue

            resultado.append({
                "username": username,
                "horas": horas,
                "expires_at": expires_at.strftime("%Y-%m-%d %H:%M:%S")
            })
        except:
            continue

    return resultado

#parte do bakupe 
def restaurar_testes_do_backup(testes):
    restaurados = 0
    agora = datetime.now()

    # mantém só testes ainda válidos
    testes_validos = []
    for item in testes:
        try:
            username = str(item.get("username", "")).strip()
            horas = int(item.get("horas", 0))
            expires_at_str = str(item.get("expires_at", "")).strip()
            expires_at = datetime.strptime(expires_at_str, "%Y-%m-%d %H:%M:%S")

            if not username or expires_at <= agora:
                continue

            testes_validos.append({
                "username": username,
                "horas": horas,
                "expires_at": expires_at
            })
        except:
            continue

    # sobrescreve o arquivo de testes com os testes válidos do backup
    salvar_testes(testes_validos)
    restaurados = len(testes_validos)

    return restaurados

#pakupe tmb 
def reaplicar_suspensoes_do_backup(payload):
    reaplicados = 0

    # revendas suspensas
    for item in payload.get("resellers", []):
        try:
            telegram_user = str(item.get("telegram", "")).strip()
            if not telegram_user or not item.get("suspenso"):
                continue

            bloqueados, falharam = bloquear_todos_usuarios_da_revenda(telegram_user)
            if falharam:
                raise Exception(f"Falha ao bloquear usuários da revenda {telegram_user}: {', '.join(falharam)}")

            definir_suspensao_revenda(telegram_user, True)
            reaplicados += 1
        except Exception:
            pass

    # sub-revendas suspensas
    for item in payload.get("subresellers", []):
        try:
            telegram_user = str(item.get("telegram", "")).strip()
            if not telegram_user or not item.get("suspenso"):
                continue

            bloqueados, falharam = bloquear_todos_usuarios_da_subrevenda(telegram_user)
            if falharam:
                raise Exception(f"Falha ao bloquear usuários da sub {telegram_user}: {', '.join(falharam)}")

            definir_suspensao_subrevenda(telegram_user, True)

            if item.get("suspenso_por_fornecedor"):
                definir_suspensao_por_fornecedor_subrevenda(telegram_user, True)

            reaplicados += 1
        except Exception:
            pass

    return reaplicados

# =========================================================
# CÁLCULO PROPORCIONAL DE LIMITE DA REVENDA
# usando os dias reais do ciclo atual
# =========================================================
def calcular_valor_limite_revenda_proporcional(limite_atual, novo_limite, vencimento_str):
    limite_atual = int(limite_atual)
    novo_limite = int(novo_limite)

    limite_extra = novo_limite - limite_atual
    if limite_extra <= 0:
        raise Exception("O novo limite deve ser maior que o limite atual.")

    hoje = datetime.now(SP_TZ).date()
    data_venc = datetime.strptime(str(vencimento_str).strip(), "%d/%m/%Y").date()

    # início do ciclo real = 1 mês antes do vencimento
    inicio_ciclo = data_venc - relativedelta(months=1)

    dias_totais_ciclo = (data_venc - inicio_ciclo).days
    if dias_totais_ciclo <= 0:
        dias_totais_ciclo = 30

    dias_restantes = (data_venc - hoje).days
    if dias_restantes < 0:
        dias_restantes = 0

    # regra base: R$ 20 = 10 limites no ciclo inteiro
    preco_por_limite_no_ciclo = 20.0 / 10.0
    valor_cheio = limite_extra * preco_por_limite_no_ciclo

    if dias_restantes <= 0:
        valor_final = valor_cheio
    else:
        valor_final = valor_cheio * (dias_restantes / dias_totais_ciclo)

    return {
        "limite_atual": limite_atual,
        "novo_limite": novo_limite,
        "limite_extra": limite_extra,
        "vencimento": data_venc.strftime("%d/%m/%Y"),
        "dias_restantes": dias_restantes,
        "dias_totais_ciclo": dias_totais_ciclo,
        "valor_final": round(valor_final, 2)
    }

# =========================================================
# CALCULAR LIMITE DA REVENDA
# PASSO 1: RECEBER @ DA REVENDA
# =========================================================
def receber_telegram_calcular_limite_revenda(message):
    if not eh_admin(message.from_user.id):
        return

    dados_fluxo = user_data.get(message.from_user.id, {})
    if dados_fluxo.get("acao") != "calcular_limite_revenda":
        return

    if not message.text:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ @ inválido. Digite /menu para tentar novamente."
        )
        return

    telegram_user = message.text.strip()

    if not telegram_revenda_valido(telegram_user):
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ @ inválido. O @ precisa começar com @.\nDigite /menu para tentar novamente."
        )
        return

    # não pode ser subrevenda
    if subrevenda_existe(telegram_user):
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Esse @ pertence a uma sub-revenda.\nDigite /menu para tentar novamente."
        )
        return

    if not revenda_existe(telegram_user):
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Revenda não encontrada. Digite /menu para tentar novamente."
        )
        return

    try:
        dados = ler_dados_revenda(telegram_user)
        limite_atual = int(str(dados.get("limite_total", "0")).strip() or "0")
        vencimento = str(dados.get("vencimento", "")).strip()

        if not vencimento:
            raise Exception("A revenda não possui vencimento definido.")

    except Exception as e:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            f"❌ Erro ao ler dados da revenda.\n<code>{esc(e)}</code>"
        )
        return

    user_data[message.from_user.id]["telegram_revenda"] = telegram_user
    user_data[message.from_user.id]["limite_atual_revenda_calc"] = limite_atual
    user_data[message.from_user.id]["vencimento_revenda_calc"] = vencimento

    msg = bot.send_message(
        message.chat.id,
        f"👥 Limite atual da revenda: <code>{esc(limite_atual)}</code>\n"
        f"📅 Vencimento atual: <code>{esc(vencimento)}</code>\n\n"
        "Informe o novo limite."
    )
    bot.register_next_step_handler(msg, receber_novo_limite_calculo_revenda)

# =========================================================
# CALCULAR LIMITE DA REVENDA
# PASSO 2: RECEBER NOVO LIMITE E CALCULAR VALOR
# =========================================================
def receber_novo_limite_calculo_revenda(message):
    if not eh_admin(message.from_user.id):
        return

    dados_fluxo = user_data.get(message.from_user.id, {})
    if dados_fluxo.get("acao") != "calcular_limite_revenda":
        return

    if not message.text:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Limite inválido. Digite /menu para tentar novamente."
        )
        return

    texto = message.text.strip()

    if not texto.isdigit() or int(texto) <= 0:
        limpar_fluxo(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "❌ Limite inválido. Digite /menu para tentar novamente."
        )
        return

    try:
        telegram_user = dados_fluxo["telegram_revenda"]
        limite_atual = int(dados_fluxo["limite_atual_revenda_calc"])
        vencimento = str(dados_fluxo["vencimento_revenda_calc"]).strip()
        novo_limite = int(texto)

        calculo = calcular_valor_limite_revenda_proporcional(
            limite_atual=limite_atual,
            novo_limite=novo_limite,
            vencimento_str=vencimento
        )

        bot.send_message(
            message.chat.id,
            f"<b>Orçamento de +{esc(calculo['limite_extra'])} limites {esc(telegram_user)}</b>\n\n"
            f"👥 <b>Novo limite:</b> <code>{esc(calculo['novo_limite'])}</code>\n"
            f"📅 <b>Vencimento:</b> <code>{esc(calculo['vencimento'])}</code>\n"
            f"💰 <b>Valor:</b> <code>{esc(formatar_valor_brl(calculo['valor_final']))}</code>"
        )

    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Erro ao calcular valor.\n<code>{esc(e)}</code>"
        )
    finally:
        limpar_fluxo(message.from_user.id)

def formatar_valor_brl(valor):
    try:
        valor = float(valor)
    except:
        valor = 0.0

    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
# =========================================================
# SPEEDTEST
# =========================================================
def executar_speedtest():
    resultado = subprocess.run(
        ["speedtest"],
        capture_output=True,
        text=True,
        timeout=180
    )

    saida = (resultado.stdout or "").strip()
    erro = (resultado.stderr or "").strip()

    if resultado.returncode != 0:
        raise Exception(erro or saida or "Falha ao executar speedtest.")

    if not saida:
        raise Exception("O comando speedtest não retornou saída.")

    return saida


def extrair_dado_speedtest(texto, padrao):
    m = re.search(padrao, texto, re.MULTILINE)
    return m.group(1).strip() if m else ""


def parsear_speedtest(texto):
    servidor = extrair_dado_speedtest(texto, r"Server:\s*(.+)")
    isp = extrair_dado_speedtest(texto, r"ISP:\s*(.+)")
    latencia = extrair_dado_speedtest(texto, r"Latency:\s*([^\n(]+)")
    jitter = extrair_dado_speedtest(texto, r"Latency:\s*[^\n(]+\(([^)]+)\)")
    download = extrair_dado_speedtest(texto, r"Download:\s*([^\n(]+)")
    download_data = extrair_dado_speedtest(texto, r"Download:\s*[^\n(]+\(([^)]+)\)")
    upload = extrair_dado_speedtest(texto, r"Upload:\s*([^\n(]+)")
    upload_data = extrair_dado_speedtest(texto, r"Upload:\s*[^\n(]+\(([^)]+)\)")
    packet_loss = extrair_dado_speedtest(texto, r"Packet Loss:\s*(.+)")
    result_url = extrair_dado_speedtest(texto, r"Result URL:\s*(https?://\S+)")

    return {
        "servidor": servidor,
        "isp": isp,
        "latencia": latencia,
        "jitter": jitter,
        "download": download,
        "download_data": download_data,
        "upload": upload,
        "upload_data": upload_data,
        "packet_loss": packet_loss,
        "result_url": result_url
    }


def montar_msg_speedtest(dados):
    ping = str(dados.get("latencia", "")).strip()
    download = str(dados.get("download", "")).strip()
    upload = str(dados.get("upload", "")).strip()
    localizacao_raw = str(dados.get("servidor", "")).strip()

    # remove o "(id = xxxx)"
    localizacao = re.sub(r"\s*\(id\s*=\s*\d+\)", "", localizacao_raw).strip()

    # se vier algo como "JD Net - São Paulo", pega só "São Paulo"
    if " - " in localizacao:
        localizacao = localizacao.split(" - ", 1)[1].strip()

    return (
        "=========================\n"
        "🚀 <b>TESTE DE VELOCIDADE</b> 🚀\n"
        "=========================\n"
        f"<b>PING:</b> {esc(ping)}\n"
        f"<b>DOWNLOAD:</b> {esc(download)}\n"
        f"<b>UPLOAD:</b> {esc(upload)}\n\n"
        f"<i><b>LOCALIZAÇÃO:</b> {esc(localizacao)}</i>\n"
        "========================="
    )

def normalizar_telegram_user(telegram_user):
    tg = str(telegram_user or "").strip()

    if not tg:
        return ""

    if not tg.startswith("@"):
        tg = "@" + tg

    return tg.lower()

def obter_telegram_admin():
    try:
        chat_admin = bot.get_chat(ADMIN_ID)
        username_admin = getattr(chat_admin, "username", None)
        if username_admin:
            return normalizar_telegram_user("@" + username_admin)
    except:
        pass
    return None


def telegram_ja_existe_global(telegram_user, ignorar_telegram=None):
    tg = normalizar_telegram_user(telegram_user)
    ignorar = normalizar_telegram_user(ignorar_telegram) if ignorar_telegram else ""

    if not tg.startswith("@"):
        return False

    if ignorar and tg == ignorar:
        return False

    # bloqueia admin
    tg_admin = obter_telegram_admin()
    if tg_admin and tg == tg_admin:
        return True

    # bloqueia revendas
    for rev in listar_todas_revendas():
        rev_norm = normalizar_telegram_user(rev)
        if rev_norm == tg and rev_norm != ignorar:
            return True

    # bloqueia sub-revendas
    for sub_tg in listar_todas_subrevendas():
        sub_norm = normalizar_telegram_user(sub_tg)
        if sub_norm == tg and sub_norm != ignorar:
            return True

    return False

# =========================================================
# ENCONTRAR DE QUAL SUB REVENDA É UM USUÁRIO/TESTE
# =========================================================
def encontrar_subrevenda_do_usuario(username):
    for telegram_sub in listar_todas_subrevendas():
        try:
            caminho = caminho_arquivo_subrevenda(telegram_sub)
            if not os.path.exists(caminho):
                continue

            with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
                for linha in f:
                    texto = linha.strip()
                    if not texto or "=" in texto:
                        continue

                    partes = texto.split()
                    if partes and partes[0] == username:
                        return telegram_sub
        except:
            pass

    return None


revenda.init_revenda_module(
    bot=bot,
    esc=esc,
    preview_url=PREVIEW_URL,
    user_data=user_data,
    obter_telegram_atual=obter_telegram_atual,
    ler_dados_revenda=ler_dados_revenda,
    salvar_revenda=salvar_revenda,
    criar_usuario_sistema=criar_usuario_sistema,
    username_valido=username_valido,
    username_apenas_numeros=username_apenas_numeros,
    adicionar_usuario_revenda_arquivo=adicionar_usuario_revenda_arquivo,
    adicionar_teste_revenda_arquivo=adicionar_teste_revenda_arquivo,
    extrair_uuid_vless=extrair_uuid_vless,
    uuid_mode_ativo=uuid_mode_ativo,
    gerar_username_disponivel=gerar_username_disponivel,
    adicionar_teste_arquivo=adicionar_teste_arquivo,
    montar_msg_teste=montar_msg_teste,
    sincronizar_arquivo_revenda=sincronizar_arquivo_revenda,
    recalcular_limite_restante_revenda=recalcular_limite_restante_revenda,
    alterar_limite_usuario_sistema=alterar_limite_usuario_sistema,
    listar_usuarios_da_revenda=listar_usuarios_da_revenda,
    ler_usuarios_revenda_completos=ler_usuarios_revenda_completos,
    alterar_senha_usuario_sistema=alterar_senha_usuario_sistema,
    alterar_data_usuario_sistema=alterar_data_usuario_sistema,
    obter_data_vencimento_usuario=obter_data_vencimento_usuario,
    calcular_renovacao_mais_um_mes=calcular_renovacao_mais_um_mes,
    calcular_dias_ate_data_futura=calcular_dias_ate_data_futura,
    deletar_usuario_sistema=deletar_usuario_sistema,
    usuario_existe=usuario_existe,
    obter_data_expiracao_usuario=obter_data_expiracao_usuario,
    obter_uuid_disponivel_usuario=obter_uuid_disponivel_usuario,
    obter_usuarios_online_plugin=obter_usuarios_online_plugin,
    obter_maior_tempo_online_usuario=obter_maior_tempo_online_usuario,
    subrevenda_existe=subrevenda_existe,
    salvar_subrevenda_arquivo=salvar_subrevenda,
    deletar_subrevenda_arquivo=deletar_subrevenda,
    ler_dados_subrevenda=ler_dados_subrevenda,
    calcular_limite_usado_real_subrevenda=calcular_limite_usado_real_subrevenda,
    sincronizar_arquivo_subrevenda=sincronizar_arquivo_subrevenda,
    ler_usuarios_subrevenda_completos=ler_usuarios_subrevenda_completos,
    suspender_subrevenda_automaticamente=suspender_subrevenda_automaticamente,
    subrevenda_suspensa=subrevenda_suspensa,
    suspender_subrevenda_manualmente=suspender_subrevenda_manualmente,
    reativar_subrevenda=reativar_subrevenda,
    renovar_subrevenda=renovar_subrevenda,
    revenda_existe=revenda_existe,
    admin_id=ADMIN_ID,
    sub_dir=SUB_DIR
)

sub.init_sub_module(
    bot=bot,
    esc=esc,
    preview_url="https://a.imagem.app/GG1KMm.png",
    user_data=user_data,
    obter_telegram_atual=obter_telegram_atual,
    ler_dados_subrevenda=ler_dados_subrevenda,
    salvar_subrevenda=salvar_subrevenda,
    criar_usuario_sistema=criar_usuario_sistema,
    username_valido=username_valido,
    username_apenas_numeros=username_apenas_numeros,
    adicionar_usuario_sub_arquivo=adicionar_usuario_sub_arquivo,
    adicionar_teste_sub_arquivo=adicionar_teste_sub_arquivo,
    extrair_uuid_vless=extrair_uuid_vless,
    uuid_mode_ativo=uuid_mode_ativo,
    gerar_username_disponivel=gerar_username_disponivel,
    adicionar_teste_arquivo=adicionar_teste_arquivo,
    montar_msg_teste=montar_msg_teste,
    usuario_existe=usuario_existe,
    alterar_limite_usuario_sistema=alterar_limite_usuario_sistema,
    ler_usuarios_subrevenda_completos=ler_usuarios_subrevenda_completos,
    reescrever_arquivo_subrevenda=reescrever_arquivo_subrevenda,
    alterar_senha_usuario_sistema=alterar_senha_usuario_sistema,
    sincronizar_arquivo_subrevenda=sincronizar_arquivo_subrevenda,
    alterar_data_usuario_sistema=alterar_data_usuario_sistema,
    obter_data_vencimento_usuario=obter_data_vencimento_usuario,
    calcular_renovacao_mais_um_mes=calcular_renovacao_mais_um_mes,
    calcular_dias_ate_data_futura=calcular_dias_ate_data_futura,
    deletar_usuario_sistema=deletar_usuario_sistema,
    obter_usuarios_online_plugin=obter_usuarios_online_plugin,
    obter_maior_tempo_online_usuario=obter_maior_tempo_online_usuario,
    obter_data_expiracao_usuario=obter_data_expiracao_usuario,
    obter_uuid_disponivel_usuario=obter_uuid_disponivel_usuario
)

# =========================================================
# INICIALIZAÇÃO
# =========================================================
print("Iniciando monitor de testes...")
iniciar_monitor_testes()

print("Verificando revendas vencidas ao iniciar...")
verificar_revendas_vencidas_ao_iniciar()

print("Sincronizando dados das revendas ao iniciar...")
sincronizar_revendas_ao_iniciar()

print("Iniciando monitor de revendas...")
iniciar_monitor_revendas()

print("Iniciando monitor de sincronização das revendas...")
iniciar_monitor_sincronizacao_revendas()
sincronizar_subrevendas_ao_iniciar()
iniciar_monitor_sincronizacao_subrevendas()
verificar_subrevendas_vencidas_ao_iniciar()
iniciar_monitor_subrevendas()
iniciar_monitor_auto_backup()
print("Iniciando monitor de UUIDs vencidos do XRay...")
iniciar_monitor_uuid_vencidos_xray()

socket.setdefaulttimeout(30)
apihelper.CONNECT_TIMEOUT = 15
apihelper.READ_TIMEOUT = 30

print("Bot rodando...")

try:
    try:
        bot.remove_webhook()
        time.sleep(1)
    except Exception as e:
        print(f"[ERRO REMOVE WEBHOOK] {repr(e)}")

    while True:
        try:
            bot.infinity_polling(
                skip_pending=True,
                timeout=20,
                long_polling_timeout=20
            )
        except Exception as e:
            print(f"[ERRO POLLING] {repr(e)}")
            time.sleep(5)

except KeyboardInterrupt:
    print("\nParando bot...")
    try:
        bot.stop_polling()
    except:
        pass
    print("Bot finalizado pelo usuário.")
