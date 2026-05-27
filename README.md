# 🤖 Bot de Revendas — LUBU NET

Bot em Python para gerenciamento de usuários, testes, revendas e sub-revendas via Telegram.

O projeto foi feito para facilitar o controle de logins diretamente pelo Telegram, com painel administrativo, criação de usuários, testes temporários, controle de limite, renovação, exclusão, relatórios e integração com o sistema da VPS.

---

## ✨ Funções principais

- 👤 Criar usuários manualmente
- ⏱️ Criar testes temporários
- ⚡ Criar usuários automáticos
- 🔐 Alterar senha de usuários
- 📊 Alterar limite de conexões
- 📅 Alterar vencimento
- 🔄 Renovar usuários
- 🗑️ Deletar usuários
- 🧹 Apagar expirados
- 📋 Listar usuários
- 🔎 Consultar usuário individual
- 🧾 Painel de revendas
- 👥 Painel de sub-revendas
- 📦 Backup e restauração
- 🧠 Monitoramento automático de testes expirados
- ⚙️ Opção para iniciar junto com o sistema usando `systemctl`

---

## 📁 Estrutura instalada

Após a instalação, os arquivos principais do bot ficam em:

```bash
/root/revenda
```

Arquivos principais do projeto:

```bash
bot.py
revenda.py
sub.py
```

O arquivo principal executado pelo serviço é:

```bash
/root/revenda/bot.py
```

---

## 🧰 Requisitos

Recomendado:

- VPS Linux baseada em Debian/Ubuntu
- Acesso root
- Python 3
- pip3
- curl
- unzip
- Sistema com suporte a `systemctl`

O instalador já tenta instalar automaticamente:

```bash
python3
python3-pip
curl
unzip
pyTelegramBotAPI
reportlab
python-dateutil
```

---

## 🚀 Instalação sem Git

Você não precisa usar `git clone`.

Execute como root:

```bash
curl -fsSL https://raw.githubusercontent.com/lubunet/bot_revendas/main/install.sh -o install.sh && chmod +x install.sh && ./install.sh
```

Ou, se preferir usando `wget`:

```bash
wget -O install.sh https://raw.githubusercontent.com/lubunet/bot_revendas/main/install.sh && chmod +x install.sh && ./install.sh
```

---

## ⚙️ O que o instalador faz?

Durante a instalação, o script executa automaticamente as seguintes etapas:

1. Atualiza os pacotes do sistema
2. Instala Python 3 e pip
3. Instala curl e unzip
4. Baixa os arquivos do GitHub em formato `.zip`
5. Cria a pasta `/root/revenda`
6. Copia os arquivos `.py` para `/root/revenda`
7. Instala `pyTelegramBotAPI`
8. Instala `reportlab`
9. Instala `python-dateutil`

No final, ele pergunta:

```bash
Deseja adicionar o bot no systemctl e iniciar agora? [Y/N]
```

Digite:

```bash
Y
```

para criar o serviço automaticamente.

---

## ▶️ Iniciar com systemctl

Se você escolher `Y` no final da instalação, o bot será adicionado como serviço:

```bash
revenda.service
```

Comandos úteis:

```bash
systemctl status revenda.service
```

```bash
systemctl restart revenda.service
```

```bash
journalctl -u revenda.service -f
```

---

## ▶️ Rodar manualmente

Caso você escolha não adicionar ao `systemctl`, ainda pode iniciar o bot manualmente:

```bash
cd /root/revenda
python3 bot.py
```

---

## 🔧 Configuração do bot

Antes de usar, confira as configurações principais dentro do arquivo:

```bash
/root/revenda/bot.py
```

Procure por:

```python
TOKEN = "SEU_TOKEN_DO_BOT"
ADMIN_ID = 123456789
```

Altere para o token correto do seu bot do Telegram e para o ID do administrador.

---

## 🔐 Aviso importante de segurança

Nunca deixe o token real do Telegram exposto em repositório público.

Se você já publicou o token no GitHub, faça o seguinte:

1. Acesse o BotFather no Telegram
2. Gere um novo token para o bot
3. Atualize o `TOKEN` no arquivo `bot.py`
4. Reinicie o serviço

Depois de alterar:

```bash
systemctl restart revenda.service
```

---

## 🧩 Dependências extras

Se ao iniciar aparecer erro como:

```bash
ModuleNotFoundError
```

instale manualmente os módulos que faltarem:

```bash
pip3 install requests pytz
```

Depois reinicie:

```bash
systemctl restart revenda.service
```

---

## 🧪 Comandos no Telegram

No Telegram, envie:

```bash
/start
```

Depois abra o painel com:

```bash
/menu
```

O painel será liberado apenas para o administrador configurado no `ADMIN_ID`.

---

## 🗂️ Dados usados pelo bot

O bot utiliza alguns caminhos importantes na VPS:

```bash
/root/revenda/testes.txt
/root/revenda/uuid_mode.txt
/root/revenda/uuid_exp_mode.txt
/root/revenda/uuid_exp.txt
/root/revenda/auto_backup.txt
/root/revenda/dados_rev
/root/revenda/dados_sub
/root/usuarios.db
/etc/SSHPlus/senha
/usr/local/etc/xray/config.json
```

---

## 🔄 Atualizar o bot

Para reinstalar a versão mais recente do repositório:

```bash
curl -fsSL https://raw.githubusercontent.com/lubunet/bot_revendas/main/install.sh -o install.sh && chmod +x install.sh && ./install.sh
```

Depois reinicie o serviço:

```bash
systemctl restart revenda.service
```

---

## ❌ Remover o serviço

Se quiser parar e remover o serviço do sistema:

```bash
systemctl stop revenda.service
systemctl disable revenda.service
rm -f /etc/systemd/system/revenda.service
systemctl daemon-reload
```

Se quiser apagar também os arquivos do bot:

```bash
rm -rf /root/revenda
```

---

## 📌 Observações

- Execute sempre como root.
- O bot depende da estrutura da VPS e dos caminhos configurados no código.
- O serviço criado usa o arquivo `/root/revenda/bot.py`.
- Caso altere o token, ID do admin ou arquivos internos, reinicie o serviço.
- Para acompanhar erros em tempo real, use:

```bash
journalctl -u revenda.service -f
```

---

## 👨‍💻 Projeto

Bot de gerenciamento de revendas desenvolvido para uso com painel via Telegram.

Use:

```bash
/menu
```

para abrir o painel principal do administrador.
