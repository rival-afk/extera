"""Отправка файлов через Telethon"""

import asyncio
from pathlib import Path
from typing import Optional

from .metadata import PluginMetadata, generate_plugin_caption

try:
    from telethon import TelegramClient
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False


async def send_to_saved(
    file_path: Path, 
    api_id: int, 
    api_hash: str,
    metadata: Optional[PluginMetadata] = None
) -> bool:
    """Отправляет файл в Избранное с caption и иконкой как preview"""
    
    if not TELEGRAM_AVAILABLE:
        print("❌ Telethon не установлен")
        print("   Установите: pip install telethon")
        return False
    
    client = TelegramClient('plugin_builder_session', api_id, api_hash)
    
    try:
        await client.connect()
        
        if not await client.is_user_authorized():
            print("🔐 Требуется авторизация...")
            await client.start()
            print("✅ Авторизация успешна")
        
        me = await client.get_me()
        
        # Генерируем caption
        if metadata and metadata.is_valid():
            caption = generate_plugin_caption(metadata, file_path.name)
        else:
            caption = f"📎 Плагин: {file_path.name}"
        
        # Подготовка к отправке
        send_kwargs = {
            'file': str(file_path),
            'caption': caption,
            'parse_mode': 'markdown',
            'force_document': True
        }
        
        # Если есть PNG иконка - прикрепляем как preview
        if metadata and metadata.has_png_icon():
            icon_path = metadata.get_png_icon_path()
            send_kwargs['thumb'] = str(icon_path)
            print(f"   🖼️  Иконка прикреплена: {icon_path.name}")
        
        # Отправляем
        await client.send_file(me.id, **send_kwargs)
        
        print(f"📤 Плагин {file_path.name} отправлен в Избранное")
        
        if metadata and metadata.is_valid():
            print(f"   📌 {metadata.get('name')} v{metadata.get('version', '?')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")
        return False
    finally:
        await client.disconnect()
