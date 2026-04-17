# 🔐 Esteganografia LSB

Trabalho final da disciplina de **Sistemas Multimídia**.

Aplicação que esconde mensagens secretas dentro de imagens usando o algoritmo **LSB (Least Significant Bit)** — técnica que manipula o bit menos significativo de cada canal de cor (R, G, B) dos pixels, tornando a alteração imperceptível ao olho humano.

---

## 🧠 Como funciona

Cada pixel de uma imagem é formado por 3 canais de cor: **Vermelho (R), Verde (G) e Azul (B)**, cada um com um valor de 0 a 255. Em binário, o número 200 por exemplo é `11001000`.

O algoritmo altera apenas o **último bit** desse número — a diferença entre `11001000` (200) e `11001001` (201) é invisível visualmente, mas permite esconder informação bit a bit ao longo dos pixels da imagem.

A mensagem é convertida para bits e distribuída pelos pixels. Um caractere delimitador especial (`ETX`) é inserido ao final para marcar onde a mensagem termina na hora de revelar.

---

## 🚀 Como rodar (GitHub Codespaces)

A forma mais fácil — não precisa instalar nada no computador.

**1.** Acesse o repositório no GitHub

**2.** Clique no botão verde **Code** → aba **Codespaces** → **Create codespace on main**

**3.** Espere o ambiente carregar (cerca de 30 segundos)

**4.** No terminal que aparecer, rode:

```bash
pip install -r requirements.txt
python -m streamlit run esteganografia_streamlit.py
```

**5.** Um popup vai aparecer com **"Open in Browser"** — clique nele

A interface abre no navegador, pronta para usar!

---

## 💻 Como rodar localmente

Se preferir rodar no seu próprio computador:

**Pré-requisitos:** Python 3.8 ou superior instalado

```bash
# 1. Clone o repositório
git clone https://github.com/Marialuizabss/sistemas_multimidia.git
cd sistemas_multimidia

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Rode o app
python -m streamlit run esteganografia_streamlit.py
```

---

## 🖥️ Como usar

### Esconder uma mensagem

1. Abra a aba **"Esconder mensagem"**
2. Faça upload de uma imagem — PNG, BMP, TIFF ou JPEG
3. Se enviar um **JPEG**, a ferramenta converte automaticamente para PNG antes de processar (o log explica o motivo)
4. Digite a mensagem secreta no campo de texto
5. Clique em **"Executar algoritmo"**
6. Acompanhe o **log em tempo real** mostrando cada etapa do processo
7. Baixe a imagem gerada com a mensagem oculta (sempre salva em PNG)

### Revelar uma mensagem

1. Abra a aba **"Revelar mensagem"**
2. Faça upload da imagem com a mensagem oculta — PNG, BMP, TIFF ou JPEG
3. Clique em **"Extrair mensagem"**
4. A mensagem oculta aparece na tela

> ⚠️ **Atenção com JPEG:** o formato JPEG usa compressão com perda (*lossy*) — se você esconder uma mensagem, salvar como JPEG e tentar revelar, os bits LSB podem ter sido corrompidos. Sempre use o **PNG gerado pela ferramenta** para revelar.

---

## 📋 Dependências

| Biblioteca | Uso |
|---|---|
| `streamlit` | Interface web |
| `Pillow` | Manipulação de imagens |

---

## 📁 Estrutura do projeto

```
sistemas_multimidia/
├── esteganografia_streamlit.py   # código principal
├── requirements.txt              # dependências
└── README.md                     # este arquivo
```

---

## 🔗 Conceitos abordados

- Representação digital de imagens (RGB, pixels, bits)
- Algoritmo LSB (Least Significant Bit)
- Codificação de texto em UTF-8
- Formatos de imagem com e sem perda (lossless vs lossy)
- Processamento e manipulação de mídia digital
