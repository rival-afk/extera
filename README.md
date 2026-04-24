# 🔌 Plugin Builder for exteraGram / AyuGram

**Компилятор многомодульных плагинов в `.plugin` файл с автоматическим встраиванием зависимостей из venv**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://www.python.org/)

## ✨ Возможности

- 📁 **Многомодульная разработка** — разделяйте код на несколько файлов
- 🔗 **Автоматическое разрешение зависимостей** — правильный порядок вставки
- 📦 **Встраивание внешних библиотек** — берёт реальный код из venv и встраивает в плагин
- 🧹 **Очистка от локальных импортов** — удаляет ненужные импорты из итогового файла
- 🖼️ **Поддержка PNG иконок** — отправка `icon.png` как preview
- 📤 **Отправка в Telegram** — опционально, через Telethon
- 🚀 **Простая установка** — одна команда и `epb` готов к использованию

## 📦 Установка

```bash
git clone https://github.com/yourusername/plugin-builder.git
cd plugin-builder
./install.sh
```

После установки команда epb будет доступна глобально.

🎯 Использование

```bash
cd ~/projects/my_plugin
epb              # Просто собрать плагин
epb -s           # Собрать и отправить в Избранное
epb -v           # Подробный вывод
epb -s -v        # Отправить с подробностями
```

📁 Структура проекта плагина

```
my_plugin/
├── main.py       # Обязательный файл с метаданными
├── config.py     # Любые дополнительные модули
├── utils.py
└── icon.png      # Опционально (будет preview в Telegram)
```

Пример main.py

```python
__id__ = "my_plugin"
__name__ = "My Plugin"
__description__ = "Описание плагина [.cmd]"
__author__ = "@username"
__version__ = "1.0.0"
__icon__ = "exteraPlugins/5"  # Только для интерфейса

from base_plugin import BasePlugin
from .config import SETTINGS

class MyPlugin(BasePlugin):
    def on_plugin_load(self):
        print(f"Loaded with {SETTINGS}")
```

🔐 Настройка отправки в Telegram (опционально)

1. Зайдите на my.telegram.org
2. Создайте приложение (название любое)
3. Скопируйте api_id и api_hash
4. Создайте файл .env в корне plugin-builder:

```
API_ID=12345678
API_HASH=your_api_hash_here
```

📤 Отправка в Избранное

```bash
cd ~/projects/my_plugin
epb -s
```

При первом запуске Telethon запросит номер телефона и код подтверждения.

🛠️ Как работает встраивание библиотек

Компилятор автоматически:

1. Анализирует все импорты в файлах проекта
2. Определяет, какие библиотеки являются внешними
3. Находит установленные библиотеки в .venv/lib/python*/site-packages/
4. Рекурсивно встраивает код библиотек и их зависимостей
5. Удаляет строки импорта, заменяя их на встроенный код

Установка внешних библиотек в venv

```bash
cd plugin-builder
source .venv/bin/activate
pip install pycryptodome  # или любая другая библиотека
```

📝 Метаданные плагина

Поле Обязательно Описание
__id__ ✅ Уникальный идентификатор плагина
__name__ ✅ Отображаемое имя
__description__ ❌ Описание функционала
__author__ ❌ Автор плагина
__version__ ❌ Версия (по умолчанию 1.0)
__icon__ ❌ Эмодзи иконка (например exteraPlugins/5)
__min_version__ ❌ Минимальная версия клиента

🗂️ Структура билдера

```
plugin-builder/
├── builder/
│   ├── compiler.py      # Основная логика сборки
│   ├── deps.py          # Анализ зависимостей
│   ├── cleaner.py       # Очистка синтаксических ошибок
│   ├── metadata.py      # Работа с метаданными
│   ├── sender.py        # Отправка через Telethon
│   └── importer.py      # Встраивание библиотек из venv
├── build.py             # Точка входа
├── epb                  # Исполняемый файл
├── install.sh           # Установщик
├── requirements.txt     # Базовые зависимости
└── .env.example         # Пример конфига API
```

🐛 Устранение проблем

epb: command not found

```bash
source ~/.zshrc  # или source ~/.bashrc
```

Ошибка импорта библиотеки

Установите нужную библиотеку в venv билдера:

```bash
cd plugin-builder
source .venv/bin/activate
pip install название_библиотеки
```

Плагин не загружается в клиенте

Проверьте метаданные в main.py:

· __id__ только латиница, цифры, _ и -
· __name__ не пустой
· __min_version__ соответствует версии клиента

📝 Лицензия

MIT
