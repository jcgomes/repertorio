import flet as ft
from datetime import datetime

class ChecklistsTab:
    def __init__(self, app, page, db):
        self.app = app
        self.page = page
        self.db = db
        self.cursor = db.cursor
        self.conn = db.conn
        
        self.checklists_data = []
        self.checklists_table = None
        self.campo_pesquisa = None

    def build(self):
        """Constrói a interface da aba de checklists"""
        self.checklists_data = self.carregar_checklists()
        
        self.checklists_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Data")),
                ft.DataColumn(ft.Text("Título")),
                ft.DataColumn(ft.Text("Itens")),
                ft.DataColumn(ft.Text("Progresso")),
                ft.DataColumn(ft.Text("Ações"))
            ],
            rows=[],
        )
        
        self.atualizar_tabela()
        
        self.campo_pesquisa = ft.TextField(
            label="Pesquisar checklists por título...",
            width=300,
            on_change=self.filtrar_checklists,
            autofocus=True
        )
        
        btn_novo_checklist = ft.ElevatedButton(
            "Novo Checklist",
            icon=ft.icons.ADD,
            on_click=lambda e: self.abrir_dialog_checklist()
        )
        
        table_container = ft.Container(
            content=ft.ListView(
                controls=[self.checklists_table],
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
                    btn_novo_checklist
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

    def carregar_checklists(self):
        """Carrega os checklists do banco de dados ordenados por data decrescente"""
        self.cursor.execute("""
            SELECT * FROM checklist 
            ORDER BY 
                substr(data, 7, 4) DESC,
                substr(data, 4, 2) DESC,
                substr(data, 1, 2) DESC
        """)
        return self.cursor.fetchall()

    def contar_itens_checklist(self, id_checklist):
        """Conta o total de itens de um checklist"""
        self.cursor.execute("SELECT COUNT(*) FROM checklist_detail WHERE id_checklist = ?", (id_checklist,))
        return self.cursor.fetchone()[0]

    def contar_itens_concluidos(self, id_checklist):
        """Conta os itens concluídos de um checklist"""
        self.cursor.execute("SELECT COUNT(*) FROM checklist_detail WHERE id_checklist = ? AND status = 1", (id_checklist,))
        return self.cursor.fetchone()[0]

    def filtrar_checklists(self, e):
        """Filtra os checklists na tabela"""
        termo = self.campo_pesquisa.value.lower()
        if termo:
            checklists_filtrados = [c for c in self.checklists_data if termo in c[2].lower()]
        else:
            checklists_filtrados = self.checklists_data
        
        self.atualizar_tabela(checklists_filtrados)

    def atualizar_tabela(self, checklists_data=None):
        """Atualiza a tabela de checklists"""
        if checklists_data is None:
            checklists_data = self.checklists_data
            
        rows = []
        for checklist in checklists_data:
            total_itens = self.contar_itens_checklist(checklist[0])
            itens_concluidos = self.contar_itens_concluidos(checklist[0])
            
            if total_itens > 0:
                progresso = int((itens_concluidos / total_itens) * 100)
                progresso_texto = f"{progresso}%"
                progresso_bar = ft.ProgressBar(value=progresso/100, width=80)
            else:
                progresso_texto = "0%"
                progresso_bar = ft.ProgressBar(value=0, width=80)
            
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(checklist[0]))),
                        ft.DataCell(ft.Text(checklist[1])),
                        ft.DataCell(ft.Text(checklist[2])),
                        ft.DataCell(ft.Text(str(total_itens))),
                        ft.DataCell(
                            ft.Column([
                                progresso_bar,
                                ft.Text(progresso_texto, size=12)
                            ], spacing=2)
                        ),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.icons.EDIT,
                                    tooltip="Editar",
                                    on_click=lambda e, id=checklist[0]: self.abrir_dialog_checklist(id)
                                ),
                                ft.IconButton(
                                    icon=ft.icons.DELETE,
                                    tooltip="Excluir",
                                    on_click=lambda e, id=checklist[0]: self.excluir_checklist(id)
                                ),
                                ft.IconButton(
                                    icon=ft.icons.CHECKLIST,
                                    tooltip="Ver Itens",
                                    on_click=lambda e, id_checklist=checklist[0]: self.ver_checklist(id_checklist)
                                )
                            ])
                        )
                    ]
                )
            )
        self.checklists_table.rows = rows
        self.page.update()

    def abrir_dialog_checklist(self, id_checklist=None):
        """Abre o diálogo para adicionar/editar um checklist"""
        checklist = None
        itens = []
        
        if id_checklist:
            self.cursor.execute("SELECT * FROM checklist WHERE id=?", (id_checklist,))
            checklist = self.cursor.fetchone()
            
            self.cursor.execute("SELECT * FROM checklist_detail WHERE id_checklist = ? ORDER BY id", (id_checklist,))
            itens = self.cursor.fetchall()
        
        # Campos do formulário
        campo_data = ft.TextField(
            label="Data (DD/MM/AAAA)", 
            value=checklist[1] if checklist else datetime.now().strftime("%d/%m/%Y"),
            width=200
        )
        campo_titulo = ft.TextField(
            label="Título do Checklist", 
            value=checklist[2] if checklist else "",
            width=400,
            autofocus=True  # FOCO NO TÍTULO
        )
        
        # Lista de itens
        itens_container = ft.Column([], spacing=10)
        
        def adicionar_item(descricao="", status=0, focar=False):
            checkbox = ft.Checkbox(
                value=bool(status),
                data={"status": status}
            )
            
            text_field = ft.TextField(
                label="Descrição",
                value=descricao,
                expand=True,
                autofocus=focar  # Só foca se for explicitamente solicitado
            )
            
            btn_remover = ft.IconButton(
                icon=ft.icons.DELETE,
                tooltip="Remover item",
            )
            
            item_row = ft.Row([
                checkbox,
                text_field,
                btn_remover
            ], alignment=ft.MainAxisAlignment.START)
            
            item_row.data = {
                "id": None,
                "checkbox": checkbox,
                "text_field": text_field,
                "btn_remover": btn_remover,
                "status": status
            }
            
            checkbox.on_change = lambda e, row=item_row: toggle_status(row)
            text_field.on_change = lambda e, row=item_row: salvar_edicao_item(row)
            btn_remover.on_click = lambda e, row=item_row: remover_item(row)
            
            itens_container.controls.append(item_row)
            self.page.update()
        
        def toggle_status(row):
            checkbox = row.data["checkbox"]
            row.data["status"] = 1 if checkbox.value else 0
            
            if id_checklist and row.data.get("id"):
                descricao = row.data["text_field"].value
                if descricao and descricao.strip():
                    try:
                        self.cursor.execute(
                            "UPDATE checklist_detail SET status = ? WHERE id = ?",
                            (row.data["status"], row.data["id"])
                        )
                        self.conn.commit()
                    except Exception as ex:
                        print(f"Erro ao salvar status: {ex}")
        
        def salvar_edicao_item(row):
            descricao = row.data["text_field"].value
            if id_checklist and row.data.get("id") and descricao and descricao.strip():
                try:
                    self.cursor.execute(
                        "UPDATE checklist_detail SET descricao = ? WHERE id = ?",
                        (descricao.strip(), row.data["id"])
                    )
                    self.conn.commit()
                except Exception as ex:
                    print(f"Erro ao salvar descrição: {ex}")
        
        def remover_item(row):
            if id_checklist and row.data.get("id"):
                try:
                    self.cursor.execute("DELETE FROM checklist_detail WHERE id = ?", (row.data["id"],))
                    self.conn.commit()
                except Exception as ex:
                    print(f"Erro ao remover item: {ex}")
            itens_container.controls.remove(row)
            self.page.update()
        
        # Carregar itens existentes
        if id_checklist and itens:
            for item in itens:
                adicionar_item(item[2], item[3], False)  # Sem foco
                item_row = itens_container.controls[-1]
                item_row.data["id"] = item[0]
        else:
            # Adicionar item inicial SEM foco (o foco fica no título)
            adicionar_item(focar=False)
        
        def salvar_checklist(e):
            nonlocal id_checklist
            
            if not campo_titulo.value or not campo_titulo.value.strip():
                self.page.snack_bar = ft.SnackBar(ft.Text("O título é obrigatório!"))
                self.page.snack_bar.open = True
                self.page.update()
                return
            
            try:
                datetime.strptime(campo_data.value, "%d/%m/%Y")
            except ValueError:
                self.page.snack_bar = ft.SnackBar(ft.Text("Data inválida! Use DD/MM/AAAA"))
                self.page.snack_bar.open = True
                self.page.update()
                return
            
            titulo = campo_titulo.value.strip()
            data = campo_data.value
            
            try:
                if id_checklist:
                    # Atualizar checklist
                    self.cursor.execute(
                        "UPDATE checklist SET data = ?, titulo = ? WHERE id = ?",
                        (data, titulo, id_checklist)
                    )
                    
                    # Remover itens que não estão mais na lista
                    ids_atuais = [row.data.get("id") for row in itens_container.controls if row.data.get("id")]
                    if ids_atuais:
                        placeholders = ",".join("?" * len(ids_atuais))
                        self.cursor.execute(
                            f"DELETE FROM checklist_detail WHERE id_checklist = ? AND id NOT IN ({placeholders})",
                            [id_checklist] + ids_atuais
                        )
                    else:
                        self.cursor.execute("DELETE FROM checklist_detail WHERE id_checklist = ?", (id_checklist,))
                    
                    # Adicionar ou atualizar itens
                    for row in itens_container.controls:
                        descricao = row.data["text_field"].value
                        if descricao and descricao.strip():
                            if row.data.get("id"):
                                # Atualizar item existente
                                self.cursor.execute(
                                    "UPDATE checklist_detail SET descricao = ?, status = ? WHERE id = ?",
                                    (descricao.strip(), row.data["status"], row.data["id"])
                                )
                            else:
                                # Inserir novo item
                                self.cursor.execute(
                                    "INSERT INTO checklist_detail (id_checklist, descricao, status) VALUES (?, ?, ?)",
                                    (id_checklist, descricao.strip(), row.data["status"])
                                )
                else:
                    # Inserir novo checklist
                    self.cursor.execute(
                        "INSERT INTO checklist (data, titulo) VALUES (?, ?)",
                        (data, titulo)
                    )
                    id_checklist = self.cursor.lastrowid
                    
                    # Inserir itens
                    for row in itens_container.controls:
                        descricao = row.data["text_field"].value
                        if descricao and descricao.strip():
                            self.cursor.execute(
                                "INSERT INTO checklist_detail (id_checklist, descricao, status) VALUES (?, ?, ?)",
                                (id_checklist, descricao.strip(), row.data["status"])
                            )
                
                self.conn.commit()
                
                # Atualizar dados e tabela
                self.checklists_data = self.carregar_checklists()
                self.atualizar_tabela()
                
                # Atualizar cards de estatística
                if hasattr(self.app, 'tabs') and 'configuracoes' in self.app.tabs:
                    self.app.tabs['configuracoes'].atualizar_cards()
                
                # Fechar o diálogo
                self.page.dialog.open = False
                self.page.update()
                
                # Snackbar de sucesso
                self.page.snack_bar = ft.SnackBar(ft.Text("Checklist salvo com sucesso!"))
                self.page.snack_bar.open = True
                self.page.update()
                
            except Exception as ex:
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Erro ao salvar: {str(ex)}"))
                self.page.snack_bar.open = True
                self.page.update()
        
        def cancelar(e):
            self.page.dialog.open = False
            self.page.update()
            self.campo_pesquisa.focus()
        
        # Botão para adicionar item
        btn_adicionar_item = ft.ElevatedButton(
            "Adicionar Item",
            icon=ft.icons.ADD,
            on_click=lambda e: adicionar_item(focar=True)  # Novo item ganha foco
        )
        
        # Container com scroll para os itens
        itens_scroll = ft.Container(
            content=ft.Column(
                controls=[itens_container],
                scroll=ft.ScrollMode.AUTO,
                expand=True
            ),
            height=300,
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=5,
            padding=10,
            bgcolor=ft.colors.WHITE,
            expand=True
        )
        
        # Criar o diálogo
        dialog = ft.AlertDialog(
            title=ft.Text("Editar Checklist" if id_checklist else "Novo Checklist", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    ft.Row([campo_data, campo_titulo], alignment=ft.MainAxisAlignment.START),
                    ft.Divider(height=10),
                    ft.Text("Itens do Checklist:", weight=ft.FontWeight.BOLD, size=16),
                    itens_scroll,
                    btn_adicionar_item
                ], tight=True, spacing=10),
                width=600,
                padding=10
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar),
                ft.TextButton("Salvar", on_click=salvar_checklist)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        # Abrir o diálogo
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def ver_checklist(self, id_checklist):
        """Visualiza um checklist com opção de marcar itens como concluídos"""
        # Buscar dados do checklist
        self.cursor.execute("SELECT * FROM checklist WHERE id=?", (id_checklist,))
        checklist = self.cursor.fetchone()
        
        if not checklist:
            self.page.snack_bar = ft.SnackBar(ft.Text("Checklist não encontrado!"))
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        # Buscar itens do checklist
        self.cursor.execute(
            "SELECT id, descricao, status FROM checklist_detail WHERE id_checklist = ? ORDER BY id",
            (id_checklist,)
        )
        itens = self.cursor.fetchall()
        
        titulo = ft.Text(f"📋 {checklist[2]}", size=24, weight=ft.FontWeight.BOLD)
        subtitulo = ft.Text(f"📅 {checklist[1]}", size=16, color=ft.colors.GREY_700)
        
        # Lista de itens
        itens_lista = ft.Column([], scroll=ft.ScrollMode.AUTO, expand=True)
        
        def alternar_status_item(id_item, checkbox):
            """Alterna o status de um item do checklist"""
            novo_status = 1 if checkbox.value else 0
            self.cursor.execute(
                "UPDATE checklist_detail SET status = ? WHERE id = ?",
                (novo_status, id_item)
            )
            self.conn.commit()
            carregar_itens()
            self.page.update()
        
        def carregar_itens():
            itens_lista.controls.clear()
            
            # Buscar itens atualizados
            self.cursor.execute(
                "SELECT id, descricao, status FROM checklist_detail WHERE id_checklist = ? ORDER BY id",
                (id_checklist,)
            )
            itens_atualizados = self.cursor.fetchall()
            
            if not itens_atualizados:
                itens_lista.controls.append(
                    ft.Text("Nenhum item cadastrado neste checklist.", 
                        size=16, 
                        color=ft.colors.GREY_600,
                        italic=True)
                )
                self.page.update()
                return
            
            for item in itens_atualizados:
                # Criar checkbox
                checkbox = ft.Checkbox(
                    value=bool(item[2]),
                )
                
                # Criar função de callback separada para evitar problemas de closure
                def criar_callback(id_item, cb):
                    return lambda e: alternar_status_item(id_item, cb)
                
                # Atribuir o callback ao checkbox
                checkbox.on_change = criar_callback(item[0], checkbox)
                
                # Texto da descrição
                descricao_text = ft.Text(
                    item[1],
                    size=16,
                    color=ft.colors.GREY_600 if item[2] else ft.colors.BLACK,
                )
                
                # Se concluído, adicionar estilo de tachado (riscado)
                if item[2]:
                    descricao_text = ft.Text(
                        item[1],
                        size=16,
                        color=ft.colors.GREY_400,
                        weight=ft.FontWeight.NORMAL,
                    )
                
                item_row = ft.Row([
                    checkbox,
                    descricao_text,
                ], alignment=ft.MainAxisAlignment.START, spacing=10)
                
                card_item = ft.Card(
                    content=ft.Container(
                        content=item_row,
                        padding=15,
                        bgcolor=ft.colors.GREY_50 if item[2] else ft.colors.WHITE
                    ),
                    elevation=2 if not item[2] else 1
                )
                
                itens_lista.controls.append(card_item)
            self.page.update()
        
        def voltar(e):
            """Volta para a lista de checklists"""
            self.app.main_page()
            # Mudar para a aba de checklists (índice 2)
            if hasattr(self.app, 'page') and self.app.page.controls:
                try:
                    self.app.page.controls[0].selected_index = 2
                    self.app.page.update()
                except:
                    pass
            self.campo_pesquisa.focus()
        
        def excluir_checklist_confirm(e):
            """Exclui o checklist atual"""
            def confirmar_exclusao(e):
                self.cursor.execute("DELETE FROM checklist WHERE id = ?", (id_checklist,))
                self.conn.commit()
                
                self.checklists_data = self.carregar_checklists()
                self.atualizar_tabela()
                
                if hasattr(self.app, 'tabs') and 'configuracoes' in self.app.tabs:
                    self.app.tabs['configuracoes'].atualizar_cards()
                
                self.page.dialog.open = False
                voltar(e)
            
            def cancelar_exclusao(e):
                self.page.dialog.open = False
                self.page.update()
            
            dialog = ft.AlertDialog(
                title=ft.Text("Confirmar Exclusão"),
                content=ft.Text("Tem certeza que deseja excluir este checklist e todos os seus itens?"),
                actions=[
                    ft.TextButton("Cancelar", on_click=cancelar_exclusao),
                    ft.TextButton("Excluir", on_click=confirmar_exclusao)
                ]
            )
            
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()
        
        def editar_checklist(e):
            """Abre o diálogo de edição do checklist"""
            # Fechar a visualização e abrir a edição
            self.page.clean()
            self.abrir_dialog_checklist(id_checklist)
        
        # Carregar itens inicialmente
        carregar_itens()
        
        # Calcular progresso
        total_itens = len(itens)
        itens_concluidos = sum(1 for item in itens if item[2] == 1)
        progresso_texto = f"{itens_concluidos}/{total_itens}" if total_itens > 0 else "0/0"
        
        # Layout da página de visualização
        content = ft.Column([
            ft.Row([
                ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=voltar),
                titulo,
                ft.Row([
                    ft.Text(progresso_texto, size=16, color=ft.colors.GREY_700),
                    ft.IconButton(
                        icon=ft.icons.EDIT,
                        tooltip="Editar",
                        on_click=editar_checklist
                    ),
                    ft.IconButton(
                        icon=ft.icons.DELETE,
                        tooltip="Excluir",
                        on_click=excluir_checklist_confirm
                    )
                ])
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            subtitulo,
            ft.Divider(height=10),
            ft.Text("Itens do Checklist:", weight=ft.FontWeight.BOLD, size=18),
            ft.Container(
                content=itens_lista,
                border=ft.border.all(1, ft.colors.GREY_300),
                border_radius=8,
                padding=10,
                expand=True,
                bgcolor=ft.colors.WHITE
            )
        ], expand=True)
        
        self.page.clean()
        self.page.add(content)
        self.page.update()

    def excluir_checklist(self, id_checklist):
        """Exclui um checklist do banco de dados"""
        def confirmar_exclusao(e):
            self.cursor.execute("DELETE FROM checklist WHERE id=?", (id_checklist,))
            self.conn.commit()
            self.checklists_data = self.carregar_checklists()
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
            content=ft.Text("Tem certeza que deseja excluir este checklist e todos os seus itens?"),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar),
                ft.TextButton("Excluir", on_click=confirmar_exclusao)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()