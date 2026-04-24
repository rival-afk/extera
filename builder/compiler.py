"""Основная логика компиляции с встраиванием библиотек"""

from pathlib import Path
from typing import List, Optional, Tuple, Set
import re
from .cleaner import clean_code
from .deps import find_py_files, build_dependency_graph, resolve_dependencies
from .metadata import PluginMetadata
from .importer import LibraryEmbedder


def compile_plugin(
    project_dir: Path, 
    output_path: Path = None,
    verbose: bool = False
) -> Tuple[Path, Optional[PluginMetadata]]:
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
    
    # Анализируем импорты
    external_libs = _find_external_imports(all_py)
    
    if verbose and external_libs:
        print(f"📦 Внешние библиотеки: {list(external_libs)}")
    
    graph = build_dependency_graph(main_file, all_py)
    dependencies = resolve_dependencies(main_file, graph)
    
    if output_path is None:
        output_filename = project_path.name + '.plugin'
        output_path = project_path / output_filename
    
    content = _generate_plugin_content(main_file, dependencies, external_libs, verbose)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    file_size = output_path.stat().st_size
    if verbose:
        print(f"✅ Собран плагин: {output_path}")
        print(f"   Размер: {file_size:,} байт")
    
    return output_path, metadata


def _find_external_imports(py_files: List[Path]) -> Set[str]:
    imports = set()
    patterns = [
        r'^import\s+(\w+)',
        r'^from\s+(\w+)\s+import',
        r'^from\s+(\w+\.\w+)\s+import',
    ]
    
    for py_file in py_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for pattern in patterns:
                matches = re.findall(pattern, content, re.MULTILINE)
                for match in matches:
                    module = match.split('.')[0]
                    if module not in ['base_plugin', 'client_utils', 'android_utils', 
                                     'ui', 'file_utils', 'hook_utils', 'markdown_utils',
                                     'typing', 'hashlib', 'json', 'base64', 'os', 'time',
                                     'secrets', 'struct', 'hmac']:
                        imports.add(module)
        except:
            pass
    
    return imports


def _generate_plugin_content(
    main_file: Path, 
    dependencies: List[Path], 
    external_libs: Set[str],
    verbose: bool
) -> str:
    all_modules = {f.stem for f in dependencies} | {main_file.stem}
    result_parts = []
    
    # Встраиваем библиотеки
    embedded_libs = set()
    for lib in external_libs:
        lib_code = LibraryEmbedder.get_library_code(lib)
        if lib_code and lib not in embedded_libs:
            result_parts.append(f"# --- Embedded: {lib} ---\n{lib_code}\n")
            embedded_libs.add(lib)
            if verbose:
                print(f"   📚 Встроена: {lib}")
    
    # Встраиваем зависимости
    for dep_file in dependencies:
        with open(dep_file, 'r', encoding='utf-8') as f:
            original = f.read()
        cleaned = _clean_imports(original, all_modules, embedded_libs)
        result_parts.append(f"# --- file: {dep_file.name} ---\n{cleaned}\n")
    
    # Встраиваем main.py
    with open(main_file, 'r', encoding='utf-8') as f:
        main_original = f.read()
    main_cleaned = _clean_imports(main_original, all_modules, embedded_libs)
    result_parts.append(main_cleaned)
    
    return '\n'.join(result_parts)


def _clean_imports(content: str, local_modules: Set[str], embedded_libs: Set[str]) -> str:
    lines = content.split('\n')
    filtered = []
    
    for line in lines:
        stripped = line.strip()
        
        # Пропускаем локальные импорты
        is_local = False
        for mod in local_modules:
            if f'import {mod}' in stripped or f'from {mod}' in stripped:
                is_local = True
                break
            if f'from .{mod}' in stripped:
                is_local = True
                break
        
        if is_local:
            continue
        
        # Преобразуем импорты встроенных библиотек
        for lib in embedded_libs:
            lib_name = lib.split('.')[-1]
            if f'import {lib_name}' in stripped or f'from {lib}' in stripped:
                filtered.append(f'# {line}  # already embedded')
                break
        else:
            filtered.append(line)
    
    return '\n'.join(filtered)
