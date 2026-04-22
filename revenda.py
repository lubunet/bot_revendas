from datetime import datetime, timedelta
from telebot import types
import time
import os
import random
import tempfile
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

BOT = None
ESC = None
PREVIEW_URL = None
USER_DATA = None
REV_USERS_BUSY = {}
REV_BUSY_TIMEOUT = 20

OBTER_TELEGRAM_ATUAL = None
LER_DADOS_REVENDA = None
SALVAR_REVENDA = None
CRIAR_USUARIO_SISTEMA = None
SINCRONIZAR_ARQUIVO_REVENDA = None
RECALCULAR_LIMITE_RESTANTE_REVENDA = None
ALTERAR_SENHA_USUARIO_SISTEMA = None
ALTERAR_LIMITE_USUARIO_SISTEMA = None
ALTERAR_DATA_USUARIO_SISTEMA = None
OBTER_DATA_VENCIMENTO_USUARIO = None
CALCULAR_RENOVACAO_MAIS_UM_MES = None
CALCULAR_DIAS_ATE_DATA_FUTURA = None
LISTAR_USUARIOS_DA_REVENDA = None
DELETAR_USUARIO_SISTEMA = None
USUARIO_EXISTE = None
OBTER_DATA_EXPIRACAO_USUARIO = None
OBTER_UUID_DISPONIVEL_USUARIO = None
LER_USUARIOS_REVENDA_COMPLETOS = None
USERNAME_VALIDO = None
USERNAME_APENAS_NUMEROS = None
ADICIONAR_USUARIO_REVENDA_ARQUIVO = None
ADICIONAR_TESTE_REVENDA_ARQUIVO = None
EXTRAIR_UUID_VLESS = None
UUID_MODE_ATIVO = None
GERAR_USERNAME_DISPONIVEL = None
ADICIONAR_TESTE_ARQUIVO = None
MONTAR_MSG_TESTE = None
OBTER_USUARIOS_ONLINE_PLUGIN = None
OBTER_MAIOR_TEMPO_ONLINE_USUARIO = None
SUBREVENDA_EXISTE = None
SALVAR_SUBREVENDA_ARQUIVO = None
DELETAR_SUBREVENDA_ARQUIVO = None
LER_DADOS_SUBREVENDA = None
CALCULAR_LIMITE_USADO_REAL_SUBREVENDA = None
SINCRONIZAR_ARQUIVO_SUBREVENDA = None
LER_USUARIOS_SUBREVENDA_COMPLETOS = None
SUSPENDER_SUBREVENDA_AUTOMATICAMENTE = None
SUBREVENDA_SUSPENSA = None
SUSPENDER_SUBREVENDA_MANUALMENTE = None
REATIVAR_SUBREVENDA = None
RENOVAR_SUBREVENDA = None
REVENDA_EXISTE = None
ADMIN_ID = None
SUB_DIR = None

# =========================================================
# INICIAR MÓDULO REVENDA
# =========================================================
def init_revenda_module(
    bot,
    esc,
    preview_url,
    user_data,
    obter_telegram_atual,
    ler_dados_revenda,
    salvar_revenda,
    criar_usuario_sistema,
    username_valido,
    username_apenas_numeros,
    adicionar_usuario_revenda_arquivo,
    adicionar_teste_revenda_arquivo,
    extrair_uuid_vless,
    uuid_mode_ativo,
    gerar_username_disponivel,
    adicionar_teste_arquivo,
    montar_msg_teste,
    sincronizar_arquivo_revenda,
    recalcular_limite_restante_revenda,
    alterar_limite_usuario_sistema,
    listar_usuarios_da_revenda,
    ler_usuarios_revenda_completos,
    alterar_senha_usuario_sistema,
    alterar_data_usuario_sistema,
    obter_data_vencimento_usuario,
    calcular_renovacao_mais_um_mes,
    calcular_dias_ate_data_futura,
    deletar_usuario_sistema,
    usuario_existe,
    obter_data_expiracao_usuario,
    obter_uuid_disponivel_usuario,
    obter_usuarios_online_plugin,
    obter_maior_tempo_online_usuario,
    subrevenda_existe,
    salvar_subrevenda_arquivo,
    deletar_subrevenda_arquivo,
    ler_dados_subrevenda,
    calcular_limite_usado_real_subrevenda,
    sincronizar_arquivo_subrevenda,
    ler_usuarios_subrevenda_completos,
    suspender_subrevenda_automaticamente,
    subrevenda_suspensa,
    suspender_subrevenda_manualmente,
    reativar_subrevenda,
    renovar_subrevenda,
    revenda_existe,
    admin_id,
    sub_dir
):
    global BOT, ESC, PREVIEW_URL, USER_DATA
    global OBTER_TELEGRAM_ATUAL, LER_DADOS_REVENDA, SALVAR_REVENDA
    global CRIAR_USUARIO_SISTEMA, USERNAME_VALIDO, USERNAME_APENAS_NUMEROS
    global ADICIONAR_USUARIO_REVENDA_ARQUIVO, ADICIONAR_TESTE_REVENDA_ARQUIVO
    global EXTRAIR_UUID_VLESS, UUID_MODE_ATIVO
    global GERAR_USERNAME_DISPONIVEL, ADICIONAR_TESTE_ARQUIVO, MONTAR_MSG_TESTE
    global SINCRONIZAR_ARQUIVO_REVENDA, RECALCULAR_LIMITE_RESTANTE_REVENDA
    global ALTERAR_LIMITE_USUARIO_SISTEMA, LISTAR_USUARIOS_DA_REVENDA, LER_USUARIOS_REVENDA_COMPLETOS
    global ALTERAR_SENHA_USUARIO_SISTEMA, ALTERAR_DATA_USUARIO_SISTEMA
    global OBTER_DATA_VENCIMENTO_USUARIO, CALCULAR_RENOVACAO_MAIS_UM_MES, CALCULAR_DIAS_ATE_DATA_FUTURA
    global DELETAR_USUARIO_SISTEMA, USUARIO_EXISTE, OBTER_DATA_EXPIRACAO_USUARIO
    global OBTER_UUID_DISPONIVEL_USUARIO
    global OBTER_USUARIOS_ONLINE_PLUGIN, OBTER_MAIOR_TEMPO_ONLINE_USUARIO
    global SUBREVENDA_EXISTE, SALVAR_SUBREVENDA_ARQUIVO, DELETAR_SUBREVENDA_ARQUIVO, LER_DADOS_SUBREVENDA
    global CALCULAR_LIMITE_USADO_REAL_SUBREVENDA
    global SINCRONIZAR_ARQUIVO_SUBREVENDA, LER_USUARIOS_SUBREVENDA_COMPLETOS
    global SUSPENDER_SUBREVENDA_AUTOMATICAMENTE, SUBREVENDA_SUSPENSA
    global SUSPENDER_SUBREVENDA_MANUALMENTE
    global REATIVAR_SUBREVENDA
    global RENOVAR_SUBREVENDA
    global REVENDA_EXISTE, ADMIN_ID
    global SUB_DIR


    BOT = bot
    ESC = esc
    PREVIEW_URL = preview_url
    USER_DATA = user_data

    OBTER_TELEGRAM_ATUAL = obter_telegram_atual
    LER_DADOS_REVENDA = ler_dados_revenda
    SALVAR_REVENDA = salvar_revenda
    CRIAR_USUARIO_SISTEMA = criar_usuario_sistema
    USERNAME_VALIDO = username_valido
    USERNAME_APENAS_NUMEROS = username_apenas_numeros
    ADICIONAR_USUARIO_REVENDA_ARQUIVO = adicionar_usuario_revenda_arquivo
    ADICIONAR_TESTE_REVENDA_ARQUIVO = adicionar_teste_revenda_arquivo
    EXTRAIR_UUID_VLESS = extrair_uuid_vless
    UUID_MODE_ATIVO = uuid_mode_ativo
    GERAR_USERNAME_DISPONIVEL = gerar_username_disponivel
    ADICIONAR_TESTE_ARQUIVO = adicionar_teste_arquivo
    MONTAR_MSG_TESTE = montar_msg_teste
    SINCRONIZAR_ARQUIVO_REVENDA = sincronizar_arquivo_revenda
    RECALCULAR_LIMITE_RESTANTE_REVENDA = recalcular_limite_restante_revenda
    ALTERAR_LIMITE_USUARIO_SISTEMA = alterar_limite_usuario_sistema
    LISTAR_USUARIOS_DA_REVENDA = listar_usuarios_da_revenda
    LER_USUARIOS_REVENDA_COMPLETOS = ler_usuarios_revenda_completos
    ALTERAR_SENHA_USUARIO_SISTEMA = alterar_senha_usuario_sistema
    ALTERAR_DATA_USUARIO_SISTEMA = alterar_data_usuario_sistema
    OBTER_DATA_VENCIMENTO_USUARIO = obter_data_vencimento_usuario
    CALCULAR_RENOVACAO_MAIS_UM_MES = calcular_renovacao_mais_um_mes
    CALCULAR_DIAS_ATE_DATA_FUTURA = calcular_dias_ate_data_futura
    DELETAR_USUARIO_SISTEMA = deletar_usuario_sistema
    USUARIO_EXISTE = usuario_existe
    OBTER_DATA_EXPIRACAO_USUARIO = obter_data_expiracao_usuario
    OBTER_UUID_DISPONIVEL_USUARIO = obter_uuid_disponivel_usuario
    OBTER_USUARIOS_ONLINE_PLUGIN = obter_usuarios_online_plugin
    OBTER_MAIOR_TEMPO_ONLINE_USUARIO = obter_maior_tempo_online_usuario
    SUBREVENDA_EXISTE = subrevenda_existe
    SALVAR_SUBREVENDA_ARQUIVO = salvar_subrevenda_arquivo
    DELETAR_SUBREVENDA_ARQUIVO = deletar_subrevenda_arquivo
    LER_DADOS_SUBREVENDA = ler_dados_subrevenda
    CALCULAR_LIMITE_USADO_REAL_SUBREVENDA = calcular_limite_usado_real_subrevenda
    SINCRONIZAR_ARQUIVO_SUBREVENDA = sincronizar_arquivo_subrevenda
    LER_USUARIOS_SUBREVENDA_COMPLETOS = ler_usuarios_subrevenda_completos
    SUSPENDER_SUBREVENDA_AUTOMATICAMENTE = suspender_subrevenda_automaticamente
    SUBREVENDA_SUSPENSA = subrevenda_suspensa
    SUSPENDER_SUBREVENDA_MANUALMENTE = suspender_subrevenda_manualmente
    REATIVAR_SUBREVENDA = reativar_subrevenda
    RENOVAR_SUBREVENDA = renovar_subrevenda
    REVENDA_EXISTE = revenda_existe
    ADMIN_ID = admin_id
    SUB_DIR = sub_dir

# =========================================================
# CANCELAR FLUXO ANTERIOR DO USUÁRIO
# Garante que só a última ação aberta continue válida
# =========================================================
def resetar_fluxo_revenda(user_id):
    try:
        BOT.clear_step_handler_by_chat_id(user_id)
    except:
        pass

    USER_DATA.pop(user_id, None)
    limpar_trava_revenda(user_id)

# =========================================================
# PROTEÇÃO CONTRA CLIQUES REPETIDOS NO PAINEL REVENDA
# =========================================================
def callback_revenda_protegido(callback_data):
    protegidos = {
        "rev_add_usuario",
        "rev_add_teste",
        "rev_add_usuario_auto",
        "rev_alt_limite",
        "rev_alt_senha",
        "rev_alt_data",
        "rev_renovar",
        "rev_del_usuario",
        "rev_del_expirados",
        "rev_confirmar_del_expirados",
        "rev_listar_usuarios",
        "rev_usuarios_online",
        "rev_consultar_usuario",
        "rev_subrevendas",
        "rev_add_subrevenda",
        "rev_del_subrevenda",
        "rev_alt_data_subrevenda",
        "rev_alt_limite_subrevenda",
        "rev_relatorio_subrevendas",
        "rev_relatorio_individual_subrevenda",
        "rev_suspender_subrevenda",
        "rev_renovar_subrevenda",
        "rev_relatorio"
    }
    return callback_data in protegidos


def obter_usuario_existente_revenda(telegram_user, username):
    username = str(username or "").strip()
    if not username:
        return None

    try:
        usuarios = LER_USUARIOS_REVENDA_COMPLETOS(telegram_user)
    except:
        return None

    for item in usuarios:
        if str(item.get("username", "")).strip() == username:
            return item

    return None


def revenda_usuario_esta_ocupado(user_id):
    agora = time.time()
    expira_em = REV_USERS_BUSY.get(user_id, 0)

    if expira_em > agora:
        return True

    if user_id in REV_USERS_BUSY:
        REV_USERS_BUSY.pop(user_id, None)

    return False


def iniciar_trava_revenda(user_id, segundos=REV_BUSY_TIMEOUT):
    REV_USERS_BUSY[user_id] = time.time() + segundos


def limpar_trava_revenda(user_id):
    REV_USERS_BUSY.pop(user_id, None)

# =========================================================
# MARKUP DO PAINEL REVENDA
# =========================================================
def painel_revenda_markup():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("Adicionar usuário", callback_data="rev_add_usuario"),
        types.InlineKeyboardButton("Criar teste", callback_data="rev_add_teste")
    )
    kb.add(
        types.InlineKeyboardButton("Criar usuário automático", callback_data="rev_add_usuario_auto")
    )
    kb.add(
        types.InlineKeyboardButton("Alterar Limite", callback_data="rev_alt_limite"),
        types.InlineKeyboardButton("Alterar Senha", callback_data="rev_alt_senha")
    )
    kb.add(
        types.InlineKeyboardButton("Alterar Data", callback_data="rev_alt_data"),
        types.InlineKeyboardButton("Renovar", callback_data="rev_renovar")
    )
    kb.add(
        types.InlineKeyboardButton("Deletar usuário", callback_data="rev_del_usuario"),
        types.InlineKeyboardButton("Deletar expirados", callback_data="rev_del_expirados")
    )
    kb.add(
        types.InlineKeyboardButton("Listar usuários", callback_data="rev_listar_usuarios"),
        types.InlineKeyboardButton("Usuários Online", callback_data="rev_usuarios_online")
    )
    kb.add(
        types.InlineKeyboardButton("Consultar usuário", callback_data="rev_consultar_usuario")
    )
    kb.add(
        types.InlineKeyboardButton("SUB-REVENDAS", callback_data="rev_subrevendas")
    )
    kb.add(
        types.InlineKeyboardButton("Relatório", callback_data="rev_relatorio")
    )
    return kb


# =========================================================
# MARKUP DO RELATÓRIO REVENDA
# =========================================================
def painel_relatorio_revenda_markup():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("⬅️ Voltar", callback_data="rev_voltar_menu"))
    return kb

# =========================================================
# MARKUP DE VOLTAR DO RELATÓRIO INDIVIDUAL DA SUB-REVENDA
# =========================================================
def painel_relatorio_individual_subrevenda_markup():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("⬅️ Voltar", callback_data="rev_subrevendas"))
    return kb

# =========================================================
# MARKUP DO PAINEL DE SUB REVENDAS
# =========================================================
def painel_subrevendas_markup():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton("Cadastrar sub-revenda", callback_data="rev_add_subrevenda"))
    kb.add(types.InlineKeyboardButton("Deletar sub-revenda", callback_data="rev_del_subrevenda"))
    kb.add(types.InlineKeyboardButton("Alterar data sub-revenda", callback_data="rev_alt_data_subrevenda"))
    kb.add(types.InlineKeyboardButton("Alterar limite sub-revenda", callback_data="rev_alt_limite_subrevenda"))
    kb.add(types.InlineKeyboardButton("Relatorio sub-revendas", callback_data="rev_relatorio_subrevendas"))
    kb.add(types.InlineKeyboardButton("Relatorio individual sub-revenda", callback_data="rev_relatorio_individual_subrevenda"))
    kb.add(
        types.InlineKeyboardButton("Suspender", callback_data="rev_suspender_subrevenda"),
        types.InlineKeyboardButton("Renovar", callback_data="rev_renovar_subrevenda")
    )
    kb.add(types.InlineKeyboardButton("⬅️ Voltar", callback_data="rev_voltar_menu"))
    return kb

# =========================================================
# MARKUP DA LISTA DE USUÁRIOS DA REVENDA
# =========================================================
def painel_lista_usuarios_revenda_markup():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("⬅️ Voltar", callback_data="rev_voltar_menu"))
    return kb

# =========================================================
# MARKUP DE VOLTAR DA LISTA DE USUÁRIOS ONLINE DA REVENDA
# =========================================================
def painel_usuarios_online_revenda_voltar_markup():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("⬅️ Voltar", callback_data="rev_voltar_menu"))
    return kb

# =========================================================
# MARKUP DOS EXPIRADOS DA REVENDA
# =========================================================
def painel_expirados_revenda_markup(tem_expirados=True):
    kb = types.InlineKeyboardMarkup(row_width=1)

    if tem_expirados:
        kb.add(types.InlineKeyboardButton("🗑️ Deletar expirados", callback_data="rev_confirmar_del_expirados"))

    kb.add(types.InlineKeyboardButton("⬅️ Voltar", callback_data="rev_voltar_menu"))
    return kb

# =========================================================
# TECLADO DE TIPO DA CONFIG
# =========================================================
def teclado_tipo_revenda():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.row(types.KeyboardButton("XRay"), types.KeyboardButton("Nenhum"))
    return kb


# =========================================================
# DADOS DA REVENDA ATUAL
# =========================================================
def dados_revenda_atual(obj):
    telegram_user = OBTER_TELEGRAM_ATUAL(obj)
    if not telegram_user:
        raise Exception("Telegram da revenda não encontrado.")

    dados = LER_DADOS_REVENDA(telegram_user)

    limite_total = int(dados.get("limite_total", "0"))
    limite_restante = int(dados.get("limite_restante", "0"))
    vencimento = dados.get("vencimento", "-")

    return telegram_user, limite_total, limite_restante, vencimento


# =========================================================
# CAMINHO DO ARQUIVO DA REVENDA
# =========================================================
def caminho_arquivo_revenda_local(telegram_user):
    return f"/root/revenda/dados_rev/{telegram_user.lstrip('@')}.txt"

# =========================================================
# LISTAR SUB-REVENDAS DE UMA REVENDA
# =========================================================
def listar_subrevendas_da_revenda_local(telegram_revenda):
    pasta = "/root/revenda/dados_sub"
    resultado = []

    try:
        if not os.path.exists(pasta):
            return []

        for nome in os.listdir(pasta):
            if not nome.endswith(".txt"):
                continue

            telegram_sub = "@" + nome[:-4]

            try:
                dados_sub = LER_DADOS_SUBREVENDA(telegram_sub)
                dono = str(dados_sub.get("dono", "")).strip()

                if dono == telegram_revenda:
                    resultado.append(telegram_sub)
            except:
                continue

    except:
        pass

    return sorted(resultado, key=lambda x: x.lower())

# =========================================================
# PEGAR DADOS RESUMIDOS DE UMA SUB-REVENDA PARA O RELATÓRIO
# =========================================================
def obter_dados_relatorio_subrevenda(telegram_sub):
    dados = LER_DADOS_SUBREVENDA(telegram_sub)

    limite_total = int(str(dados.get("limite_total", "0")).strip())
    vencimento = str(dados.get("vencimento", "")).strip()
    status = "suspenso" if SUBREVENDA_SUSPENSA and SUBREVENDA_SUSPENSA(telegram_sub) else "ativo"

    usado = CALCULAR_LIMITE_USADO_REAL_SUBREVENDA(telegram_sub)

    if usado < 0:
        usado = 0

    return {
        "telegram_user": telegram_sub,
        "usado": usado,
        "limite_total": limite_total,
        "vencimento": vencimento,
        "status": status
    }


# =========================================================
# LISTA COMPLETA DE DADOS PARA O RELATÓRIO DAS SUB-REVENDAS
# =========================================================
def obter_lista_relatorio_subrevendas(telegram_revenda):
    resultado = []

    for telegram_sub in listar_subrevendas_da_revenda_local(telegram_revenda):
        try:
            item = obter_dados_relatorio_subrevenda(telegram_sub)
            resultado.append(item)
        except:
            continue

    resultado.sort(key=lambda x: x["telegram_user"].lower())
    return resultado

def total_conexoes_online_revenda(usuarios_online):
    total = 0

    for item in usuarios_online or []:
        try:
            total += int(str(item.get("online", 0)).strip() or "0")
        except:
            continue

    return total

# =========================================================
# GERAR PDF TEMPORÁRIO DO RELATÓRIO DE SUB-REVENDAS
# Mesmo estilo do admin
# =========================================================
def gerar_pdf_relatorio_subrevendas(subrevendas):
    nome_pdf = f"relatorio_subrevendas_{random.randint(100, 999)}.pdf"
    pdf_path = os.path.join(tempfile.gettempdir(), nome_pdf)

    c = canvas.Canvas(pdf_path, pagesize=A4)
    largura_pagina, altura_pagina = A4

    rodape = 40

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
        titulo = "SUB-REVENDAS LUBU NET"
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

    for item in subrevendas:
        if y < rodape:
            y = nova_pagina()
            c.setFont("Helvetica", 10)

        usuario = cortar_texto(item["telegram_user"], largura_max=colunas[0][1])
        uso_limite = cortar_texto(f"{item['usado']}/{item['limite_total']}", largura_max=colunas[1][1])
        expiracao = cortar_texto(item["vencimento"], largura_max=colunas[2][1])
        status = cortar_texto(item["status"], largura_max=colunas[3][1])

        linha = [usuario, uso_limite, expiracao, status]

        x = x_inicial
        altura_linha = 22

        for i, valor in enumerate(linha):
            largura_coluna = colunas[i][1]
            c.rect(x, y, largura_coluna, altura_linha)
            c.drawString(x + 8, y + 7, valor)
            x += largura_coluna

        y -= altura_linha

    c.save()
    return pdf_path

# =========================================================
# LER LINHAS DE ACESSOS DA REVENDA
# =========================================================
def linhas_acessos_revenda(telegram_user):
    caminho = caminho_arquivo_revenda_local(telegram_user)
    linhas = []

    try:
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

                linhas.append(linha)
    except:
        pass

    return linhas

# =========================================================
# ATUALIZAR APENAS A DATA DE UM USUÁRIO NO ARQUIVO DA REVENDA
# Mantém senha, limite e uuid
# =========================================================
def atualizar_data_usuario_revenda_local(telegram_user, username, novos_dias):
    caminho = caminho_arquivo_revenda_local(telegram_user)
    if not caminho:
        return False

    linhas_novas = []
    alterou = False

    try:
        with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
            for linha in f:
                linha_sem_quebra = linha.rstrip("\n")
                texto = linha_sem_quebra.strip()

                if not texto:
                    linhas_novas.append(linha_sem_quebra)
                    continue

                if "=" in texto:
                    linhas_novas.append(linha_sem_quebra)
                    continue

                partes = texto.split()
                if len(partes) < 4:
                    linhas_novas.append(linha_sem_quebra)
                    continue

                user_linha = partes[0].strip()

                if user_linha == username:
                    senha = partes[1].strip()
                    limite = partes[2].strip()
                    uuid_code = partes[4].strip() if len(partes) >= 5 else ""

                    nova_linha = f"{username} {senha} {limite} {novos_dias}"
                    if uuid_code:
                        nova_linha += f" {uuid_code}"

                    linhas_novas.append(nova_linha)
                    alterou = True
                else:
                    linhas_novas.append(linha_sem_quebra)

        with open(caminho, "w", encoding="utf-8") as f:
            for linha in linhas_novas:
                f.write(linha + "\n")

        return alterou
    except:
        return False
    
# =========================================================
# CALCULAR RESTANTE DA REVENDA
# =========================================================
def restante_revenda(vencimento_str):
    try:
        data_venc = datetime.strptime(vencimento_str, "%d/%m/%Y").date()
        hoje = datetime.now().date()
        dias = (data_venc - hoje).days

        if dias < 0:
            return "Venceu"

        return str(dias)
    except:
        return "Desconhecido"


# =========================================================
# TEXTO DO MENU REVENDA
# =========================================================
def texto_menu_revenda(obj):
    nome = ESC(obj.from_user.first_name or "Usuário")
    telegram_user, limite_total, limite_restante, vencimento = dados_revenda_atual(obj)

    return (
        f"🚀 <b>{nome}</b>, Bem Vindoª Ao Painel REVENDA LUBU NET\n\n"
    )


# =========================================================
# TEXTO DO RELATÓRIO REVENDA
# =========================================================
def texto_relatorio_revenda(obj):
    telegram_user, limite_total, limite_restante, vencimento = dados_revenda_atual(obj)
    restante = restante_revenda(vencimento)

    linhas = [
        "<b>RELATÓRIO REVENDA</b>",
        "",
        f"👤 <b>Usuário:</b> {ESC(telegram_user)}",
        "",
        f"📦 <b>Limite total:</b> <code>{ESC(limite_total)}</code>",
        f"📉 <b>Limite restante:</b> <code>{ESC(limite_restante)}</code>",
        f"📅 <b>Vencimento:</b> <code>{ESC(vencimento)}</code>",
        f"⏳ <b>Dias restantes:</b> <code>{ESC(restante)}</code>",
    ]

    subs = listar_subrevendas_da_revenda_relatorio(telegram_user)

    if subs:
        linhas.append("")
        linhas.append("📌 <b>Limite gasto com sub-revendas</b>")

        for telegram_sub in subs:
            try:
                dados_sub = LER_DADOS_SUBREVENDA(telegram_sub)
                limite_sub = int(str(dados_sub.get("limite_total", "0")).strip() or "0")
                linhas.append(f"{ESC(telegram_sub)} - limite atual: {ESC(limite_sub)}")
            except:
                continue

    return "\n".join(linhas)


# =========================================================
# ABRIR MENU DA REVENDA
# =========================================================
def abrir_menu_revenda(message):
    preview = types.LinkPreviewOptions(
        is_disabled=False,
        url="https://a.imagem.app/GG1KMm.png",
        show_above_text=True,
        prefer_large_media=True
    )

    BOT.send_message(
        message.chat.id,
        texto_menu_revenda(message),
        reply_markup=painel_revenda_markup(),
        link_preview_options=preview
    )


# =========================================================
# CALLBACKS DA REVENDA
# =========================================================
def handle_callback_revenda(c):
    # -----------------------------------------------------
    # PROTEÇÃO CONTRA CLIQUES REPETIDOS
    # -----------------------------------------------------
    if callback_revenda_protegido(c.data):
        if revenda_usuario_esta_ocupado(c.from_user.id):
            BOT.answer_callback_query(c.id, "Aguarde...", show_alert=True)
            return True

        iniciar_trava_revenda(c.from_user.id)

    if c.data == "rev_add_usuario":
        try:
            _, _, limite_restante, _ = dados_revenda_atual(c)
        except:
            limite_restante = 0

        # sem créditos -> apaga o painel e bloqueia
        if limite_restante <= 0:
            try:
                BOT.delete_message(c.message.chat.id, c.message.message_id)
            except:
                pass

            resetar_fluxo_revenda(c.from_user.id)

            BOT.send_message(
                c.message.chat.id,
                "❌ <b>Vc esta sem creditos!</b>\n\nExecute /menu para voltar"
            )
            return True

        # último crédito -> só avisa
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

        resetar_fluxo_revenda(c.from_user.id)
        USER_DATA[c.from_user.id] = {"acao": "rev_add_usuario"}

        msg = BOT.send_message(c.message.chat.id, "Envie o nome do usuário.")
        BOT.register_next_step_handler(msg, receber_usuario_revenda)
        return True

    if c.data == "rev_add_teste":
        try:
            _, _, limite_restante, _ = dados_revenda_atual(c)
        except:
            limite_restante = 0

        # sem créditos -> apaga o painel e bloqueia
        if limite_restante <= 0:
            try:
                BOT.delete_message(c.message.chat.id, c.message.message_id)
            except:
                pass

            resetar_fluxo_revenda(c.from_user.id)

            BOT.send_message(
                c.message.chat.id,
                "❌ <b>Vc esta sem creditos!</b>\n\nExecute /menu para voltar"
            )
            return True

        # último crédito -> só avisa
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

        resetar_fluxo_revenda(c.from_user.id)
        USER_DATA[c.from_user.id] = {"acao": "rev_add_teste"}

        msg = BOT.send_message(
            c.message.chat.id,
            "Envie a quantidade de horas do teste. Máximo: 24"
        )
        BOT.register_next_step_handler(msg, receber_horas_teste_revenda)
        return True
    
    if c.data == "rev_add_usuario_auto":
        try:
            _, _, limite_restante, _ = dados_revenda_atual(c)
        except:
            limite_restante = 0

        # sem créditos -> apaga o painel e bloqueia
        if limite_restante <= 0:
            try:
                BOT.delete_message(c.message.chat.id, c.message.message_id)
            except:
                pass

            resetar_fluxo_revenda(c.from_user.id)

            BOT.send_message(
                c.message.chat.id,
                "❌ <b>Vc esta sem creditos!</b>\n\nExecute /menu para voltar"
            )
            return True

        # último crédito -> só avisa
        if limite_restante == 1:
            BOT.answer_callback_query(
                c.id,
                "Esse é seu último crédito.",
                show_alert=True
            )
        else:
            BOT.answer_callback_query(c.id, "Abrindo...")

        resetar_fluxo_revenda(c.from_user.id)
        USER_DATA[c.from_user.id] = {"acao": "rev_add_usuario_auto"}

        try:
            BOT.edit_message_text(
                chat_id=c.message.chat.id,
                message_id=c.message.message_id,
                text=(
                    "<b>Criar usuário automático</b>\n\n"
                    "Escolha abaixo a validade do usuário:"
                ),
                reply_markup=painel_revenda_auto_meses_markup()
            )
        except Exception as e:
            BOT.send_message(
                c.message.chat.id,
                f"❌ Erro ao abrir painel.\n<code>{ESC(e)}</code>"
            )
        return True

    if c.data == "rev_alt_limite":
        BOT.answer_callback_query(c.id, "Abrindo...")

        try:
            telegram_user, _, _, _ = dados_revenda_atual(c)
        except Exception as e:
            limpar_trava_revenda(c.from_user.id)
            BOT.send_message(
                c.message.chat.id,
                f"❌ Erro ao ler dados da revenda.\n<code>{ESC(e)}</code>"
            )
            return True

        try:
            # varredura apenas dessa revenda antes do fluxo
            if SINCRONIZAR_ARQUIVO_REVENDA:
                SINCRONIZAR_ARQUIVO_REVENDA(telegram_user)

            if RECALCULAR_LIMITE_RESTANTE_REVENDA:
                RECALCULAR_LIMITE_RESTANTE_REVENDA(telegram_user)
        except:
            pass

        try:
            BOT.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        resetar_fluxo_revenda(c.from_user.id)
        USER_DATA[c.from_user.id] = {"acao": "rev_alt_limite"}

        msg = BOT.send_message(
            c.message.chat.id,
            "Envie o nome do usuário."
        )
        BOT.register_next_step_handler(msg, receber_usuario_alterar_limite_revenda)
        return True
    
    if c.data == "rev_alt_senha":
        BOT.answer_callback_query(c.id, "Abrindo...")

        try:
            telegram_user, _, _, _ = dados_revenda_atual(c)
        except Exception as e:
            limpar_trava_revenda(c.from_user.id)
            BOT.send_message(
                c.message.chat.id,
                f"❌ Erro ao ler dados da revenda.\n<code>{ESC(e)}</code>"
            )
            return True

        try:
            # varredura apenas dessa revenda antes do fluxo
            if SINCRONIZAR_ARQUIVO_REVENDA:
                SINCRONIZAR_ARQUIVO_REVENDA(telegram_user)

            if RECALCULAR_LIMITE_RESTANTE_REVENDA:
                RECALCULAR_LIMITE_RESTANTE_REVENDA(telegram_user)
        except:
            pass

        try:
            BOT.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        resetar_fluxo_revenda(c.from_user.id)
        USER_DATA[c.from_user.id] = {"acao": "rev_alt_senha"}

        msg = BOT.send_message(
            c.message.chat.id,
            "Envie o nome do usuário."
        )
        BOT.register_next_step_handler(msg, receber_usuario_alterar_senha_revenda)
        return True
    
    if c.data == "rev_alt_data":
        BOT.answer_callback_query(c.id, "Abrindo...")

        try:
            BOT.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        resetar_fluxo_revenda(c.from_user.id)
        USER_DATA[c.from_user.id] = {"acao": "rev_alt_data"}

        msg = BOT.send_message(
            c.message.chat.id,
            "Envie o nome do usuário."
        )
        BOT.register_next_step_handler(msg, receber_usuario_alterar_data_revenda)
        return True
    
    if c.data == "rev_renovar":
        BOT.answer_callback_query(
            c.id,
            "Este usuário será renovado em 1 mês.",
            show_alert=True
        )

        try:
            BOT.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        resetar_fluxo_revenda(c.from_user.id)
        USER_DATA[c.from_user.id] = {"acao": "rev_renovar"}

        msg = BOT.send_message(
            c.message.chat.id,
            "Envie o nome do usuário."
        )
        BOT.register_next_step_handler(msg, receber_usuario_renovar_revenda)
        return True
    
    if c.data == "rev_del_usuario":
        BOT.answer_callback_query(c.id, "Abrindo...")

        try:
            BOT.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        resetar_fluxo_revenda(c.from_user.id)
        USER_DATA[c.from_user.id] = {"acao": "rev_del_usuario"}

        msg = BOT.send_message(
            c.message.chat.id,
            "Envie o nome do usuário."
        )
        BOT.register_next_step_handler(msg, receber_usuario_deletar_revenda)
        return True
    
    if c.data == "rev_del_expirados":
        BOT.answer_callback_query(c.id, "Verificando...")

        try:
            telegram_user, _, _, _ = dados_revenda_atual(c)
        except Exception as e:
            limpar_trava_revenda(c.from_user.id)
            BOT.send_message(
                c.message.chat.id,
                f"❌ Erro ao ler dados da revenda.\n<code>{ESC(e)}</code>"
            )
            return True

        try:
            BOT.edit_message_text(
                chat_id=c.message.chat.id,
                message_id=c.message.message_id,
                text="⏳ <b>Verificando expirados...</b>"
            )

            try:
                if SINCRONIZAR_ARQUIVO_REVENDA:
                    SINCRONIZAR_ARQUIVO_REVENDA(telegram_user)

                if RECALCULAR_LIMITE_RESTANTE_REVENDA:
                    RECALCULAR_LIMITE_RESTANTE_REVENDA(telegram_user)
            except:
                pass

            expirados = obter_usuarios_expirados_revenda(telegram_user)

            USER_DATA[c.from_user.id] = {
                "acao": "rev_del_expirados",
                "expirados": expirados
            }

            limpar_trava_revenda(c.from_user.id)

            if expirados:
                BOT.edit_message_text(
                    chat_id=c.message.chat.id,
                    message_id=c.message.message_id,
                    text=montar_texto_expirados_revenda(expirados),
                    reply_markup=painel_expirados_revenda_markup(tem_expirados=True)
                )
            else:
                BOT.edit_message_text(
                    chat_id=c.message.chat.id,
                    message_id=c.message.message_id,
                    text="🗑️ <b>Nenhum usuário expirado.</b>",
                    reply_markup=painel_expirados_revenda_markup(tem_expirados=False)
                )

        except Exception as e:
            limpar_trava_revenda(c.from_user.id)
            BOT.send_message(
                c.message.chat.id,
                f"❌ Erro ao verificar expirados.\n<code>{ESC(e)}</code>"
            )
        return True
    
    if c.data == "rev_confirmar_del_expirados":
        BOT.answer_callback_query(c.id, "Apagando...")

        dados = USER_DATA.get(c.from_user.id)
        if not dados or dados.get("acao") != "rev_del_expirados":
            limpar_trava_revenda(c.from_user.id)
            USER_DATA.pop(c.from_user.id, None)
            BOT.send_message(
                c.message.chat.id,
                "❌ Fluxo inválido. Digite /menu para tentar novamente."
            )
            return True

        expirados = dados.get("expirados", [])
        apagados = 0

        try:
            telegram_user, _, _, _ = dados_revenda_atual(c)

            BOT.edit_message_text(
                chat_id=c.message.chat.id,
                message_id=c.message.message_id,
                text="⏳ <b>Apagando usuários expirados...</b>"
            )

            for username in expirados:
                try:
                    if USUARIO_EXISTE(username):
                        DELETAR_USUARIO_SISTEMA(username)
                        apagados += 1
                except:
                    continue

            try:
                if SINCRONIZAR_ARQUIVO_REVENDA:
                    SINCRONIZAR_ARQUIVO_REVENDA(telegram_user)

                if RECALCULAR_LIMITE_RESTANTE_REVENDA:
                    RECALCULAR_LIMITE_RESTANTE_REVENDA(telegram_user)
            except:
                pass

            USER_DATA.pop(c.from_user.id, None)
            limpar_trava_revenda(c.from_user.id)

            BOT.edit_message_text(
                chat_id=c.message.chat.id,
                message_id=c.message.message_id,
                text=f"✅ <b>{apagados} usuário{'s' if apagados != 1 else ''} expirado{'s' if apagados != 1 else ''} foram deletados!</b>",
                reply_markup=painel_relatorio_revenda_markup()
            )

        except Exception as e:
            limpar_trava_revenda(c.from_user.id)
            USER_DATA.pop(c.from_user.id, None)
            BOT.send_message(
                c.message.chat.id,
                f"❌ Erro ao apagar expirados.\n<code>{ESC(e)}</code>"
            )
        return True
    
    if c.data in ["rev_auto_mes_1", "rev_auto_mes_2", "rev_auto_mes_3"]:
        BOT.answer_callback_query(c.id, "Continuando...")

        mapa_meses = {
            "rev_auto_mes_1": 1,
            "rev_auto_mes_2": 2,
            "rev_auto_mes_3": 3
        }
        meses = mapa_meses[c.data]

        if UUID_MODE_ATIVO():
            USER_DATA[c.from_user.id] = {
                "acao": "rev_add_usuario_auto",
                "meses": meses
            }

            try:
                BOT.edit_message_text(
                    chat_id=c.message.chat.id,
                    message_id=c.message.message_id,
                    text=(
                        "<b>Criar usuário automático</b>\n\n"
                        "Escolha o tipo da configuração:"
                    ),
                    reply_markup=painel_revenda_auto_tipo_markup()
                )
            except Exception as e:
                USER_DATA.pop(c.from_user.id, None)
                BOT.send_message(
                    c.message.chat.id,
                    f"❌ Erro ao abrir opções.\n<code>{ESC(e)}</code>"
                )
            return True

        try:
            BOT.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        criar_usuario_auto_revenda_final(c, meses, usar_v2ray=False)
        return True

    if c.data in ["rev_auto_tipo_xray", "rev_auto_tipo_nenhum"]:
        BOT.answer_callback_query(c.id, "Criando...")

        dados = USER_DATA.get(c.from_user.id)
        if not dados or dados.get("acao") != "rev_add_usuario_auto" or "meses" not in dados:
            USER_DATA.pop(c.from_user.id, None)
            BOT.send_message(
                c.message.chat.id,
                "❌ Fluxo inválido. Digite /menu para tentar novamente."
            )
            return True

        meses = dados["meses"]
        usar_v2ray = c.data == "rev_auto_tipo_xray"

        try:
            BOT.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        criar_usuario_auto_revenda_final(c, meses, usar_v2ray=usar_v2ray)
        return True

    if c.data == "rev_listar_usuarios":
        BOT.answer_callback_query(c.id, "Consultando...")

        msg_consultando = None

        try:
            telegram_user = OBTER_TELEGRAM_ATUAL(c)
            if not telegram_user:
                limpar_trava_revenda(c.from_user.id)
                BOT.send_message(
                    c.message.chat.id,
                    "❌ Telegram da revenda não encontrado."
                )
                return True

            # roda a varredura apenas dessa revenda
            try:
                if SINCRONIZAR_ARQUIVO_REVENDA:
                    SINCRONIZAR_ARQUIVO_REVENDA(telegram_user)

                if RECALCULAR_LIMITE_RESTANTE_REVENDA:
                    RECALCULAR_LIMITE_RESTANTE_REVENDA(telegram_user)
            except:
                pass

            texto, usuarios = montar_texto_lista_usuarios_revenda(telegram_user)

            # Se couber no Telegram, aí sim substitui o painel
            if len(texto) <= 3500:
                limpar_trava_revenda(c.from_user.id)

                BOT.edit_message_text(
                    chat_id=c.message.chat.id,
                    message_id=c.message.message_id,
                    text=texto,
                    reply_markup=painel_lista_usuarios_revenda_markup()
                )

            else:
                # Se for PDF, mantém o painel e só manda uma msg temporária abaixo
                msg_consultando = BOT.send_message(
                    c.message.chat.id,
                    "<b>Consultando...</b>"
                )

                pdf_path = gerar_pdf_lista_usuarios_revenda(telegram_user)

                try:
                    with open(pdf_path, "rb") as pdf_file:
                        BOT.send_document(
                            c.message.chat.id,
                            pdf_file,
                            caption=f"Lista de usuários ({len(usuarios)} no total)"
                        )
                finally:
                    try:
                        if msg_consultando:
                            BOT.delete_message(
                                c.message.chat.id,
                                msg_consultando.message_id
                            )
                    except:
                        pass

                    if os.path.exists(pdf_path):
                        os.remove(pdf_path)

                limpar_trava_revenda(c.from_user.id)

        except Exception as e:
            try:
                if msg_consultando:
                    BOT.delete_message(
                        c.message.chat.id,
                        msg_consultando.message_id
                    )
            except:
                pass

            limpar_trava_revenda(c.from_user.id)
            BOT.send_message(
                c.message.chat.id,
                f"❌ Erro ao listar usuários.\n<code>{ESC(e)}</code>"
            )
        return True
    
    if c.data == "rev_usuarios_online":
        BOT.answer_callback_query(c.id, "Consultando...")

        msg_consultando = None

        try:
            telegram_user, _, _, _ = dados_revenda_atual(c)

            usuarios_online = obter_lista_usuarios_online_revenda(telegram_user)
            total_online = total_conexoes_online_revenda(usuarios_online)
            texto = montar_texto_usuarios_online_revenda(usuarios_online)

            # Se couber no Telegram, substitui o painel pela lista
            if len(texto) <= 3500:
                BOT.edit_message_text(
                    chat_id=c.message.chat.id,
                    message_id=c.message.message_id,
                    text=texto,
                    reply_markup=painel_usuarios_online_revenda_voltar_markup()
                )
                limpar_trava_revenda(c.from_user.id)

            else:
                # Se for grande, mantém o painel e manda um "Consultando..." abaixo
                msg_consultando = BOT.send_message(
                    c.message.chat.id,
                    "<b>Consultando...</b>"
                )

                pdf_path = gerar_pdf_usuarios_online_revenda(telegram_user, usuarios_online)

                try:
                    with open(pdf_path, "rb") as pdf_file:
                        BOT.send_document(
                            c.message.chat.id,
                            pdf_file,
                            caption=f"Usuários online ({total_online} no total)"
                        )
                finally:
                    try:
                        if msg_consultando:
                            BOT.delete_message(c.message.chat.id, msg_consultando.message_id)
                    except:
                        pass

                    if os.path.exists(pdf_path):
                        os.remove(pdf_path)

                limpar_trava_revenda(c.from_user.id)

        except Exception as e:
            try:
                if msg_consultando:
                    BOT.delete_message(c.message.chat.id, msg_consultando.message_id)
            except:
                pass

            limpar_trava_revenda(c.from_user.id)
            BOT.send_message(
                c.message.chat.id,
                f"❌ Erro ao consultar usuários online.\n<code>{ESC(e)}</code>"
            )
        return True
    
    if c.data == "rev_consultar_usuario":
        BOT.answer_callback_query(c.id, "Abrindo...")

        try:
            BOT.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        resetar_fluxo_revenda(c.from_user.id)
        USER_DATA[c.from_user.id] = {"acao": "rev_consultar_usuario"}

        msg = BOT.send_message(
            c.message.chat.id,
            "Informe o usuário ou uuid."
        )
        BOT.register_next_step_handler(msg, receber_consulta_usuario_revenda)
        return True
    
    if c.data == "rev_subrevendas":
        BOT.answer_callback_query(c.id, "Abrindo.")

        try:
            preview = types.LinkPreviewOptions(
                is_disabled=False,
                url="https://a.imagem.app/GG1KMm.png",
                show_above_text=True,
                prefer_large_media=True
            )

            limpar_trava_revenda(c.from_user.id)

            BOT.edit_message_text(
                chat_id=c.message.chat.id,
                message_id=c.message.message_id,
                text="<b>PAINEL SUB-REVENDAS</b>\n\nEscolha uma opção:",
                reply_markup=painel_subrevendas_markup(),
                link_preview_options=preview
            )
        except Exception as e:
            limpar_trava_revenda(c.from_user.id)
            BOT.send_message(
                c.message.chat.id,
                f"❌ Erro ao abrir painel.\n<code>{ESC(e)}</code>"
            )
        return True

    if c.data == "rev_add_subrevenda":
        BOT.answer_callback_query(c.id, "Abrindo.")

        try:
            BOT.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        resetar_fluxo_revenda(c.from_user.id)
        USER_DATA[c.from_user.id] = {"acao": "rev_add_subrevenda"}

        limpar_trava_revenda(c.from_user.id)

        msg = BOT.send_message(
            c.message.chat.id,
            "Envie o @ da sub revenda."
        )
        BOT.register_next_step_handler(msg, receber_telegram_subrevenda)
        return True
    
    if c.data == "rev_del_subrevenda":
        BOT.answer_callback_query(c.id, "Abrindo.")

        try:
            BOT.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        resetar_fluxo_revenda(c.from_user.id)
        USER_DATA[c.from_user.id] = {"acao": "rev_del_subrevenda"}

        msg = BOT.send_message(
            c.message.chat.id,
            "Envie o @ da sub revenda."
        )
        BOT.register_next_step_handler(msg, receber_telegram_del_subrevenda)
        return True
    
    if c.data == "rev_alt_data_subrevenda":
        BOT.answer_callback_query(c.id, "Abrindo.")

        try:
            BOT.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        resetar_fluxo_revenda(c.from_user.id)
        USER_DATA[c.from_user.id] = {"acao": "rev_alt_data_subrevenda"}

        limpar_trava_revenda(c.from_user.id)

        msg = BOT.send_message(
            c.message.chat.id,
            "Envie o @ da sub revenda."
        )
        BOT.register_next_step_handler(msg, receber_telegram_alt_data_subrevenda)
        return True
    
    if c.data == "rev_alt_limite_subrevenda":
        BOT.answer_callback_query(c.id, "Abrindo.")

        try:
            BOT.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        resetar_fluxo_revenda(c.from_user.id)
        USER_DATA[c.from_user.id] = {"acao": "rev_alt_limite_subrevenda"}

        limpar_trava_revenda(c.from_user.id)

        msg = BOT.send_message(
            c.message.chat.id,
            "Envie o @ da sub revenda."
        )
        BOT.register_next_step_handler(msg, receber_telegram_alt_limite_subrevenda)
        return True
    
    if c.data == "rev_relatorio_subrevendas":
        BOT.answer_callback_query(c.id, "Consultando.")

        msg_consultando = None

        try:
            telegram_revenda, _, _, _ = dados_revenda_atual(c)

            # mantém o painel atual e envia "Consultando." abaixo
            msg_consultando = BOT.send_message(
                c.message.chat.id,
                "<b>Consultando.</b>"
            )

            subrevendas = obter_lista_relatorio_subrevendas(telegram_revenda)

            pdf_path = gerar_pdf_relatorio_subrevendas(subrevendas)

            try:
                if msg_consultando:
                    try:
                        BOT.delete_message(
                            msg_consultando.chat.id,
                            msg_consultando.message_id
                        )
                    except:
                        pass

                with open(pdf_path, "rb") as pdf_file:
                    BOT.send_document(
                        c.message.chat.id,
                        pdf_file,
                        caption=f"Relatório de sub-revendas ({len(subrevendas)} no total)"
                    )
            finally:
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)

        except Exception as e:
            try:
                if msg_consultando:
                    BOT.delete_message(
                        msg_consultando.chat.id,
                        msg_consultando.message_id
                    )
            except:
                pass

            BOT.send_message(
                c.message.chat.id,
                f"❌ Erro ao gerar relatório de sub-revendas.\n<code>{ESC(e)}</code>"
            )
        finally:
            limpar_trava_revenda(c.from_user.id)

        return True
    
    if c.data == "rev_relatorio_individual_subrevenda":
        BOT.answer_callback_query(c.id, "Abrindo.")

        try:
            BOT.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        resetar_fluxo_revenda(c.from_user.id)
        USER_DATA[c.from_user.id] = {"acao": "rev_relatorio_individual_subrevenda"}

        limpar_trava_revenda(c.from_user.id)

        msg = BOT.send_message(
            c.message.chat.id,
            "Envie o @ da sub-revenda."
        )
        BOT.register_next_step_handler(msg, receber_telegram_relatorio_individual_subrevenda)
        return True
    
    if c.data == "rev_suspender_subrevenda":
        BOT.answer_callback_query(c.id, "Abrindo.")

        try:
            BOT.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        resetar_fluxo_revenda(c.from_user.id)
        USER_DATA[c.from_user.id] = {"acao": "rev_suspender_subrevenda"}

        limpar_trava_revenda(c.from_user.id)

        msg = BOT.send_message(
            c.message.chat.id,
            "Envie o @ da sub-revenda."
        )
        BOT.register_next_step_handler(msg, receber_telegram_suspender_subrevenda)
        return True
    
    if c.data == "rev_renovar_subrevenda":
        BOT.answer_callback_query(
            c.id,
            "Esta sub-revenda será renovada em 1 mês.",
            show_alert=True
        )

        try:
            BOT.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        resetar_fluxo_revenda(c.from_user.id)
        USER_DATA[c.from_user.id] = {"acao": "rev_renovar_subrevenda"}

        limpar_trava_revenda(c.from_user.id)

        msg = BOT.send_message(
            c.message.chat.id,
            "Envie o @ da sub-revenda."
        )
        BOT.register_next_step_handler(msg, receber_telegram_renovar_subrevenda)
        return True
    
    if c.data == "rev_relatorio":
        BOT.answer_callback_query(c.id, "Consultando...")

        try:
            telegram_user = OBTER_TELEGRAM_ATUAL(c)
            if not telegram_user:
                BOT.send_message(
                    c.message.chat.id,
                    "❌ Telegram da revenda não encontrado."
                )
                limpar_trava_revenda(c.from_user.id)
                return True

            BOT.edit_message_text(
                chat_id=c.message.chat.id,
                message_id=c.message.message_id,
                text="<b>Consultando...</b>"
            )

            try:
                if SINCRONIZAR_ARQUIVO_REVENDA:
                    SINCRONIZAR_ARQUIVO_REVENDA(telegram_user)

                if RECALCULAR_LIMITE_RESTANTE_REVENDA:
                    RECALCULAR_LIMITE_RESTANTE_REVENDA(telegram_user)
            except:
                pass

            limpar_trava_revenda(c.from_user.id)

            BOT.edit_message_text(
                chat_id=c.message.chat.id,
                message_id=c.message.message_id,
                text=texto_relatorio_revenda(c),
                reply_markup=painel_relatorio_revenda_markup()
            )
        except Exception as e:
            limpar_trava_revenda(c.from_user.id)
            BOT.send_message(
                c.message.chat.id,
                f"❌ Erro ao abrir relatório.\n<code>{ESC(e)}</code>"
            )
        return True

    if c.data == "rev_voltar_menu":
        BOT.answer_callback_query(c.id, "Voltando...")

        try:
            preview = types.LinkPreviewOptions(
                is_disabled=False,
                url="https://a.imagem.app/GG1KMm.png",
                show_above_text=True,
                prefer_large_media=True
            )

            BOT.edit_message_text(
                chat_id=c.message.chat.id,
                message_id=c.message.message_id,
                text=texto_menu_revenda(c),
                reply_markup=painel_revenda_markup(),
                link_preview_options=preview
            )
        except Exception as e:
            BOT.send_message(
                c.message.chat.id,
                f"❌ Erro ao voltar ao menu.\n<code>{ESC(e)}</code>"
            )
        return True

    return False


# =========================================================
# FLUXO REVENDA - RECEBER USUÁRIO
# =========================================================
def receber_usuario_revenda(message):
    dados = USER_DATA.get(message.from_user.id, {})
    if dados.get("acao") != "rev_add_usuario":
        return

    if not BOT:
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
    BOT.register_next_step_handler(msg, receber_limite_revenda_usuario)


# =========================================================
# FLUXO REVENDA - RECEBER LIMITE
# =========================================================
def receber_limite_revenda_usuario(message):
    if not BOT:
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
        _, _, limite_restante, _ = dados_revenda_atual(message)
    except Exception as e:
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(message.chat.id, f"❌ Erro ao ler dados da revenda.\n<code>{ESC(e)}</code>")
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
    BOT.register_next_step_handler(msg, receber_dias_revenda_usuario)


# =========================================================
# FLUXO REVENDA - RECEBER DIAS
# =========================================================
def receber_dias_revenda_usuario(message):
    if not BOT:
        return

    if not message.text:
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(message.chat.id, "❌ Quantidade inválida. Digite /menu para tentar novamente.")
        return

    texto = message.text.strip()

    if not texto.isdigit() or int(texto) <= 0:
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(message.chat.id, "❌ Quantidade inválida. Digite /menu para tentar novamente.")
        return

    dias = int(texto)
    USER_DATA[message.from_user.id]["dias"] = dias

    if UUID_MODE_ATIVO():
        msg = BOT.send_message(
            message.chat.id,
            "Qual config deseja gerar?",
            reply_markup=teclado_tipo_revenda()
        )
        BOT.register_next_step_handler(msg, receber_tipo_revenda)
        return

    criar_usuario_revenda_final(message, usar_v2ray=False)


# =========================================================
# FLUXO REVENDA - RECEBER TIPO DA CONFIG
# =========================================================
def receber_tipo_revenda(message):
    if not BOT:
        return

    if not message.text:
        criar_usuario_revenda_final(message, usar_v2ray=False)
        return

    texto = message.text.strip().lower()

    if texto == "xray":
        criar_usuario_revenda_final(message, usar_v2ray=True)
        return

    # qualquer outra coisa vira "Nenhum"
    criar_usuario_revenda_final(message, usar_v2ray=False)


# =========================================================
# FLUXO REVENDA - CRIAR USUÁRIO FINAL
# =========================================================
def criar_usuario_revenda_final(message, usar_v2ray):
    try:
        dados_fluxo = USER_DATA.get(message.from_user.id)
        if not dados_fluxo:
            BOT.send_message(
                message.chat.id,
                "❌ Fluxo inválido. Digite /menu para tentar novamente.",
                reply_markup=types.ReplyKeyboardRemove()
            )
            return

        username = dados_fluxo["username"]
        limite = dados_fluxo["limite"]
        dias = dados_fluxo["dias"]
        senha = f"{__import__('random').randint(1000, 9999)}"

        telegram_user, limite_total, limite_restante, vencimento_rev = dados_revenda_atual(message)

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

        SALVAR_REVENDA(
            telegram_user=telegram_user,
            limite_total=limite_total,
            limite_restante=novo_limite_restante,
            vencimento_formatado=vencimento_rev
        )

        ADICIONAR_USUARIO_REVENDA_ARQUIVO(
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
# CRIAR USUÁRIO AUTOMÁTICO DA REVENDA
# Formato: redexxx
# =========================================================
def criar_usuario_auto_revenda_final(obj, meses, usar_v2ray):
    try:
        telegram_user, limite_total, limite_restante, vencimento_rev = dados_revenda_atual(obj)

        limite = 1

        if limite > limite_restante:
            USER_DATA.pop(obj.from_user.id, None)
            BOT.send_message(
                obj.message.chat.id if hasattr(obj, "message") else obj.chat.id,
                f"❌ Limite acima do permitido.\nSeu limite restante atual é <code>{ESC(limite_restante)}</code>.\nDigite /menu para tentar novamente."
            )
            return

        username = None
        for _ in range(3):
            candidato = gerar_username_auto_revenda()
            try:
                if not USUARIO_EXISTE(candidato):
                    username = candidato
                    break
            except Exception:
                continue

        if not username:
            USER_DATA.pop(obj.from_user.id, None)
            BOT.send_message(
                obj.message.chat.id if hasattr(obj, "message") else obj.chat.id,
                "❌ Não foi possível gerar um usuário disponível. Digite /menu para tentar novamente."
            )
            return

        senha = f"{__import__('random').randint(1000, 9999)}"
        vencimento = calcular_vencimento_mensal_revenda(meses)
        dias = calcular_dias_ate_vencimento_revenda(vencimento)

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

        SALVAR_REVENDA(
            telegram_user=telegram_user,
            limite_total=limite_total,
            limite_restante=novo_limite_restante,
            vencimento_formatado=vencimento_rev
        )

        ADICIONAR_USUARIO_REVENDA_ARQUIVO(
            telegram_user=telegram_user,
            username=username,
            senha=senha,
            limite=limite,
            dias_restantes=dias,
            uuid_code=uuid_code
        )

        vencimento_formatado = vencimento.strftime("%d/%m/%Y")

        texto_final = (
            "✅ <b>Usuário criado com sucesso!</b>\n\n"
            f"👤 <b>Usuário:</b> <code>{ESC(username)}</code>\n"
            f"🔑 <b>Senha:</b> <code>{ESC(senha)}</code>\n"
            f"👥 <b>Limite:</b> {ESC(limite)}\n"
            f"📅 <b>Vencimento:</b> {ESC(vencimento_formatado)}"
        )

        if uuid_code:
            texto_final += f"\n\n🆔 <b>UUID:</b> <code>{ESC(uuid_code)}</code>"

        BOT.send_message(
            obj.message.chat.id if hasattr(obj, "message") else obj.chat.id,
            texto_final
        )

    except Exception as e:
        BOT.send_message(
            obj.message.chat.id if hasattr(obj, "message") else obj.chat.id,
            f"❌ Falha ao criar usuário automático.\n<code>{ESC(e)}</code>"
        )
    finally:
        USER_DATA.pop(obj.from_user.id, None)

# =========================================================
# FLUXO REVENDA - CRIAR TESTE
# Agora desconta 1 do limite restante da revenda
# e salva o teste no arquivo da revenda
# =========================================================
def receber_horas_teste_revenda(message):
    if not BOT:
        return

    dados = USER_DATA.get(message.from_user.id, {})
    if dados.get("acao") != "rev_add_teste":
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
        telegram_user, limite_total, limite_restante, vencimento_rev = dados_revenda_atual(message)

        # cada teste consome 1 crédito da revenda
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

        # desconta 1 crédito da revenda
        novo_limite_restante = limite_restante - 1

        SALVAR_REVENDA(
            telegram_user=telegram_user,
            limite_total=limite_total,
            limite_restante=novo_limite_restante,
            vencimento_formatado=vencimento_rev
        )

        # salva o teste no arquivo da revenda
        ADICIONAR_TESTE_REVENDA_ARQUIVO(
            telegram_user=telegram_user,
            username=username,
            senha=senha,
            limite=1,
            horas=horas,
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

# =========================================================
# FLUXO REVENDA - ALTERAR LIMITE - RECEBER USUÁRIO
# =========================================================
def receber_usuario_alterar_limite_revenda(message):
    if not BOT:
        return

    dados = USER_DATA.get(message.from_user.id, {})
    if dados.get("acao") != "rev_alt_limite":
        return

    if not message.text:
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ Usuário inválido. Digite /menu para tentar novamente."
        )
        return

    username = message.text.strip()

    try:
        telegram_user, _, limite_restante, _ = dados_revenda_atual(message)

        usuario_encontrado = obter_usuario_existente_revenda(telegram_user, username)
        if not usuario_encontrado:
            USER_DATA.pop(message.from_user.id, None)
            BOT.send_message(
                message.chat.id,
                "❌ Usuário não encontrado. Digite /menu para tentar novamente."
            )
            return

        limite_atual_usuario = int(str(usuario_encontrado.get("limite", "0")).strip() or "0")

        USER_DATA[message.from_user.id]["username_alterar_limite_revenda"] = username
        USER_DATA[message.from_user.id]["limite_atual_usuario_revenda"] = limite_atual_usuario
        USER_DATA[message.from_user.id]["limite_restante_revenda_atual"] = int(limite_restante)

        msg = BOT.send_message(
            message.chat.id,
            f"👥 Limite atual do usuário: <code>{ESC(limite_atual_usuario)}</code>\n\nEnvie o novo limite."
        )
        BOT.register_next_step_handler(msg, receber_novo_limite_alterar_limite_revenda)

    except Exception as e:
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            f"❌ Erro ao ler dados do usuário.\n<code>{ESC(e)}</code>"
        )

# =========================================================
# FLUXO REVENDA - ALTERAR LIMITE - RECEBER NOVO LIMITE
# =========================================================
def receber_novo_limite_alterar_limite_revenda(message):
    if not BOT:
        return

    dados = USER_DATA.get(message.from_user.id, {})
    if dados.get("acao") != "rev_alt_limite":
        return

    if not message.text:
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ Limite inválido. Digite /menu para tentar novamente."
        )
        return

    texto = message.text.strip()

    if not texto.isdigit() or int(texto) <= 0:
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ Limite inválido. Digite /menu para tentar novamente."
        )
        return

    novo_limite = int(texto)

    try:
        telegram_user, limite_total, limite_restante_real, vencimento_rev = dados_revenda_atual(message)

        username = dados["username_alterar_limite_revenda"]
        limite_atual_usuario = int(dados["limite_atual_usuario_revenda"])
        limite_restante_painel = int(dados["limite_restante_revenda_atual"])

        # diferença do que vai consumir/devolver
        # exemplo: 5 -> 1  => delta = -4  => devolve 4
        # exemplo: 1 -> 5  => delta = +4  => precisa ter 4 disponíveis
        delta = novo_limite - limite_atual_usuario

        if delta > 0 and delta > limite_restante_painel:
            USER_DATA.pop(message.from_user.id, None)
            BOT.send_message(
                message.chat.id,
                "❌ Limite acima do permitido.\nDigite /menu para tentar novamente."
            )
            return

        ALTERAR_LIMITE_USUARIO_SISTEMA(username, novo_limite)

        # ajusta rapidamente o restante do painel
        novo_limite_restante = limite_restante_real - delta

        if novo_limite_restante < 0:
            novo_limite_restante = 0

        SALVAR_REVENDA(
            telegram_user=telegram_user,
            limite_total=limite_total,
            limite_restante=novo_limite_restante,
            vencimento_formatado=vencimento_rev
        )

        # sincroniza novamente essa revenda para manter tudo correto
        try:
            if SINCRONIZAR_ARQUIVO_REVENDA:
                SINCRONIZAR_ARQUIVO_REVENDA(telegram_user)

            if RECALCULAR_LIMITE_RESTANTE_REVENDA:
                RECALCULAR_LIMITE_RESTANTE_REVENDA(telegram_user)
        except:
            pass

        BOT.send_message(
            message.chat.id,
            "✅ <b>Limite alterado!</b>\n\n"
            f"👤 <b>Usuário:</b> <code>{ESC(username)}</code>\n"
            f"👥 <b>Novo limite:</b> {ESC(novo_limite)}"
        )

    except Exception as e:
        BOT.send_message(
            message.chat.id,
            f"❌ Erro ao alterar limite.\n<code>{ESC(e)}</code>"
        )
    finally:
        USER_DATA.pop(message.from_user.id, None)

# =========================================================
# FLUXO REVENDA - ALTERAR SENHA - RECEBER USUÁRIO
# =========================================================
def receber_usuario_alterar_senha_revenda(message):
    if not BOT:
        return

    dados = USER_DATA.get(message.from_user.id, {})
    if dados.get("acao") != "rev_alt_senha":
        return

    if not message.text:
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ Usuário inválido. Digite /menu para tentar novamente."
        )
        return

    username = message.text.strip()

    try:
        telegram_user, _, _, _ = dados_revenda_atual(message)

        if not obter_usuario_existente_revenda(telegram_user, username):
            USER_DATA.pop(message.from_user.id, None)
            BOT.send_message(
                message.chat.id,
                "❌ Usuário não encontrado. Digite /menu para tentar novamente."
            )
            return

        USER_DATA[message.from_user.id]["username_alterar_senha_revenda"] = username

        msg = BOT.send_message(
            message.chat.id,
            "Envie a nova senha."
        )
        BOT.register_next_step_handler(msg, receber_nova_senha_alterar_senha_revenda)

    except Exception as e:
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            f"❌ Erro ao ler dados do usuário.\n<code>{ESC(e)}</code>"
        )

# =========================================================
# FLUXO REVENDA - ALTERAR SENHA - RECEBER NOVA SENHA
# =========================================================
def receber_nova_senha_alterar_senha_revenda(message):
    if not BOT:
        return

    dados = USER_DATA.get(message.from_user.id, {})
    if dados.get("acao") != "rev_alt_senha":
        return

    if not message.text:
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ Senha inválida. Digite /menu para tentar novamente."
        )
        return

    nova_senha = message.text.strip()

    if len(nova_senha) < 4 or len(nova_senha) > 8:
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ Senha inválida. Use de 4 a 8 caracteres.\nDigite /menu para tentar novamente."
        )
        return

    if not nova_senha.isalnum():
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ Senha inválida. Use apenas letras e números, sem caracteres especiais.\nDigite /menu para tentar novamente."
        )
        return

    username = dados.get("username_alterar_senha_revenda")
    if not username:
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ Fluxo inválido. Digite /menu para tentar novamente."
        )
        return

    try:
        telegram_user, _, _, _ = dados_revenda_atual(message)

        ALTERAR_SENHA_USUARIO_SISTEMA(username, nova_senha)

        # sincroniza novamente essa revenda para manter tudo correto
        try:
            if SINCRONIZAR_ARQUIVO_REVENDA:
                SINCRONIZAR_ARQUIVO_REVENDA(telegram_user)

            if RECALCULAR_LIMITE_RESTANTE_REVENDA:
                RECALCULAR_LIMITE_RESTANTE_REVENDA(telegram_user)
        except:
            pass

        BOT.send_message(
            message.chat.id,
            "✅ <b>Senha alterada!</b>\n\n"
            f"👤 <b>Usuário:</b> <code>{ESC(username)}</code>\n"
            f"🔑 <b>Nova senha:</b> <code>{ESC(nova_senha)}</code>"
        )

    except Exception as e:
        BOT.send_message(
            message.chat.id,
            f"❌ Erro ao alterar senha.\n<code>{ESC(e)}</code>"
        )
    finally:
        USER_DATA.pop(message.from_user.id, None)

# =========================================================
# FLUXO REVENDA - ALTERAR DATA - RECEBER USUÁRIO
# =========================================================
def receber_usuario_alterar_data_revenda(message):
    if not BOT:
        return

    dados = USER_DATA.get(message.from_user.id, {})
    if dados.get("acao") != "rev_alt_data":
        return

    if not message.text:
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ Usuário inválido. Digite /menu para tentar novamente."
        )
        return

    username = message.text.strip()

    try:
        telegram_user, _, _, _ = dados_revenda_atual(message)

        if not obter_usuario_existente_revenda(telegram_user, username):
            USER_DATA.pop(message.from_user.id, None)
            BOT.send_message(
                message.chat.id,
                "❌ Usuário não encontrado. Digite /menu para tentar novamente."
            )
            return

        USER_DATA[message.from_user.id]["username_alterar_data_revenda"] = username

        msg = BOT.send_message(
            message.chat.id,
            "Envie a quantidade de dias. Ex: 30"
        )
        BOT.register_next_step_handler(msg, receber_nova_data_alterar_data_revenda)

    except Exception as e:
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            f"❌ Erro ao ler dados do usuário.\n<code>{ESC(e)}</code>"
        )

# =========================================================
# FLUXO REVENDA - ALTERAR DATA - RECEBER NOVA DATA
# =========================================================
def receber_nova_data_alterar_data_revenda(message):
    if not BOT:
        return

    dados = USER_DATA.get(message.from_user.id, {})
    if dados.get("acao") != "rev_alt_data":
        return

    if not message.text:
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ Quantidade inválida. Digite /menu para tentar novamente."
        )
        return

    texto = message.text.strip()

    if not texto.isdigit() or int(texto) <= 0:
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ Quantidade inválida. Digite /menu para tentar novamente."
        )
        return

    dias = int(texto)
    username = dados.get("username_alterar_data_revenda")

    if not username:
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ Fluxo inválido. Digite /menu para tentar novamente."
        )
        return

    try:
        telegram_user, _, _, _ = dados_revenda_atual(message)

        ALTERAR_DATA_USUARIO_SISTEMA(username, dias)

        # atualiza apenas aquele usuário específico no arquivo da revenda
        try:
            if SINCRONIZAR_ARQUIVO_REVENDA:
                SINCRONIZAR_ARQUIVO_REVENDA(telegram_user)

            if RECALCULAR_LIMITE_RESTANTE_REVENDA:
                RECALCULAR_LIMITE_RESTANTE_REVENDA(telegram_user)
        except:
            pass

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
        USER_DATA.pop(message.from_user.id, None)

# =========================================================
# FLUXO REVENDA - RENOVAR - RECEBER USUÁRIO
# =========================================================
def receber_usuario_renovar_revenda(message):
    if not BOT:
        return

    dados = USER_DATA.get(message.from_user.id, {})
    if dados.get("acao") != "rev_renovar":
        return

    if not message.text:
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ Usuário não encontrado. Digite /menu para tentar novamente."
        )
        return

    username = message.text.strip()

    try:
        telegram_user, _, _, _ = dados_revenda_atual(message)

        if not obter_usuario_existente_revenda(telegram_user, username):
            USER_DATA.pop(message.from_user.id, None)
            BOT.send_message(
                message.chat.id,
                "❌ Usuário não encontrado. Digite /menu para tentar novamente."
            )
            return

        USER_DATA[message.from_user.id]["username_renovar_revenda"] = username
        renovar_usuario_revenda_final(message)

    except Exception as e:
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            f"❌ Erro ao verificar usuário.\n<code>{ESC(e)}</code>"
        )

# =========================================================
# FLUXO REVENDA - RENOVAR USUÁRIO FINAL
# Regra:
# - se NÃO venceu: soma 1 mês em cima do vencimento atual
# - se venceu: soma 1 mês em cima de hoje
# Atualiza só a data daquele usuário na lista da revenda
# =========================================================
def renovar_usuario_revenda_final(message):
    try:
        dados = USER_DATA.get(message.from_user.id, {})
        username = dados.get("username_renovar_revenda")

        if not username:
            BOT.send_message(
                message.chat.id,
                "❌ Fluxo inválido. Digite /menu para tentar novamente."
            )
            return

        telegram_user, _, _, _ = dados_revenda_atual(message)

        vencimento_atual = OBTER_DATA_VENCIMENTO_USUARIO(username)
        hoje = datetime.now()

        # se ainda não venceu, renova a partir do vencimento atual
        # se já venceu, renova a partir de hoje
        if vencimento_atual.date() >= hoje.date():
            data_base = vencimento_atual
        else:
            data_base = hoje

        novo_vencimento = CALCULAR_RENOVACAO_MAIS_UM_MES(data_base)
        dias_para_novo_vencimento = CALCULAR_DIAS_ATE_DATA_FUTURA(novo_vencimento)

        ALTERAR_DATA_USUARIO_SISTEMA(username, dias_para_novo_vencimento)

        # atualiza apenas aquele usuário no arquivo da revenda
        dias_local = (novo_vencimento.date() - datetime.now().date()).days
        if dias_local < 1:
            dias_local = 1

        atualizar_data_usuario_revenda_local(telegram_user, username, dias_local)

        vencimento_formatado = novo_vencimento.strftime("%d/%m/%Y")

        BOT.send_message(
            message.chat.id,
            "✅ <b>Usuário renovado!</b>\n\n"
            f"👤 <b>Usuário:</b> <code>{ESC(username)}</code>\n"
            f"📅 <b>Nova Data:</b> {ESC(vencimento_formatado)}"
        )

    except Exception as e:
        BOT.send_message(
            message.chat.id,
            f"❌ Falha ao renovar usuário.\n<code>{ESC(e)}</code>"
        )
    finally:
        USER_DATA.pop(message.from_user.id, None)

# =========================================================
# FLUXO REVENDA - DELETAR USUÁRIO - RECEBER USUÁRIO
# =========================================================
def receber_usuario_deletar_revenda(message):
    if not BOT:
        return

    dados = USER_DATA.get(message.from_user.id, {})
    if dados.get("acao") != "rev_del_usuario":
        return

    if not message.text:
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ Usuário não encontrado. Digite /menu para tentar novamente."
        )
        return

    username = message.text.strip()

    try:
        telegram_user, _, _, _ = dados_revenda_atual(message)

        if not obter_usuario_existente_revenda(telegram_user, username):
            USER_DATA.pop(message.from_user.id, None)
            BOT.send_message(
                message.chat.id,
                "❌ Usuário não encontrado. Digite /menu para tentar novamente."
            )
            return

        # Se está no banco da revenda mas não existe mais na VPS:
        # roda a varredura daquela revenda e informa
        if not USUARIO_EXISTE(username):
            try:
                if SINCRONIZAR_ARQUIVO_REVENDA:
                    SINCRONIZAR_ARQUIVO_REVENDA(telegram_user)

                if RECALCULAR_LIMITE_RESTANTE_REVENDA:
                    RECALCULAR_LIMITE_RESTANTE_REVENDA(telegram_user)
            except:
                pass

            USER_DATA.pop(message.from_user.id, None)
            BOT.send_message(
                message.chat.id,
                "❌ Usuário não existe. Digite /menu para tentar novamente."
            )
            return

        # Existe na VPS -> deleta e depois sincroniza
        DELETAR_USUARIO_SISTEMA(username)

        try:
            if SINCRONIZAR_ARQUIVO_REVENDA:
                SINCRONIZAR_ARQUIVO_REVENDA(telegram_user)

            if RECALCULAR_LIMITE_RESTANTE_REVENDA:
                RECALCULAR_LIMITE_RESTANTE_REVENDA(telegram_user)
        except:
            pass

        BOT.send_message(
            message.chat.id,
            f"🗑️ Usuário <b>{ESC(username)}</b> deletado com sucesso!"
        )

    except Exception as e:
        BOT.send_message(
            message.chat.id,
            f"❌ Erro ao deletar usuário.\n<code>{ESC(e)}</code>"
        )
    finally:
        USER_DATA.pop(message.from_user.id, None)

# =========================================================
# VERIFICAR SE USUÁRIO ESTÁ EXPIRADO
# Expirado = data de expiração é hoje ou anterior
# =========================================================
def usuario_revenda_esta_expirado(username):
    data_exp = OBTER_DATA_EXPIRACAO_USUARIO(username)

    if data_exp is None:
        return True

    hoje = datetime.now().date()
    data_final = data_exp.date()

    return data_final <= hoje


# =========================================================
# OBTER APENAS OS USUÁRIOS EXPIRADOS DAQUELA REVENDA
# =========================================================
def obter_usuarios_expirados_revenda(telegram_user):
    expirados = []

    try:
        usuarios_revenda = LISTAR_USUARIOS_DA_REVENDA(telegram_user)

        for username in usuarios_revenda:
            try:
                # se não existe mais na VPS, ignora aqui;
                # a varredura já limpa isso antes
                if not USUARIO_EXISTE(username):
                    continue

                if usuario_revenda_esta_expirado(username):
                    expirados.append(username)
            except:
                continue
    except:
        pass

    return expirados


# =========================================================
# MONTAR TEXTO DOS EXPIRADOS DA REVENDA
# =========================================================
def montar_texto_expirados_revenda(expirados):
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
# TEXTO DA LISTA DE USUÁRIOS DA REVENDA
# Mesmo formato do relatório individual
# =========================================================
def montar_texto_lista_usuarios_revenda(telegram_user):
    usuarios = LER_USUARIOS_REVENDA_COMPLETOS(telegram_user)
    dados = LER_DADOS_REVENDA(telegram_user)
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
            dias_int = int(str(item["dias"]).strip())
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
# GERAR PDF DA LISTA DE USUÁRIOS DA REVENDA
# Mesmo estilo do relatório individual
# =========================================================
def gerar_pdf_lista_usuarios_revenda(telegram_user):
    dados = LER_DADOS_REVENDA(telegram_user)

    vencimento = str(dados.get("vencimento", "")).strip()
    limite_total = int(dados.get("limite_total", "0"))
    limite_restante = int(dados.get("limite_restante", "0"))

    # status opcional no topo
    status = "suspenso" if False else "ativo"

    usuarios = LER_USUARIOS_REVENDA_COMPLETOS(telegram_user)

    nome_pdf = f"usuarios_revenda_{random.randint(100,999)}.pdf"
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
        titulo = "LISTA DE USUARIOS DA REVENDA"
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
# JUNTAR DADOS DOS USUÁRIOS ONLINE DA REVENDA
# Formato:
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
def obter_lista_usuarios_online_revenda(telegram_user):
    online_dict = OBTER_USUARIOS_ONLINE_PLUGIN()

    if not online_dict:
        return []

    usuarios_revenda = set(LISTAR_USUARIOS_DA_REVENDA(telegram_user))
    if not usuarios_revenda:
        return []

    usuarios_completos = LER_USUARIOS_REVENDA_COMPLETOS(telegram_user)
    mapa_limites = {}

    for item in usuarios_completos:
        try:
            mapa_limites[str(item["username"]).strip()] = int(str(item["limite"]).strip())
        except:
            mapa_limites[str(item["username"]).strip()] = 0

    resultado = []

    for username in sorted(online_dict.keys(), key=lambda x: x.lower()):
        if username not in usuarios_revenda:
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

# =========================================================
# MONTAR TEXTO DOS USUÁRIOS ONLINE PARA O TELEGRAM
# Mesmo formato do admin
# =========================================================
def montar_texto_usuarios_online_revenda(usuarios_online):
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
    linhas.append(f"<b><i>Total Usuários: {total_conexoes_online_revenda(usuarios_online)} onlines</i></b>")

    return "\n".join(linhas)

# =========================================================
# GERAR PDF DOS USUÁRIOS ONLINE DA REVENDA
# =========================================================
def gerar_pdf_usuarios_online_revenda(telegram_user, usuarios_online):
    nome_pdf = f"usuarios_online_revenda_{random.randint(100,999)}.pdf"
    pdf_path = os.path.join(tempfile.gettempdir(), nome_pdf)

    c = canvas.Canvas(pdf_path, pagesize=A4)
    largura_pagina, altura_pagina = A4

    margem_esq = 35
    margem_dir = 35
    topo = altura_pagina - 40
    rodape = 35
    largura_util = largura_pagina - margem_esq - margem_dir

    colunas = [
        ("USUARIO", 180),
        ("ONLINE/LIMITE", 110),
        ("TEMPO", 140),
    ]

    largura_tabela = sum(l for _, l in colunas)
    x_inicial = (largura_pagina - largura_tabela) / 2

    def cortar_texto(texto, fonte="Helvetica", tamanho=9, largura_max=100):
        texto = str(texto)
        while stringWidth(texto, fonte, tamanho) > largura_max - 8 and len(texto) > 1:
            texto = texto[:-1]
        return texto

    def desenhar_topo():
        c.setFont("Helvetica-Bold", 15)
        titulo = "USUARIOS ONLINE DA REVENDA"
        largura_titulo = stringWidth(titulo, "Helvetica-Bold", 15)
        c.drawString((largura_pagina - largura_titulo) / 2, topo, titulo)

        c.setFont("Helvetica", 10)
        y = topo - 24
        c.drawString(margem_esq, y, f"Revenda: {telegram_user}")
        y -= 16
        c.drawString(margem_esq, y, f"Total online: {len(usuarios_online)}")
        y -= 22

        x = x_inicial
        altura_cab = 22
        c.setFont("Helvetica-Bold", 9)
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

    for item in usuarios_online:
        if y < rodape:
            y = nova_pagina()
            c.setFont("Helvetica", 9)

        linha = [
            cortar_texto(item["username"], largura_max=colunas[0][1]),
            cortar_texto(f"{item['online']}/{item['limit']}", largura_max=colunas[1][1]),
            cortar_texto(item["tempo"], largura_max=colunas[2][1]),
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
# IDENTIFICAR SE O TEXTO PARECE UM UUID
# =========================================================
def parece_uuid(texto):
    texto = str(texto).strip()
    partes = texto.split("-")

    if len(partes) != 5:
        return False

    tamanhos = [8, 4, 4, 4, 12]
    if [len(p) for p in partes] != tamanhos:
        return False

    hexdigits = "0123456789abcdefABCDEF"
    return all(all(ch in hexdigits for ch in parte) for parte in partes)

# =========================================================
# MONTAR TEXTO DA CONSULTA DE USUÁRIO
# =========================================================
def montar_texto_consulta_usuario_revenda(item):
    username = str(item.get("username", "")).strip()
    senha = str(item.get("senha", "")).strip()
    limite = str(item.get("limite", "")).strip()
    uuid_code = str(item.get("uuid", "")).strip()

    if not uuid_code and OBTER_UUID_DISPONIVEL_USUARIO:
        try:
            uuid_code = str(OBTER_UUID_DISPONIVEL_USUARIO(username)).strip()
        except:
            uuid_code = ""

    try:
        dias_int = int(str(item.get("dias", "0")).strip())
    except:
        dias_int = 0

    try:
        data_expiracao = OBTER_DATA_EXPIRACAO_USUARIO(username)
        if data_expiracao:
            expira_txt = data_expiracao.strftime("%d/%m/%Y")
        else:
            expira_txt = "Venceu"
    except:
        expira_txt = "Venceu"

    if dias_int <= 0:
        restam_txt = "0 dias"
    elif dias_int == 1:
        restam_txt = "1 dia"
    else:
        restam_txt = f"{dias_int} dias"

    linhas = [
        "📋 <b>Dados Do Usuário</b>",
        "",
        f"• Usuário: <code>{ESC(username)}</code>",
        f"• Senha: <code>{ESC(senha)}</code>",
        f"• Limite: <code>{ESC(limite)}</code>",
        f"• Expira em: <code>{ESC(expira_txt)}</code>",
        f"<blockquote>• Restam: {ESC(restam_txt)}</blockquote>",
    ]

    if uuid_code:
        linhas.extend([
            "",
            "UUID:",
            f"<code>{ESC(uuid_code)}</code>"
        ])

    return "\n".join(linhas)

# =========================================================
# FLUXO REVENDA - CONSULTAR USUÁRIO OU UUID
# Busca apenas no banco de dados da própria revenda
# =========================================================
def receber_consulta_usuario_revenda(message):
    if not BOT:
        return

    dados = USER_DATA.get(message.from_user.id, {})
    if dados.get("acao") != "rev_consultar_usuario":
        return

    if not message.text:
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ Usuário não encontrado. Digite /menu para tentar novamente."
        )
        return

    consulta = message.text.strip()

    try:
        telegram_user, _, _, _ = dados_revenda_atual(message)
        usuarios = LER_USUARIOS_REVENDA_COMPLETOS(telegram_user)

        # -------------------------------------------------
        # CONSULTA POR UUID
        # -------------------------------------------------
        if parece_uuid(consulta):
            item_encontrado = None

            for item in usuarios:
                username_item = str(item.get("username", "")).strip()
                uuid_code = str(item.get("uuid", "")).strip()

                if not uuid_code and OBTER_UUID_DISPONIVEL_USUARIO:
                    try:
                        uuid_code = str(OBTER_UUID_DISPONIVEL_USUARIO(username_item)).strip()
                    except:
                        uuid_code = ""

                if uuid_code and uuid_code.lower() == consulta.lower():
                    item_encontrado = dict(item)
                    item_encontrado["uuid"] = uuid_code
                    break

            USER_DATA.pop(message.from_user.id, None)

            if not item_encontrado:
                BOT.send_message(
                    message.chat.id,
                    "❌ UUID não encontrado. Digite /menu para tentar novamente."
                )
                return

            BOT.send_message(
                message.chat.id,
                montar_texto_consulta_usuario_revenda(item_encontrado)
            )
            return

        # -------------------------------------------------
        # CONSULTA POR USUÁRIO
        # -------------------------------------------------
        item_encontrado = None

        for item in usuarios:
            username = str(item.get("username", "")).strip()
            if username.lower() == consulta.lower():
                item_encontrado = dict(item)

                uuid_code = str(item_encontrado.get("uuid", "")).strip()
                if not uuid_code and OBTER_UUID_DISPONIVEL_USUARIO:
                    try:
                        item_encontrado["uuid"] = str(OBTER_UUID_DISPONIVEL_USUARIO(username)).strip()
                    except:
                        pass
                break

        USER_DATA.pop(message.from_user.id, None)

        if not item_encontrado:
            BOT.send_message(
                message.chat.id,
                "❌ Usuário não encontrado. Digite /menu para tentar novamente."
            )
            return

        BOT.send_message(
            message.chat.id,
            montar_texto_consulta_usuario_revenda(item_encontrado)
        )

    except Exception as e:
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            f"❌ Erro ao consultar dados.\n<code>{ESC(e)}</code>"
        )

def telegram_ja_existe_no_banco(telegram_user, telegram_revenda_atual=None):
    tg = str(telegram_user or "").strip().lower()
    dono = str(telegram_revenda_atual or "").strip().lower()

    if not tg.startswith("@"):
        return False

    # bloqueia usar o mesmo @ da própria revenda que está cadastrando
    if dono and tg == dono:
        return True

    # bloqueia se já existe como sub-revenda
    try:
        if SUBREVENDA_EXISTE and SUBREVENDA_EXISTE(tg):
            return True
    except:
        pass

    # bloqueia se já existe como revenda
    try:
        if REVENDA_EXISTE and REVENDA_EXISTE(tg):
            return True
    except:
        pass

    # bloqueia se for o @ do admin
    try:
        if BOT and ADMIN_ID:
            chat_admin = BOT.get_chat(ADMIN_ID)
            username_admin = getattr(chat_admin, "username", None)
            if username_admin and tg == f"@{username_admin}".lower():
                return True
    except:
        pass

    return False

# =========================================================
# CADASTRAR SUB REVENDA - PASSO 1
# =========================================================
def receber_telegram_subrevenda(message):
    if not BOT:
        return

    dados = USER_DATA.get(message.from_user.id, {})
    if dados.get("acao") != "rev_add_subrevenda":
        return

    if not message.text:
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(message.chat.id, "❌ @ inválido. Digite /menu para tentar novamente.")
        return

    telegram_sub = message.text.strip()

    if not telegram_sub.startswith("@"):
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(message.chat.id, "❌ @ inválido. Digite /menu para tentar novamente.")
        return

    try:
        telegram_revenda, _, _, _ = dados_revenda_atual(message)
    except Exception as e:
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            f"❌ Erro ao ler dados da revenda.\n<code>{ESC(e)}</code>"
        )
        return

    if telegram_ja_existe_no_banco(telegram_sub, telegram_revenda_atual=telegram_revenda):
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ Esse usuário já existe em nosso banco de dados.\nDigite /menu para tentar novamente."
        )
        return

    USER_DATA[message.from_user.id]["telegram_sub"] = telegram_sub
    limpar_trava_revenda(message.from_user.id)

    msg = BOT.send_message(message.chat.id, "Envie o limite da sub revenda.")
    BOT.register_next_step_handler(msg, receber_limite_subrevenda)

# =========================================================
# CADASTRAR SUB REVENDA - PASSO 2
# =========================================================
def receber_limite_subrevenda(message):
    if not BOT:
        return

    dados = USER_DATA.get(message.from_user.id, {})
    if dados.get("acao") != "rev_add_subrevenda":
        return

    if not message.text:
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(message.chat.id, "❌ Limite inválido. Digite /menu para tentar novamente.")
        return

    texto = message.text.strip()

    if not texto.isdigit():
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(message.chat.id, "❌ Limite inválido. Digite /menu para tentar novamente.")
        return

    limite = int(texto)

    if limite <= 0:
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(message.chat.id, "❌ Limite inválido. Digite /menu para tentar novamente.")
        return

    try:
        telegram_revenda, _, limite_restante, _ = dados_revenda_atual(message)
    except Exception as e:
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(message.chat.id, f"❌ Erro ao ler dados da revenda.\n<code>{ESC(e)}</code>")
        return

    if limite > limite_restante:
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(message.chat.id, "❌ Limite insuficiente. Digite /menu para tentar novamente.")
        return

    USER_DATA[message.from_user.id]["limite_sub"] = limite
    limpar_trava_revenda(message.from_user.id)

    msg = BOT.send_message(message.chat.id, "Envie a quantidade de dias da sub revenda.")
    BOT.register_next_step_handler(msg, receber_data_subrevenda)

# =========================================================
# CADASTRAR SUB REVENDA - PASSO 3
# =========================================================
def receber_data_subrevenda(message):
    if not BOT:
        return

    dados = USER_DATA.get(message.from_user.id, {})
    if dados.get("acao") != "rev_add_subrevenda":
        return

    if not message.text:
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(message.chat.id, "❌ Quantidade de dias inválida. Digite /menu para tentar novamente.")
        return

    texto = message.text.strip()

    if not texto.isdigit():
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(message.chat.id, "❌ Quantidade de dias inválida. Digite /menu para tentar novamente.")
        return

    dias = int(texto)

    if dias <= 0:
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(message.chat.id, "❌ Quantidade de dias inválida. Digite /menu para tentar novamente.")
        return

    try:
        telegram_revenda, _, limite_restante_rev, _ = dados_revenda_atual(message)

        telegram_sub = dados["telegram_sub"]
        limite_sub = int(dados["limite_sub"])

        if limite_sub > limite_restante_rev:
            limpar_trava_revenda(message.from_user.id)
            USER_DATA.pop(message.from_user.id, None)
            BOT.send_message(message.chat.id, "❌ Limite insuficiente. Digite /menu para tentar novamente.")
            return

        vencimento_sub = (datetime.now() + timedelta(days=dias)).strftime("%d/%m/%Y")

        if telegram_ja_existe_no_banco(telegram_sub, telegram_revenda_atual=telegram_revenda):
            limpar_trava_revenda(message.from_user.id)
            USER_DATA.pop(message.from_user.id, None)
            BOT.send_message(
                message.chat.id,
                "❌ Esse usuário já existe em nosso banco de dados.\nDigite /menu para tentar novamente."
            )
            return
        
        SALVAR_SUBREVENDA_ARQUIVO(
            dono=telegram_revenda,
            telegram_user=telegram_sub,
            limite_total=limite_sub,
            limite_restante=limite_sub,
            vencimento_formatado=vencimento_sub
        )

        # recalcula corretamente a revenda mãe já considerando a nova subrevenda
        if RECALCULAR_LIMITE_RESTANTE_REVENDA:
            RECALCULAR_LIMITE_RESTANTE_REVENDA(telegram_revenda)

        try:
            username_bot = f"@{BOT.get_me().username}"
        except:
            username_bot = "@do_bot_usado"

        BOT.send_message(
            message.chat.id,
            "✅ <b>Usuario cadastrado!</b>\n\n"
            f"<b>Usuario:</b> {ESC(telegram_sub)}\n"
            f"<b>Limite De Logins:</b> {ESC(limite_sub)}\n"
            f"<b>Validade:</b> {ESC(vencimento_sub)}\n\n"
            f"<b>Bot (Painel) :</b> {ESC(username_bot)}"
        )

    except Exception as e:
        BOT.send_message(
            message.chat.id,
            f"❌ Erro ao cadastrar-sub revenda.\n<code>{ESC(e)}</code>"
        )
    finally:
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)

# =========================================================
# DELETAR SUB REVENDA
# =========================================================
def receber_telegram_del_subrevenda(message):
    if not BOT:
        return

    dados = USER_DATA.get(message.from_user.id, {})
    if dados.get("acao") != "rev_del_subrevenda":
        return

    if not message.text:
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ @ inválido. Digite /menu para tentar novamente."
        )
        return

    telegram_sub = message.text.strip()

    if not telegram_sub.startswith("@"):
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ @ inválido. Digite /menu para tentar novamente."
        )
        return

    if not SUBREVENDA_EXISTE(telegram_sub):
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ Sub revenda não encontrada. Digite /menu para tentar novamente."
        )
        return

    try:
        DELETAR_SUBREVENDA_ARQUIVO(telegram_sub)

        BOT.send_message(
            message.chat.id,
            "🗑️ <b>Sub-revenda deletada!</b>\n\n"
            f"👤 <b>Telegram:</b> {ESC(telegram_sub)}"
        )

    except Exception as e:
        BOT.send_message(
            message.chat.id,
            f"❌ Erro ao deletar sub revenda.\n<code>{ESC(e)}</code>"
        )
    finally:
        USER_DATA.pop(message.from_user.id, None)

# =========================================================
# ALTERAR DATA DA SUB REVENDA - PASSO 1
# =========================================================
def receber_telegram_alt_data_subrevenda(message):
    if not BOT:
        return

    dados = USER_DATA.get(message.from_user.id, {})
    if dados.get("acao") != "rev_alt_data_subrevenda":
        return

    if not message.text:
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ @ inválido. Digite /menu para tentar novamente."
        )
        return

    telegram_sub = message.text.strip()

    if not telegram_sub.startswith("@"):
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ @ inválido. Digite /menu para tentar novamente."
        )
        return

    if not SUBREVENDA_EXISTE(telegram_sub):
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ Sub revenda não encontrada. Digite /menu para tentar novamente."
        )
        return

    USER_DATA[message.from_user.id]["telegram_sub_alt_data"] = telegram_sub
    limpar_trava_revenda(message.from_user.id)

    msg = BOT.send_message(
        message.chat.id,
        "Envie a nova quantidade de dias. Ex: 30"
    )
    BOT.register_next_step_handler(msg, receber_nova_data_subrevenda)

# =========================================================
# ALTERAR DATA DA SUB REVENDA - PASSO 2
# =========================================================
def receber_nova_data_subrevenda(message):
    if not BOT:
        return

    dados = USER_DATA.get(message.from_user.id, {})
    if dados.get("acao") != "rev_alt_data_subrevenda":
        return

    if not message.text:
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ Quantidade de dias inválida. Digite /menu para tentar novamente."
        )
        return

    texto = message.text.strip()

    if not texto.isdigit():
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ Quantidade de dias inválida. Digite /menu para tentar novamente."
        )
        return

    dias = int(texto)

    if dias <= 0:
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ Quantidade de dias inválida. Digite /menu para tentar novamente."
        )
        return

    telegram_sub = dados.get("telegram_sub_alt_data")
    if not telegram_sub:
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ Fluxo inválido. Digite /menu para tentar novamente."
        )
        return

    try:
        dados_sub = LER_DADOS_SUBREVENDA(telegram_sub)

        dono = str(dados_sub.get("dono", "")).strip()
        limite_total = int(dados_sub.get("limite_total", "0"))
        limite_restante = int(dados_sub.get("limite_restante", "0"))

        novo_vencimento = (datetime.now() + timedelta(days=dias)).strftime("%d/%m/%Y")

        SALVAR_SUBREVENDA_ARQUIVO(
            dono=dono,
            telegram_user=telegram_sub,
            limite_total=limite_total,
            limite_restante=limite_restante,
            vencimento_formatado=novo_vencimento
        )
        
        info_reativacao = {"estava_suspensa": False, "desbloqueados": []}
        
        if REATIVAR_SUBREVENDA:
            info_reativacao = REATIVAR_SUBREVENDA(telegram_sub)
        
        if info_reativacao.get("estava_suspensa"):
            BOT.send_message(
                message.chat.id,
                "✅ <b>A sub-revenda estava suspensa e não está mais.</b>"
            )
        
        BOT.send_message(
            message.chat.id,
            "✅ <b>Data da sub-revenda alterada!</b>\n\n"
            f"👤 <b>Telegram:</b> {ESC(telegram_sub)}\n"
            f"📅 <b>Novo vencimento:</b> {ESC(novo_vencimento)}"
        )

    except Exception as e:
        BOT.send_message(
            message.chat.id,
            f"❌ Erro ao alterar data da sub revenda.\n<code>{ESC(e)}</code>"
        )
    finally:
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)

# =========================================================
# ALTERAR LIMITE DA SUB REVENDA - PASSO 1
# =========================================================
def receber_telegram_alt_limite_subrevenda(message):
    if not BOT:
        return

    dados = USER_DATA.get(message.from_user.id, {})
    if dados.get("acao") != "rev_alt_limite_subrevenda":
        return

    if not message.text:
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ @ inválido. Digite /menu para tentar novamente."
        )
        return

    telegram_sub = message.text.strip()

    if not telegram_sub.startswith("@"):
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ @ inválido. Digite /menu para tentar novamente."
        )
        return

    if not SUBREVENDA_EXISTE(telegram_sub):
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ Sub revenda não encontrada. Digite /menu para tentar novamente."
        )
        return

    try:
        dados_sub = LER_DADOS_SUBREVENDA(telegram_sub)
        limite_atual = int(str(dados_sub.get("limite_total", "0")).strip())

        USER_DATA[message.from_user.id]["telegram_sub_alt_limite"] = telegram_sub
        USER_DATA[message.from_user.id]["limite_atual_sub"] = limite_atual

        limpar_trava_revenda(message.from_user.id)

        msg = BOT.send_message(
            message.chat.id,
            f"👥 Limite atual da sub revenda: <code>{ESC(limite_atual)}</code>\n\nEnvie o novo limite."
        )
        BOT.register_next_step_handler(msg, receber_novo_limite_subrevenda)

    except Exception as e:
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            f"❌ Erro ao ler dados da sub revenda.\n<code>{ESC(e)}</code>"
        )

# =========================================================
# ALTERAR LIMITE DA SUB REVENDA - PASSO 2
# Regras:
# - novo limite deve ser > 0
# - se aumentar, precisa haver crédito suficiente na revenda mãe
# - se diminuir, devolve crédito para a revenda mãe
# - não pode ficar abaixo do uso real da sub revenda
# =========================================================
def receber_novo_limite_subrevenda(message):
    if not BOT:
        return

    dados = USER_DATA.get(message.from_user.id, {})
    if dados.get("acao") != "rev_alt_limite_subrevenda":
        return

    if not message.text:
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ Limite inválido. Digite /menu para tentar novamente."
        )
        return

    texto = message.text.strip()

    if not texto.isdigit():
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ Limite inválido. Digite /menu para tentar novamente."
        )
        return

    novo_limite = int(texto)

    if novo_limite <= 0:
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ Limite inválido. Digite /menu para tentar novamente."
        )
        return

    telegram_sub = dados.get("telegram_sub_alt_limite")
    limite_atual_sub = int(dados.get("limite_atual_sub", 0))

    if not telegram_sub:
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ Fluxo inválido. Digite /menu para tentar novamente."
        )
        return

    try:
        dados_sub = LER_DADOS_SUBREVENDA(telegram_sub)

        dono = str(dados_sub.get("dono", "")).strip()
        limite_restante_sub = int(str(dados_sub.get("limite_restante", "0")).strip())
        vencimento_sub = str(dados_sub.get("vencimento", "")).strip()

        # uso real dos usuários da sub
        usado_sub = CALCULAR_LIMITE_USADO_REAL_SUBREVENDA(telegram_sub)

        # não pode baixar abaixo do uso atual
        if novo_limite < usado_sub:
            limpar_trava_revenda(message.from_user.id)
            USER_DATA.pop(message.from_user.id, None)
            BOT.send_message(
                message.chat.id,
                f"❌ Sub-revenda com limite acima de {ESC(novo_limite)} usados.\n\nExecute /menu e tente dnv"
            )
            return

        # diferença que falta para chegar no novo limite
        delta = novo_limite - limite_atual_sub

        # se aumentou, a revenda mãe precisa ter esse crédito disponível
        if delta > 0:
            dados_rev = LER_DADOS_REVENDA(dono)
            limite_restante_rev = int(str(dados_rev.get("limite_restante", "0")).strip())

            if delta > limite_restante_rev:
                limpar_trava_revenda(message.from_user.id)
                USER_DATA.pop(message.from_user.id, None)
                BOT.send_message(
                    message.chat.id,
                    "❌ Créditos insuficientes. Digite /menu para tentar novamente."
                )
                return

        # novo restante da sub = novo limite - usado
        novo_limite_restante_sub = novo_limite - usado_sub
        if novo_limite_restante_sub < 0:
            novo_limite_restante_sub = 0

        SALVAR_SUBREVENDA_ARQUIVO(
            dono=dono,
            telegram_user=telegram_sub,
            limite_total=novo_limite,
            limite_restante=novo_limite_restante_sub,
            vencimento_formatado=vencimento_sub
        )

        # recalcula corretamente a revenda mãe
        if RECALCULAR_LIMITE_RESTANTE_REVENDA:
            RECALCULAR_LIMITE_RESTANTE_REVENDA(dono)

        BOT.send_message(
            message.chat.id,
            "✅ <b>Limite da sub revenda alterado com sucesso!</b>\n\n"
            f"👤 <b>Telegram:</b> {ESC(telegram_sub)}\n"
            f"👥 <b>Novo limite:</b> <code>{ESC(novo_limite)}</code>"
        )

    except Exception as e:
        BOT.send_message(
            message.chat.id,
            f"❌ Erro ao alterar limite da sub revenda.\n<code>{ESC(e)}</code>"
        )
    finally:
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)

# =========================================================
# MONTAR TEXTO DO RELATÓRIO INDIVIDUAL DA SUB-REVENDA
# =========================================================
def montar_texto_relatorio_individual_subrevenda(telegram_sub):
    dados = LER_DADOS_SUBREVENDA(telegram_sub)

    dono = str(dados.get("dono", "")).strip()
    vencimento = str(dados.get("vencimento", "")).strip()
    limite_total = int(dados.get("limite_total", "0"))
    limite_restante = int(dados.get("limite_restante", "0"))
    status = "suspenso" if SUBREVENDA_SUSPENSA and SUBREVENDA_SUSPENSA(telegram_sub) else "ativo"

    usuarios = LER_USUARIOS_SUBREVENDA_COMPLETOS(telegram_sub)

    linhas = []
    linhas.append("⚠️ <b>DADOS DA SUB-REVENDA ⚠️</b>")
    linhas.append("")
    linhas.append(f"<b>Usuário:</b> {ESC(telegram_sub)}")
    linhas.append(f"<b>Data de vencimento:</b> {ESC(vencimento)}")
    linhas.append(f"<b>Limite atual:</b> {ESC(limite_total)}")
    linhas.append(f"<b>Limite restante:</b> {ESC(limite_restante)}")
    linhas.append(f"<b>Status:</b> {ESC(status)}")
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
# GERAR PDF DO RELATÓRIO INDIVIDUAL DA SUB-REVENDA
# =========================================================
def gerar_pdf_relatorio_individual_subrevenda(telegram_sub):
    dados = LER_DADOS_SUBREVENDA(telegram_sub)

    dono = str(dados.get("dono", "")).strip()
    vencimento = str(dados.get("vencimento", "")).strip()
    limite_total = int(dados.get("limite_total", "0"))
    limite_restante = int(dados.get("limite_restante", "0"))
    status = "suspenso" if SUBREVENDA_SUSPENSA and SUBREVENDA_SUSPENSA(telegram_sub) else "ativo"

    usuarios = LER_USUARIOS_SUBREVENDA_COMPLETOS(telegram_sub)

    nome_pdf = f"relatorio_individual_subrevenda_{random.randint(100,999)}.pdf"
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
        titulo = "RELATÓRIO INDIVIDUAL DA SUB-REVENDA"
        largura_titulo = stringWidth(titulo, "Helvetica-Bold", 16)
        c.drawString((largura_pagina - largura_titulo) / 2, altura_pagina - 35, titulo)

        c.setFont("Helvetica", 10)
        y = altura_pagina - 62

        c.drawString(margem_lateral, y, f"Usuário: {telegram_sub}")
        y -= 16
        c.drawString(margem_lateral, y, f"Dono: {dono}")
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
# RELATÓRIO INDIVIDUAL DA SUB-REVENDA
# =========================================================
def receber_telegram_relatorio_individual_subrevenda(message):
    if not BOT:
        return

    dados_fluxo = USER_DATA.get(message.from_user.id, {})
    if dados_fluxo.get("acao") != "rev_relatorio_individual_subrevenda":
        return

    if not message.text:
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ @ inválido. Digite /menu para tentar novamente."
        )
        return

    telegram_sub = message.text.strip()

    if not telegram_sub.startswith("@"):
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ @ inválido. Digite /menu para tentar novamente."
        )
        return

    if not SUBREVENDA_EXISTE(telegram_sub):
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ Sub-revenda não encontrada. Digite /menu para tentar novamente."
        )
        return

    msg_consultando = None

    try:
        # varredura individual da sub-revenda antes de gerar o relatório
        if SINCRONIZAR_ARQUIVO_SUBREVENDA:
            SINCRONIZAR_ARQUIVO_SUBREVENDA(telegram_sub)

        texto, usuarios = montar_texto_relatorio_individual_subrevenda(telegram_sub)

        # se couber em texto, substitui a mensagem atual
        if len(texto) <= 3500:
            limpar_trava_revenda(message.from_user.id)
            USER_DATA.pop(message.from_user.id, None)

            BOT.send_message(
                message.chat.id,
                texto,
                reply_markup=painel_relatorio_individual_subrevenda_markup()
            )
            return

        # se não couber, mantém o painel e manda consultando embaixo
        msg_consultando = BOT.send_message(
            message.chat.id,
            "<b>Consultando.</b>"
        )

        pdf_path = gerar_pdf_relatorio_individual_subrevenda(telegram_sub)

        try:
            with open(pdf_path, "rb") as pdf_file:
                BOT.send_document(
                    message.chat.id,
                    pdf_file,
                    caption=f"Relatório individual da sub-revenda ({len(usuarios)} usuário(s))"
                )
        finally:
            try:
                if msg_consultando:
                    BOT.delete_message(message.chat.id, msg_consultando.message_id)
            except:
                pass

            if os.path.exists(pdf_path):
                os.remove(pdf_path)

    except Exception as e:
        try:
            if msg_consultando:
                BOT.delete_message(message.chat.id, msg_consultando.message_id)
        except:
            pass

        BOT.send_message(
            message.chat.id,
            f"❌ Erro ao gerar relatório individual da sub-revenda.\n<code>{ESC(e)}</code>"
        )
    finally:
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)

# =========================================================
# SUSPENDER SUB-REVENDA MANUALMENTE
# =========================================================
def receber_telegram_suspender_subrevenda(message):
    if not BOT:
        return

    dados_fluxo = USER_DATA.get(message.from_user.id, {})
    if dados_fluxo.get("acao") != "rev_suspender_subrevenda":
        return

    if not message.text:
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ @ inválido. Digite /menu para tentar novamente."
        )
        return

    telegram_sub = message.text.strip()

    if not telegram_sub.startswith("@"):
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ @ inválido. Digite /menu para tentar novamente."
        )
        return

    if not SUBREVENDA_EXISTE(telegram_sub):
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ Sub-revenda não encontrada. Digite /menu para tentar novamente."
        )
        return

    if SUBREVENDA_SUSPENSA(telegram_sub):
        BOT.send_message(
            message.chat.id,
            f"⚠️ A sub-revenda {ESC(telegram_sub)} já está suspensa."
        )
        resetar_fluxo_revenda(message.from_user.id)
        return
    
    try:
        # varredura antes de tudo, como você pediu
        if SINCRONIZAR_ARQUIVO_SUBREVENDA:
            SINCRONIZAR_ARQUIVO_SUBREVENDA(telegram_sub)

        if SUBREVENDA_SUSPENSA and SUBREVENDA_SUSPENSA(telegram_sub):
            limpar_trava_revenda(message.from_user.id)
            USER_DATA.pop(message.from_user.id, None)
            BOT.send_message(
                message.chat.id,
                "❌ Essa sub-revenda já está suspensa.\nDigite /menu para tentar novamente."
            )
            return

        SUSPENDER_SUBREVENDA_MANUALMENTE(telegram_sub)

        BOT.send_message(
            message.chat.id,
            "⛔ <b>Painel suspenso com sucesso!</b>\n\n"
            f"👤 <b>Sub-revenda:</b> {ESC(telegram_sub)}"
        )

    except Exception as e:
        BOT.send_message(
            message.chat.id,
            f"❌ Erro ao suspender sub-revenda.\n<code>{ESC(e)}</code>"
        )
    finally:
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)

# =========================================================
# RENOVAR SUB-REVENDA
# Segue o mesmo conceito da renovação da revenda:
# - ativa -> +1 mês sobre o vencimento atual
# - suspensa -> +1 mês sobre hoje e reativa usuários
# =========================================================
def receber_telegram_renovar_subrevenda(message):
    if not BOT:
        return

    dados_fluxo = USER_DATA.get(message.from_user.id, {})
    if dados_fluxo.get("acao") != "rev_renovar_subrevenda":
        return

    if not message.text:
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ @ inválido. Digite /menu para tentar novamente."
        )
        return

    telegram_sub = message.text.strip()

    if not telegram_sub.startswith("@"):
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ @ inválido. Digite /menu para tentar novamente."
        )
        return

    if not SUBREVENDA_EXISTE(telegram_sub):
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)
        BOT.send_message(
            message.chat.id,
            "❌ Sub-revenda não encontrada. Digite /menu para tentar novamente."
        )
        return

    try:
        info = RENOVAR_SUBREVENDA(telegram_sub)

        # Se a sub estava suspensa e foi reativada, manda aviso separado antes
        if info.get("estava_suspensa"):
            BOT.send_message(
                message.chat.id,
                "✅ <b>A sub-revenda estava suspensa e não está mais.</b>"
            )

        BOT.send_message(
            message.chat.id,
            "✅ <b>Sub-revenda renovada com sucesso!</b>\n\n"
            f"👤 <b>Telegram:</b> {ESC(telegram_sub)}\n"
            f"📅 <b>Novo vencimento:</b> {ESC(info['novo_vencimento'])}"
        )

    except Exception as e:
        BOT.send_message(
            message.chat.id,
            f"❌ Erro ao renovar sub-revenda.\n<code>{ESC(e)}</code>"
        )
    finally:
        limpar_trava_revenda(message.from_user.id)
        USER_DATA.pop(message.from_user.id, None)
        
# =========================================================
# LISTAR SUB-REVENDAS DE UMA REVENDA
# =========================================================
def listar_subrevendas_da_revenda_relatorio(telegram_revenda):
    resultado = []

    if not SUB_DIR or not os.path.exists(SUB_DIR):
        return resultado

    for nome_arquivo in os.listdir(SUB_DIR):
        if not nome_arquivo.endswith(".txt"):
            continue

        telegram_sub = "@" + nome_arquivo[:-4]

        try:
            dados = LER_DADOS_SUBREVENDA(telegram_sub)
            dono = str(dados.get("dono", "")).strip()

            if dono == telegram_revenda:
                resultado.append(telegram_sub)
        except:
            continue

    return sorted(resultado, key=lambda x: x.lower())


# =========================================================
# MARKUP DO USUÁRIO AUTOMÁTICO DA REVENDA
# =========================================================
def painel_revenda_auto_meses_markup():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("📅 1 mês", callback_data="rev_auto_mes_1"))
    kb.add(types.InlineKeyboardButton("📅 2 meses", callback_data="rev_auto_mes_2"))
    kb.add(types.InlineKeyboardButton("📅 3 meses", callback_data="rev_auto_mes_3"))
    return kb


def painel_revenda_auto_tipo_markup():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("XRay", callback_data="rev_auto_tipo_xray"),
        types.InlineKeyboardButton("Nenhum", callback_data="rev_auto_tipo_nenhum")
    )
    return kb

# =========================================================
# CALCULAR VENCIMENTO MENSAL POR DATA
# =========================================================
def calcular_vencimento_mensal_revenda(meses):
    hoje = datetime.now().date()
    return hoje + __import__("dateutil").relativedelta.relativedelta(months=+meses)


# =========================================================
# CALCULAR DIAS ATÉ O VENCIMENTO
# =========================================================
def calcular_dias_ate_vencimento_revenda(vencimento):
    hoje = datetime.now().date()
    dias = (vencimento - hoje).days

    if dias <= 0:
        dias = 1

    return dias


# =========================================================
# GERAR USERNAME AUTOMÁTICO DA REVENDA
# Formato: redexxx
# =========================================================
def gerar_username_auto_revenda():
    return f"rede{__import__('random').randint(100, 999)}"
