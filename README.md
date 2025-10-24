# 🎵 Gerenciador de Repertório Musical

Um aplicativo desktop desenvolvido em Python com Flet para gerenciar repertórios musicais, shows e exportar PDFs profissionais.

## 📋 Índice

- [Funcionalidades](#Funcionalidades)
- [Instalação](#instalação)
- [Como Usar](#como-usar)
  - [Gerenciar Músicas](#gerenciar-músicas)
  - [Gerenciar Shows](#gerenciar-shows)
  - [Criar Repertórios](#criar-repertórios)
  - [Exportar PDF](#exportar-pdf)
- [Estrutura do Banco de Dados](#estrutura-do-banco-de-dados)
- [Formatação de Cifras](#formatação-de-cifras)
- [Atalhos e Dicas](#atalhos-e-dicas)
- [Tecnologias](#tecnologias)

##Funcionalidades 🚀

### 🎼 Gestão de Músicas
- ✅ Cadastro completo de músicas (nome, autor, estilo, tom, cifra)
- ✅ Pesquisa em tempo real por nome, autor ou estilo
- ✅ Ordenação automática por ID
- ✅ Verificação de duplicatas
- ✅ Formatação automática do tom entre parênteses

### 🎪 Gestão de Shows
- ✅ Cadastro de shows com data, local e artista
- ✅ Visualização em ordem cronológica
- ✅ Criação de repertórios personalizados

### 📋 Criação de Repertórios
- ✅ Adição de músicas ao repertório com arrastar e soltar
- ✅ Reordenação com setas (↑↓)
- ✅ Pesquisa de músicas disponíveis
- ✅ Sequenciamento automático

### 📄 Exportação para PDF
- ✅ Layout profissional em A4 paisagem
- ✅ Destaque automático de texto entre colchetes em azul
- ✅ Preservação de espaços múltiplos entre acordes
- ✅ Tamanho de fonte adaptável ao conteúdo
- ✅ Fundo amarelo para cifras

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
1. Use o campo **"Pesquisar música..."** para encontrar músicas
2. Clique na música desejada na lista de disponíveis
3. A música será automaticamente adicionada ao final do repertório

#### Gerenciar Ordem
- **↑ (Seta para cima)**: Move a música para cima
- **↓ (Seta para baixo)**: Move a música para baixo
- **🗑️ (Lixeira)**: Remove a música do repertório

### 📄 Exportar PDF

#### Gerar PDF do Repertório
1. No repertório do show, clique em **"Exportar PDF"**
2. O PDF será gerado automaticamente e aberto no visualizador padrão

#### Características do PDF
- **Formato**: A4 paisagem
- **Layout**: Otimizado para leitura em palco
- **Cores**:
  - ➔ Seta vermelha
  - Nome da música em preto
  - Tom da musica em marrom
  - Cifra destacada em amarelo
  - Texto entre colchetes em azul sem destaque em amarelo. Funcinoa como lembretes, por exemplo:
    <img width="1350" height="199" alt="image" src="https://github.com/user-attachments/assets/895486b9-dea6-4fb6-b527-b0ccfb61b6e4" />

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
- `Am7 - D --  G - C - D` → Fundo amarelo, negrito
- `--` → indica o limite entre partes, exemplo: fim da parte A -- inicio da parte B
<img width="1356" height="143" alt="image" src="https://github.com/user-attachments/assets/2a8a845b-d164-4aa4-b0e2-83ecf95730b2" />

### Preservação de Espaços
- Múltiplos espaços não são preservados
- Use um traço entre os acordes para melhor organização visual da cifra

**Exemplo recomendado:**
G - A - G - D - (Em) -- D - A/C# (os dois traços indica, por exemplo, o limite entre parte A e parte B)  


## ⌨️ Atalhos e Dicas

### Dicas de Uso
1. **Tom automático**: Ao digitar o tom, ele é automaticamente formatado entre parênteses
2. **Limpeza de pesquisa**: O campo de pesquisa é limpo automaticamente ao adicionar nova música
3. **Verificação de duplicatas**: O sistema impede cadastro de músicas com mesmo nome e autor
4. **Ordenação**: Músicas são sempre ordenadas por ID para consistência

### Boas Práticas
1. **Padronização de nomes**: Mantenha consistência nos nomes das músicas
2. **Tom padrão**: Sempre informe o tom para facilitar transposições
3. **Cifras detalhadas**: Use colchetes para anotações específicas
4. **Espaçamento**: Use o formato ACORDE ESPAÇO TRAÇO ESPAÇO ACORDE para melhor legibilidade da cifra, exemplo: Dm - Am - E

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
