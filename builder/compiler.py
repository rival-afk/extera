"""Основная логика компиляции с встраиванием библиотек из venv"""

import sys
from pathlib import Path
from typing import List, Optional, Tuple, Set
import re
from .cleaner import clean_code
from .deps import find_py_files, build_dependency_graph, resolve_dependencies
from .metadata import PluginMetadata
from .importer import LibraryEmbedder


def get_venv_site_packages() -> Path:
    """Возвращает путь к site-packages текущего venv"""
    # Проверяем, что мы в venv
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        # Мы в venv
        for path in sys.path:
            if 'site-packages' in path:
                return Path(path)
    
    # Пробуем найти относительно текущего скрипта
    builder_dir = Path(__file__).parent.parent
    venv_path = builder_dir / '.venv'
    if venv_path.exists():
        lib_dir = venv_path / 'lib'
        if lib_dir.exists():
            for python_dir in lib_dir.iterdir():
                if python_dir.name.startswith('python'):
                    site_packages = python_dir / 'site-packages'
                    if site_packages.exists():
                        return site_packages
    
    raise RuntimeError("Не удалось найти site-packages. Убедитесь, что вы в venv")


def compile_plugin(
    project_dir: Path, 
    output_path: Path = None,
    verbose: bool = False
) -> Tuple[Path, Optional[PluginMetadata]]:
    """Компилирует проект с встраиванием библиотек из venv"""
    
    project_path = Path(project_dir).resolve()
    
    if not project_path.is_dir():
        raise NotADirectoryError(f"{project_path} не является папкой")
    
    main_file = project_path / 'main.py'
    if not main_file.exists():
        raise FileNotFoundError(f"В папке {project_path} отсутствует main.py")
    
    metadata = PluginMetadata(main_file, project_path, verbose)
    
    if verbose:
        print(f"📋 Метаданные:")
        print(f"   ID: {metadata.get('id')}")
        print(f"   Имя: {metadata.get('name')}")
        print(f"   Версия: {metadata.get('version', 'не указана')}")
        print(f"   Автор: {metadata.get('author', 'не указан')}")
        if metadata.has_png_icon():
            print(f"   🖼️  Иконка: {metadata.get_png_icon_path().name}")
    
    all_py = find_py_files(project_path)
    if not all_py:
        raise ValueError("Нет .py файлов в папке")
    
    # Находим все импорты
    all_imports = _find_all_imports(all_py)
    
    # Фильтруем внешние библиотеки
    external_libs = _filter_external_imports(all_imports)
    
    if verbose and external_libs:
        print(f"📦 Внешние библиотеки: {list(external_libs)}")
    
    # Получаем путь к site-packages
    site_packages = get_venv_site_packages()
    if verbose:
        print(f"📁 Site-packages: {site_packages}")
    
    # Встраиваем библиотеки
    embedded_code = ""
    for lib in external_libs:
        lib_code = LibraryEmbedder.embed_library(lib, site_packages)
        if lib_code:
            embedded_code += lib_code
            if verbose:
                print(f"   📚 Встроена: {lib}")
        else:
            if verbose:
                print(f"   ⚠️ Не встроена: {lib}")
    
    # Строим граф зависимостей проекта
    graph = build_dependency_graph(main_file, all_py)
    dependencies = resolve_dependencies(main_file, graph)
    
    if output_path is None:
        output_filename = project_path.name + '.plugin'
        output_path = project_path / output_filename
    
    # Генерируем содержимое
    content = _generate_plugin_content(
        main_file, dependencies, 
        all_imports, embedded_code,
        verbose
    )
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    file_size = output_path.stat().st_size
    if verbose:
        print(f"✅ Собран плагин: {output_path}")
        print(f"   Размер: {file_size:,} байт")
    
    return output_path, metadata


def _find_all_imports(py_files: List[Path]) -> Set[str]:
    """Находит все импорты во всех файлах проекта"""
    imports = set()
    
    patterns = [
        r'^import\s+(\w+)',
        r'^from\s+(\w+(?:\.\w+)*)\s+import',
    ]
    
    for py_file in py_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for pattern in patterns:
                matches = re.findall(pattern, content, re.MULTILINE)
                for match in matches:
                    imports.add(match)
        except:
            pass
    
    return imports


def _filter_external_imports(imports: Set[str]) -> Set[str]:
    """Оставляет только импорты внешних библиотек"""
    internal_modules = {
        'base_plugin', 'client_utils', 'android_utils',
        'ui', 'file_utils', 'hook_utils', 'markdown_utils',
        'typing', 'hashlib', 'json', 'base64', 'os', 'time',
        'secrets', 'struct', 'hmac', 're', 'sqlite3', 'threading',
        'collections', 'itertools', 'functools', 'datetime',
        'random', 'math', 'copy', 'pprint', 'logging',
    }
    
    external = set()
    for imp in imports:
        base = imp.split('.')[0]
        if base not in internal_modules and not base.startswith('_'):
            external.add(imp)
    
    return external


def _generate_plugin_content(
    main_file: Path,
    dependencies: List[Path],
    all_imports: Set[str],
    embedded_code: str,
    verbose: bool
) -> str:
    """Генерирует содержимое .plugin файла"""
    
    local_modules = {f.stem for f in dependencies} | {main_file.stem}
    result_parts = []
    
    # Вставляем код встроенных библиотек
    if embedded_code:
        result_parts.append("# === Embedded Libraries ===\n")
        result_parts.append(embedded_code)
        result_parts.append("# === End Embedded Libraries ===\n")
    
    # Вставляем зависимости проекта
    for dep_file in dependencies:
        with open(dep_file, 'r', encoding='utf-8') as f:
            original = f.read()
        cleaned = _remove_local_imports(original, local_modules, all_imports)
        result_parts.append(f"# --- file: {dep_file.name} ---\n{cleaned}\n")
    
    # Вставляем main.py
    with open(main_file, 'r', encoding='utf-8') as f:
        main_original = f.read()
    main_cleaned = _remove_local_imports(main_original, local_modules, all_imports)
    result_parts.append(main_cleaned)
    
    return '\n'.join(result_parts)


def _remove_local_imports(content: str, local_modules: Set[str], all_imports: Set[str]) -> str:
    """Удаляет импорты локальных модулей и внешних библиотек (они уже встроены)"""
    lines = content.split('\n')
    filtered = []
    
    for line in lines:
        stripped = line.strip()
        
        # Проверяем локальные импорты
        is_local = False
        for mod in local_modules:
            if f'import {mod}' in stripped or f'from {mod}' in stripped:
                is_local = True
                break
            if f'from .{mod}' in stripped:
                is_local = True
                break
        
        if is_local:
            filtered.append(f"# {line}  # local import removed")
            continue
        
        # Проверяем импорты внешних библиотек (они встроены выше)
        for imp in all_imports:
            base = imp.split('.')[0]
            if f'import {base}' in stripped or f'from {base}' in stripped:
                filtered.append(f"# {line}  # embedded library")
                break
        else:
            filtered.append(line)
    
    return '\n'.join(filtered)
