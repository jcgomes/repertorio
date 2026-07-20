import flet as ft
from tabs.musicas import MusicasTab
from tabs.shows import ShowsTab
from tabs.configuracoes import ConfiguracoesTab
from tabs.sobre import SobreTab
from database import Database
from tabs.checklists import ChecklistsTab

class MusicApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Gerenciador de Repertório Musical"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        
        try:
            self.page.window.maximized = True
        except AttributeError:
            self.page.window_width = 1200
            self.page.window_height = 800
        
        # Inicializar banco de dados
        self.db = Database()
        
        # Inicializar abas
        self.tabs = {}
        self.setup_tabs()
        self.main_page()

    def setup_tabs(self):
        """Inicializa todas as abas"""
        # Cada aba recebe a referência do app principal e do page
        self.tabs['musicas'] = MusicasTab(self, self.page, self.db)
        self.tabs['shows'] = ShowsTab(self, self.page, self.db)
        self.tabs['checklists'] = ChecklistsTab(self, self.page, self.db)
        self.tabs['configuracoes'] = ConfiguracoesTab(self, self.page, self.db)
        self.tabs['sobre'] = SobreTab(self, self.page, self.db)

    def main_page(self):
        """Cria a página principal com as abas"""
        tab_musicas = ft.Tab(text="Músicas", content=self.tabs['musicas'].build())
        tab_shows = ft.Tab(text="Shows", content=self.tabs['shows'].build())
        tab_checklists = ft.Tab(text="Checklists", content=self.tabs['checklists'].build())
        tab_configuracoes = ft.Tab(text="Configurações", content=self.tabs['configuracoes'].build())
        tab_sobre = ft.Tab(text="Sobre", content=self.tabs['sobre'].build())
        
        tabs = ft.Tabs(
            tabs=[tab_musicas, tab_shows, tab_checklists, tab_configuracoes, tab_sobre],
            expand=True,
            on_change=self.ao_mudar_aba
        )
        
        self.page.clean()
        self.page.add(tabs)

    def ao_mudar_aba(self, e):
        """Quando muda de aba, chama o evento correspondente"""
        if e.control.selected_index == 0:
            self.tabs['musicas'].on_enter()
        elif e.control.selected_index == 1:
            self.tabs['shows'].on_enter()
        elif e.control.selected_index == 2:
            self.tabs['checklists'].on_enter()
        elif e.control.selected_index == 3:
            self.tabs['configuracoes'].on_enter()
        elif e.control.selected_index == 4:
            self.tabs['sobre'].on_enter()

def main(page: ft.Page):
    app = MusicApp(page)

if __name__ == "__main__":
    ft.app(target=main)