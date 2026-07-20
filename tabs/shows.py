import flet as ft
import sqlite3
from datetime import datetime
import math
import re
import os
from io import BytesIO
from xhtml2pdf import pisa
from utils.helpers import abrir_arquivo_multiplataforma

class ShowsTab:
    def __init__(self, app, page, db):
        self.app = app
        self.page = page
        self.db = db
        self.cursor = db.cursor
        self.conn = db.conn
        
        self.shows_data = []
        self.shows_table = None
        self.campo_pesquisa = None

    def build(self):
        """Constrói a interface da aba de shows"""
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
        )
        
        self.atualizar_tabela()
        
        self.campo_pesquisa = ft.TextField(
            label="Pesquisar shows (data, local ou artista)...",
            width=300,
            on_change=self.filtrar_shows,
            autofocus=True
        )
        
        btn_novo_show = ft.ElevatedButton(
            "Novo Show",
            icon=ft.icons.ADD,
            on_click=lambda e: self.abrir_dialog_show()
        )
        
        table_container = ft.Container(
            content=ft.ListView(
                controls=[self.shows_table],
                expand=True,
                auto_scroll=False
            ),
            expand=True,
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=5
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    self.campo_pesquisa,
                    btn_novo_show
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                table_container
            ], expand=True),
            padding=20,
            expand=True
        )

    def on_enter(self):
        """Quando a aba recebe foco"""
        if self.campo_pesquisa:
            self.campo_pesquisa.focus()

    def carregar_shows(self):
        """Carrega os shows do banco de dados ordenados por data decrescente"""
        # SQLite não tem tipo DATE, então usamos substr para converter DD/MM/AAAA para AAAA-MM-DD
        # substr(data_show, 7, 4) pega o ano, substr(data_show, 4, 2) pega o mês, substr(data_show, 1, 2) pega o dia
        self.cursor.execute("""
            SELECT * FROM shows 
            ORDER BY 
                substr(data_show, 7, 4) DESC,  -- Ano (posições 7-10)
                substr(data_show, 4, 2) DESC,  -- Mês (posições 4-5)
                substr(data_show, 1, 2) DESC   -- Dia (posições 1-2)
        """)
        return self.cursor.fetchall()

    def atualizar_tabela(self, shows_data=None):
        """Atualiza a tabela de shows"""
        if shows_data is None:
            shows_data = self.shows_data
            
        rows = []
        for show in shows_data:
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
                                ft.PopupMenuButton(
                                    icon=ft.icons.PICTURE_AS_PDF,
                                    tooltip="Exportar PDF",
                                    items=[
                                        ft.PopupMenuItem(
                                            text="Repertório Cifrado",
                                            on_click=lambda e, id=show[0]: self.exportar_pdf(id, tipo="cifrado")
                                        ),
                                        ft.PopupMenuItem(
                                            text="Repertório Simplificado", 
                                            on_click=lambda e, id=show[0]: self.exportar_pdf(id, tipo="simplificado")
                                        )
                                    ]
                                )
                            ])
                        )
                    ]
                )
            )
        self.shows_table.rows = rows
        self.page.update()

    def filtrar_shows(self, e):
        """Filtra os shows na tabela"""
        termo = self.campo_pesquisa.value.lower()
        if termo:
            shows_filtrados = [s for s in self.shows_data if 
                             termo in s[1].lower() or
                             termo in s[2].lower() or
                             termo in s[3].lower()]
        else:
            shows_filtrados = self.shows_data
        
        self.atualizar_tabela(shows_filtrados)

    def abrir_dialog_show(self, id_show=None):
        """Abre o diálogo para adicionar/editar um show"""
        show = None
        if id_show:
            self.cursor.execute("SELECT * FROM shows WHERE id=?", (id_show,))
            show = self.cursor.fetchone()
        
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
            self.atualizar_tabela()
            
            if hasattr(self.app, 'tabs') and 'configuracoes' in self.app.tabs:
                self.app.tabs['configuracoes'].atualizar_cards()
            
            self.page.dialog.open = False
            self.page.update()
        
        def cancelar(e):
            self.page.dialog.open = False
            self.page.update()
            self.campo_pesquisa.focus()
        
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
        self.cursor.execute("SELECT * FROM shows WHERE id=?", (id_show,))
        show = self.cursor.fetchone()
        
        self.cursor.execute('''
            SELECT m.id, m.musica, m.tom, m.cifra, rs.sequencia 
            FROM repertorios_shows rs 
            JOIN musicas m ON rs.id_musica = m.id 
            WHERE rs.id_show = ? 
            ORDER BY rs.sequencia
        ''', (id_show,))
        repertorio = self.cursor.fetchall()
        
        self.cursor.execute("SELECT id, musica, tom FROM musicas ORDER BY id")
        todas_musicas = self.cursor.fetchall()
        
        titulo = ft.Text(f"Repertório: {show[3]} - {show[2]} - {show[1]}", size=20)
        
        lista_musicas = ft.Column([], scroll=ft.ScrollMode.AUTO, expand=True)
        
        campo_pesquisa = ft.TextField(
            label="Pesquisar música...",
            width=300,
            autofocus=True
        )
        
        musicas_filtradas = todas_musicas
        lista_musicas_disponiveis = ft.ListView([], expand=True, height=200)
        
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
                self.cursor.execute(
                    "SELECT 1 FROM repertorios_shows WHERE id_show=? AND id_musica=?",
                    (id_show, musica[0])
                )
                ja_no_repertorio = self.cursor.fetchone() is not None
                
                if not ja_no_repertorio:
                    lista_musicas_disponiveis.controls.append(
                        ft.ListTile(
                            title=ft.Text(musica[1]),
                            subtitle=ft.Text(f"Tom: {musica[2]}"),
                            on_click=lambda e, id=musica[0]: selecionar_musica(id),
                        )
                    )
            self.page.update()
        
        def selecionar_musica(id_musica):
            self.cursor.execute(
                "SELECT rs.sequencia, m.musica FROM repertorios_shows rs JOIN musicas m ON rs.id_musica = m.id WHERE rs.id_show = ? AND rs.id_musica = ?",
                (id_show, id_musica)
            )
            musica_existente = self.cursor.fetchone()
            
            if musica_existente:
                self.page.snack_bar = ft.SnackBar(
                    ft.Text(f"Esta música já está no repertório na posição {musica_existente[0]}: {musica_existente[1]}")
                )
                self.page.snack_bar.open = True
                self.page.update()
                return
                
            self.cursor.execute("SELECT MAX(sequencia) FROM repertorios_shows WHERE id_show=?", (id_show,))
            max_seq = self.cursor.fetchone()[0] or 0
            nova_seq = max_seq + 1
            
            try:
                self.cursor.execute(
                    "INSERT INTO repertorios_shows (id_show, id_musica, sequencia) VALUES (?, ?, ?)",
                    (id_show, id_musica, nova_seq)
                )
                self.conn.commit()
                carregar_repertorio()
                
                nonlocal musicas_filtradas
                musicas_filtradas = todas_musicas
                
                campo_pesquisa.value = ""
                campo_pesquisa.focus()
                
                atualizar_lista_musicas()
                self.page.update()
                
            except sqlite3.IntegrityError:
                self.page.snack_bar = ft.SnackBar(ft.Text("Esta música já está no repertório"))
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
            self.cursor.execute("SELECT sequencia, id_show FROM repertorios_shows WHERE id=?", (id_item,))
            item = self.cursor.fetchone()
            seq_atual = item[0]
            
            nova_seq = seq_atual + direcao
            if nova_seq < 1:
                return
                
            self.cursor.execute(
                "SELECT id FROM repertorios_shows WHERE id_show=? AND sequencia=?",
                (id_show, nova_seq)
            )
            item_troca = self.cursor.fetchone()
            
            if item_troca:
                self.cursor.execute(
                    "UPDATE repertorios_shows SET sequencia=? WHERE id=?",
                    (nova_seq, id_item)
                )
                self.cursor.execute(
                    "UPDATE repertorios_shows SET sequencia=? WHERE id=?",
                    (seq_atual, item_troca[0])
                )
            else:
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
            atualizar_lista_musicas()
        
        def voltar(e):
            self.app.main_page()
            self.campo_pesquisa.focus()
        
        campo_pesquisa.on_change = filtrar_musicas
        
        carregar_repertorio()
        atualizar_lista_musicas()
        
        content = ft.Column([
            ft.Row([ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=voltar), titulo]),
            ft.Row([campo_pesquisa]),
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
                ft.ElevatedButton("Exportar PDF Cifrado", on_click=lambda e: self.exportar_pdf(id_show, tipo="cifrado")),
                ft.ElevatedButton("Exportar PDF Simplificado", on_click=lambda e: self.exportar_pdf(id_show, tipo="simplificado")),
                ft.ElevatedButton("Voltar", on_click=voltar)
            ])
        ], expand=True)
        
        self.page.clean()
        self.page.add(content)

    def processar_cifra_para_pdf(self, cifra):
        """Processa a cifra para destacar texto entre colchetes em azul e substituir -- por →"""
        if not cifra:
            return cifra
            
        cifra_com_setas = re.sub(r'--', '→', cifra)
        
        padrao_colchetes = r'(\[[^\]]+\])'
        
        def substituir_colchetes(match):
            texto_entre_colchetes = match.group(1)
            return f'<span class="colchetes">{texto_entre_colchetes}</span>'
        
        cifra_processada = re.sub(padrao_colchetes, substituir_colchetes, cifra_com_setas)
        return cifra_processada

    def exportar_pdf(self, id_show, tipo="cifrado"):
        """Exporta o repertório para PDF usando xhtml2pdf"""
        self.cursor.execute("SELECT * FROM shows WHERE id=?", (id_show,))
        show = self.cursor.fetchone()
        
        data_show = show[1]
        try:
            data_obj = datetime.strptime(data_show, "%d/%m/%Y")
            data_formatada = data_obj.strftime("%d-%m-%Y")
        except:
            data_formatada = "data-desconhecida"
        
        artista_limpo = re.sub(r'[^\w\s-]', '', show[3]).replace(' ', '-')
        local_limpo = re.sub(r'[^\w\s-]', '', show[2]).replace(' ', '-')
        
        if tipo == "simplificado":
            nome_arquivo = f"{data_formatada} - {artista_limpo} - {local_limpo} - SIMPLIFICADO.pdf"
        else:
            nome_arquivo = f"{data_formatada} - {artista_limpo} - {local_limpo}.pdf"
        
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
        
        # Gerar PDF
        if tipo == "simplificado":
            html_content = self._gerar_pdf_simplificado(repertorio)
        else:
            html_content = self._gerar_pdf_cifrado(repertorio)
        
        pdf_buffer = BytesIO()
        pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)
        
        if pisa_status.err:
            self.page.snack_bar = ft.SnackBar(ft.Text("Erro ao gerar PDF"))
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        def salvar_pdf(e: ft.FilePickerResultEvent):
            if e.path:
                try:
                    if hasattr(e, 'files') and e.files:
                        caminho_completo = e.files[0].path
                    else:
                        if os.path.isdir(e.path):
                            caminho_completo = os.path.join(e.path, nome_arquivo)
                        else:
                            caminho_completo = e.path
                    
                    if not caminho_completo.lower().endswith('.pdf'):
                        caminho_completo += '.pdf'
                    
                    with open(caminho_completo, 'wb') as f:
                        f.write(pdf_buffer.getvalue())
                    
                    abrir_arquivo_multiplataforma(caminho_completo)
                    
                    self.page.snack_bar = ft.SnackBar(
                        ft.Text(f"PDF exportado com sucesso: {os.path.basename(caminho_completo)}")
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
                    
                except Exception as ex:
                    self.page.snack_bar = ft.SnackBar(ft.Text(f"Erro ao salvar PDF: {str(ex)}"))
                    self.page.snack_bar.open = True
                    self.page.update()
            else:
                self.page.snack_bar = ft.SnackBar(ft.Text("Exportação de PDF cancelada"))
                self.page.snack_bar.open = True
                self.page.update()
        
        file_picker = ft.FilePicker(on_result=salvar_pdf)
        self.page.overlay.append(file_picker)
        self.page.update()
        
        file_picker.save_file(
            file_name=nome_arquivo,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["pdf"]
        )

    def _gerar_pdf_simplificado(self, repertorio):
        """Gera o HTML para PDF simplificado"""
        html_content = """<!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    @page {
                        size: A4 landscape;
                        margin: 0.5cm;
                    }
                    body {
                        font-family: Arial, sans-serif;
                        font-size: 30px;
                        font-weight: bold;
                        background-color: #F0F0F0;
                        margin: 0;
                        padding: 0;
                    }
                    table {
                        width: 100%;
                        border-collapse: collapse;
                        table-layout: fixed;
                    }
                    td {
                        vertical-align: top;
                        padding: 5px 15px;
                        width: 50%;
                    }
                    .musica {
                        margin-bottom: 10px;
                        line-height: 1.3;
                        display: block;
                        page-break-inside: avoid;
                        white-space: nowrap;
                    }
                    .numero {
                        color: black;
                        font-weight: bold;
                        display: inline-block;
                        min-width: 40px;
                        text-align: right;
                        margin-right: 10px;
                    }
                    .conteudo {
                        display: inline-block;
                    }
                    .nome {
                        color: black;
                    }
                    .tom {
                        color: #8B4513;
                    }
                </style>
            </head>
            <body>
                <table>
                    <tr>
                        <td>"""
        
        num_musicas = len(repertorio)
        metade = (num_musicas + 1) // 2
        
        for i in range(metade):
            musica = repertorio[i]
            html_content += f"""
            <div class="musica">
                <span class="numero">{i+1}.</span>
                <span class="conteudo">
                    <span class="nome">{musica[1]}</span>
                    <span class="tom"> {musica[2]}</span>
                </span>
            </div>"""
        
        html_content += """
            </td>
            <td>"""
        
        for i in range(metade, num_musicas):
            musica = repertorio[i]
            html_content += f"""
            <div class="musica">
                <span class="numero">{i+1}.</span>
                <span class="conteudo">
                    <span class="nome">{musica[1]}</span>
                    <span class="tom"> {musica[2]}</span>
                </span>
            </div>"""
        
        html_content += """
                        </td>
                    </tr>
                </table>
            </body>
            </html>"""
        
        return html_content

    def _gerar_pdf_cifrado(self, repertorio):
        """Gera o HTML para PDF cifrado"""
        # Calcular tamanho da fonte baseado no número de caracteres
        textos = []
        for musica in repertorio:
            texto = f"➔ {musica[1]} {musica[2]} {musica[3] or ''}"
            textos.append(texto)
        
        max_caracteres = max(len(texto) for texto in textos) if textos else 0
        tamanho_fonte = min(34, 26 + (max_caracteres // 3))
        
        html_parts = []
        html_parts.append(f"""<!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    @page {{
                        size: A4 landscape;
                        margin: 0.5cm;
                    }}
                    body {{
                        font-family: Arial, sans-serif;
                        font-size: {tamanho_fonte}px;
                        font-weight: bold;
                        background-color: #F0F0F0;
                        margin: 0;
                        padding: 0.5cm;
                        line-height: 1.0;
                    }}
                    .musica {{
                        margin-bottom: 0.1cm;
                        line-height: 1.0;
                        page-break-inside: avoid;
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
                        padding: 0.02cm 0.05cm;
                    }}
                    .colchetes {{
                        color: blue;
                        background-color: #F0F0F0;
                        font-weight: normal;
                    }}
                </style>
            </head>
            <body>""")
        
        for musica in repertorio:
            cifra_processada = self.processar_cifra_para_pdf(musica[3] or "")
            html_parts.append(f"""
                <div class="musica">
                    <span class="seta">➔</span>
                    <span class="nome">{musica[1]}</span>
                    <span class="tom">{musica[2]}</span>
                    <span class="cifra">{cifra_processada}</span>
                </div>""")
        
        html_parts.append("""
            </body>
            </html>""")
        
        return "\n".join(html_parts)

    def excluir_show(self, id_show):
        """Exclui um show do banco de dados"""
        def confirmar_exclusao(e):
            self.cursor.execute("DELETE FROM repertorios_shows WHERE id_show=?", (id_show,))
            self.cursor.execute("DELETE FROM shows WHERE id=?", (id_show,))
            self.conn.commit()
            self.shows_data = self.carregar_shows()
            self.atualizar_tabela()
            
            if hasattr(self.app, 'tabs') and 'configuracoes' in self.app.tabs:
                self.app.tabs['configuracoes'].atualizar_cards()
            
            self.page.dialog.open = False
            self.page.update()
        
        def cancelar(e):
            self.page.dialog.open = False
            self.page.update()
            self.campo_pesquisa.focus()
        
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