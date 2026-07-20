import flet as ft

class SobreTab:
    def __init__(self, app, page, db):
        self.app = app
        self.page = page
        self.db = db

    def build(self):
        """Constrói a interface da aba sobre"""
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
                    title=ft.Text("Repositório e manual:"),
                ),
                ft.ElevatedButton(
                    "📂 Abrir no GitHub",
                    icon=ft.icons.OPEN_IN_NEW,
                    on_click=lambda e: self.page.launch_url("https://github.com/jcgomes/repertorio")
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

    def on_enter(self):
        """Quando a aba recebe foco"""
        pass