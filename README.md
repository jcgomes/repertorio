# 🎵 Gerenciador de Repertório Musical

Um aplicativo desktop desenvolvido em Python com Flet para gerenciar repertórios musicais, shows e exportar PDFs profissionais.

## 📋 Índice

- [Funcionalidades](#funcionalidades)
- [Instalação](#instalação)
- [Como Usar](#como-usar)
  - [Gerenciar Músicas](#gerenciar-músicas)
  - [Gerenciar Shows](#gerenciar-shows)
  - [Criar Repertórios](#criar-repertórios)
  - [Exportar PDF](#exportar-pdf)
- [Estrutura do Banco de Dados](#estrutura-do-banco-de-dados)
- [Formatação de Cifras](#formatação-de-cifras)
- [Atalhos e Dicas](#atalhos-e-dicas)
- [Backup e Restauração](#backup-e-restauração)
- [Tecnologias](#tecnologias)

## 🚀 Funcionalidades

### 🎼 Gestão de Músicas
- ✅ Cadastro completo de músicas (nome, autor, estilo, tom, cifra)
- ✅ Pesquisa em tempo real por nome, autor ou estilo
- ✅ Ordenação automática por ID
- ✅ Verificação de duplicatas
- ✅ Formatação automática do tom entre parênteses
- ✅ Tabela expansível que ocupa toda a tela

### 🎪 Gestão de Shows
- ✅ Cadastro de shows com data, local e artista
- ✅ Visualização em ordem cronológica
- ✅ Criação de repertórios personalizados
- ✅ Tabela expansível que ocupa toda a tela

### 📋 Criação de Repertórios
- ✅ Adição de músicas ao repertório com um clique
- ✅ Reordenação com setas (↑↓)
- ✅ Pesquisa de músicas disponíveis com foco automático
- ✅ Sequenciamento automático
- ✅ Verificação de duplicatas no repertório

### 📄 Exportação para PDF
- ✅ Layout profissional em A4 paisagem
- ✅ Destaque automático de texto entre colchetes em azul
- ✅ Substituição automática de "--" por seta (→)
- ✅ Tamanho de fonte adaptável ao conteúdo
- ✅ Fundo amarelo para cifras
- ✅ Nome do arquivo automático: dd-mm-aaaa - artista - local.pdf

### 💾 Backup e Segurança
- ✅ Exportação completa do banco de dados
- ✅ Importação de backups
- ✅ Estatísticas em tempo real (total de músicas e shows)
- ✅ Sincronização inteligente de dados

## 💻 Instalação

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes do Python)

### Passo a Passo

1. **Clone o repositório:**
```bash
git clone https://github.com/jcgomes/repertorio.git
cd repertorio
```

2. **Instale as dependências:**
```bash
pip install flet sqlite3 xhtml2pdf
```

3. **Execute o aplicativo:**
```bash
python repertorio.py
```

## 🎮 Como Usar

### 🎼 Gerenciar Músicas

#### Adicionar Nova Música
1. Acesse a aba **"Músicas"**
2. Clique em **"Nova Música"**
3. Preencha os campos:
   - **Música**: Nome da música (obrigatório)
   - **Autor**: Compositor/Intérprete
   - **Estilo**: Selecione da lista pré-definida
   - **Tom**: Informe o tom (formatação automática entre parênteses)
   - **Cifra**: Acordes e anotações

#### Pesquisar Músicas
- Use o campo **"Pesquisar música..."** para filtrar por:
  - Nome da música
  - Autor
  - Estilo musical

#### Editar/Excluir
- Clique nos ícones de **✏️ (Editar)** ou **🗑️ (Excluir)** na coluna "Ações"

### 🎪 Gerenciar Shows

#### Criar Novo Show
1. Acesse a aba **"Shows"**
2. Clique em **"Novo Show"**
3. Preencha os dados:
   - **Data**: Formato DD/MM/AAAA
   - **Local**: Local do show
   - **Artista**: Nome da banda/artista

### 📋 Criar Repertórios

#### Acessar Repertório
1. Na aba **"Shows"**, clique no ícone **👁️ (Ver Repertório)**

#### Adicionar Músicas
1. Use o campo **"Pesquisar música..."** (já com foco automático) para encontrar músicas
2. Clique na música desejada na lista de disponíveis
3. A música será automaticamente adicionada ao final do repertório

#### Gerenciar Ordem
- **↑ (Seta para cima)**: Move a música para cima
- **↓ (Seta para baixo)**: Move a música para baixo
- **🗑️ (Lixeira)**: Remove a música do repertório

### 📄 Exportar PDF

#### Gerar PDF do Repertório
1. No repertório do show, clique em **"Exportar PDF"**
2. Escolha o local para salvar o arquivo
3. O PDF será gerado automaticamente e aberto no visualizador padrão

#### Características do PDF
- **Formato**: A4 paisagem
- **Layout**: Otimizado para leitura em palco
- **Cores**:
  - ➔ Seta vermelha
  - Nome da música em preto
  - Tom da música em marrom
  - Cifra destacada em amarelo
  - Seta para direita servindo para indicar a passagem de uma parte para a outra (exemplo: fim da parte A `→` inicio da parte B)
  - Texto entre colchetes em azul sem destaque em amarelo, servindo para inserir dicas ou qualquer observação.
  <img width="1155" height="117" alt="image" src="https://github.com/user-attachments/assets/80e23542-a316-4c6d-8b00-f88b0eb1dd17" />


## 🗃️ Estrutura do Banco de Dados

### Tabela `musicas`
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INTEGER PRIMARY KEY | Identificador único |
| musica | TEXT NOT NULL | Nome da música |
| autor | TEXT | Compositor/Intérprete |
| estilo | TEXT | Estilo musical |
| tom | TEXT | Tom da música |
| cifra | TEXT | Acordes e anotações |

### Tabela `shows`
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INTEGER PRIMARY KEY | Identificador único |
| data_show | TEXT NOT NULL | Data do show (DD/MM/AAAA) |
| local_show | TEXT NOT NULL | Local do show |
| artista | TEXT NOT NULL | Nome do artista/banda |

### Tabela `repertorios_shows`
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INTEGER PRIMARY KEY | Identificador único |
| id_show | INTEGER NOT NULL | Referência ao show |
| id_musica | INTEGER NOT NULL | Referência à música |
| sequencia | INTEGER NOT NULL | Ordem no repertório |

## 🎵 Formatação de Cifras

### Destaque com Colchetes
Use colchetes `[ ]` para destacar texto na cifra:

**Exemplo:**
Am7 - D [inicio pizzicato] G - C [fim pizzicato]  Am7 - D --  G - C - D


**Resultado no PDF:**
- `Am7 - D` → Fundo amarelo, negrito
- `[inicio pizzicato]` → **Azul**, fundo cinza, sem negrito
- `G - C` → Fundo amarelo, negrito
- `[fim pizzicato]` → **Azul**, fundo cinza, sem negrito
- `Am7 - D -- G - C - D` → Fundo amarelo, negrito
- `--` → Substituído automaticamente por `→` (seta)

### Símbolos Especiais
- `--` → automaticamente convertido para `→` (seta para direita)
- Use para indicar transições entre partes da música

**Exemplo recomendado:**
G - A - G - D - (Em) → D - A/C# (a seta para direita indica, por exemplo, o limite entre parte A e parte B)  


## 💾 Backup e Restauração

### Exportar Backup
1. Acesse a aba **"Configurações"**
2. Clique em **"Exportar Banco de Dados"**
3. Escolha o local para salvar o arquivo de backup
4. O backup será salvo como `backup-app-repertorio-dd-mm-aaaa.txt`

### Importar Backup
1. Acesse a aba **"Configurações"**
2. Clique em **"Importar Banco de Dados"**
3. Selecione o arquivo de backup anteriormente exportado (Um exemplo de base de dados a ser importada: https://github.com/jcgomes/repertorio/blob/main/backup-app-repertorio-24-10-2025.txt)
4. Os dados serão sincronizados inteligentemente com o banco atual

### Estatísticas em Tempo Real
- **Total de Músicas**: Atualizado automaticamente ao adicionar/remover músicas
- **Total de Shows**: Atualizado automaticamente ao adicionar/remover shows

## ⌨️ Atalhos e Dicas

### Dicas de Uso
1. **Tom automático**: Ao digitar o tom, ele é automaticamente formatado entre parênteses
2. **Foco automático**: Ao acessar um repertório, o campo de pesquisa já está com foco
3. **Verificação de duplicatas**: O sistema impede cadastro de músicas com mesmo nome e autor
4. **Estatísticas atualizadas**: Os totais são atualizados automaticamente em todas as operações

### Boas Práticas
1. **Padronização de nomes**: Mantenha consistência nos nomes das músicas
2. **Tom padrão**: Sempre informe o tom para facilitar transposições
3. **Cifras detalhadas**: Use colchetes para anotações específicas
4. **Backup regular**: Exporte backups periódicamente para segurança dos dados

## 🛠️ Tecnologias

- **Python 3**: Linguagem principal
- **Flet**: Framework para interface gráfica
- **SQLite**: Banco de dados embutido
- **xhtml2pdf**: Geração de PDFs
- **HTML/CSS**: Formatação de PDFs

## 📞 Suporte

Em caso de problemas ou dúvidas:
1. Verifique se todas as dependências estão instaladas
2. Confirme que o Python está na versão 3.8 ou superior
3. Consulte as [Issues do GitHub](https://github.com/jcgomes/repertorio/issues)

## 👨‍💻 Desenvolvido por

**Juliano Da Cunha Gomes**  
- GitHub: [@jcgomes](https://github.com/jcgomes)
- Repositório: [https://github.com/jcgomes/repertorio](https://github.com/jcgomes/repertorio)

---

**© 2024 - Todos os direitos reservados**
