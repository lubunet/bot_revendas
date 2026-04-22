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
    echo -e "  ${STEP5} Criar pasta /root/revenda"
    echo -e "  ${STEP6} Instalar pyTelegramBotAPI"
    echo -e "  ${STEP7} Instalar reportlab"
    echo -e "  ${STEP8} Instalar python-dateutil"
    echo
}

refresh_screen() {
    print_header
    print_list
}

run_step() {
    local stepvar="$1"
    local label="$2"
    shift 2

    eval "$stepvar=\"\$doing\""
    refresh_screen

    local frames=(
        "[=         ]"
        "[==        ]"
        "[===       ]"
        "[ ====     ]"
        "[  ====    ]"
        "[   ====   ]"
        "[    ====  ]"
        "[     ==== ]"
        "[      ====]"
        "[     ==== ]"
        "[    ====  ]"
        "[   ====   ]"
        "[  ====    ]"
        "[ ====     ]"
        "[===       ]"
        "[==        ]"
    )

    (
        while true; do
            for frame in "${frames[@]}"; do
                printf "\r${BLUE}%b${NC} Instalando: ${WHITE}%s${NC}   " "$frame" "$label"
                sleep 0.12
            done
        done
    ) &
    local anim_pid=$!

    if "$@" >/dev/null 2>&1; then
        kill "$anim_pid" 2>/dev/null || true
        wait "$anim_pid" 2>/dev/null || true
        printf "\r\033[K"
        eval "$stepvar=\"\$done_mark\""
        refresh_screen
    else
        kill "$anim_pid" 2>/dev/null || true
        wait "$anim_pid" 2>/dev/null || true
        printf "\r\033[K"
        echo -e "${RED}Erro durante: ${label}${NC}"
        exit 1
    fi
}

if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Este instalador precisa ser executado como root.${NC}"
    exit 1
fi

run_step STEP1 "Atualizando pacotes do sistema" apt update -y
run_step STEP2 "Instalando Git" apt install -y git
run_step STEP3 "Instalando Python 3 e pip" apt install -y python3 python3-pip
run_step STEP4 "Baixando arquivos do GitHub" git clone "$REPO_URL" "$TEMP_DIR"

run_step STEP5 "Criando pasta /root/revenda e movendo arquivos" bash -c "
rm -rf '$INSTALL_DIR'
mkdir -p '$INSTALL_DIR'
find '$TEMP_DIR' -maxdepth 1 -type f -name '*.py' -exec cp {} '$INSTALL_DIR'/ \;
if [ -f '$TEMP_DIR/install.sh' ]; then
    cp '$TEMP_DIR/install.sh' '$INSTALL_DIR'/install.sh
fi
rm -rf '$TEMP_DIR'
"

run_step STEP6 "Instalando pyTelegramBotAPI" pip3 install pyTelegramBotAPI
run_step STEP7 "Instalando reportlab" pip3 install reportlab
run_step STEP8 "Instalando python-dateutil" pip3 install python-dateutil

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
