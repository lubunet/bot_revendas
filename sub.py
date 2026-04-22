
from datetime import datetime, timedelta
from telebot import types
import time
import random
from dateutil.relativedelta import relativedelta

BOT = None
ESC = None
PREVIEW_URL = None
USER_DATA = None
SUB_USERS_BUSY = {}
SUB_BUSY_TIMEOUT = 20

OBTER_TELEGRAM_ATUAL = None
LER_DADOS_SUBREVENDA = None
SALVAR_SUBREVENDA = None
CRIAR_USUARIO_SISTEMA = None
USERNAME_VALIDO = None
USERNAME_APENAS_NUMEROS = None
ADICIONAR_USUARIO_SUB_ARQUIVO = None
ADICIONAR_TESTE_SUB_ARQUIVO = None
EXTRAIR_UUID_VLESS = None
UUID_MODE_ATIVO = None
GERAR_USERNAME_DISPONIVEL = None
ADICIONAR_TESTE_ARQUIVO = None
MONTAR_MSG_TESTE = None
USUARIO_EXISTE = None
ALTERAR_LIMITE_USUARIO_SISTEMA = None
LER_USUARIOS_SUBREVENDA_COMPLETOS = None
REESCREVER_ARQUIVO_SUBREVENDA = None
ALTERAR_SENHA_USUARIO_SISTEMA = None
SINCRONIZAR_ARQUIVO_SUBREVENDA = None
ALTERAR_DATA_USUARIO_SISTEMA = None
OBTER_DATA_VENCIMENTO_USUARIO = None
CALCULAR_RENOVACAO_MAIS_UM_MES = None
CALCULAR_DIAS_ATE_DATA_FUTURA = None
DELETAR_USUARIO_SISTEMA = None
OBTER_USUARIOS_ONLINE_PLUGIN = None
OBTER_MAIOR_TEMPO_ONLINE_USUARIO = None
OBTER_DATA_EXPIRACAO_USUARIO = None
OBTER_UUID_DISPONIVEL_USUARIO = None

# =========================================================
# INICIAR MÓDULO SUB REVENDA
# =========================================================
def init_sub_module(
    bot,
    esc,
    preview_url,
    user_data,
    obter_telegram_atual,
    ler_dados_subrevenda,
    salvar_subrevenda,
    criar_usuario_sistema,
    username_valido,
    username_apenas_numeros,
    adicionar_usuario_sub_arquivo,
    adicionar_teste_sub_arquivo,
    extrair_uuid_vless,
    uuid_mode_ativo,
    gerar_username_disponivel,
    adicionar_teste_arquivo,
    montar_msg_teste,
    usuario_existe,
    alterar_limite_usuario_sistema,
    ler_usuarios_subrevenda_completos,
    reescrever_arquivo_subrevenda,
    alterar_senha_usuario_sistema,
    sincronizar_arquivo_subrevenda,
    alterar_data_usuario_sistema,
    obter_data_vencimento_usuario,
    calcular_renovacao_mais_um_mes,
    calcular_dias_ate_data_futura,
    deletar_usuario_sistema,
    obter_usuarios_online_plugin,
    obter_maior_tempo_online_usuario,
    obter_data_expiracao_usuario,
    obter_uuid_disponivel_usuario
):
    
    global BOT, ESC, PREVIEW_URL, USER_DATA
    global OBTER_TELEGRAM_ATUAL, LER_DADOS_SUBREVENDA, SALVAR_SUBREVENDA
    global CRIAR_USUARIO_SISTEMA, USERNAME_VALIDO, USERNAME_APENAS_NUMEROS
    global ADICIONAR_USUARIO_SUB_ARQUIVO, ADICIONAR_TESTE_SUB_ARQUIVO
    global EXTRAIR_UUID_VLESS, UUID_MODE_ATIVO
    global GERAR_USERNAME_DISPONIVEL, ADICIONAR_TESTE_ARQUIVO, MONTAR_MSG_TESTE
    global USUARIO_EXISTE
    global ALTERAR_LIMITE_USUARIO_SISTEMA
    global LER_USUARIOS_SUBREVENDA_COMPLETOS
    global REESCREVER_ARQUIVO_SUBREVENDA
    global ALTERAR_SENHA_USUARIO_SISTEMA
    global SINCRONIZAR_ARQUIVO_SUBREVENDA
    global ALTERAR_DATA_USUARIO_SISTEMA
    global OBTER_DATA_VENCIMENTO_USUARIO
    global CALCULAR_RENOVACAO_MAIS_UM_MES
    global CALCULAR_DIAS_ATE_DATA_FUTURA
    global DELETAR_USUARIO_SISTEMA
    global OBTER_USUARIOS_ONLINE_PLUGIN
    global OBTER_MAIOR_TEMPO_ONLINE_USUARIO
    global OBTER_DATA_EXPIRACAO_USUARIO
    global OBTER_UUID_DISPONIVEL_USUARIO

    BOT = bot
    ESC = esc
    PREVIEW_URL = preview_url
    USER_DATA = user_data

    OBTER_TELEGRAM_ATUAL = obter_telegram_atual
    LER_DADOS_SUBREVENDA = ler_dados_subrevenda
    SALVAR_SUBREVENDA = salvar_subrevenda
    CRIAR_USUARIO_SISTEMA = criar_usuario_sistema
    USERNAME_VALIDO = username_valido
    USERNAME_APENAS_NUMEROS = username_apenas_numeros
    ADICIONAR_USUARIO_SUB_ARQUIVO = adicionar_usuario_sub_arquivo
    ADICIONAR_TESTE_SUB_ARQUIVO = adicionar_teste_sub_arquivo
    EXTRAIR_UUID_VLESS = extrair_uuid_vless
    UUID_MODE_ATIVO = uuid_mode_ativo
    GERAR_USERNAME_DISPONIVEL = gerar_username_disponivel
    ADICIONAR_TESTE_ARQUIVO = adicionar_teste_arquivo
    MONTAR_MSG_TESTE = montar_msg_teste
    USUARIO_EXISTE = usuario_existe
    ALTERAR_LIMITE_USUARIO_SISTEMA = alterar_limite_usuario_sistema
    LER_USUARIOS_SUBREVENDA_COMPLETOS = ler_usuarios_subrevenda_completos
    REESCREVER_ARQUIVO_SUBREVENDA = reescrever_arquivo_subrevenda
    ALTERAR_SENHA_USUARIO_SISTEMA = alterar_senha_usuario_sistema
    SINCRONIZAR_ARQUIVO_SUBREVENDA = sincronizar_arquivo_subrevenda
    ALTERAR_DATA_USUARIO_SISTEMA = alterar_data_usuario_sistema
    OBTER_DATA_VENCIMENTO_USUARIO = obter_data_vencimento_usuario
    CALCULAR_RENOVACAO_MAIS_UM_MES = calcular_renovacao_mais_um_mes
    CALCULAR_DIAS_ATE_DATA_FUTURA = calcular_dias_ate_data_futura
    DELETAR_USUARIO_SISTEMA = deletar_usuario_sistema
    OBTER_USUARIOS_ONLINE_PLUGIN = obter_usuarios_online_plugin
    OBTER_MAIOR_TEMPO_ONLINE_USUARIO = obter_maior_tempo_online_usuario
    OBTER_DATA_EXPIRACAO_USUARIO = obter_data_expiracao_usuario
    OBTER_UUID_DISPONIVEL_USUARIO = obter_uuid_disponivel_usuario

# =========================================================
# RESETAR FLUXO ANTERIOR DO USUÁRIO
# =========================================================
def resetar_fluxo_sub(user_id):
    try:
        BOT.clear_step_handler_by_chat_id(user_id)
    except:
        pass

    USER_DATA.pop(user_id, None)
    limpar_trava_sub(user_id)


# =========================================================
# PROTEÇÃO CONTRA CLIQUES REPETIDOS NO PAINEL SUB
# =========================================================
def callback_sub_protegido(callback_data):
    protegidos = {
        "sub_add_usuario",
        "sub_add_teste",
        "sub_add_usuario_auto",
        "sub_alt_limite",
        "sub_alt_senha",
        "sub_alt_data",
        "sub_renovar",
        "sub_del_usuario",
        "sub_confirmar_del_expirados",
        "sub_listar_usuarios",
        "sub_usuarios_online",
        "sub_consultar_usuario",
        "sub_relatorio"
    }
    return callback_data in protegidos


def sub_usuario_esta_ocupado(user_id):
    agora = time.time()
    expira_em = SUB_USERS_BUSY.get(user_id, 0)

    if expira_em > agora:
        return True

    if user_id in SUB_USERS_BUSY:
        SUB_USERS_BUSY.pop(user_id, None)

    return False


def iniciar_trava_sub(user_id, segundos=SUB_BUSY_TIMEOUT):
    SUB_USERS_BUSY[user_id] = time.time() + segundos


def limpar_trava_sub(user_id):
    SUB_USERS_BUSY.pop(user_id, None)


# =========================================================
# MARKUP DO PAINEL SUB REVENDA
# =========================================================
def painel_sub_markup():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("Adicionar usuário", callback_data="sub_add_usuario"),
        types.InlineKeyboardButton("Criar teste", callback_data="sub_add_teste")
    )
    kb.add(
        types.InlineKeyboardButton("Criar usuário automático", callback_data="sub_add_usuario_auto")
    )
    kb.add(
        types.InlineKeyboardButton("Alterar Limite", callback_data="sub_alt_limite"),
        types.InlineKeyboardButton("Alterar Senha", callback_data="sub_alt_senha")
    )
    kb.add(
        types.InlineKeyboardButton("Alterar Data", callback_data="sub_alt_data"),
        types.InlineKeyboardButton("Renovar", callback_data="sub_renovar")
    )
    kb.add(
        types.InlineKeyboardButton("Deletar usuário", callback_data="sub_del_usuario"),
        types.InlineKeyboardButton("Deletar expirados", callback_data="sub_del_expirados")
    )
    kb.add(
        types.InlineKeyboardButton("Listar usuários", callback_data="sub_listar_usuarios"),
        types.InlineKeyboardButton("Listar online", callback_data="sub_usuarios_online")
    )
    kb.add(
        types.InlineKeyboardButton("Consultar usuário", callback_data="sub_consultar_usuario")
    )
    kb.add(
        types.InlineKeyboardButton("Relatorio", callback_data="sub_relatorio")
    )
    return kb
    

# =========================================================
# MARKUP DOS EXPIRADOS DO SUB
# =========================================================
def painel_expirados_sub_markup(tem_expirados=True):
    kb = types.InlineKeyboardMarkup(row_width=1)

    if tem_expirados:
        kb.add(types.InlineKeyboardButton("🗑️ Deletar expirados", callback_data="sub_confirmar_del_expirados"))

    kb.add(types.InlineKeyboardButton("⬅️ Voltar", callback_data="sub_voltar_menu"))
    return kb

# =========================================================
# MARKUP / TEXTO DE VOLTA DO MENU SUB
# =========================================================
def editar_menu_subrevenda(chat_id, message_id, obj):
    preview = types.LinkPreviewOptions(
        is_disabled=False,
        url=PREVIEW_URL,
        show_above_text=True,
        prefer_large_media=True
    )

    BOT.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=texto_menu_sub(obj),
        reply_markup=painel_sub_markup(),
        link_preview_options=preview
    )

# =========================================================
# MARKUP DE VOLTAR DO RELATÓRIO DO SUB
# =========================================================
def painel_relatorio_sub_markup():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("⬅️ Voltar", callback_data="sub_voltar_menu"))
    return kb

# =========================================================
# MARKUP DE VOLTAR DA LISTA DE USUÁRIOS ONLINE DO SUB
# =========================================================
def painel_usuarios_online_sub_voltar_markup():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("⬅️ Voltar", callback_data="sub_voltar_menu"))
    return kb

# =========================================================
# MARKUP DE VOLTAR DA LISTA DE USUÁRIOS DO SUB
# =========================================================
def painel_lista_usuarios_sub_markup():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("⬅️ Voltar", callback_data="sub_voltar_menu"))
    return kb

# =========================================================
# DADOS DA SUB REVENDA ATUAL
# =========================================================
def dados_subrevenda_atual(obj):
    telegram_user = OBTER_TELEGRAM_ATUAL(obj)
    if not telegram_user:
        raise Exception("Telegram da sub revenda não encontrado.")

    dados = LER_DADOS_SUBREVENDA(telegram_user)

    limite_total = int(dados.get("limite_total", "0"))
    limite_restante = int(dados.get("limite_restante", "0"))
    vencimento = dados.get("vencimento", "-")
    dono = dados.get("dono", "-")

    return telegram_user, dono, limite_total, limite_restante, vencimento


# =========================================================
# TEXTO DO MENU SUB REVENDA
# =========================================================
def texto_menu_sub(obj):
    nome = ESC(obj.from_user.first_name or "Usuário")
    telegram_user, dono, limite_total, limite_restante, vencimento = dados_subrevenda_atual(obj)

    return (
        f"🚀 <b>{nome}</b>, Bem Vindoª Ao Painel LUBU NET\n\n"
    )


# =========================================================
# ABRIR MENU DA SUB REVENDA
# =========================================================
def abrir_menu_subrevenda(message):
    preview = types.LinkPreviewOptions(
        is_disabled=False,
        url=PREVIEW_URL,
        show_above_text=True,
        prefer_large_media=True
    )

    BOT.send_message(
        message.chat.id,
        texto_menu_sub(message),
        reply_markup=painel_sub_markup(),
        link_preview_options=preview
    )


# =========================================================
# CALLBACKS DA SUB REVENDA
# =========================================================
def handle_callback_subrevenda(c):
    if callback_sub_protegido(c.data):
        if sub_usuario_esta_ocupado(c.from_user.id):
            BOT.answer_callback_query(c.id, "Aguarde.", show_alert=True)
            return True

        iniciar_trava_sub(c.from_user.id)

    if c.data == "sub_add_usuario":
        try:
            _, _, _, limite_restante, _ = dados_subrevenda_atual(c)
        except:
            limite_restante = 0

        if limite_restante <= 0:
            try:
                BOT.delete_message(c.message.chat.id, c.message.message_id)
            except:
                pass

            resetar_fluxo_sub(c.from_user.id)

            BOT.send_message(
                c.message.chat.id,
                "❌ <b>Vc esta sem creditos!</b>\n\nExecute /menu para voltar"
            )
            return True

        if limite_restante == 1:
            BOT.answer_callback_query(
                c.id,
                "Esse é seu último crédito.",
                show_alert=True
            )
        else:
            BOT.answer_callback_query(c.id, "Abrindo...")

        try:
            BOT.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        resetar_fluxo_sub(c.from_user.id)
        USER_DATA[c.from_user.id] = {"acao": "sub_add_usuario"}

        msg = BOT.send_message(c.message.chat.id, "Envie o nome do usuário.")
        BOT.register_next_step_handler(msg, receber_usuario_sub)
        return True

    if c.data == "sub_add_teste":
        try:
            _, _, _, limite_restante, _ = dados_subrevenda_atual(c)
        except:
            limite_restante = 0

        if limite_restante <= 0:
            try:
                BOT.delete_message(c.message.chat.id, c.message.message_id)
            except:
                pass

            resetar_fluxo_sub(c.from_user.id)

            BOT.send_message(
                c.message.chat.id,
                "❌ <b>Vc esta sem creditos!</b>\n\nExecute /menu para voltar"
            )
            return True

        if limite_restante == 1:
            BOT.answer_callback_query(
                c.id,
                "Esse é seu último crédito.",
                show_alert=True
            )
        else:
            BOT.answer_callback_query(c.id, "Abrindo...")

        try:
            BOT.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        resetar_fluxo_sub(c.from_user.id)
        USER_DATA[c.from_user.id] = {"acao": "sub_add_teste"}

        msg = BOT.send_message(
            c.message.chat.id,
            "Envie a quantidade de horas do teste. Máximo: 24"
        )
        BOT.register_next_step_handler(msg, receber_horas_teste_sub)
        return True

    if c.data == "sub_add_usuario_auto":
        try:
            _, _, _, limite_restante, _ = dados_subrevenda_atual(c)
        except:
            limite_restante = 0

        if limite_restante <= 0:
            try:
                BOT.delete_message(c.message.chat.id, c.message.message_id)
            except:
                pass

            resetar_fluxo_sub(c.from_user.id)

            BOT.send_message(
                c.message.chat.id,
                "❌ <b>Vc esta sem creditos!</b>\n\nExecute /menu para voltar"
            )
            return True

        if limite_restante == 1:
            BOT.answer_callback_query(
                c.id,
                "Esse é seu último crédito.",
                show_alert=True
            )
        else:
            BOT.answer_callback_query(c.id, "Abrindo...")

        resetar_fluxo_sub(c.from_user.id)
        USER_DATA[c.from_user.id] = {"acao": "sub_add_usuario_auto"}
        limpar_trava_sub(c.from_user.id)

        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(types.InlineKeyboardButton("📅 1 mês", callback_data="sub_auto_mes_1"))
        kb.add(types.InlineKeyboardButton("📅 2 meses", callback_data="sub_auto_mes_2"))
        kb.add(types.InlineKeyboardButton("📅 3 meses", callback_data="sub_auto_mes_3"))

        try:
            BOT.edit_message_text(
                chat_id=c.message.chat.id,
                message_id=c.message.message_id,
                text=(
                    "<b>Criar usuário automático</b>\n\n"
                    "Escolha abaixo a validade do usuário:"
                ),
                reply_markup=kb
            )
        except Exception as e:
            BOT.send_message(
                c.message.chat.id,
                f"❌ Erro ao abrir painel.\n<code>{ESC(e)}</code>"
            )
        return True

    if c.data == "sub_alt_limite":
        BOT.answer_callback_query(c.id, "Abrindo...")
    
        try:
            telegram_sub, _, _, _, _ = dados_subrevenda_atual(c)
    
            if SINCRONIZAR_ARQUIVO_SUBREVENDA:
                SINCRONIZAR_ARQUIVO_SUBREVENDA(telegram_sub)
        except Exception as e:
            resetar_fluxo_sub(c.from_user.id)
            limpar_trava_sub(c.from_user.id)
            BOT.send_message(
                c.message.chat.id,
                f"❌ Erro ao sincronizar dados da sub-revenda.\n<code>{ESC(e)}</code>"
            )
            return True
    
        try:
            BOT.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass
    
        resetar_fluxo_sub(c.from_user.id)
        USER_DATA[c.from_user.id] = {"acao": "sub_alt_limite"}
    
        limpar_trava_sub(c.from_user.id)
    
        msg = BOT.send_message(c.message.chat.id, "Envie o nome do usuário.")
        BOT.register_next_step_handler(msg, receber_usuario_alterar_limite_sub)
        return True
    
    if c.data == "sub_alt_senha":
        BOT.answer_callback_query(c.id, "Abrindo...")
    
        try:
            BOT.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass
    
        resetar_fluxo_sub(c.from_user.id)
        USER_DATA[c.from_user.id] = {"acao": "sub_alt_senha"}
    
        limpar_trava_sub(c.from_user.id)
    
        msg = BOT.send_message(c.message.chat.id, "Envie o nome do usuário.")
        BOT.register_next_step_handler(msg, receber_usuario_alterar_senha_sub)
        return True
    
    if c.data == "sub_alt_data":
        BOT.answer_callback_query(c.id, "Abrindo...")
    
        try:
            BOT.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass
    
        resetar_fluxo_sub(c.from_user.id)
        USER_DATA[c.from_user.id] = {"acao": "sub_alt_data"}
    
        limpar_trava_sub(c.from_user.id)
    
        msg = BOT.send_message(c.message.chat.id, "Envie o nome do usuário.")
        BOT.register_next_step_handler(msg, receber_usuario_alterar_data_sub)
        return True
    
    if c.data == "sub_renovar":
        BOT.answer_callback_query(c.id, "Abrindo...")

        try:
            BOT.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        resetar_fluxo_sub(c.from_user.id)
        USER_DATA[c.from_user.id] = {"acao": "sub_renovar"}

        limpar_trava_sub(c.from_user.id)

        msg = BOT.send_message(c.message.chat.id, "Envie o nome do usuário.")
        BOT.register_next_step_handler(msg, receber_usuario_renovar_sub)
        return True
    
    # =========================================================
    # DELETAR USUÁRIO
    # =========================================================
    if c.data == "sub_del_usuario":
        BOT.answer_callback_query(c.id, "Abrindo...")

        try:
            BOT.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        resetar_fluxo_sub(c.from_user.id)
        USER_DATA[c.from_user.id] = {"acao": "sub_del_usuario"}

        limpar_trava_sub(c.from_user.id)

        msg = BOT.send_message(c.message.chat.id, "Envie o nome do usuário.")
        BOT.register_next_step_handler(msg, receber_usuario_deletar_sub)
        return True
    
    # =========================================================
    # LISTAR / PAINEL DE EXPIRADOS
    # =========================================================
    if c.data == "sub_del_expirados":
        BOT.answer_callback_query(c.id, "Consultando...")

        try:
            telegram_sub, _, _, _, _ = dados_subrevenda_atual(c)

            # varredura daquele sub antes da consulta
            if SINCRONIZAR_ARQUIVO_SUBREVENDA:
                SINCRONIZAR_ARQUIVO_SUBREVENDA(telegram_sub)

            BOT.edit_message_text(
                chat_id=c.message.chat.id,
                message_id=c.message.message_id,
                text="<b>Consultando...</b>"
            )

            expirados = obter_usuarios_expirados_sub(telegram_sub)
            texto = montar_texto_expirados_sub(expirados)

            partes = quebrar_texto_em_partes(texto)

            if len(partes) == 1:
                BOT.edit_message_text(
                    chat_id=c.message.chat.id,
                    message_id=c.message.message_id,
                    text=partes[0],
                    reply_markup=painel_expirados_sub_markup(tem_expirados=bool(expirados))
                )
            else:
                # primeira parte substitui o painel
                BOT.edit_message_text(
                    chat_id=c.message.chat.id,
                    message_id=c.message.message_id,
                    text=partes[0]
                )

                # partes intermediárias sem botão
                for parte in partes[1:-1]:
                    BOT.send_message(c.message.chat.id, parte)

                # última com botão
                BOT.send_message(
                    c.message.chat.id,
                    partes[-1],
                    reply_markup=painel_expirados_sub_markup(tem_expirados=bool(expirados))
                )

        except Exception as e:
            BOT.send_message(
                c.message.chat.id,
                f"❌ Erro ao consultar expirados.\n<code>{ESC(e)}</code>"
            )
        finally:
            limpar_trava_sub(c.from_user.id)

        return True
    
    # =========================================================
    # CONFIRMAR EXCLUSÃO DOS EXPIRADOS
    # =========================================================
    if c.data == "sub_confirmar_del_expirados":
        BOT.answer_callback_query(c.id, "Apagando...")

        try:
            telegram_sub, _, _, _, _ = dados_subrevenda_atual(c)

            # varredura antes de apagar
            if SINCRONIZAR_ARQUIVO_SUBREVENDA:
                SINCRONIZAR_ARQUIVO_SUBREVENDA(telegram_sub)

            expirados = obter_usuarios_expirados_sub(telegram_sub)

            apagados = []
            falharam = []

            for username in expirados:
                try:
                    DELETAR_USUARIO_SISTEMA(username)
                    apagados.append(username)
                except Exception as e:
                    falharam.append(f"{username}: {e}")

            # varredura de novo para limpar o banco local e reajustar limite
            if SINCRONIZAR_ARQUIVO_SUBREVENDA:
                SINCRONIZAR_ARQUIVO_SUBREVENDA(telegram_sub)

            if falharam:
                BOT.send_message(
                    c.message.chat.id,
                    "❌ <b>Alguns usuários não puderam ser apagados.</b>\n\n"
                    + "\n".join(f"<code>{ESC(x)}</code>" for x in falharam[:20])
                )

            BOT.edit_message_text(
                chat_id=c.message.chat.id,
                message_id=c.message.message_id,
                text=(
                    "🗑️ <b>Expirados apagados com sucesso!</b>\n\n"
                    f"📊 <b>Total apagado:</b> {ESC(len(apagados))}"
                ),
                reply_markup=painel_expirados_sub_markup(tem_expirados=False)
            )

        except Exception as e:
            BOT.send_message(
                c.message.chat.id,
                f"❌ Erro ao apagar expirados.\n<code>{ESC(e)}</code>"
            )
        finally:
            limpar_trava_sub(c.from_user.id)

        return True
    
    # =========================================================
    # VOLTAR AO MENU DO SUB
    # =========================================================
    if c.data == "sub_voltar_menu":
        BOT.answer_callback_query(c.id, "Voltando...")

        try:
            editar_menu_subrevenda(
                c.message.chat.id,
                c.message.message_id,
                c
            )
        except Exception as e:
            BOT.send_message(
                c.message.chat.id,
                f"❌ Erro ao voltar para o menu.\n<code>{ESC(e)}</code>"
            )

        return True
    
    # =========================================================
    # LISTAR USUÁRIOS DO SUB
    # =========================================================
    if c.data == "sub_listar_usuarios":
        BOT.answer_callback_query(c.id, "Consultando...")

        try:
            telegram_sub, _, _, _, _ = dados_subrevenda_atual(c)

            # varredura antes da lista
            if SINCRONIZAR_ARQUIVO_SUBREVENDA:
                SINCRONIZAR_ARQUIVO_SUBREVENDA(telegram_sub)

            texto, usuarios = montar_texto_lista_usuarios_sub(telegram_sub)

            if len(texto) <= 3500:
                BOT.edit_message_text(
                    chat_id=c.message.chat.id,
                    message_id=c.message.message_id,
                    text=texto,
                    reply_markup=painel_lista_usuarios_sub_markup()
                )
            else:
                pdf_path = gerar_pdf_usuarios_sub(telegram_sub)

                try:
                    with open(pdf_path, "rb") as pdf_file:
                        BOT.send_document(
                            c.message.chat.id,
                            pdf_file,
                            caption=f"Lista de usuários ({len(usuarios)} no total)"
                        )
                finally:
                    if os.path.exists(pdf_path):
                        os.remove(pdf_path)

        except Exception as e:
            BOT.send_message(
                c.message.chat.id,
                f"❌ Erro ao listar usuários.\n<code>{ESC(e)}</code>"
            )
        finally:
            limpar_trava_sub(c.from_user.id)

        return True
    
    # =========================================================
    # USUÁRIOS ONLINE DO SUB
    # =========================================================
    if c.data == "sub_usuarios_online":
        BOT.answer_callback_query(c.id, "Consultando...")

        try:
            telegram_sub, _, _, _, _ = dados_subrevenda_atual(c)

            usuarios_online = obter_lista_usuarios_online_sub(telegram_sub)
            total_online = total_conexoes_online_sub(usuarios_online)
            texto = montar_texto_usuarios_online_sub(usuarios_online)

            if len(texto) <= 3500:
                BOT.edit_message_text(
                    chat_id=c.message.chat.id,
                    message_id=c.message.message_id,
                    text=texto,
                    reply_markup=painel_usuarios_online_sub_voltar_markup()
                )
            else:
                pdf_path = gerar_pdf_usuarios_online_sub(telegram_sub, usuarios_online)

                try:
                    with open(pdf_path, "rb") as pdf_file:
                        BOT.send_document(
                            c.message.chat.id,
                            pdf_file,
                            caption=f"Usuários online ({total_online} no total)"
                        )
                finally:
                    if os.path.exists(pdf_path):
                        os.remove(pdf_path)

        except Exception as e:
            BOT.send_message(
                c.message.chat.id,
                f"❌ Erro ao listar usuários online.\n<code>{ESC(e)}</code>"
            )
        finally:
            limpar_trava_sub(c.from_user.id)

        return True
    
    # =========================================================
    # CONSULTAR USUÁRIO
    # =========================================================
    if c.data == "sub_consultar_usuario":
        BOT.answer_callback_query(c.id, "Abrindo...")

        try:
            BOT.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        resetar_fluxo_sub(c.from_user.id)
        USER_DATA[c.from_user.id] = {"acao": "sub_consultar_usuario"}

        limpar_trava_sub(c.from_user.id)

        msg = BOT.send_message(
            c.message.chat.id,
            "Envie o nome do usuário ou UUID."
        )
        BOT.register_next_step_handler(msg, receber_consulta_usuario_sub)
        return True
    
    # =========================================================
    # RELATÓRIO DO SUB
    # =========================================================
    if c.data == "sub_relatorio":
        BOT.answer_callback_query(c.id, "Consultando...")

        try:
            BOT.edit_message_text(
                chat_id=c.message.chat.id,
                message_id=c.message.message_id,
                text="<b>Consultando...</b>"
            )

            telegram_sub, _, _, _, _ = dados_subrevenda_atual(c)

            if SINCRONIZAR_ARQUIVO_SUBREVENDA:
                SINCRONIZAR_ARQUIVO_SUBREVENDA(telegram_sub)

            BOT.edit_message_text(
                chat_id=c.message.chat.id,
                message_id=c.message.message_id,
                text=montar_texto_relatorio_sub(c),
                reply_markup=painel_relatorio_sub_markup()
            )

        except Exception as e:
            BOT.send_message(
                c.message.chat.id,
                f"❌ Erro ao gerar relatório.\n<code>{ESC(e)}</code>"
            )
        finally:
            limpar_trava_sub(c.from_user.id)

        return True
    
    if c.data in ["sub_auto_mes_1", "sub_auto_mes_2", "sub_auto_mes_3"]:
        BOT.answer_callback_query(c.id, "Continuando...")

        mapa_meses = {
            "sub_auto_mes_1": 1,
            "sub_auto_mes_2": 2,
            "sub_auto_mes_3": 3
        }
        meses = mapa_meses[c.data]

        if UUID_MODE_ATIVO():
            USER_DATA[c.from_user.id] = {
                "acao": "sub_add_usuario_auto",
                "meses": meses
            }

            kb = types.InlineKeyboardMarkup(row_width=2)
            kb.add(
                types.InlineKeyboardButton("XRay", callback_data="sub_auto_tipo_xray"),
                types.InlineKeyboardButton("Nenhum", callback_data="sub_auto_tipo_nenhum")
            )

            try:
                BOT.edit_message_text(
                    chat_id=c.message.chat.id,
                    message_id=c.message.message_id,
                    text=(
                        "<b>Criar usuário automático</b>\n\n"
                        "Escolha o tipo da configuração:"
                    ),
                    reply_markup=kb
                )
            except Exception as e:
                resetar_fluxo_sub(c.from_user.id)
                BOT.send_message(c.message.chat.id, f"❌ Erro ao abrir opções.\n<code>{ESC(e)}</code>")
            return True

        try:
            BOT.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        try:
            criar_usuario_auto_sub_final(c, meses, usar_v2ray=False)
        finally:
            limpar_trava_sub(c.from_user.id)
        return True

    if c.data in ["sub_auto_tipo_xray", "sub_auto_tipo_nenhum"]:
        BOT.answer_callback_query(c.id, "Criando...")

        dados = USER_DATA.get(c.from_user.id)
        if not dados or dados.get("acao") != "sub_add_usuario_auto" or "meses" not in dados:
            resetar_fluxo_sub(c.from_user.id)
            BOT.send_message(c.message.chat.id, "❌ Fluxo inválido. Digite /menu para tentar novamente.")
            return True

        meses = dados["meses"]
        usar_v2ray = c.data == "sub_auto_tipo_xray"

        try:
            BOT.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        try:
            criar_usuario_auto_sub_final(c, meses, usar_v2ray=usar_v2ray)
        finally:
            limpar_trava_sub(c.from_user.id)
        return True

    return False

# =========================================================
# GERAÇÃO DE USERNAME AUTOMÁTICO DA SUB-REVENDA
# =========================================================
def gerar_username_auto_sub():
    return f"rede{random.randint(100, 999)}"

# =========================================================
# FLUXO SUB - RECEBER USUÁRIO
# =========================================================
def receber_usuario_sub(message):
    if not BOT:
        return

    dados = USER_DATA.get(message.from_user.id, {})
    if dados.get("acao") != "sub_add_usuario":
        return

    if not message.text:
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(message.chat.id, "❌ Usuário inválido. Digite /menu para tentar novamente.")
        return

    username = message.text.strip()

    if not USERNAME_VALIDO(username):
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ Nome inválido. Use 4 a 8 caracteres com apenas letras e números.\nDigite /menu para tentar novamente."
        )
        return

    if USERNAME_APENAS_NUMEROS(username):
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ Nome inválido. Não pode ser apenas números.\nDigite /menu para tentar novamente."
        )
        return

    try:
        if USUARIO_EXISTE(username):
            USER_DATA.pop(message.from_user.id, None)
            BOT.send_message(
                message.chat.id,
                "❌ Usuário já existe. Digite /menu para tentar novamente."
            )
            return
    except Exception as e:
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            f"❌ Erro ao verificar usuários.\n<code>{ESC(e)}</code>"
        )
        return

    USER_DATA[message.from_user.id]["username"] = username

    msg = BOT.send_message(message.chat.id, "Envie o limite. Ex: 1")
    BOT.register_next_step_handler(msg, receber_limite_sub_usuario)


# =========================================================
# FLUXO SUB - RECEBER LIMITE
# =========================================================
def receber_limite_sub_usuario(message):
    if not BOT:
        return

    dados = USER_DATA.get(message.from_user.id, {})
    if dados.get("acao") != "sub_add_usuario":
        return

    if not message.text:
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(message.chat.id, "❌ Limite inválido. Digite /menu para tentar novamente.")
        return

    texto = message.text.strip()

    if not texto.isdigit() or int(texto) <= 0:
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(message.chat.id, "❌ Limite inválido. Digite /menu para tentar novamente.")
        return

    limite = int(texto)

    try:
        _, _, _, limite_restante, _ = dados_subrevenda_atual(message)
    except Exception as e:
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(message.chat.id, f"❌ Erro ao ler dados da sub revenda.\n<code>{ESC(e)}</code>")
        return

    if limite > limite_restante:
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            f"❌ Limite acima do permitido.\nSeu limite restante atual é <code>{ESC(limite_restante)}</code>.\nDigite /menu para tentar novamente."
        )
        return

    USER_DATA[message.from_user.id]["limite"] = limite

    msg = BOT.send_message(message.chat.id, "Envie a quantidade de dias. Ex: 30")
    BOT.register_next_step_handler(msg, receber_dias_sub_usuario)


# =========================================================
# FLUXO SUB - RECEBER DIAS
# =========================================================
def receber_dias_sub_usuario(message):
    if not BOT:
        return

    dados = USER_DATA.get(message.from_user.id, {})
    if dados.get("acao") != "sub_add_usuario":
        return

    if not message.text:
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(message.chat.id, "❌ Quantidade de dias inválida. Digite /menu para tentar novamente.")
        return

    texto = message.text.strip()

    if not texto.isdigit() or int(texto) <= 0:
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(message.chat.id, "❌ Quantidade de dias inválida. Digite /menu para tentar novamente.")
        return

    dias = int(texto)
    USER_DATA[message.from_user.id]["dias"] = dias

    if UUID_MODE_ATIVO():
        msg = BOT.send_message(
            message.chat.id,
            "Escolha o tipo da configuração:",
            reply_markup=teclado_tipo_sub()
        )
        BOT.register_next_step_handler(msg, receber_tipo_sub)
        return

    try:
        criar_usuario_sub_final(message, usar_v2ray=False)
    finally:
        limpar_trava_sub(message.from_user.id)


# =========================================================
# TECLADO DE TIPO DA CONFIG
# =========================================================
def teclado_tipo_sub():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.row(types.KeyboardButton("XRay"), types.KeyboardButton("Nenhum"))
    return kb


# =========================================================
# FLUXO SUB - RECEBER TIPO
# =========================================================
def receber_tipo_sub(message):
    if not BOT:
        return

    dados = USER_DATA.get(message.from_user.id, {})
    if dados.get("acao") != "sub_add_usuario":
        return

    if not message.text:
        try:
            criar_usuario_sub_final(message, usar_v2ray=False)
        finally:
            limpar_trava_sub(message.from_user.id)
        return

    tipo = message.text.strip().lower()

    usar_v2ray = (tipo == "xray")

    try:
        criar_usuario_sub_final(message, usar_v2ray=usar_v2ray)
    finally:
        limpar_trava_sub(message.from_user.id)


# =========================================================
# CRIAR USUÁRIO NORMAL DA SUB REVENDA
# =========================================================
def criar_usuario_sub_final(message, usar_v2ray):
    try:
        dados_fluxo = USER_DATA[message.from_user.id]

        username = dados_fluxo["username"]
        limite = dados_fluxo["limite"]
        dias = dados_fluxo["dias"]
        senha = f"{__import__('random').randint(1000, 9999)}"

        telegram_user, dono, limite_total, limite_restante, vencimento_sub = dados_subrevenda_atual(message)

        if limite > limite_restante:
            USER_DATA.pop(message.from_user.id, None)
            BOT.send_message(
                message.chat.id,
                f"❌ Limite acima do permitido.\nSeu limite restante atual é <code>{ESC(limite_restante)}</code>.\nDigite /menu para tentar novamente.",
                reply_markup=types.ReplyKeyboardRemove()
            )
            return

        retorno_v2ray = CRIAR_USUARIO_SISTEMA(
            username,
            senha,
            limite,
            dias,
            usar_v2ray=usar_v2ray
        )

        uuid_code = None
        if usar_v2ray and retorno_v2ray:
            uuid_code = EXTRAIR_UUID_VLESS(retorno_v2ray.get("v2ray"))

        novo_limite_restante = limite_restante - limite

        SALVAR_SUBREVENDA(
            dono=dono,
            telegram_user=telegram_user,
            limite_total=limite_total,
            limite_restante=novo_limite_restante,
            vencimento_formatado=vencimento_sub
        )

        ADICIONAR_USUARIO_SUB_ARQUIVO(
            telegram_user=telegram_user,
            username=username,
            senha=senha,
            limite=limite,
            dias_restantes=dias,
            uuid_code=uuid_code
        )

        vencimento_usuario = (datetime.now() + timedelta(days=dias)).strftime("%d/%m/%Y")

        texto_final = (
            "✅ <b>Usuário criado com sucesso!</b>\n\n"
            f"👤 <b>Usuário:</b> <code>{ESC(username)}</code>\n"
            f"🔑 <b>Senha:</b> <code>{ESC(senha)}</code>\n"
            f"👥 <b>Limite:</b> {ESC(limite)}\n"
            f"📅 <b>Vencimento:</b> {ESC(vencimento_usuario)}"
        )

        if uuid_code:
            texto_final += f"\n\n🆔 <b>UUID:</b> <code>{ESC(uuid_code)}</code>"

        BOT.send_message(
            message.chat.id,
            texto_final,
            reply_markup=types.ReplyKeyboardRemove()
        )

    except Exception as e:
        BOT.send_message(
            message.chat.id,
            f"❌ Falha ao criar usuário.\n<code>{ESC(e)}</code>",
            reply_markup=types.ReplyKeyboardRemove()
        )
    finally:
        USER_DATA.pop(message.from_user.id, None)


# =========================================================
# CRIAR USUÁRIO AUTOMÁTICO DA SUB REVENDA
# Formato: appxxx
# =========================================================
def criar_usuario_auto_sub_final(obj, meses, usar_v2ray):
    try:
        telegram_user, dono, limite_total, limite_restante, vencimento_sub = dados_subrevenda_atual(obj)

        limite = 1

        if limite > limite_restante:
            BOT.send_message(
                obj.message.chat.id if hasattr(obj, "message") else obj.chat.id,
                "❌ Sem limite disponível para criar usuário automático."
            )
            return

        username = None
        for _ in range(3):
            candidato = gerar_username_auto_sub()
            try:
                if not USUARIO_EXISTE(candidato):
                    username = candidato
                    break
            except Exception:
                continue

        if not username:
            BOT.send_message(
                obj.message.chat.id if hasattr(obj, "message") else obj.chat.id,
                "❌ Não foi possível gerar um usuário disponível. Digite /menu e tente novamente."
            )
            return

        senha = f"{__import__('random').randint(1000, 9999)}"

        hoje = datetime.now().date()
        vencimento = hoje + __import__('dateutil').relativedelta.relativedelta(months=+meses)
        dias = (vencimento - hoje).days
        if dias <= 0:
            dias = 1

        retorno_v2ray = CRIAR_USUARIO_SISTEMA(
            username,
            senha,
            limite,
            dias,
            usar_v2ray=usar_v2ray
        )

        uuid_code = None
        if usar_v2ray and retorno_v2ray:
            uuid_code = EXTRAIR_UUID_VLESS(retorno_v2ray.get("v2ray"))

        novo_limite_restante = limite_restante - limite

        SALVAR_SUBREVENDA(
            dono=dono,
            telegram_user=telegram_user,
            limite_total=limite_total,
            limite_restante=novo_limite_restante,
            vencimento_formatado=vencimento_sub
        )

        ADICIONAR_USUARIO_SUB_ARQUIVO(
            telegram_user=telegram_user,
            username=username,
            senha=senha,
            limite=limite,
            dias_restantes=dias,
            uuid_code=uuid_code
        )

        vencimento_formatado = vencimento.strftime("%d/%m/%Y")

        texto = (
            "✅ <b>Usuário criado com sucesso!</b>\n\n"
            f"👤 <b>Usuário:</b> <code>{ESC(username)}</code>\n"
            f"🔑 <b>Senha:</b> <code>{ESC(senha)}</code>\n"
            f"👥 <b>Limite:</b> {ESC(limite)}\n"
            f"📅 <b>Vencimento:</b> {ESC(vencimento_formatado)}"
        )

        if uuid_code:
            texto += f"\n\n🆔 <b>UUID:</b> <code>{ESC(uuid_code)}</code>"

        chat_id = obj.message.chat.id if hasattr(obj, "message") else obj.chat.id
        BOT.send_message(chat_id, texto)

    except Exception as e:
        chat_id = obj.message.chat.id if hasattr(obj, "message") else obj.chat.id
        BOT.send_message(
            chat_id,
            f"❌ Falha ao criar usuário automático.\n<code>{ESC(e)}</code>"
        )
    finally:
        USER_DATA.pop(obj.from_user.id, None)

def receber_usuario_alterar_limite_sub(message):
    if not BOT:
        return

    dados_fluxo = USER_DATA.get(message.from_user.id, {})
    if dados_fluxo.get("acao") != "sub_alt_limite":
        return

    if not message.text:
        resetar_fluxo_sub(message.from_user.id)
        BOT.send_message(message.chat.id, "❌ Usuário não encontrado. Digite /menu para tentar novamente.")
        return

    username_digitado = message.text.strip()

    try:
        telegram_sub, _, limite_total, limite_restante, vencimento = dados_subrevenda_atual(message)
        usuarios = LER_USUARIOS_SUBREVENDA_COMPLETOS(telegram_sub)
    except Exception as e:
        resetar_fluxo_sub(message.from_user.id)
        BOT.send_message(message.chat.id, f"❌ Erro ao ler dados da sub-revenda.\n<code>{ESC(e)}</code>")
        return

    usuario_encontrado = None
    for item in usuarios:
        if str(item.get("username", "")).strip() == username_digitado:
            usuario_encontrado = item
            break

    if not usuario_encontrado:
        resetar_fluxo_sub(message.from_user.id)
        BOT.send_message(message.chat.id, "❌ Usuário não encontrado. Digite /menu para tentar novamente.")
        return

    limite_atual_usuario = int(str(usuario_encontrado.get("limite", "0")).strip() or "0")

    USER_DATA[message.from_user.id]["telegram_sub"] = telegram_sub
    USER_DATA[message.from_user.id]["username"] = username_digitado
    USER_DATA[message.from_user.id]["limite_atual_usuario"] = limite_atual_usuario

    msg = BOT.send_message(
        message.chat.id,
        f"👥 Limite atual do usuário: <code>{ESC(limite_atual_usuario)}</code>\n\nInforme o novo limite."
    )
    BOT.register_next_step_handler(msg, receber_novo_limite_sub)

def receber_novo_limite_sub(message):
    if not BOT:
        return

    dados_fluxo = USER_DATA.get(message.from_user.id, {})
    if dados_fluxo.get("acao") != "sub_alt_limite":
        return

    if not message.text:
        resetar_fluxo_sub(message.from_user.id)
        BOT.send_message(message.chat.id, "❌ Limite inválido. Digite /menu para tentar novamente.")
        return

    texto = message.text.strip()
    if not texto.isdigit() or int(texto) <= 0:
        resetar_fluxo_sub(message.from_user.id)
        BOT.send_message(message.chat.id, "❌ Limite inválido. Digite /menu para tentar novamente.")
        return

    novo_limite = int(texto)

    try:
        telegram_sub = dados_fluxo["telegram_sub"]
        username = dados_fluxo["username"]
        limite_atual_usuario = int(dados_fluxo["limite_atual_usuario"])

        telegram_sub_real, dono, limite_total, limite_restante, vencimento = dados_subrevenda_atual(message)

        diferenca = novo_limite - limite_atual_usuario

        # se aumentou, precisa ter crédito disponível
        if diferenca > 0 and diferenca > limite_restante:
            resetar_fluxo_sub(message.from_user.id)
            BOT.send_message(message.chat.id, "❌ Limite insuficiente. Digite /menu para tentar novamente.")
            return

        ALTERAR_LIMITE_USUARIO_SISTEMA(username, novo_limite)

        usuarios = LER_USUARIOS_SUBREVENDA_COMPLETOS(telegram_sub)

        for item in usuarios:
            if str(item.get("username", "")).strip() == username:
                item["limite"] = str(novo_limite)
                break

        REESCREVER_ARQUIVO_SUBREVENDA(telegram_sub, usuarios)

        usado = 0
        for item in usuarios:
            try:
                usado += int(str(item.get("limite", "0")).strip())
            except:
                pass

        novo_limite_restante = limite_total - usado
        if novo_limite_restante < 0:
            novo_limite_restante = 0

        SALVAR_SUBREVENDA(
            dono=dono,
            telegram_user=telegram_sub,
            limite_total=limite_total,
            limite_restante=novo_limite_restante,
            vencimento_formatado=vencimento
        )

        BOT.send_message(
            message.chat.id,
            "✅ <b>Limite alterado!</b>\n\n"
            f"👤 <b>Usuário:</b> <code>{ESC(username)}</code>\n"
            f"👥 <b>Novo limite:</b> {ESC(novo_limite)}"
        )

    except Exception as e:
        BOT.send_message(
            message.chat.id,
            f"❌ Falha ao alterar limite.\n<code>{ESC(e)}</code>"
        )
    finally:
        resetar_fluxo_sub(message.from_user.id)

def receber_usuario_alterar_senha_sub(message):
    if not BOT:
        return

    dados_fluxo = USER_DATA.get(message.from_user.id, {})
    if dados_fluxo.get("acao") != "sub_alt_senha":
        return

    if not message.text:
        resetar_fluxo_sub(message.from_user.id)
        BOT.send_message(message.chat.id, "❌ Usuário não encontrado. Digite /menu para tentar novamente.")
        return

    username_digitado = message.text.strip()

    try:
        telegram_sub, _, _, _, _ = dados_subrevenda_atual(message)
        usuarios = LER_USUARIOS_SUBREVENDA_COMPLETOS(telegram_sub)
    except Exception as e:
        resetar_fluxo_sub(message.from_user.id)
        BOT.send_message(message.chat.id, f"❌ Erro ao ler dados da sub-revenda.\n<code>{ESC(e)}</code>")
        return

    usuario_encontrado = None
    for item in usuarios:
        if str(item.get("username", "")).strip() == username_digitado:
            usuario_encontrado = item
            break

    if not usuario_encontrado:
        resetar_fluxo_sub(message.from_user.id)
        BOT.send_message(message.chat.id, "❌ Usuário não encontrado. Digite /menu para tentar novamente.")
        return

    USER_DATA[message.from_user.id]["telegram_sub"] = telegram_sub
    USER_DATA[message.from_user.id]["username"] = username_digitado

    msg = BOT.send_message(
        message.chat.id,
        "Envie a nova senha."
    )
    BOT.register_next_step_handler(msg, receber_nova_senha_sub)

def receber_nova_senha_sub(message):
    if not BOT:
        return

    dados_fluxo = USER_DATA.get(message.from_user.id, {})
    if dados_fluxo.get("acao") != "sub_alt_senha":
        return

    if not message.text:
        resetar_fluxo_sub(message.from_user.id)
        BOT.send_message(message.chat.id, "❌ Senha inválida. Digite /menu para tentar novamente.")
        return

    nova_senha = message.text.strip()

    if not (4 <= len(nova_senha) <= 8) or not nova_senha.isalnum():
        resetar_fluxo_sub(message.from_user.id)
        BOT.send_message(
            message.chat.id,
            "❌ Senha inválida. Use 4 a 8 caracteres com letras e números.\nDigite /menu para tentar novamente."
        )
        return

    try:
        telegram_sub = dados_fluxo["telegram_sub"]
        username = dados_fluxo["username"]

        ALTERAR_SENHA_USUARIO_SISTEMA(username, nova_senha)

        usuarios = LER_USUARIOS_SUBREVENDA_COMPLETOS(telegram_sub)

        for item in usuarios:
            if str(item.get("username", "")).strip() == username:
                item["senha"] = nova_senha
                break

        REESCREVER_ARQUIVO_SUBREVENDA(telegram_sub, usuarios)

        BOT.send_message(
            message.chat.id,
            "✅ <b>Senha alterada!</b>\n\n"
            f"👤 <b>Usuário:</b> <code>{ESC(username)}</code>\n"
            f"🔑 <b>Nova senha:</b> <code>{ESC(nova_senha)}</code>"
        )

    except Exception as e:
        BOT.send_message(
            message.chat.id,
            f"❌ Falha ao alterar senha.\n<code>{ESC(e)}</code>"
        )
    finally:
        resetar_fluxo_sub(message.from_user.id)

def receber_usuario_alterar_data_sub(message):
    if not BOT:
        return

    dados_fluxo = USER_DATA.get(message.from_user.id, {})
    if dados_fluxo.get("acao") != "sub_alt_data":
        return

    if not message.text:
        resetar_fluxo_sub(message.from_user.id)
        BOT.send_message(message.chat.id, "❌ Usuário não encontrado. Digite /menu para tentar novamente.")
        return

    username_digitado = message.text.strip()

    try:
        telegram_sub, _, _, _, _ = dados_subrevenda_atual(message)
        usuarios = LER_USUARIOS_SUBREVENDA_COMPLETOS(telegram_sub)
    except Exception as e:
        resetar_fluxo_sub(message.from_user.id)
        BOT.send_message(message.chat.id, f"❌ Erro ao ler dados da sub-revenda.\n<code>{ESC(e)}</code>")
        return

    usuario_encontrado = None
    for item in usuarios:
        if str(item.get("username", "")).strip() == username_digitado:
            usuario_encontrado = item
            break

    if not usuario_encontrado:
        resetar_fluxo_sub(message.from_user.id)
        BOT.send_message(message.chat.id, "❌ Usuário não encontrado. Digite /menu para tentar novamente.")
        return

    USER_DATA[message.from_user.id]["telegram_sub"] = telegram_sub
    USER_DATA[message.from_user.id]["username_alterar_data_sub"] = username_digitado

    msg = BOT.send_message(
        message.chat.id,
        "Envie a quantidade de dias. Ex: 30"
    )
    BOT.register_next_step_handler(msg, receber_nova_data_alterar_data_sub)

def receber_nova_data_alterar_data_sub(message):
    if not BOT:
        return

    dados = USER_DATA.get(message.from_user.id, {})
    if dados.get("acao") != "sub_alt_data":
        return

    if not message.text:
        resetar_fluxo_sub(message.from_user.id)
        BOT.send_message(
            message.chat.id,
            "❌ Quantidade inválida. Digite /menu para tentar novamente."
        )
        return

    texto = message.text.strip()

    if not texto.isdigit() or int(texto) <= 0:
        resetar_fluxo_sub(message.from_user.id)
        BOT.send_message(
            message.chat.id,
            "❌ Quantidade inválida. Digite /menu para tentar novamente."
        )
        return

    dias = int(texto)
    username = dados.get("username_alterar_data_sub")

    if not username:
        resetar_fluxo_sub(message.from_user.id)
        BOT.send_message(
            message.chat.id,
            "❌ Fluxo inválido. Digite /menu para tentar novamente."
        )
        return

    try:
        telegram_sub = dados.get("telegram_sub")
        if not telegram_sub:
            telegram_sub, _, _, _, _ = dados_subrevenda_atual(message)

        ALTERAR_DATA_USUARIO_SISTEMA(username, dias)

        usuarios = LER_USUARIOS_SUBREVENDA_COMPLETOS(telegram_sub)

        alterou = False
        for item in usuarios:
            if str(item.get("username", "")).strip() == username:
                item["dias"] = str(dias)
                alterou = True
                break

        if not alterou:
            raise Exception("Usuário não encontrado no arquivo da sub-revenda.")

        REESCREVER_ARQUIVO_SUBREVENDA(telegram_sub, usuarios)

        nova_data = datetime.now() + timedelta(days=dias)
        nova_data_formatada = nova_data.strftime("%d/%m/%Y")

        BOT.send_message(
            message.chat.id,
            "✅ <b>Data alterada!</b>\n\n"
            f"👤 <b>Usuário:</b> <code>{ESC(username)}</code>\n"
            f"📅 <b>Nova data:</b> <code>{ESC(nova_data_formatada)}</code>"
        )

    except Exception as e:
        BOT.send_message(
            message.chat.id,
            f"❌ Erro ao alterar data.\n<code>{ESC(e)}</code>"
        )
    finally:
        resetar_fluxo_sub(message.from_user.id)

# =========================================================
# FLUXO SUB - RECEBER USUÁRIO PARA RENOVAR
# =========================================================
def receber_usuario_renovar_sub(message):
    if not BOT:
        return

    dados_fluxo = USER_DATA.get(message.from_user.id, {})
    if dados_fluxo.get("acao") != "sub_renovar":
        return

    if not message.text:
        resetar_fluxo_sub(message.from_user.id)
        BOT.send_message(message.chat.id, "❌ Usuário não encontrado. Digite /menu para tentar novamente.")
        return

    username_digitado = message.text.strip()

    try:
        telegram_sub, _, _, _, _ = dados_subrevenda_atual(message)
        usuarios = LER_USUARIOS_SUBREVENDA_COMPLETOS(telegram_sub)
    except Exception as e:
        resetar_fluxo_sub(message.from_user.id)
        BOT.send_message(message.chat.id, f"❌ Erro ao ler dados da sub-revenda.\n<code>{ESC(e)}</code>")
        return

    usuario_encontrado = None
    for item in usuarios:
        if str(item.get("username", "")).strip() == username_digitado:
            usuario_encontrado = item
            break

    if not usuario_encontrado:
        resetar_fluxo_sub(message.from_user.id)
        BOT.send_message(message.chat.id, "❌ Usuário não encontrado. Digite /menu para tentar novamente.")
        return

    USER_DATA[message.from_user.id]["telegram_sub"] = telegram_sub
    USER_DATA[message.from_user.id]["username_renovar_sub"] = username_digitado

    try:
        vencimento_atual = OBTER_DATA_VENCIMENTO_USUARIO(username_digitado)
        hoje = datetime.now()
        
        if vencimento_atual.date() >= hoje.date():
            data_base = vencimento_atual
        else:
            data_base = hoje
        
        novo_vencimento = CALCULAR_RENOVACAO_MAIS_UM_MES(data_base)
        dias_para_novo_vencimento = CALCULAR_DIAS_ATE_DATA_FUTURA(novo_vencimento)

        ALTERAR_DATA_USUARIO_SISTEMA(username_digitado, dias_para_novo_vencimento)

        usuarios = LER_USUARIOS_SUBREVENDA_COMPLETOS(telegram_sub)

        alterou = False
        for item in usuarios:
            if str(item.get("username", "")).strip() == username_digitado:
                item["dias"] = str(dias_para_novo_vencimento)
                alterou = True
                break

        if not alterou:
            raise Exception("Usuário não encontrado no arquivo da sub-revenda.")

        REESCREVER_ARQUIVO_SUBREVENDA(telegram_sub, usuarios)

        vencimento_formatado = novo_vencimento.strftime("%d/%m/%Y")

        BOT.send_message(
            message.chat.id,
            "✅ <b>Usuário renovado!</b>\n\n"
            f"👤 <b>Usuário:</b> <code>{ESC(username_digitado)}</code>\n"
            f"📅 <b>Nova Data:</b> {ESC(vencimento_formatado)}"
        )

    except Exception as e:
        BOT.send_message(
            message.chat.id,
            f"❌ Falha ao renovar usuário.\n<code>{ESC(e)}</code>"
        )
    finally:
        resetar_fluxo_sub(message.from_user.id)

# =========================================================
# FLUXO SUB - DELETAR USUÁRIO
# =========================================================
def receber_usuario_deletar_sub(message):
    if not BOT:
        return

    dados_fluxo = USER_DATA.get(message.from_user.id, {})
    if dados_fluxo.get("acao") != "sub_del_usuario":
        return

    if not message.text:
        resetar_fluxo_sub(message.from_user.id)
        BOT.send_message(
            message.chat.id,
            "❌ Usuário não encontrado. Digite /menu para tentar novamente."
        )
        return

    username_digitado = message.text.strip()

    try:
        telegram_sub, _, _, _, _ = dados_subrevenda_atual(message)
        usuarios = LER_USUARIOS_SUBREVENDA_COMPLETOS(telegram_sub)
    except Exception as e:
        resetar_fluxo_sub(message.from_user.id)
        BOT.send_message(
            message.chat.id,
            f"❌ Erro ao ler dados da sub-revenda.\n<code>{ESC(e)}</code>"
        )
        return

    usuario_encontrado = None
    for item in usuarios:
        if str(item.get("username", "")).strip() == username_digitado:
            usuario_encontrado = item
            break

    if not usuario_encontrado:
        resetar_fluxo_sub(message.from_user.id)
        BOT.send_message(
            message.chat.id,
            "❌ Usuário não encontrado. Digite /menu para tentar novamente."
        )
        return

    try:
        DELETAR_USUARIO_SISTEMA(username_digitado)

        if SINCRONIZAR_ARQUIVO_SUBREVENDA:
            SINCRONIZAR_ARQUIVO_SUBREVENDA(telegram_sub)

        BOT.send_message(
            message.chat.id,
            f"🗑️ Usuário <b>{ESC(username_digitado)}</b> deletado com sucesso!"
        )

    except Exception as e:
        BOT.send_message(
            message.chat.id,
            f"❌ Falha ao deletar usuário.\n<code>{ESC(e)}</code>"
        )
    finally:
        resetar_fluxo_sub(message.from_user.id)

# =========================================================
# VERIFICA SE USUÁRIO DO SUB ESTÁ EXPIRADO
# =========================================================
def usuario_sub_esta_expirado(item):
    try:
        dias = int(str(item.get("dias", "0")).strip())
        return dias <= 0
    except:
        return True


# =========================================================
# LISTAR EXPIRADOS DO SUB
# Consulta apenas o banco local daquele sub
# =========================================================
def obter_usuarios_expirados_sub(telegram_sub):
    expirados = []

    try:
        usuarios = LER_USUARIOS_SUBREVENDA_COMPLETOS(telegram_sub)

        for item in usuarios:
            try:
                username = str(item.get("username", "")).strip()
                if not username:
                    continue

                # se não existe mais no sistema, a varredura limpa isso antes
                if not USUARIO_EXISTE(username):
                    continue

                if usuario_sub_esta_expirado(item):
                    expirados.append(username)
            except:
                continue
    except:
        pass

    return expirados

# =========================================================
# QUEBRAR TEXTO LONGO EM PARTES
# =========================================================
def quebrar_texto_em_partes(texto, limite=3500):
    if len(texto) <= limite:
        return [texto]

    linhas = texto.split("\n")
    partes = []
    atual = []

    for linha in linhas:
        teste = "\n".join(atual + [linha])
        if len(teste) > limite and atual:
            partes.append("\n".join(atual))
            atual = [linha]
        else:
            atual.append(linha)

    if atual:
        partes.append("\n".join(atual))

    return partes

# =========================================================
# MONTAR TEXTO DOS EXPIRADOS DO SUB
# =========================================================
def montar_texto_expirados_sub(expirados):
    linhas = ["🗑️ <b>USUÁRIOS EXPIRADOS</b>", ""]

    if expirados:
        for username in expirados:
            linhas.append(f"👤 <b>Usuário:</b> <code>{ESC(username)}</code>")
    else:
        linhas.append("Nenhum usuário expirado encontrado.")

    linhas.append("")
    linhas.append(f"📊 <b>Total:</b> {len(expirados)} usuário{'s' if len(expirados) != 1 else ''}")

    return "\n".join(linhas)

# =========================================================
# TEXTO DA LISTA DE USUÁRIOS DO SUB
# Mesmo formato da revenda
# =========================================================
def montar_texto_lista_usuarios_sub(telegram_sub):
    usuarios = LER_USUARIOS_SUBREVENDA_COMPLETOS(telegram_sub)
    dados = LER_DADOS_SUBREVENDA(telegram_sub)
    limite_restante = int(dados.get("limite_restante", "0"))

    linhas = []
    linhas.append("<b>⚠️ LISTA DE USUÁRIOS ⚠️</b>")
    linhas.append("")
    linhas.append(f"<b>Total usuários:</b> <code>{ESC(len(usuarios))}</code>")
    linhas.append(f"<b>Limite restante:</b> <code>{ESC(limite_restante)}</code>")
    linhas.append("")
    linhas.append("<b>USUÁRIO | SENHA | LIMITE | DATA</b>")

    for item in usuarios:
        try:
            dias_int = int(str(item.get("dias", "")).strip())
        except:
            dias_int = 0

        if dias_int <= 0:
            data_txt = "Venceu"
        else:
            data_txt = f"{dias_int} DIAS"

        linha = f"{item['username']} • {item['senha']} • {item['limite']} • {data_txt}"
        linhas.append(f"<blockquote>{ESC(linha)}</blockquote>")

    uuids = [u for u in usuarios if str(u.get("uuid", "")).strip()]

    if uuids:
        linhas.append("")
        linhas.append("<b>XRAY DISPONÍVEL:</b>")
        linhas.append("")

        for item in uuids:
            linhas.append(
                f"<blockquote>Usuário: {ESC(item['username'])}\nUUID: {ESC(item['uuid'])}</blockquote>"
            )

    texto = "\n".join(linhas)
    return texto, usuarios

# =========================================================
# GERAR PDF DA LISTA DE USUÁRIOS DO SUB
# Mesmo estilo da revenda
# =========================================================
def gerar_pdf_usuarios_sub(telegram_sub):
    dados = LER_DADOS_SUBREVENDA(telegram_sub)

    vencimento = str(dados.get("vencimento", "")).strip()
    limite_total = int(dados.get("limite_total", "0"))
    limite_restante = int(dados.get("limite_restante", "0"))

    usuarios = LER_USUARIOS_SUBREVENDA_COMPLETOS(telegram_sub)

    nome_pdf = f"usuarios_sub_{random.randint(100,999)}.pdf"
    pdf_path = os.path.join(tempfile.gettempdir(), nome_pdf)

    c = canvas.Canvas(pdf_path, pagesize=A4)
    largura_pagina, altura_pagina = A4

    y = altura_pagina - 40

    # Cabeçalho principal
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(largura_pagina / 2, y, "LISTA DE USUÁRIOS")
    y -= 25

    c.setFont("Helvetica", 10)
    c.drawString(40, y, f"Total usuários: {len(usuarios)}")
    y -= 15
    c.drawString(40, y, f"Limite total: {limite_total}")
    y -= 15
    c.drawString(40, y, f"Limite restante: {limite_restante}")
    y -= 15
    c.drawString(40, y, f"Vencimento do sub: {vencimento}")
    y -= 25

    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, y, "USUÁRIO | SENHA | LIMITE | DATA")
    y -= 18

    c.setFont("Helvetica", 10)

    for item in usuarios:
        try:
            dias_int = int(str(item.get("dias", "")).strip())
        except:
            dias_int = 0

        if dias_int <= 0:
            data_txt = "Venceu"
        else:
            data_txt = f"{dias_int} DIAS"

        linha = f"{item['username']} • {item['senha']} • {item['limite']} • {data_txt}"

        if y < 50:
            c.showPage()
            y = altura_pagina - 40
            c.setFont("Helvetica", 10)

        c.drawString(40, y, linha[:110])
        y -= 15

    uuids = [u for u in usuarios if str(u.get("uuid", "")).strip()]

    if uuids:
        if y < 80:
            c.showPage()
            y = altura_pagina - 40

        y -= 10
        c.setFont("Helvetica-Bold", 11)
        c.drawString(40, y, "XRAY DISPONÍVEL:")
        y -= 20
        c.setFont("Helvetica", 10)

        for item in uuids:
            bloco1 = f"Usuário: {item['username']}"
            bloco2 = f"UUID: {item['uuid']}"

            if y < 60:
                c.showPage()
                y = altura_pagina - 40
                c.setFont("Helvetica", 10)

            c.drawString(40, y, bloco1[:110])
            y -= 15
            c.drawString(40, y, bloco2[:110])
            y -= 20

    c.save()
    return pdf_path

# =========================================================
# PEGAR OS USERNAMES DO BANCO DAQUELE SUB
# =========================================================
def obter_usernames_do_sub(telegram_sub):
    usuarios_sub = set()

    try:
        usuarios = LER_USUARIOS_SUBREVENDA_COMPLETOS(telegram_sub)
        for item in usuarios:
            username = str(item.get("username", "")).strip()
            if username:
                usuarios_sub.add(username)
    except:
        pass

    return usuarios_sub


# =========================================================
# JUNTAR DADOS DOS USUÁRIOS ONLINE - SOMENTE DAQUELE SUB
# =========================================================
def obter_lista_usuarios_online_sub(telegram_sub):
    online_dict = OBTER_USUARIOS_ONLINE_PLUGIN()

    if not online_dict:
        return []

    usuarios_sub = obter_usernames_do_sub(telegram_sub)

    # mapa de limites a partir do banco local da sub
    mapa_limites = {}
    try:
        usuarios = LER_USUARIOS_SUBREVENDA_COMPLETOS(telegram_sub)
        for item in usuarios:
            try:
                mapa_limites[str(item.get("username", "")).strip()] = int(str(item.get("limite", "0")).strip())
            except:
                mapa_limites[str(item.get("username", "")).strip()] = 0
    except:
        pass

    resultado = []

    for username in sorted(online_dict.keys(), key=lambda x: x.lower()):
        if username not in usuarios_sub:
            continue

        qtd_online = int(online_dict.get(username, 0))
        limite = int(mapa_limites.get(username, 0))
        tempo, tempo_segundos = OBTER_MAIOR_TEMPO_ONLINE_USUARIO(username)

        resultado.append({
            "username": username,
            "online": qtd_online,
            "limit": limite,
            "tempo": tempo,
            "tempo_segundos": tempo_segundos
        })

    return resultado

def total_conexoes_online_sub(usuarios_online):
    total = 0

    for item in usuarios_online or []:
        try:
            total += int(str(item.get("online", 0)).strip() or "0")
        except:
            continue

    return total


# =========================================================
# MONTAR TEXTO DOS USUÁRIOS ONLINE DO SUB
# Mesmo formato da revenda
# =========================================================
def montar_texto_usuarios_online_sub(usuarios_online):
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
        linha = f"{item['username']} {item['online']}/{item['limit']} ⏳{item['tempo']}"
        linhas.append(f"<blockquote>🟢 {ESC(linha)}</blockquote>")

    linhas.append("")
    linhas.append(f"<b><i>Total Usuários: {total_conexoes_online_sub(usuarios_online)} onlines</i></b>")

    return "\n".join(linhas)

# =========================================================
# GERAR PDF DOS USUÁRIOS ONLINE DO SUB
# Mesmo estilo da revenda
# =========================================================
def gerar_pdf_usuarios_online_sub(telegram_sub, usuarios_online):
    nome_pdf = f"usuarios_online_sub_{random.randint(100,999)}.pdf"
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

        return altura - 95

    def desenhar_cabecalho_tabela(y):
        c.setFont("Helvetica-Bold", 10)
        x = margem
        for titulo, largura_coluna in colunas:
            c.drawString(x, y, titulo)
            x += largura_coluna
        return y - 15

    y = desenhar_primeira_pagina()
    y = desenhar_cabecalho_tabela(y)

    c.setFont("Helvetica", 10)

    for item in usuarios_online:
        if y < rodape:
            c.showPage()
            y = altura - 40
            y = desenhar_cabecalho_tabela(y)
            c.setFont("Helvetica", 10)

        x = margem
        valores = [
            item["username"],
            str(item["online"]),
            str(item["limit"]),
            str(item["tempo"])
        ]

        for valor, (_, largura_coluna) in zip(valores, colunas):
            c.drawString(x, y, str(valor)[:22])
            x += largura_coluna

        y -= 15

    c.save()
    return pdf_path

# =========================================================
# LOCALIZAR USUÁRIO DO SUB POR USERNAME OU UUID
# =========================================================
def localizar_usuario_sub_por_username_ou_uuid(telegram_sub, termo):
    termo = str(termo or "").strip().lower()
    if not termo:
        return None

    usuarios = LER_USUARIOS_SUBREVENDA_COMPLETOS(telegram_sub)

    for item in usuarios:
        username = str(item.get("username", "")).strip()
        uuid = str(item.get("uuid", "")).strip()

        if not uuid and OBTER_UUID_DISPONIVEL_USUARIO:
            try:
                uuid = str(OBTER_UUID_DISPONIVEL_USUARIO(username)).strip()
            except:
                uuid = ""

        if username.lower() == termo:
            item_encontrado = dict(item)
            if uuid:
                item_encontrado["uuid"] = uuid
            return item_encontrado

        if uuid and uuid.lower() == termo:
            item_encontrado = dict(item)
            item_encontrado["uuid"] = uuid
            return item_encontrado

    return None

# =========================================================
# MONTAR TEXTO DA CONSULTA DO USUÁRIO DO SUB
# =========================================================
def montar_texto_consulta_usuario_sub(item):
    username = str(item.get("username", "")).strip()
    senha = str(item.get("senha", "")).strip()
    limite = str(item.get("limite", "")).strip()
    uuid = str(item.get("uuid", "")).strip()

    if not uuid and OBTER_UUID_DISPONIVEL_USUARIO:
        try:
            uuid = str(OBTER_UUID_DISPONIVEL_USUARIO(username)).strip()
        except:
            uuid = ""

    try:
        dias_restantes = int(str(item.get("dias", "0")).strip())
    except:
        dias_restantes = 0

    try:
        data_expiracao = OBTER_DATA_EXPIRACAO_USUARIO(username)
        if data_expiracao:
            expira_em = data_expiracao.strftime("%d/%m/%Y")
        else:
            expira_em = "Venceu"
    except:
        expira_em = "Venceu"

    if dias_restantes <= 0:
        restam_txt = "0 dias"
    elif dias_restantes == 1:
        restam_txt = "1 dia"
    else:
        restam_txt = f"{dias_restantes} dias"

    linhas = [
        "📋 <b>Dados Do Usuário</b>",
        "",
        f"• Usuário: <code>{ESC(username)}</code>",
        f"• Senha: <code>{ESC(senha)}</code>",
        f"• Limite: <code>{ESC(limite)}</code>",
        f"• Expira em: <code>{ESC(expira_em)}</code>",
        f"<blockquote>• Restam: {ESC(restam_txt)}</blockquote>",
    ]

    if uuid:
        linhas.extend([
            "",
            "UUID:",
            f"<code>{ESC(uuid)}</code>"
        ])

    return "\n".join(linhas)

# =========================================================
# FLUXO SUB - CONSULTAR USUÁRIO
# Consulta por username ou UUID
# Faz varredura do sub antes da busca
# Mesmo comportamento da revenda: sem botão de voltar
# =========================================================
def receber_consulta_usuario_sub(message):
    if not BOT:
        return

    dados_fluxo = USER_DATA.get(message.from_user.id, {})
    if dados_fluxo.get("acao") != "sub_consultar_usuario":
        return

    if not message.text:
        resetar_fluxo_sub(message.from_user.id)
        BOT.send_message(
            message.chat.id,
            "❌ Usuário não encontrado. Digite /menu para tentar novamente."
        )
        return

    termo = message.text.strip()

    try:
        telegram_sub, _, _, _, _ = dados_subrevenda_atual(message)

        # varredura do sub antes da consulta
        if SINCRONIZAR_ARQUIVO_SUBREVENDA:
            SINCRONIZAR_ARQUIVO_SUBREVENDA(telegram_sub)

        item = localizar_usuario_sub_por_username_ou_uuid(telegram_sub, termo)

        if not item:
            BOT.send_message(
                message.chat.id,
                "❌ Usuário não encontrado. Digite /menu para tentar novamente."
            )
            return

        texto = montar_texto_consulta_usuario_sub(item)

        BOT.send_message(
            message.chat.id,
            texto
        )

    except Exception as e:
        BOT.send_message(
            message.chat.id,
            f"❌ Erro ao consultar usuário.\n<code>{ESC(e)}</code>"
        )
    finally:
        resetar_fluxo_sub(message.from_user.id)

# =========================================================
# CALCULAR DIAS RESTANTES DO VENCIMENTO DO SUB
# =========================================================
def calcular_dias_restantes_sub(vencimento_str):
    try:
        data_venc = datetime.strptime(str(vencimento_str).strip(), "%d/%m/%Y").date()
        hoje = datetime.now().date()
        return (data_venc - hoje).days
    except:
        return 0
    
# =========================================================
# TEXTO DO RELATÓRIO DO SUB
# =========================================================
def montar_texto_relatorio_sub(obj):
    telegram_user, dono, limite_total, limite_restante, vencimento = dados_subrevenda_atual(obj)
    dias_restantes = calcular_dias_restantes_sub(vencimento)

    return (
        "<b>RELATÓRIO DE ACESSOS</b>\n\n"
        f"👤 <b>Usuário:</b> {ESC(telegram_user)}\n"
        f"📌 <b>Fornecedor:</b> {ESC(dono)}\n\n"
        f"📦 <b>Limite total:</b> {ESC(limite_total)}\n"
        f"📉 <b>Limite restante:</b> {ESC(limite_restante)}\n"
        f"📅 <b>Vencimento:</b> {ESC(vencimento)}\n"
        f"⏳ <b>Dias restantes:</b> {ESC(dias_restantes)}"
    )


# =========================================================
# FLUXO SUB - CRIAR TESTE
# =========================================================
def receber_horas_teste_sub(message):
    if not BOT:
        return

    dados = USER_DATA.get(message.from_user.id, {})
    if dados.get("acao") != "sub_add_teste":
        return

    if not message.text:
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(message.chat.id, "❌ Horas inválidas. Digite /menu para tentar novamente.")
        return

    texto = message.text.strip()

    if not texto.isdigit():
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(message.chat.id, "❌ Horas inválidas. Digite /menu para tentar novamente.")
        return

    horas = int(texto)

    if horas <= 0 or horas > 24:
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ O teste deve ter entre 1 e 24 horas.\nDigite /menu para tentar novamente."
        )
        return

    try:
        telegram_user, dono, limite_total, limite_restante, vencimento_sub = dados_subrevenda_atual(message)

        if limite_restante < 1:
            USER_DATA.pop(message.from_user.id, None)
            BOT.send_message(
                message.chat.id,
                "❌ Você não tem limite restante para criar teste.\nDigite /menu para tentar novamente."
            )
            return

        username = GERAR_USERNAME_DISPONIVEL("teste", max_tentativas=3)

        if not username:
            USER_DATA.pop(message.from_user.id, None)
            BOT.send_message(
                message.chat.id,
                "❌ Não foi possível gerar um teste disponível. Digite /menu e tente novamente."
            )
            return

        senha = f"{__import__('random').randint(1000, 9999)}"
        limite = 1
        dias_sistema = 2
        expira_em = datetime.now() + timedelta(hours=horas)

        usar_v2ray = UUID_MODE_ATIVO()

        retorno_v2ray = CRIAR_USUARIO_SISTEMA(
            username, senha, limite, dias_sistema, usar_v2ray=usar_v2ray
        )

        ADICIONAR_TESTE_ARQUIVO(username, horas, expira_em)

        uuid_code = None
        if usar_v2ray and retorno_v2ray:
            uuid_code = EXTRAIR_UUID_VLESS(retorno_v2ray.get("v2ray"))

        novo_limite_restante = limite_restante - 1

        SALVAR_SUBREVENDA(
            dono=dono,
            telegram_user=telegram_user,
            limite_total=limite_total,
            limite_restante=novo_limite_restante,
            vencimento_formatado=vencimento_sub
        )

        ADICIONAR_TESTE_SUB_ARQUIVO(
            telegram_user=telegram_user,
            username=username,
            senha=senha,
            limite=1,
            dias_restantes=dias_sistema,
            uuid_code=uuid_code
        )

        BOT.send_message(
            message.chat.id,
            MONTAR_MSG_TESTE(username, senha, horas, uuid_code),
            reply_markup=types.ReplyKeyboardRemove()
        )

    except Exception as e:
        BOT.send_message(
            message.chat.id,
            f"❌ Falha ao criar teste.\n<code>{ESC(e)}</code>",
            reply_markup=types.ReplyKeyboardRemove()
        )
    finally:
        USER_DATA.pop(message.from_user.id, None)
