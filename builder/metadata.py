"""Извлечение метаданных плагина и работа с иконками"""

import re
from pathlib import Path
from typing import Dict, Optional


class PluginMetadata:
    """Класс для работы с метаданными плагина"""
    
    def __init__(self, main_file: Path, project_dir: Path = None, verbose: bool = False):
        self.main_file = main_file
        self.project_dir = project_dir or main_file.parent
        self.verbose = verbose
        self.metadata = self._extract_metadata()
        self.png_icon_path = self._find_png_icon()
    
    def _extract_metadata(self) -> Dict[str, Optional[str]]:
        """Извлекает метаданные из main.py"""
        metadata = {
            'id': None, 'name': None, 'description': None,
            'author': None, 'version': None, 'icon': None, 'min_version': None
        }
        
        if not self.main_file.exists():
            return metadata
        
        with open(self.main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        patterns = {
            'id': r'^__id__\s*=\s*["\']([^"\']+)["\']',
            'name': r'^__name__\s*=\s*["\']([^"\']+)["\']',
            'description': r'^__description__\s*=\s*["\']([^"\']+)["\']',
            'author': r'^__author__\s*=\s*["\']([^"\']+)["\']',
            'version': r'^__version__\s*=\s*["\']([^"\']+)["\']',
            'icon': r'^__icon__\s*=\s*["\']([^"\']+)["\']',
            'min_version': r'^__min_version__\s*=\s*["\']([^"\']+)["\']'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                metadata[key] = match.group(1)
                if self.verbose and key == 'icon':
                    print(f"   📍 __icon__: {metadata[key]}")
        
        return metadata
    
    def _find_png_icon(self) -> Optional[Path]:
        """Ищет PNG/JPG/WEBP иконку в корне проекта"""
        possible_names = ['icon.png', 'icon.jpg', 'icon.jpeg', 'icon.webp']
        
        if self.verbose:
            print(f"   🔍 Поиск иконки в {self.project_dir}")
        
        for name in possible_names:
            icon_path = self.project_dir / name
            if icon_path.exists() and icon_path.is_file():
                if self.verbose:
                    print(f"   ✅ Найдена иконка: {icon_path.name}")
                return icon_path
        
        if self.verbose:
            print(f"   ❌ Иконка не найдена")
        return None
    
    def get(self, key: str, default=None):
        return self.metadata.get(key, default)
    
    def is_valid(self) -> bool:
        return self.metadata['id'] is not None and self.metadata['name'] is not None
    
    def has_png_icon(self) -> bool:
        return self.png_icon_path is not None
    
    def get_png_icon_path(self) -> Optional[Path]:
        return self.png_icon_path


def generate_plugin_caption(metadata: PluginMetadata, filename: str) -> str:
    """Генерирует caption для отправки"""
    name = metadata.get('name', '')
    version = metadata.get('version', '')
    author = metadata.get('author', '')
    description = metadata.get('description', '')
    plugin_id = metadata.get('id', '')
    
    lines = []
    lines.append(f"🎉 **{name}**")
    
    meta_parts = []
    if version:
        meta_parts.append(f"v{version}")
    if author:
        meta_parts.append(f"👤 {author}")
    if meta_parts:
        lines.append(" | ".join(meta_parts))
    
    if description:
        clean_desc = re.sub(r'\[.*?\]', '', description).strip()
        if clean_desc:
            lines.append(f"📝 {clean_desc[:120]}")
    
    if plugin_id:
        lines.append(f"`{plugin_id}.plugin`")
    
    lines.append("")
    lines.append("📎 Файл готов к установке")
    
    return "\n".join(lines)
