"""Импортёр внешних библиотек - встраивает реальный код из venv в плагин"""

import os
import re
from pathlib import Path
from typing import Dict, Optional, Set, List


class LibraryEmbedder:
    """Встраивает код библиотек из venv в финальный плагин"""
    
    _cache: Dict[str, str] = {}
    
    @classmethod
    def get_library_code(cls, import_name: str, venv_site_packages: Path) -> Optional[str]:
        """
        Возвращает полный код библиотеки из site-packages
        import_name: например "Crypto.Cipher.AES" или "Crypto"
        """
        if import_name in cls._cache:
            return cls._cache[import_name]
        
        # Разбираем импорт
        parts = import_name.split('.')
        module_path = os.path.join(venv_site_packages, *parts[:-1]) if len(parts) > 1 else venv_site_packages
        module_file = f"{parts[-1]}.py"
        
        # Ищем файл
        possible_paths = [
            os.path.join(module_path, module_file),
            os.path.join(venv_site_packages, *parts, '__init__.py'),
            os.path.join(venv_site_packages, import_name.replace('.', os.sep) + '.py'),
            os.path.join(venv_site_packages, import_name.replace('.', os.sep), '__init__.py'),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    code = f.read()
                cls._cache[import_name] = code
                return code
        
        # Если не нашли, пробуем найти через importlib
        try:
            import importlib.util
            spec = importlib.util.find_spec(import_name)
            if spec and spec.origin:
                with open(spec.origin, 'r', encoding='utf-8') as f:
                    code = f.read()
                cls._cache[import_name] = code
                return code
        except:
            pass
        
        return None
    
    @classmethod
    def get_module_dependencies(cls, import_name: str, venv_site_packages: Path) -> Set[str]:
        """Находит все внутренние импорты модуля"""
        code = cls.get_library_code(import_name, venv_site_packages)
        if not code:
            return set()
        
        # Ищем относительные импорты внутри библиотеки
        deps = set()
        patterns = [
            r'^from\s+\.(\w+)\s+import',
            r'^from\s+(\w+)\s+import',
            r'^import\s+(\w+)',
        ]
        
        base_module = import_name.split('.')[0]
        for pattern in patterns:
            matches = re.findall(pattern, code, re.MULTILINE)
            for match in matches:
                if match != '__future__':
                    full_import = f"{base_module}.{match}" if '.' not in match else match
                    deps.add(full_import)
        
        return deps
    
    @classmethod
    def embed_library(cls, import_name: str, venv_site_packages: Path, visited: Set = None) -> str:
        """Рекурсивно встраивает библиотеку и все её зависимости"""
        if visited is None:
            visited = set()
        
        if import_name in visited:
            return ""
        
        visited.add(import_name)
        
        code_parts = []
        
        # Получаем код библиотеки
        lib_code = cls.get_library_code(import_name, venv_site_packages)
        if not lib_code:
            return ""
        
        # Находим зависимости
        deps = cls.get_module_dependencies(import_name, venv_site_packages)
        
        # Рекурсивно встраиваем зависимости
        for dep in deps:
            dep_code = cls.embed_library(dep, venv_site_packages, visited)
            if dep_code:
                code_parts.append(dep_code)
        
        # Добавляем текущую библиотеку
        code_parts.append(f"# --- Library: {import_name} ---\n{lib_code}\n")
        
        return "\n".join(code_parts)
