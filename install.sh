#!/usr/bin/env bash
# install.sh - установка plugin-builder

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Plugin Builder - Установка          ${NC}"
echo -e "${BLUE}========================================${NC}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Определяем shell
if [ -f "$HOME/.zshrc" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
    SHELL_TYPE="zsh"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
    SHELL_TYPE="bash"
else
    SHELL_CONFIG="$HOME/.zshrc"
    SHELL_TYPE="zsh"
fi

echo -e "${GREEN}📁 Shell: $SHELL_TYPE, Конфиг: $SHELL_CONFIG${NC}"

# Создаём ~/bin
BIN_DIR="$HOME/bin"
mkdir -p "$BIN_DIR"
echo -e "${GREEN}✅ Создана директория: $BIN_DIR${NC}"

# Добавляем ~/bin в PATH
if ! grep -q 'export PATH="$HOME/bin:$PATH"' "$SHELL_CONFIG" 2>/dev/null; then
    echo -e "${BLUE}📝 Добавляем ~/bin в PATH...${NC}"
    echo "" >> "$SHELL_CONFIG"
    echo "# Добавлено Plugin Builder" >> "$SHELL_CONFIG"
    echo 'export PATH="$HOME/bin:$PATH"' >> "$SHELL_CONFIG"
    echo -e "${GREEN}✅ PATH обновлён в $SHELL_CONFIG${NC}"
else
    echo -e "${GREEN}✅ ~/bin уже в PATH${NC}"
fi

export PATH="$BIN_DIR:$PATH"

# Виртуальное окружение
echo -e "${BLUE}📦 Настройка виртуального окружения...${NC}"

if [ ! -d ".venv" ]; then
    python -m venv .venv
    echo -e "${GREEN}✅ Виртуальное окружение создано${NC}"
else
    echo -e "${GREEN}✅ Виртуальное окружение уже существует${NC}"
fi

# Активируем venv
source .venv/bin/activate

# Устанавливаем зависимости
echo -e "${BLUE}📦 Установка зависимостей...${NC}"
pip install --upgrade pip -q
pip install python-dotenv -q
echo -e "${GREEN}✅ Базовые зависимости установлены${NC}"

# Проверяем .env
if [ -f ".env" ]; then
    source .env
    if [ -n "$API_ID" ] && [ -n "$API_HASH" ] && [ "$API_ID" != "12345678" ]; then
        pip install telethon -q
        echo -e "${GREEN}✅ Telethon установлен (для отправки)${NC}"
        
        # Устанавливаем pycryptodome если нужно для тестов
        if [ -f "requirements_extra.txt" ]; then
            pip install -r requirements_extra.txt -q 2>/dev/null || true
        fi
    else
        echo -e "${YELLOW}⚠️ API_ID или API_HASH не настроены${NC}"
        echo -e "${YELLOW}   Отправка в Telegram будет недоступна${NC}"
    fi
else
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✅ Создан .env из примера${NC}"
        echo -e "${YELLOW}⚠️ Отредактируйте .env для отправки в Telegram${NC}"
        echo -e "${BLUE}   Получить API: https://my.telegram.org/apps${NC}"
    fi
fi

# Создаём исполняемый файл epb
cat > epb << 'EOF'
#!/usr/bin/env bash
BUILDER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(pwd)"

cd "$BUILDER_DIR"
source .venv/bin/activate
exec python build.py "$PROJECT_DIR" "$@"
EOF

chmod +x epb
echo -e "${GREEN}✅ Создан скрипт epb${NC}"

# Символическая ссылка
LINK_PATH="$BIN_DIR/epb"
if [ -L "$LINK_PATH" ] || [ -f "$LINK_PATH" ]; then
    rm -f "$LINK_PATH"
fi
ln -s "$SCRIPT_DIR/epb" "$LINK_PATH"
echo -e "${GREEN}✅ Создана команда: epb -> $LINK_PATH${NC}"

# Деактивируем venv
deactivate

echo -e ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Установка завершена!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e ""
echo -e "${BLUE}📖 Использование:${NC}"
echo -e "  cd ~/projects/my_plugin"
echo -e "  epb              # Собрать плагин"
echo -e "  epb -s           # Собрать и отправить"
echo -e "  epb -v           # Подробный вывод"
echo -e ""
echo -e "${BLUE}📁 Структура проекта плагина:${NC}"
echo -e "  my_plugin/"
echo -e "  ├── main.py       # Обязательный файл"
echo -e "  ├── config.py     # Дополнительные модули"
echo -e "  └── icon.png      # Иконка (опционально)"
echo -e ""
echo -e "${YELLOW}⚠️  Для применения изменений выполните:${NC}"
echo -e "  source $SHELL_CONFIG"
echo -e "  или перезапустите Termux"
