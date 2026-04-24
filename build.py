#!/usr/bin/env python3
"""Plugin Builder - точка входа"""

import os
import sys
import asyncio
import argparse
from pathlib import Path
from dotenv import load_dotenv

from builder.compiler import compile_plugin


def load_env(builder_dir: Path):
    env_file = builder_dir / '.env'
    if env_file.exists():
        load_dotenv(env_file)


def main():
    parser = argparse.ArgumentParser(description='Plugin Builder for exteraGram/AyuGram')
    parser.add_argument('project_dir', help='Путь к папке проекта')
    parser.add_argument('-s', '--send', action='store_true', help='Отправить в Избранное')
    parser.add_argument('-v', '--verbose', action='store_true', help='Подробный вывод')
    
    args = parser.parse_args()
    
    builder_dir = Path(__file__).parent.resolve()
    load_env(builder_dir)
    
    api_id = os.environ.get('API_ID')
    api_hash = os.environ.get('API_HASH')
    
    if args.send and (not api_id or not api_hash or api_id == '12345678'):
        print("❌ Для отправки нужны API_ID и API_HASH в .env")
        print(f"   Отредактируйте: {builder_dir}/.env")
        print("   Получить: https://my.telegram.org/apps")
        sys.exit(1)
    
    try:
        project_path = Path(args.project_dir).resolve()
        plugin_file, metadata = compile_plugin(project_path, verbose=args.verbose)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)
    
    if args.send:
        try:
            from builder.sender import send_to_saved
            asyncio.run(send_to_saved(plugin_file, int(api_id), api_hash, metadata))
        except ImportError:
            print("❌ Telethon не установлен. Запустите: pip install telethon")
            sys.exit(1)


if __name__ == '__main__':
    main()
