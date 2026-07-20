import flet as ft
import json
import os
from datetime import datetime

class ConfiguracoesTab:
    def __init__(self, app, page, db):
        self.app = app
        self.page = page
        self.db = db
        self.cursor = db.cursor
        self.conn = db.conn
        
        self.card_total_musicas = None
        self.card_total_shows = None

    def build(self):
        """Constrói a interface da aba de configurações"""
        self.card_total_musicas = self.criar_card_estatistica("Total de Músicas", self.obter_total_musicas())
        self.card_total_shows = self.criar_card_estatistica("Total de Shows", self.obter_total_shows())
        self.card_total_checklists = self.criar_card_estatistica("Total de Checklists", self.obter_total_checklists())

        return ft.Container(
            content=ft.Column([
                ft.Text("Configurações", size=30, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.ListTile(
                    title=ft.Text("Backup e Restauração", weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text("Exporte ou importe todos os dados do aplicativo"),
                ),
                ft.Row([
                    ft.ElevatedButton(
                        "Exportar Banco de Dados",
                        icon=ft.icons.BACKUP,
                        on_click=self.exportar_banco_dados
                    ),
                    ft.ElevatedButton(
                        "Importar Banco de Dados", 
                        icon=ft.icons.RESTORE,
                        on_click=self.importar_banco_dados
                    )
                ]),
                ft.Divider(),
                ft.ListTile(
                    title=ft.Text("Informações do Banco de Dados", weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text("Estatísticas do sistema"),
                ),
                ft.Row([
                    self.card_total_musicas,
                    self.card_total_shows,
                    self.card_total_checklists,
                ])
            ], scroll=ft.ScrollMode.AUTO),
            padding=30,
            expand=True
        )

    def on_enter(self):
        """Quando a aba recebe foco"""
        self.atualizar_cards()

    def criar_card_estatistica(self, titulo, valor):
        """Cria um card de estatística"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(titulo, size=14, color=ft.colors.GREY_700),
                    ft.Text(str(valor), size=24, weight=ft.FontWeight.BOLD)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20,
                width=150
            )
        )

    def atualizar_cards(self):
        """Atualiza os cards de estatística"""
        total_musicas = self.obter_total_musicas()
        total_shows = self.obter_total_shows()
        total_checklists = self.obter_total_checklists()
        
        self.card_total_musicas.content.content.controls[1].value = str(total_musicas)
        self.card_total_shows.content.content.controls[1].value = str(total_shows)
        self.card_total_checklists.content.content.controls[1].value = str(total_checklists)
        
        self.page.update()

    def obter_total_musicas(self):
        """Retorna o total de músicas no banco"""
        self.cursor.execute("SELECT COUNT(*) FROM musicas")
        return self.cursor.fetchone()[0]

    def obter_total_shows(self):
        """Retorna o total de shows no banco"""
        self.cursor.execute("SELECT COUNT(*) FROM shows")
        return self.cursor.fetchone()[0]

    def obter_total_checklists(self):
        """Retorna o total de checklists no banco"""
        self.cursor.execute("SELECT COUNT(*) FROM checklist")
        return self.cursor.fetchone()[0]

    def exportar_banco_dados(self, e):
        """Exporta todos os dados do banco para um arquivo de texto"""
        try:
            dados_exportacao = {}
            
            # Músicas
            self.cursor.execute("SELECT musica, autor, estilo, tom, cifra FROM musicas")
            dados_exportacao['musicas'] = self.cursor.fetchall()
            
            # Shows
            self.cursor.execute("SELECT data_show, local_show, artista FROM shows")
            dados_exportacao['shows'] = self.cursor.fetchall()
            
            # Repertórios
            self.cursor.execute('''
                SELECT s.data_show, s.local_show, s.artista, m.musica, m.autor, rs.sequencia 
                FROM repertorios_shows rs 
                JOIN shows s ON rs.id_show = s.id 
                JOIN musicas m ON rs.id_musica = m.id
            ''')
            dados_exportacao['repertorios'] = self.cursor.fetchall()
            
            # Checklists
            self.cursor.execute("SELECT data, titulo FROM checklist")
            dados_exportacao['checklists'] = self.cursor.fetchall()
            
            # Checklist Detalhes
            self.cursor.execute('''
                SELECT c.data, c.titulo, cd.descricao, cd.status 
                FROM checklist_detail cd 
                JOIN checklist c ON cd.id_checklist = c.id
            ''')
            dados_exportacao['checklist_detalhes'] = self.cursor.fetchall()
            
            # Criar nome do arquivo
            data_atual = datetime.now().strftime("%d-%m-%Y")
            nome_arquivo = f"backup-app-repertorio-{data_atual}.txt"
            
            # Converter para JSON string
            dados_json = json.dumps(dados_exportacao, ensure_ascii=False, indent=2)
            
            def salvar_arquivo(e: ft.FilePickerResultEvent):
                if e.path:
                    try:
                        if hasattr(e, 'files') and e.files:
                            caminho_completo = e.files[0].path
                        else:
                            if os.path.isdir(e.path):
                                caminho_completo = os.path.join(e.path, nome_arquivo)
                            else:
                                caminho_completo = e.path
                        
                        with open(caminho_completo, 'w', encoding='utf-8') as f:
                            f.write(dados_json)
                        
                        self.page.snack_bar = ft.SnackBar(
                            ft.Text(f"Backup exportado com sucesso: {os.path.basename(caminho_completo)}")
                        )
                        self.page.snack_bar.open = True
                        self.page.update()
                    except Exception as ex:
                        self.page.snack_bar = ft.SnackBar(ft.Text(f"Erro ao salvar arquivo: {str(ex)}"))
                        self.page.snack_bar.open = True
                        self.page.update()
                else:
                    self.page.snack_bar = ft.SnackBar(ft.Text("Exportação cancelada"))
                    self.page.snack_bar.open = True
                    self.page.update()
            
            file_picker = ft.FilePicker(on_result=salvar_arquivo)
            self.page.overlay.append(file_picker)
            self.page.update()
            
            file_picker.save_file(
                file_name=nome_arquivo,
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["txt"]
            )
            
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Erro ao exportar backup: {str(ex)}"))
            self.page.snack_bar.open = True
            self.page.update()

    def importar_banco_dados(self, e):
        """Importa dados de um arquivo de texto para o banco de dados"""
        try:
            def carregar_arquivo(e: ft.FilePickerResultEvent):
                if e.files and e.files[0].path:
                    caminho_arquivo = e.files[0].path
                    
                    try:
                        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                            dados_importacao = json.loads(f.read())
                        
                        # Sincronizar músicas
                        musicas_adicionadas = self._sincronizar_musicas(dados_importacao.get('musicas', []))
                        shows_adicionados = self._sincronizar_shows(dados_importacao.get('shows', []))
                        repertorios_adicionados = self._sincronizar_repertorios(dados_importacao.get('repertorios', []))
                        checklists_adicionados = self._sincronizar_checklists(
                            dados_importacao.get('checklists', []),
                            dados_importacao.get('checklist_detalhes', [])
                        )
                        
                        self.conn.commit()
                        
                        # Atualizar dados na aba de músicas
                        if hasattr(self.app, 'tabs') and 'musicas' in self.app.tabs:
                            self.app.tabs['musicas'].musicas_data = self.app.tabs['musicas'].carregar_musicas()
                            self.app.tabs['musicas'].atualizar_tabela()
                        
                        # Atualizar dados na aba de shows
                        if hasattr(self.app, 'tabs') and 'shows' in self.app.tabs:
                            self.app.tabs['shows'].shows_data = self.app.tabs['shows'].carregar_shows()
                            self.app.tabs['shows'].atualizar_tabela()
                        
                        # Atualizar dados na aba de checklists
                        if hasattr(self.app, 'tabs') and 'checklists' in self.app.tabs:
                            self.app.tabs['checklists'].checklists_data = self.app.tabs['checklists'].carregar_checklists()
                            self.app.tabs['checklists'].atualizar_tabela()
                        
                        self.atualizar_cards()
                        
                        self.page.snack_bar = ft.SnackBar(
                            ft.Text(f"Backup importado com sucesso! Músicas: {musicas_adicionadas}, Shows: {shows_adicionados}, Repertórios: {repertorios_adicionados}, Checklists: {checklists_adicionados}")
                        )
                        self.page.snack_bar.open = True
                        self.page.update()
                        
                    except Exception as ex:
                        self.page.snack_bar = ft.SnackBar(ft.Text(f"Erro ao importar backup: {str(ex)}"))
                        self.page.snack_bar.open = True
                        self.page.update()
                else:
                    self.page.snack_bar = ft.SnackBar(ft.Text("Importação cancelada"))
                    self.page.snack_bar.open = True
                    self.page.update()
            
            file_picker = ft.FilePicker(on_result=carregar_arquivo)
            self.page.overlay.append(file_picker)
            self.page.update()
            
            file_picker.pick_files(
                allowed_extensions=['txt'],
                dialog_title="Selecione o arquivo de backup"
            )
            
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Erro ao importar backup: {str(ex)}"))
            self.page.snack_bar.open = True
            self.page.update()

    def _sincronizar_musicas(self, musicas_importadas):
        """Sincroniza músicas importadas com o banco existente"""
        musicas_adicionadas = 0
        
        for musica in musicas_importadas:
            self.cursor.execute(
                "SELECT id FROM musicas WHERE musica = ? AND (autor = ? OR (autor IS NULL AND ? IS NULL))",
                (musica[0], musica[1], musica[1])
            )
            musica_existente = self.cursor.fetchone()
            
            if not musica_existente:
                self.cursor.execute(
                    "INSERT INTO musicas (musica, autor, estilo, tom, cifra) VALUES (?, ?, ?, ?, ?)",
                    (musica[0], musica[1], musica[2], musica[3], musica[4])
                )
                musicas_adicionadas += 1
        
        return musicas_adicionadas

    def _sincronizar_shows(self, shows_importados):
        """Sincroniza shows importados com o banco existente"""
        shows_adicionados = 0
        
        for show in shows_importados:
            self.cursor.execute(
                "SELECT id FROM shows WHERE data_show = ? AND local_show = ? AND artista = ?",
                (show[0], show[1], show[2])
            )
            show_existente = self.cursor.fetchone()
            
            if not show_existente:
                self.cursor.execute(
                    "INSERT INTO shows (data_show, local_show, artista) VALUES (?, ?, ?)",
                    (show[0], show[1], show[2])
                )
                shows_adicionados += 1
        
        return shows_adicionados

    def _sincronizar_repertorios(self, repertorios_importados):
        """Sincroniza repertórios importados com o banco existente"""
        repertorios_adicionados = 0
        
        for repertorio in repertorios_importados:
            data_show, local_show, artista, musica, autor, sequencia = repertorio
            
            self.cursor.execute(
                "SELECT id FROM shows WHERE data_show = ? AND local_show = ? AND artista = ?",
                (data_show, local_show, artista)
            )
            show_result = self.cursor.fetchone()
            
            self.cursor.execute(
                "SELECT id FROM musicas WHERE musica = ? AND (autor = ? OR (autor IS NULL AND ? IS NULL))",
                (musica, autor, autor)
            )
            musica_result = self.cursor.fetchone()
            
            if show_result and musica_result:
                id_show = show_result[0]
                id_musica = musica_result[0]
                
                self.cursor.execute(
                    "SELECT id FROM repertorios_shows WHERE id_show = ? AND id_musica = ?",
                    (id_show, id_musica)
                )
                repertorio_existente = self.cursor.fetchone()
                
                if not repertorio_existente:
                    self.cursor.execute(
                        "INSERT INTO repertorios_shows (id_show, id_musica, sequencia) VALUES (?, ?, ?)",
                        (id_show, id_musica, sequencia)
                    )
                    repertorios_adicionados += 1
        
        return repertorios_adicionados
    
    def _sincronizar_checklists(self, checklists_importados, detalhes_importados):
        """Sincroniza checklists importados com o banco existente"""
        checklists_adicionados = 0
        
        # Primeiro, importar checklists
        for checklist in checklists_importados:
            data, titulo = checklist
            
            # Verificar se o checklist já existe
            self.cursor.execute(
                "SELECT id FROM checklist WHERE data = ? AND titulo = ?",
                (data, titulo)
            )
            checklist_existente = self.cursor.fetchone()
            
            if not checklist_existente:
                # Inserir novo checklist
                self.cursor.execute(
                    "INSERT INTO checklist (data, titulo) VALUES (?, ?)",
                    (data, titulo)
                )
                checklists_adicionados += 1
        
        # Depois, importar detalhes
        for detalhe in detalhes_importados:
            data_checklist, titulo_checklist, descricao, status = detalhe
            
            # Buscar ID do checklist
            self.cursor.execute(
                "SELECT id FROM checklist WHERE data = ? AND titulo = ?",
                (data_checklist, titulo_checklist)
            )
            checklist_result = self.cursor.fetchone()
            
            if checklist_result:
                id_checklist = checklist_result[0]
                
                # Verificar se o detalhe já existe
                self.cursor.execute(
                    "SELECT id FROM checklist_detail WHERE id_checklist = ? AND descricao = ?",
                    (id_checklist, descricao)
                )
                detalhe_existente = self.cursor.fetchone()
                
                if not detalhe_existente:
                    # Inserir novo detalhe
                    self.cursor.execute(
                        "INSERT INTO checklist_detail (id_checklist, descricao, status) VALUES (?, ?, ?)",
                        (id_checklist, descricao, status)
                    )
        
        return checklists_adicionados