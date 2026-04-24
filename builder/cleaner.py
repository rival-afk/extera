"""Очистка кода от синтаксических ошибок и артефактов"""

import re
from typing import Set


def clean_code(content: str, available_modules: Set[str]) -> str:
    """
    Очищает код:
    - Удаляет BOM
    - Исправляет распространённые синтаксические ошибки
    - Удаляет пустые строки в начале/конце
    """
    if not content:
        return ""
    
    # Удаляем BOM если есть
    if content.startswith('\ufeff'):
        content = content[1:]
    
    lines = content.split('\n')
    cleaned = []
    
    for line in lines:
        # Удаляем невидимые символы в начале
        stripped = line.lstrip()
        
        # Исправляем ошибочные строки со списками имён
        if is_bad_standalone_list(stripped):
            cleaned.append(f'# [auto-fixed] {line}')
            continue
        
        # Пропускаем строки с только пробелами? Нет, оставляем для структуры
        cleaned.append(line)
    
    # Удаляем пустые строки в начале и конце
    while cleaned and not cleaned[0].strip():
        cleaned.pop(0)
    while cleaned and not cleaned[-1].strip():
        cleaned.pop()
    
    return '\n'.join(cleaned)


def is_bad_standalone_list(line: str) -> bool:
    """
    Проверяет, является ли строка ошибочным списком имён без присваивания.
    Например: get_synced_user, add_synced_user, add_pending_link,
    """
    stripped = line.strip()
    if not stripped or stripped.startswith('#'):
        return False
    
    # Если есть операторы или ключевые слова — пропускаем
    safe_keywords = ('=', '(', ')', ':', 'def', 'class', 'import', 'from',
                     'return', 'if', 'for', 'while', 'try', 'except', 'with',
                     'lambda', '[', ']', '{', '}', '@', 'async', 'await')
    
    if any(kw in stripped for kw in safe_keywords):
        return False
    
    # Если есть запятая и строка состоит только из имён переменных
    if ',' in stripped and re.match(r'^[\w\s,]+$', stripped):
        return True
    
    return False


def remove_local_imports(content: str, local_modules: Set[str]) -> str:
    """Удаляет строки импорта локальных модулей"""
    lines = content.split('\n')
    filtered = []
    
    for line in lines:
        stripped = line.strip()
        is_local = False
        
        for mod in local_modules:
            if f'import {mod}' in stripped or f'from {mod}' in stripped:
                is_local = True
                break
            if f'from .{mod}' in stripped:
                is_local = True
                break
        
        if not is_local:
            filtered.append(line)
    
    return '\n'.join(filtered)
