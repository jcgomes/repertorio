import re
import platform
import os

def formatar_tom(tom):
    """Formata o tom para ficar entre parênteses se necessário"""
    if not tom:
        return tom
        
    tom = tom.strip()
    
    if tom.startswith('(') and tom.endswith(')'):
        return tom
        
    tom = tom.replace('(', '').replace(')', '').strip()
    return f"({tom})"

def abrir_arquivo_multiplataforma(file_path):
    """Abre arquivos de forma multiplataforma"""
    system = platform.system().lower()
    
    try:
        if system == "windows":
            os.startfile(file_path)
        elif system == "darwin":
            os.system(f'open "{file_path}"')
        else:
            os.system(f'xdg-open "{file_path}"')
    except Exception as e:
        print(f"Erro ao abrir arquivo: {e}")
        try:
            import subprocess
            subprocess.run(['open' if system == 'darwin' else 'xdg-open' if system != 'windows' else 'start', file_path], 
                         shell=True, check=False)
        except:
            pass

def verificar_musica_existente(cursor, nome_musica, autor=None, id_excluir=None):
    """Verifica se uma música já existe no banco de dados"""
    if autor:
        if id_excluir:
            cursor.execute(
                "SELECT id FROM musicas WHERE LOWER(musica)=LOWER(?) AND LOWER(autor)=LOWER(?) AND id != ?",
                (nome_musica, autor, id_excluir)
            )
        else:
            cursor.execute(
                "SELECT id FROM musicas WHERE LOWER(musica)=LOWER(?) AND LOWER(autor)=LOWER(?)",
                (nome_musica, autor)
            )
    else:
        if id_excluir:
            cursor.execute(
                "SELECT id FROM musicas WHERE LOWER(musica)=LOWER(?) AND id != ?",
                (nome_musica, id_excluir)
            )
        else:
            cursor.execute(
                "SELECT id FROM musicas WHERE LOWER(musica)=LOWER(?)",
                (nome_musica,)
            )
    
    return cursor.fetchone() is not None