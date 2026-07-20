import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('repertorio.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.setup_tables()

    def setup_tables(self):
        """Cria as tabelas se não existirem"""
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
        
        # Tabela de repertórios dos shows
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

        # Tabela de checklists
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS checklist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                titulo TEXT NOT NULL
            )
        ''')

        # Tabela de detalhes do checklist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS checklist_detail (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_checklist INTEGER NOT NULL,
                descricao TEXT NOT NULL,
                status INTEGER DEFAULT 0,
                FOREIGN KEY (id_checklist) REFERENCES checklist (id) ON DELETE CASCADE
            )
        ''')

        # Criar índices
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_checklist_data ON checklist(data)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_checklist_titulo ON checklist(titulo)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_checklist_detail_id_checklist ON checklist_detail(id_checklist)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_checklist_detail_status ON checklist_detail(status)')

    def close(self):
        """Fecha a conexão com o banco"""
        self.conn.close()