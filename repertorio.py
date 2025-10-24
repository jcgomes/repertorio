import flet as ft
import sqlite3
import os
from datetime import datetime
import tempfile
from xhtml2pdf import pisa
from io import BytesIO
import base64
import math
import re

# Estilos musicais pré-definidos
ESTILOS_MUSICAIS = [
    "Samba", "Salsa", "Bossa Nova", "MPB", "Rock", "Pop", "Jazz", "Blues",
    "Funk", "Forró", "Axé", "Pagode", "Sertanejo", "Rap", "Hip Hop", "Reggae",
    "Eletrônica", "Clássica", "Gospel", "Outro"
]

class MusicApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Gerenciador de Repertório Musical"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window.width = 1200
        self.page.window.height = 800
        self.setup_database()
        self.main_page()

    def setup_database(self):
        """Configura o banco de dados e cria as tabelas se não existirem"""
        self.conn = sqlite3.connect('repertorio.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        # Tabela de músicas
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS musicas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                musica TEXT NOT NULL,
                autor TEXT,
                estilo TEXT,
                tom TEXT,
                cifra TEXT
            )
        ''')
        
        # Tabela de shows
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS shows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_show TEXT NOT NULL,
                local_show TEXT NOT NULL,
                artista TEXT NOT NULL
            )
        ''')
        
        # Tabela de repertórios dos shows (relação many-to-many)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS repertorios_shows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_show INTEGER NOT NULL,
                id_musica INTEGER NOT NULL,
                sequencia INTEGER NOT NULL,
                FOREIGN KEY (id_show) REFERENCES shows (id),
                FOREIGN KEY (id_musica) REFERENCES musicas (id),
                UNIQUE(id_show, id_musica)
            )
        ''')
        
        self.conn.commit()

    def main_page(self):
        """Cria a página principal com abas para músicas, shows e sobre"""
        self.tab_musicas = ft.Tab(text="Músicas", content=self.musicas_ui())
        self.tab_shows = ft.Tab(text="Shows", content=self.shows_ui())
        self.tab_sobre = ft.Tab(text="Sobre", content=self.sobre_ui())
        
        tabs = ft.Tabs(
            tabs=[self.tab_musicas, self.tab_shows, self.tab_sobre],
            expand=True
        )
        
        self.page.clean()
        self.page.add(tabs)

    def musicas_ui(self):
        """Interface para gerenciamento de músicas"""
        self.musicas_data = self.carregar_musicas()
        
        self.musicas_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Música")),
                ft.DataColumn(ft.Text("Autor")),
                ft.DataColumn(ft.Text("Estilo")),
                ft.DataColumn(ft.Text("Tom")),
                ft.DataColumn(ft.Text("Ações"))
            ],
            rows=[],
            expand=True
        )
        
        self.atualizar_tabela_musicas()
        
        # Campo de pesquisa
        self.campo_pesquisa_musicas = ft.TextField(
            label="Pesquisar música...",
            width=300,
            on_change=self.filtrar_musicas
        )
        
        btn_nova_musica = ft.ElevatedButton(
            "Nova Música",
            icon=ft.icons.ADD,
            on_click=lambda e: self.abrir_dialog_musica()
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    self.campo_pesquisa_musicas,
                    btn_nova_musica
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(
                    content=ft.Column([
                        self.musicas_table
                    ], scroll=ft.ScrollMode.AUTO),
                    expand=True,
                    border=ft.border.all(1, ft.colors.GREY_300),
                    border_radius=5
                )
            ], expand=True),
            padding=20,
            expand=True
        )

    def shows_ui(self):
        """Interface para gerenciamento de shows"""
        self.shows_data = self.carregar_shows()
        
        self.shows_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Data")),
                ft.DataColumn(ft.Text("Local")),
                ft.DataColumn(ft.Text("Artista")),
                ft.DataColumn(ft.Text("Ações"))
            ],
            rows=[],
            expand=True
        )
        
        self.atualizar_tabela_shows()
        
        btn_novo_show = ft.ElevatedButton(
            "Novo Show",
            icon=ft.icons.ADD,
            on_click=lambda e: self.abrir_dialog_show()
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Row([btn_novo_show], alignment=ft.MainAxisAlignment.END),
                ft.Container(
                    content=ft.Column([
                        self.shows_table
                    ], scroll=ft.ScrollMode.AUTO),
                    expand=True,
                    border=ft.border.all(1, ft.colors.GREY_300),
                    border_radius=5
                )
            ], expand=True),
            padding=20,
            expand=True
        )

    def sobre_ui(self):
        """Interface com informações sobre o aplicativo"""
        return ft.Container(
            content=ft.Column([
                ft.Text("Sobre o App", size=30, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.ListTile(
                    title=ft.Text("Gerenciador de Repertório Musical"),
                    subtitle=ft.Text("Sistema para gerenciamento de músicas e shows"),
                ),
                ft.ListTile(
                    title=ft.Text("Desenvolvido por:"),
                    subtitle=ft.Text("Juliano Da Cunha Gomes.", weight=ft.FontWeight.BOLD),
                ),
                ft.ListTile(
                    title=ft.Text("Repositório:"),
                    subtitle=ft.Text("https://github.com/jcgomes/repertorio"),
                ),
                ft.ListTile(
                    title=ft.Text("Funcionalidades:"),
                    subtitle=ft.Text("• Cadastro de músicas\n• Gerenciamento de shows\n• Criação de repertórios\n• Exportação para PDF"),
                ),
                ft.ListTile(
                    title=ft.Text("Tecnologias:"),
                    subtitle=ft.Text("Python • Flet • SQLite"),
                ),
                ft.Container(height=20),
                ft.Text("© 2024 - Todos os direitos reservados", size=12, color=ft.colors.GREY),
            ], scroll=ft.ScrollMode.AUTO),
            padding=30,
            expand=True
        )

    def carregar_musicas(self):
        """Carrega as músicas do banco de dados ordenadas por ID"""
        self.cursor.execute("SELECT * FROM musicas ORDER BY id")
        return self.cursor.fetchall()

    def carregar_shows(self):
        """Carrega os shows do banco de dados"""
        self.cursor.execute("SELECT * FROM shows ORDER BY data_show DESC")
        return self.cursor.fetchall()

    def filtrar_musicas(self, e):
        """Filtra as músicas na tabela conforme o texto pesquisado"""
        termo = self.campo_pesquisa_musicas.value.lower()
        if termo:
            musicas_filtradas = [m for m in self.musicas_data if 
                               termo in m[1].lower() or 
                               (m[2] and termo in m[2].lower()) or
                               (m[3] and termo in m[3].lower())]
        else:
            musicas_filtradas = self.musicas_data
        
        self.atualizar_tabela_musicas(musicas_filtradas)

    def atualizar_tabela_musicas(self, musicas_data=None):
        """Atualiza a tabela de músicas com os dados do banco"""
        if musicas_data is None:
            musicas_data = self.musicas_data
            
        rows = []
        for musica in musicas_data:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(musica[0]))),
                        ft.DataCell(ft.Text(musica[1])),
                        ft.DataCell(ft.Text(musica[2] or "")),
                        ft.DataCell(ft.Text(musica[3] or "")),
                        ft.DataCell(ft.Text(musica[4] or "")),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.icons.EDIT,
                                    tooltip="Editar",
                                    on_click=lambda e, id=musica[0]: self.abrir_dialog_musica(id)
                                ),
                                ft.IconButton(
                                    icon=ft.icons.DELETE,
                                    tooltip="Excluir",
                                    on_click=lambda e, id=musica[0]: self.excluir_musica(id)
                                )
                            ])
                        )
                    ]
                )
            )
        self.musicas_table.rows = rows
        self.page.update()

    def atualizar_tabela_shows(self):
        """Atualiza la tabela de shows com os dados do banco"""
        rows = []
        for show in self.shows_data:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(show[0]))),
                        ft.DataCell(ft.Text(show[1])),
                        ft.DataCell(ft.Text(show[2])),
                        ft.DataCell(ft.Text(show[3])),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.icons.EDIT,
                                    tooltip="Editar",
                                    on_click=lambda e, id=show[0]: self.abrir_dialog_show(id)
                                ),
                                ft.IconButton(
                                    icon=ft.icons.DELETE,
                                    tooltip="Excluir",
                                    on_click=lambda e, id=show[0]: self.excluir_show(id)
                                ),
                                ft.IconButton(
                                    icon=ft.icons.VISIBILITY,
                                    tooltip="Ver Repertório",
                                    on_click=lambda e, id=show[0]: self.ver_repertorio(id)
                                ),
                                ft.IconButton(
                                    icon=ft.icons.PICTURE_AS_PDF,
                                    tooltip="Exportar PDF",
                                    on_click=lambda e, id=show[0]: self.exportar_pdf(id)
                                )
                            ])
                        )
                    ]
                )
            )
        self.shows_table.rows = rows
        self.page.update()

    def formatar_tom(self, tom):
        """Formata o tom para ficar entre parênteses se necessário"""
        if not tom:
            return tom
            
        tom = tom.strip()
        
        # Verifica se já está entre parênteses
        if tom.startswith('(') and tom.endswith(')'):
            return tom
            
        # Remove parênteses existentes para evitar duplicação
        tom = tom.replace('(', '').replace(')', '').strip()
        
        # Coloca entre parênteses
        return f"({tom})"

    def verificar_musica_existente(self, nome_musica, autor=None, id_excluir=None):
        """Verifica se uma música já existe no banco de dados"""
        if autor:
            if id_excluir:
                self.cursor.execute(
                    "SELECT id FROM musicas WHERE LOWER(musica)=LOWER(?) AND LOWER(autor)=LOWER(?) AND id != ?",
                    (nome_musica, autor, id_excluir)
                )
            else:
                self.cursor.execute(
                    "SELECT id FROM musicas WHERE LOWER(musica)=LOWER(?) AND LOWER(autor)=LOWER(?)",
                    (nome_musica, autor)
                )
        else:
            if id_excluir:
                self.cursor.execute(
                    "SELECT id FROM musicas WHERE LOWER(musica)=LOWER(?) AND id != ?",
                    (nome_musica, id_excluir)
                )
            else:
                self.cursor.execute(
                    "SELECT id FROM musicas WHERE LOWER(musica)=LOWER(?)",
                    (nome_musica,)
                )
        
        return self.cursor.fetchone() is not None

    def abrir_dialog_musica(self, id_musica=None):
        """Abre o diálogo para adicionar/editar uma música"""
        musica = None
        if id_musica:
            self.cursor.execute("SELECT * FROM musicas WHERE id=?", (id_musica,))
            musica = self.cursor.fetchone()
        
        # Campos do formulário
        campo_musica = ft.TextField(label="Música", value=musica[1] if musica else "")
        campo_autor = ft.TextField(label="Autor", value=musica[2] if musica else "")
        campo_estilo = ft.Dropdown(
            label="Estilo",
            options=[ft.dropdown.Option(estilo) for estilo in ESTILOS_MUSICAIS],
            value=musica[3] if musica else None
        )
        
        # Campo tom com formatação automática
        tom_value = musica[4] if musica else ""
        campo_tom = ft.TextField(
            label="Tom", 
            value=tom_value,
            on_change=lambda e: self.formatar_tom_em_tempo_real(campo_tom)
        )
        
        campo_cifra = ft.TextField(
            label="Cifra", 
            value=musica[5] if musica else "",
            multiline=True,
            min_lines=3,
            max_lines=5
        )
        
        # Label para mensagens de erro
        mensagem_erro = ft.Text("", color=ft.colors.RED, size=12)
        
        def salvar_musica(e):
            # Verificar se a música já existe
            nome_musica = campo_musica.value.strip()
            autor_musica = campo_autor.value.strip() if campo_autor.value else None
            
            if not nome_musica:
                mensagem_erro.value = "O nome da música é obrigatório!"
                self.page.update()
                return
                
            if self.verificar_musica_existente(nome_musica, autor_musica, id_musica):
                mensagem_erro.value = "Esta música já existe no repertório!"
                self.page.update()
                return
                
            # Formatar o tom
            tom_formatado = self.formatar_tom(campo_tom.value) if campo_tom.value else ""
            
            if id_musica:
                self.cursor.execute(
                    "UPDATE musicas SET musica=?, autor=?, estilo=?, tom=?, cifra=? WHERE id=?",
                    (nome_musica, autor_musica, campo_estilo.value, 
                     tom_formatado, campo_cifra.value, id_musica)
                )
            else:
                self.cursor.execute(
                    "INSERT INTO musicas (musica, autor, estilo, tom, cifra) VALUES (?, ?, ?, ?, ?)",
                    (nome_musica, autor_musica, campo_estilo.value, 
                     tom_formatado, campo_cifra.value)
                )
            self.conn.commit()
            self.musicas_data = self.carregar_musicas()
            self.atualizar_tabela_musicas()
            
            # Limpar campo de pesquisa após adicionar nova música
            self.campo_pesquisa_musicas.value = ""
            
            self.page.dialog.open = False
            self.page.update()
        
        def formatar_tom_em_tempo_real(e):
            """Formata o tom em tempo real enquanto o usuário digita"""
            if campo_tom.value:
                campo_tom.value = self.formatar_tom(campo_tom.value)
                self.page.update()
        
        def cancelar(e):
            self.page.dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Editar Música" if id_musica else "Nova Música"),
            content=ft.Column([
                campo_musica,
                campo_autor,
                campo_estilo,
                campo_tom,
                campo_cifra,
                mensagem_erro
            ], tight=True, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar),
                ft.TextButton("Salvar", on_click=salvar_musica)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def formatar_tom_em_tempo_real(self, campo_tom):
        """Formata o tom em tempo real enquanto o usuário digita"""
        if campo_tom.value:
            campo_tom.value = self.formatar_tom(campo_tom.value)
            self.page.update()

    def abrir_dialog_show(self, id_show=None):
        """Abre o diálogo para adicionar/editar um show"""
        show = None
        if id_show:
            self.cursor.execute("SELECT * FROM shows WHERE id=?", (id_show,))
            show = self.cursor.fetchone()
        
        # Campos do formulário
        campo_data = ft.TextField(
            label="Data (DD/MM/AAAA)", 
            value=show[1] if show else datetime.now().strftime("%d/%m/%Y")
        )
        campo_local = ft.TextField(label="Local", value=show[2] if show else "")
        campo_artista = ft.TextField(label="Artista/Banda", value=show[3] if show else "")
        
        def salvar_show(e):
            if id_show:
                self.cursor.execute(
                    "UPDATE shows SET data_show=?, local_show=?, artista=? WHERE id=?",
                    (campo_data.value, campo_local.value, campo_artista.value, id_show)
                )
            else:
                self.cursor.execute(
                    "INSERT INTO shows (data_show, local_show, artista) VALUES (?, ?, ?)",
                    (campo_data.value, campo_local.value, campo_artista.value)
                )
            self.conn.commit()
            self.shows_data = self.carregar_shows()
            self.atualizar_tabela_shows()
            self.page.dialog.open = False
            self.page.update()
        
        def cancelar(e):
            self.page.dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Editar Show" if id_show else "Novo Show"),
            content=ft.Column([
                campo_data,
                campo_local,
                campo_artista
            ], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar),
                ft.TextButton("Salvar", on_click=salvar_show)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def ver_repertorio(self, id_show):
        """Abre a tela para visualizar e editar o repertório de um show"""
        # Buscar dados do show
        self.cursor.execute("SELECT * FROM shows WHERE id=?", (id_show,))
        show = self.cursor.fetchone()
        
        # Buscar músicas do repertório
        self.cursor.execute('''
            SELECT m.id, m.musica, m.tom, m.cifra, rs.sequencia 
            FROM repertorios_shows rs 
            JOIN musicas m ON rs.id_musica = m.id 
            WHERE rs.id_show = ? 
            ORDER BY rs.sequencia
        ''', (id_show,))
        repertorio = self.cursor.fetchall()
        
        # Buscar todas as músicas disponíveis
        self.cursor.execute("SELECT id, musica, tom FROM musicas ORDER BY id")
        todas_musicas = self.cursor.fetchall()
        
        # Criar interface do repertório
        titulo = ft.Text(f"Repertório: {show[3]} - {show[2]} - {show[1]}", size=20)
        
        # Lista de músicas no repertório
        lista_musicas = ft.Column([], scroll=ft.ScrollMode.AUTO, expand=True)
        
        # Campo de pesquisa
        campo_pesquisa = ft.TextField(
            label="Pesquisar música...",
            width=300
        )
        
        # Lista de músicas disponíveis (inicialmente com todas)
        musicas_filtradas = todas_musicas
        lista_musicas_disponiveis = ft.ListView(
            [],
            expand=True,
            height=200
        )
        
        def filtrar_musicas(e):
            nonlocal musicas_filtradas
            termo = campo_pesquisa.value.lower()
            if termo:
                musicas_filtradas = [m for m in todas_musicas if termo in m[1].lower()]
            else:
                musicas_filtradas = todas_musicas
            atualizar_lista_musicas()
        
        def atualizar_lista_musicas():
            lista_musicas_disponiveis.controls.clear()
            for musica in musicas_filtradas:
                lista_musicas_disponiveis.controls.append(
                    ft.ListTile(
                        title=ft.Text(musica[1]),
                        subtitle=ft.Text(f"Tom: {musica[2]}"),
                        on_click=lambda e, id=musica[0]: selecionar_musica(id),
                    )
                )
            self.page.update()
        
        def selecionar_musica(id_musica):
            # Verificar se a música já está no repertório
            self.cursor.execute(
                "SELECT rs.sequencia, m.musica FROM repertorios_shows rs JOIN musicas m ON rs.id_musica = m.id WHERE rs.id_show = ? AND rs.id_musica = ?",
                (id_show, id_musica)
            )
            musica_existente = self.cursor.fetchone()
            
            if musica_existente:
                # Música já está no repertório
                self.page.snack_bar = ft.SnackBar(
                    ft.Text(f"Esta música já está no repertório na posição {musica_existente[0]}: {musica_existente[1]}")
                )
                self.page.snack_bar.open = True
                self.page.update()
                return
                
            # Encontrar a próxima sequência
            self.cursor.execute("SELECT MAX(sequencia) FROM repertorios_shows WHERE id_show=?", (id_show,))
            max_seq = self.cursor.fetchone()[0] or 0
            nova_seq = max_seq + 1
            
            try:
                # Adicionar ao banco
                self.cursor.execute(
                    "INSERT INTO repertorios_shows (id_show, id_musica, sequencia) VALUES (?, ?, ?)",
                    (id_show, id_musica, nova_seq)
                )
                self.conn.commit()
                carregar_repertorio()
                
                # Limpar campo de pesquisa
                campo_pesquisa.value = ""
                musicas_filtradas = todas_musicas
                atualizar_lista_musicas()
                self.page.update()
                
            except sqlite3.IntegrityError:
                # Caso a música já exista (dupla verificação)
                self.page.snack_bar = ft.SnackBar(
                    ft.Text("Esta música já está no repertório")
                )
                self.page.snack_bar.open = True
                self.page.update()
        
        def carregar_repertorio():
            self.cursor.execute('''
                SELECT m.id, m.musica, m.tom, m.cifra, rs.sequencia, rs.id
                FROM repertorios_shows rs 
                JOIN musicas m ON rs.id_musica = m.id 
                WHERE rs.id_show = ? 
                ORDER BY rs.sequencia
            ''', (id_show,))
            repertorio = self.cursor.fetchall()
            
            lista_musicas.controls.clear()
            for i, musica in enumerate(repertorio):
                lista_musicas.controls.append(
                    ft.ListTile(
                        title=ft.Text(f"{i+1}. {musica[1]}"),
                        subtitle=ft.Text(f"Tom: {musica[2]}"),
                        trailing=ft.Row([
                            ft.IconButton(
                                icon=ft.icons.ARROW_UPWARD,
                                on_click=lambda e, id=musica[5]: mover_musica(id, -1)
                            ),
                            ft.IconButton(
                                icon=ft.icons.ARROW_DOWNWARD,
                                on_click=lambda e, id=musica[5]: mover_musica(id, 1)
                            ),
                            ft.IconButton(
                                icon=ft.icons.DELETE,
                                on_click=lambda e, id=musica[5]: remover_musica(id)
                            )
                        ], width=150)
                    )
                )
            self.page.update()
        
        def mover_musica(id_item, direcao):
            # Buscar item atual
            self.cursor.execute("SELECT sequencia, id_show FROM repertorios_shows WHERE id=?", (id_item,))
            item = self.cursor.fetchone()
            seq_atual = item[0]
            
            # Buscar item a ser trocado
            nova_seq = seq_atual + direcao
            if nova_seq < 1:
                return
                
            self.cursor.execute(
                "SELECT id FROM repertorios_shows WHERE id_show=? AND sequencia=?",
                (id_show, nova_seq)
            )
            item_troca = self.cursor.fetchone()
            
            if item_troca:
                # Trocar as sequências
                self.cursor.execute(
                    "UPDATE repertorios_shows SET sequencia=? WHERE id=?",
                    (nova_seq, id_item)
                )
                self.cursor.execute(
                    "UPDATE repertorios_shows SET sequencia=? WHERE id=?",
                    (seq_atual, item_troca[0])
                )
            else:
                # Apenas atualizar a sequência
                self.cursor.execute(
                    "UPDATE repertorios_shows SET sequencia=? WHERE id=?",
                    (nova_seq, id_item)
                )
            
            self.conn.commit()
            carregar_repertorio()
        
        def remover_musica(id_item):
            self.cursor.execute("DELETE FROM repertorios_shows WHERE id=?", (id_item,))
            self.conn.commit()
            carregar_repertorio()
        
        def voltar(e):
            self.main_page()
        
        # Configurar o evento de change do campo de pesquisa
        campo_pesquisa.on_change = filtrar_musicas
        
        # Inicializar listas
        carregar_repertorio()
        atualizar_lista_musicas()
        
        # Layout da página de repertório
        content = ft.Column([
            ft.Row([ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=voltar), titulo]),
            ft.Row([
                campo_pesquisa,
            ]),
            ft.Text("Músicas disponíveis:", weight=ft.FontWeight.BOLD),
            ft.Container(
                content=lista_musicas_disponiveis,
                border=ft.border.all(1),
                border_radius=5,
                height=200
            ),
            ft.Text("Repertório do show:", weight=ft.FontWeight.BOLD),
            ft.Container(
                content=lista_musicas,
                border=ft.border.all(1),
                border_radius=5,
                padding=10,
                expand=True
            ),
            ft.Row([
                ft.ElevatedButton("Exportar PDF", on_click=lambda e: self.exportar_pdf(id_show)),
                ft.ElevatedButton("Voltar", on_click=voltar)
            ])
        ], expand=True)
        
        self.page.clean()
        self.page.add(content)

    def processar_cifra_para_pdf(self, cifra):
        """Processa a cifra para destacar texto entre colchetes em azul sem fundo amarelo"""
        if not cifra:
            return cifra
            
        # Regex para encontrar texto entre colchetes
        padrao = r'(\[[^\]]+\])'
        
        # Substituir cada ocorrência com formatação HTML
        def substituir_colchetes(match):
            texto_entre_colchetes = match.group(1)
            return f'<span class="colchetes">{texto_entre_colchetes}</span>'
        
        cifra_processada = re.sub(padrao, substituir_colchetes, cifra)
        return cifra_processada

    def exportar_pdf(self, id_show):
        """Exporta o repertório para PDF usando xhtml2pdf"""
        # Buscar músicas do repertório
        self.cursor.execute('''
            SELECT m.id, m.musica, m.tom, m.cifra, rs.sequencia 
            FROM repertorios_shows rs 
            JOIN musicas m ON rs.id_musica = m.id 
            WHERE rs.id_show = ? 
            ORDER BY rs.sequencia
        ''', (id_show,))
        repertorio = self.cursor.fetchall()
        
        if not repertorio:
            self.page.snack_bar = ft.SnackBar(ft.Text("Nenhuma música no repertório para exportar!"))
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        # Calcular o comprimento máximo do texto
        textos = []
        for musica in repertorio:
            texto = f"➔ {musica[1]} {musica[2]} {musica[3] or ''}"
            textos.append(texto)
        
        max_caracteres = max(len(texto) for texto in textos)
        
        # Ajustar tamanho da fonte - aumentar para ocupar mais espaço
        tamanho_fonte = min(40, 32 + (max_caracteres // 3))
        
        # Criar conteúdo HTML para o PDF
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @page {{
                    size: A4 landscape;
                    margin: 0;
                }}
                body {{
                    font-family: Arial, sans-serif;
                    font-size: {tamanho_fonte}px;
                    font-weight: bold;
                    background-color: #F0F0F0;
                    margin: 0;
                    padding: 1cm;
                    line-height: 1.2;
                    width: 100%;
                    height: 100%;
                }}
                .page-container {{
                    background-color: #F0F0F0;
                    width: 100%;
                    height: 100%;
                    padding: 0.5cm;
                }}
                .musica {{
                    margin-bottom: 0.3cm;
                    line-height: 1.2;
                }}
                .seta {{
                    color: red;
                    font-weight: bold;
                }}
                .nome {{
                    color: black;
                    font-weight: bold;
                }}
                .tom {{
                    color: #8B4513;
                    font-weight: bold;
                }}
                .cifra {{
                    color: black;
                    background-color: yellow;
                    font-weight: bold;
                    padding: 0.05cm 0.1cm;
                }}
                .colchetes {{
                    color: blue;
                    background-color: #F0F0F0;
                    font-weight: normal;
                }}
            </style>
        </head>
        <body>
            <div class="page-container">
        """
        
        for musica in repertorio:
            # Processar a cifra para destacar texto entre colchetes
            cifra_processada = self.processar_cifra_para_pdf(musica[3] or "")
            
            html_content += f"""
                <div class="musica">
                    <span class="seta">➔</span>
                    <span class="nome">{musica[1]}</span>
                    <span class="tom">{musica[2]}</span>
                    <span class="cifra">{cifra_processada}</span>
                </div>
            """
        
        html_content += """
            </div>
        </body>
        </html>
        """
        
        # Gerar PDF
        pdf_buffer = BytesIO()
        pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)
        
        if pisa_status.err:
            self.page.snack_bar = ft.SnackBar(ft.Text("Erro ao gerar PDF"))
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        # Salvar PDF temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_buffer.getvalue())
            tmp_file_path = tmp_file.name
        
        # Abrir o PDF
        os.system(f'open "{tmp_file_path}"' if os.name == 'posix' else f'start "{tmp_file_path}"')
        
        # Mostrar mensagem de sucesso
        self.page.snack_bar = ft.SnackBar(ft.Text("PDF exportado com sucesso!"))
        self.page.snack_bar.open = True
        self.page.update()

    def excluir_musica(self, id_musica):
        """Exclui uma música do banco de dados"""
        def confirmar_exclusao(e):
            self.cursor.execute("DELETE FROM musicas WHERE id=?", (id_musica,))
            self.conn.commit()
            self.musicas_data = self.carregar_musicas()
            self.atualizar_tabela_musicas()
            self.page.dialog.open = False
            self.page.update()
        
        def cancelar(e):
            self.page.dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Confirmar Exclusão"),
            content=ft.Text("Tem certeza que deseja excluir esta música?"),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar),
                ft.TextButton("Excluir", on_click=confirmar_exclusao)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def excluir_show(self, id_show):
        """Exclui um show do banco de dados"""
        def confirmar_exclusao(e):
            # Primeiro excluir as relações no repertório
            self.cursor.execute("DELETE FROM repertorios_shows WHERE id_show=?", (id_show,))
            # Depois excluir o show
            self.cursor.execute("DELETE FROM shows WHERE id=?", (id_show,))
            self.conn.commit()
            self.shows_data = self.carregar_shows()
            self.atualizar_tabela_shows()
            self.page.dialog.open = False
            self.page.update()
        
        def cancelar(e):
            self.page.dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Confirmar Exclusão"),
            content=ft.Text("Tem certeza que deseja excluir este show? Todas as músicas do repertório também serão excluídas."),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar),
                ft.TextButton("Excluir", on_click=confirmar_exclusao)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

def main(page: ft.Page):
    app = MusicApp(page)

if __name__ == "__main__":
    ft.app(target=main)