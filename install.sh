#!/bin/bash

set -e

REPO_URL="https://github.com/lubunet/bot_revendas.git"
INSTALL_DIR="/root/revenda"
TEMP_DIR="/tmp/bot_revendas_install"
SERVICE_NAME="revenda"
MAIN_FILE="bot.py"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

CURRENT_STEP=0
TOTAL_STEPS=8

STEP1="•"
STEP2="•"
STEP3="•"
STEP4="•"
STEP5="•"
STEP6="•"
STEP7="•"
STEP8="•"

doing="➜"
done_mark="${GREEN}✔${NC}"

print_header() {
    clear
    echo -e "${CYAN}====================================================${NC}"
    echo -e "${CYAN}         INSTALADOR DO BOT DE REVENDA               ${NC}"
    echo -e "${CYAN}====================================================${NC}"
    echo
}

print_list() {
    echo -e "${YELLOW}Checklist da instalação:${NC}"
    echo -e "  ${STEP1} Atualizar pacotes"
    echo -e "  ${STEP2} Instalar Git"
    echo -e "  ${STEP3} Instalar Python 3"
    echo -e "  ${STEP4} Baixar arquivos do GitHub"
    echo -e "  ${STEP5} Criar pasta ${INSTALL_DIR}"
    echo -e "  ${STEP6} Instalar pyTelegramBotAPI"
    echo -e "  ${STEP7} Instalar reportlab"
    echo -e "  ${STEP8} Instalar python-dateutil"
    echo
}

show_progress() {
    local label="$1"
    local percent=$((CURRENT_STEP * 100 / TOTAL_STEPS))
    local filled=$((percent / 10))
    local empty=$((10 - filled))
    local bar="["

    for ((i=0; i<filled; i++)); do bar="${bar}="; done
    for ((i=0; i<empty; i++)); do bar="${bar} "; done
    bar="${bar}]"

    echo -e "${BLUE}${bar}${NC} Instalando: ${WHITE}${label}${NC}"
    echo
}

refresh_screen() {
    print_header
    print_list
}

step_start() {
    CURRENT_STEP=$((CURRENT_STEP + 1))
    refresh_screen
    show_progress "$1"
}

step_done() {
    refresh_screen
}

if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Este instalador precisa ser executado como root.${NC}"
    exit 1
fi

STEP1="$doing"
step_start "Atualizando pacotes do sistema"
apt update -y >/dev/null 2>&1
STEP1="$done_mark"
step_done

STEP2="$doing"
step_start "Instalando Git"
apt install -y git >/dev/null 2>&1
STEP2="$done_mark"
step_done

STEP3="$doing"
step_start "Instalando Python 3 e pip"
apt install -y python3 python3-pip >/dev/null 2>&1
STEP3="$done_mark"
step_done

STEP4="$doing"
step_start "Baixando arquivos do GitHub"
rm -rf "$TEMP_DIR"
git clone "$REPO_URL" "$TEMP_DIR" >/dev/null 2>&1
STEP4="$done_mark"
step_done

STEP5="$doing"
step_start "Criando pasta /root/revenda e movendo os arquivos"
mkdir -p "$INSTALL_DIR"

find "$TEMP_DIR" -maxdepth 1 -type f -name "*.py" -exec cp {} "$INSTALL_DIR"/ \;

if [ -f "$TEMP_DIR/install.sh" ]; then
    cp "$TEMP_DIR/install.sh" "$INSTALL_DIR"/install.sh
fi

rm -rf "$TEMP_DIR"
STEP5="$done_mark"
step_done

STEP6="$doing"
step_start "Instalando pyTelegramBotAPI"
pip3 install pyTelegramBotAPI >/dev/null 2>&1
STEP6="$done_mark"
step_done

STEP7="$doing"
step_start "Instalando reportlab"
pip3 install reportlab >/dev/null 2>&1
STEP7="$done_mark"
step_done

STEP8="$doing"
step_start "Instalando python-dateutil"
pip3 install python-dateutil >/dev/null 2>&1
STEP8="$done_mark"
step_done

print_header
print_list

echo -e "${GREEN}Arquivos instalados com sucesso em:${NC} ${WHITE}${INSTALL_DIR}${NC}"
echo

echo -e "${CYAN}Arquivos .py encontrados na pasta:${NC}"
ls -1 "${INSTALL_DIR}"/*.py 2>/dev/null || true
echo

while true; do
    echo -ne "${YELLOW}Deseja adicionar o bot no systemctl e iniciar agora? [Y/N]: ${NC}"
    read -r RESP

    case "$RESP" in
        Y|y)
            cat > /etc/systemd/system/${SERVICE_NAME}.service <<EOF
[Unit]
Description=Bot Revenda Telegram
After=network.target

[Service]
Type=simple
WorkingDirectory=${INSTALL_DIR}
ExecStart=/usr/bin/python3 ${INSTALL_DIR}/${MAIN_FILE}
Restart=always
RestartSec=5
User=root

[Install]
WantedBy=multi-user.target
EOF

            systemctl daemon-reload
            systemctl enable ${SERVICE_NAME}.service >/dev/null 2>&1
            systemctl restart ${SERVICE_NAME}.service

            echo
            echo -e "${GREEN}Bot adicionado ao systemctl com sucesso.${NC}"
            echo -e "${CYAN}Nome do serviço:${NC} ${WHITE}revenda.service${NC}"
            echo -e "${CYAN}Status:${NC} já foi iniciado automaticamente."
            echo
            echo -e "${CYAN}Comandos úteis:${NC}"
            echo -e "  systemctl status revenda.service"
            echo -e "  systemctl restart revenda.service"
            echo -e "  journalctl -u revenda.service -f"
            break
            ;;
        N|n)
            echo
            echo -e "${YELLOW}Bot instalado sem systemctl.${NC}"
            echo -e "${CYAN}Local da instalação:${NC} ${WHITE}/root/revenda${NC}"
            break
            ;;
        *)
            echo -e "${RED}Resposta inválida. Digite apenas Y/y ou N/n.${NC}"
            echo
            ;;
    esac
done

echo
read -rp "Pressione Enter para sair..."
