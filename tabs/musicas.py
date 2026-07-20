import flet as ft
from utils.helpers import formatar_tom, verificar_musica_existente

ESTILOS_MUSICAIS = [
    "Samba", "Salsa", "Bossa Nova", "MPB", "Rock", "Pop", "Jazz", "Blues",
    "Funk", "Forró", "Axé", "Pagode", "Sertanejo", "Rap", "Hip Hop", "Reggae",
    "Eletrônica", "Clássica", "Gospel", "Outro"
]

class MusicasTab:
    def __init__(self, app, page, db):
        self.app = app
        self.page = page
        self.db = db
        self.cursor = db.cursor
        self.conn = db.conn
        
        self.musicas_data = []
        self.musicas_table = None
        self.campo_pesquisa = None

    def build(self):
        """Constrói a interface da aba de músicas"""
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
        )
        
        self.atualizar_tabela()
        
        self.campo_pesquisa = ft.TextField(
            label="Pesquisar música...",
            width=300,
            on_change=self.filtrar_musicas,
            autofocus=True
        )
        
        btn_nova_musica = ft.ElevatedButton(
            "Nova Música",
            icon=ft.icons.ADD,
            on_click=lambda e: self.abrir_dialog_musica()
        )
        
        table_container = ft.Container(
            content=ft.ListView(
                controls=[self.musicas_table],
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
                    btn_nova_musica
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

    def carregar_musicas(self):
        """Carrega as músicas do banco de dados"""
        self.cursor.execute("SELECT * FROM musicas ORDER BY id")
        return self.cursor.fetchall()

    def atualizar_tabela(self, musicas_data=None):
        """Atualiza a tabela de músicas"""
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
                                    icon=ft.icons.VISIBILITY,
                                    tooltip="Visualizar",
                                    on_click=lambda e, id=musica[0]: self.visualizar_musica(id)
                                ),
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

    def filtrar_musicas(self, e):
        """Filtra as músicas na tabela"""
        termo = self.campo_pesquisa.value.lower()
        if termo:
            musicas_filtradas = [m for m in self.musicas_data if 
                               termo in m[1].lower() or 
                               (m[2] and termo in m[2].lower()) or
                               (m[3] and termo in m[3].lower())]
        else:
            musicas_filtradas = self.musicas_data
        
        self.atualizar_tabela(musicas_filtradas)

    def abrir_dialog_musica(self, id_musica=None):
        """Abre o diálogo para adicionar/editar uma música"""
        musica = None
        if id_musica:
            self.cursor.execute("SELECT * FROM musicas WHERE id=?", (id_musica,))
            musica = self.cursor.fetchone()
        
        campo_musica = ft.TextField(label="Música", value=musica[1] if musica else "")
        campo_autor = ft.TextField(label="Autor", value=musica[2] if musica else "")
        campo_estilo = ft.Dropdown(
            label="Estilo",
            options=[ft.dropdown.Option(estilo) for estilo in ESTILOS_MUSICAIS],
            value=musica[3] if musica else None
        )
        
        tom_value = musica[4] if musica else ""
        campo_tom = ft.TextField(
            label="Tom", 
            value=tom_value,
            on_change=lambda e: self._formatar_tom_em_tempo_real(campo_tom)
        )
        
        campo_cifra = ft.TextField(
            label="Cifra", 
            value=musica[5] if musica else "",
            multiline=True,
            min_lines=3,
            max_lines=5
        )
        
        mensagem_erro = ft.Text("", color=ft.colors.RED, size=12)
        
        def salvar_musica(e):
            nome_musica = campo_musica.value.strip()
            autor_musica = campo_autor.value.strip() if campo_autor.value else None
            
            if not nome_musica:
                mensagem_erro.value = "O nome da música é obrigatório!"
                self.page.update()
                return
                
            if verificar_musica_existente(self.cursor, nome_musica, autor_musica, id_musica):
                mensagem_erro.value = "Esta música já existe no repertório!"
                self.page.update()
                return
                
            tom_formatado = formatar_tom(campo_tom.value) if campo_tom.value else ""
            
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
            self.atualizar_tabela()
            
            # Atualizar configurações se existir
            if hasattr(self.app, 'tabs') and 'configuracoes' in self.app.tabs:
                self.app.tabs['configuracoes'].atualizar_cards()
            
            self.campo_pesquisa.value = ""
            self.page.dialog.open = False
            self.page.update()
        
        def cancelar(e):
            self.page.dialog.open = False
            self.page.update()
            self.campo_pesquisa.focus()
        
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

    def _formatar_tom_em_tempo_real(self, campo_tom):
        """Formata o tom em tempo real"""
        if campo_tom.value:
            campo_tom.value = formatar_tom(campo_tom.value)
            self.page.update()

    def excluir_musica(self, id_musica):
        """Exclui uma música do banco de dados"""
        def confirmar_exclusao(e):
            self.cursor.execute("DELETE FROM musicas WHERE id=?", (id_musica,))
            self.conn.commit()
            self.musicas_data = self.carregar_musicas()
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
            content=ft.Text("Tem certeza que deseja excluir esta música?"),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar),
                ft.TextButton("Excluir", on_click=confirmar_exclusao)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def visualizar_musica(self, id_musica):
        """Abre uma tela de visualização da música com formatação estilo Cifra Club"""
        self.cursor.execute("SELECT * FROM musicas WHERE id=?", (id_musica,))
        musica = self.cursor.fetchone()
        
        if not musica:
            self.page.snack_bar = ft.SnackBar(ft.Text("Música não encontrada!"))
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        # Processar a cifra para formatação
        cifra_formatada = self._formatar_cifra_para_visualizacao(musica[5] if musica[5] else "")
        
        # Criar a tela de visualização
        titulo = ft.Text(musica[1], size=28, weight=ft.FontWeight.BOLD)
        autor = ft.Row([
            ft.Text("Autor:", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.GREY_700),
            ft.Text(musica[2] if musica[2] else "Desconhecido", size=16, color=ft.colors.GREY_700)
        ], spacing=5)

        estilo = ft.Row([
            ft.Text("Estilo:", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.GREY_700),
            ft.Text(musica[3] if musica[3] else "Não definido", size=16, color=ft.colors.GREY_700)
        ], spacing=5)

        # Limpar o tom removendo parênteses
        tom_valor = musica[4] if musica[4] else "Não definido"
        if tom_valor.startswith('(') and tom_valor.endswith(')'):
            tom_valor = tom_valor[1:-1]

        tom = ft.Row([
            ft.Text("Tom:", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.GREY_700),
            ft.Text(tom_valor, size=16, color=ft.colors.GREY_700)
        ], spacing=5)
        
        # Container da cifra com formatação
        cifra_container = ft.Container(
            content=ft.Column([
                ft.Text("Cifra:", size=18, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Column(
                        controls=cifra_formatada,
                        spacing=5,
                        expand=True  # Adicionado expand no Column interno
                    ),
                    padding=15,
                    bgcolor=ft.colors.GREY_50,
                    border=ft.border.all(1, ft.colors.GREY_300),
                    border_radius=8,
                    expand=True,
                    width=float('inf')  # Força a ocupar toda a largura disponível
                )
            ], expand=True),
            expand=True,
            width=float('inf')  # Força o container pai a ocupar toda a largura
        )
        
        def voltar(e):
            """Volta para a lista de músicas"""
            self.page.clean()
            self.page.add(self.build())
            self.campo_pesquisa.focus()
        
        # Layout da página de visualização
        content = ft.Column([
            ft.Row([
                ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=voltar),
                ft.Text("Visualizar Música", size=20, weight=ft.FontWeight.BOLD),
            ], alignment=ft.MainAxisAlignment.START),
            ft.Divider(height=10),
            ft.Container(
                content=ft.Column([
                    titulo,
                    autor,
                    estilo,
                    tom,
                    ft.Divider(height=20),
                    cifra_container,
                ], spacing=10),
                padding=20,
                expand=True
            ),
            ft.Row([
                ft.ElevatedButton(
                    "Editar",
                    icon=ft.icons.EDIT,
                    on_click=lambda e: [self.abrir_dialog_musica(id_musica), voltar(e)]
                )
            ], alignment=ft.MainAxisAlignment.END)
        ], expand=True)
        
        self.page.clean()
        self.page.add(content)

    def _formatar_cifra_para_visualizacao(self, cifra):
        """Formata a cifra para visualização estilo Cifra Club"""
        if not cifra:
            return [ft.Text("Nenhuma cifra cadastrada", italic=True, color=ft.colors.GREY_600)]
        
        linhas = cifra.split('\n')
        controles = []
        
        for linha in linhas:
            if not linha.strip():
                controles.append(ft.Divider(height=5))
                continue
                
            # Processar a linha para destacar acordes entre colchetes
            partes = []
            texto_atual = ""
            i = 0
            
            while i < len(linha):
                if linha[i] == '[':
                    # Encontrou um acorde
                    if texto_atual:
                        partes.append(ft.Text(texto_atual, size=16))
                        texto_atual = ""
                    
                    # Extrair o acorde até o fechamento
                    j = i + 1
                    while j < len(linha) and linha[j] != ']':
                        j += 1
                    
                    if j < len(linha):
                        acorde = linha[i:j+1]
                        # Remover os colchetes para exibir
                        acorde_limpo = acorde[1:-1]
                        partes.append(
                            ft.Text(
                                acorde_limpo,
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.BLUE_700
                            )
                        )
                        i = j + 1
                    else:
                        texto_atual += linha[i]
                        i += 1
                else:
                    texto_atual += linha[i]
                    i += 1
            
            if texto_atual:
                partes.append(ft.Text(texto_atual, size=16))
            
            # Criar uma linha com todos os elementos
            if partes:
                linha_container = ft.Row(partes, spacing=2, wrap=True)
                controles.append(linha_container)
            else:
                controles.append(ft.Text(linha, size=16))
        
        return controles