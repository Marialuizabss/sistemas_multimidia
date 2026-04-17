import streamlit as st
from PIL import Image
import io
import datetime

# ───────────────────────────────────────────────
#  ALGORITMO LSB
# ───────────────────────────────────────────────

DELIMITADOR = '\u0003'  # caractere ETX — marca o fim da mensagem

def texto_para_bits(texto):
    """Converte texto em lista de bits (0s e 1s)"""
    bytes_texto = texto.encode('utf-8')
    bits = []
    for byte in bytes_texto:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits

def bits_para_texto(bits):
    """Converte lista de bits de volta para texto"""
    bytes_lista = []
    for i in range(0, len(bits) - 7, 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | bits[i + j]
        bytes_lista.append(byte)
    return bytes(bytes_lista).decode('utf-8', errors='ignore')

def capacidade_maxima(imagem):
    largura, altura = imagem.size
    return (largura * altura * 3) // 8 - 10

def ts():
    return datetime.datetime.now().strftime('%H:%M:%S.%f')[:12]

def esconder_mensagem(imagem, mensagem):
    """
    Esconde uma mensagem numa imagem usando LSB.
    Retorna (imagem_nova, log_lines)
    """
    log = []

    def L(tipo, msg):
        log.append((ts(), tipo, msg))

    largura, altura = imagem.size
    imagem_rgb = imagem.convert('RGB')

    L('INIT',   f'Imagem carregada: {largura}×{altura} px — {largura*altura:,} pixels no total')
    cap = capacidade_maxima(imagem_rgb)
    L('INIT',   f'Capacidade máxima da imagem: {cap} caracteres (3 bits por pixel × {largura*altura:,})')

    if len(mensagem) > cap:
        L('ERRO', f'Mensagem muito longa! Máximo: {cap} chars, você digitou: {len(mensagem)}')
        return None, log

    mensagem_completa = mensagem + DELIMITADOR
    L('MSG',    f'Mensagem: "{mensagem[:50]}{"..." if len(mensagem)>50 else ""}" ({len(mensagem)} chars)')
    L('MSG',    f'Adicionando delimitador ETX (\\u0003) ao final — indica onde a mensagem termina')

    bits = texto_para_bits(mensagem_completa)
    L('ENCODE', f'Convertendo para bits: {len(bits)} bits no total ({len(mensagem_completa)} bytes × 8)')

    for i, char in enumerate(mensagem[:3]):
        codigo = ord(char)
        binario = format(codigo, '08b')
        L('BIT',  f'Char "{char}" → código ASCII {codigo} → binário {binario}')
    if len(mensagem) > 3:
        L('BIT',  f'... ({len(mensagem)-3} caracteres restantes convertidos silenciosamente)')

    L('LSB',    'Iniciando gravação LSB nos canais R, G, B de cada pixel')
    L('LSB',    'Canal Alpha (transparência) é IGNORADO — alterá-lo seria perceptível visualmente')

    pixels = list(imagem_rgb.getdata())
    novos_pixels = []
    indice_bit = 0

    for idx, pixel in enumerate(pixels):
        r, g, b = pixel
        novo_r, novo_g, novo_b = r, g, b

        if indice_bit < len(bits):
            novo_r = (r & 0xFE) | bits[indice_bit]
            if idx < 3:
                L('LSB', f'Pixel {idx} canal R: {format(r,"08b")} → {format(novo_r,"08b")} '
                         f'{"← bit alterado" if r != novo_r else "(sem mudança)"}')
            indice_bit += 1

        if indice_bit < len(bits):
            novo_g = (g & 0xFE) | bits[indice_bit]
            if idx < 3:
                L('LSB', f'Pixel {idx} canal G: {format(g,"08b")} → {format(novo_g,"08b")} '
                         f'{"← bit alterado" if g != novo_g else "(sem mudança)"}')
            indice_bit += 1

        if indice_bit < len(bits):
            novo_b = (b & 0xFE) | bits[indice_bit]
            if idx < 3:
                L('LSB', f'Pixel {idx} canal B: {format(b,"08b")} → {format(novo_b,"08b")} '
                         f'{"← bit alterado" if b != novo_b else "(sem mudança)"}')
            indice_bit += 1

        novos_pixels.append((novo_r, novo_g, novo_b))

    if len(pixels) > 3:
        L('LSB', f'... (pixels 3 a {len(pixels):,} processados)')

    imagem_nova = Image.new('RGB', imagem_rgb.size)
    imagem_nova.putdata(novos_pixels)

    bits_usados   = indice_bit
    pixels_alt    = (bits_usados + 2) // 3
    cap_usada     = bits_usados / (largura * altura * 3) * 100

    L('ENCODE', f'Gravação concluída: {bits_usados} bits escritos em {pixels_alt:,} pixels')
    L('STATS',  f'Capacidade usada: {cap_usada:.1f}% | Pixels modificados: {pixels_alt:,} | Diferença visual: imperceptível')
    L('OUTPUT', 'Imagem pronta para exportar como PNG (formato lossless — bits LSB preservados)')

    return imagem_nova, log

def revelar_mensagem(imagem):
    """
    Extrai a mensagem oculta de uma imagem.
    Retorna (mensagem | None, log_lines)
    """
    log = []

    def L(tipo, msg):
        log.append((ts(), tipo, msg))

    imagem_rgb = imagem.convert('RGB')
    largura, altura = imagem_rgb.size

    L('INIT',   f'Imagem carregada: {largura}×{altura} px')
    L('LSB',    'Lendo bit menos significativo (LSB) de cada canal RGB, pixel por pixel...')

    pixels    = list(imagem_rgb.getdata())
    bits      = []
    bits_lidos = 0
    canais    = ['R', 'G', 'B']

    for idx, pixel in enumerate(pixels):
        r, g, b = pixel
        for ch_nome, val in zip(canais, [r, g, b]):
            lsb = val & 1
            if idx < 3:
                L('LSB', f'Pixel {idx} canal {ch_nome}: {format(val,"08b")} → LSB = {lsb}')
            bits.append(lsb)
            bits_lidos += 1

            if len(bits) % 8 == 0 and len(bits) >= 8:
                ultimo_char = bits_para_texto(bits[-8:])
                if ultimo_char == DELIMITADOR:
                    mensagem = bits_para_texto(bits[:-8])
                    L('DECODE', f'Delimitador ETX encontrado após {bits_lidos} bits lidos')
                    for i, char in enumerate(mensagem[:3]):
                        codigo = ord(char)
                        binario = format(codigo, '08b')
                        L('BIT', f'Byte {binario} → código {codigo} → char "{char}"')
                    if len(mensagem) > 3:
                        L('BIT', f'... ({len(mensagem)-3} chars restantes decodificados)')
                    L('OUTPUT', f'Mensagem recuperada com sucesso: {len(mensagem)} caracteres')
                    return mensagem, log

        if bits_lidos > 80000:
            break

    L('WARN', 'Nenhum delimitador ETX encontrado — imagem sem mensagem oculta ou arquivo corrompido')
    return None, log

def imagem_para_bytes(imagem):
    buf = io.BytesIO()
    imagem.save(buf, format='PNG')
    return buf.getvalue()

def renderizar_log(linhas):
    """Renderiza o log com cores usando markdown do Streamlit"""
    cores = {
        'INIT':   '#4a9eff',
        'MSG':    '#4a9eff',
        'ENCODE': '#4a9eff',
        'DECODE': '#4a9eff',
        'LSB':    '#888888',
        'BIT':    '#aaaaaa',
        'STATS':  '#2ecc71',
        'OUTPUT': '#2ecc71',
        'ERRO':   '#e74c3c',
        'WARN':   '#e67e22',
    }
    linhas_md = []
    for hora, tipo, msg in linhas:
        cor = cores.get(tipo, '#cccccc')
        linhas_md.append(
            f"`{hora}`  "
            f'<span style="color:{cor};font-weight:600">[{tipo:<7}]</span>  '
            f'<span style="color:#dddddd">{msg}</span>'
        )
    bloco = '\n\n'.join(linhas_md)
    st.markdown(
        f"""
        <div style="
            background:#1a1a1a;
            border-radius:8px;
            padding:14px 16px;
            font-family:monospace;
            font-size:12px;
            line-height:1.9;
            max-height:340px;
            overflow-y:auto;
        ">{bloco}</div>
        """,
        unsafe_allow_html=True,
    )

# ───────────────────────────────────────────────
#  INTERFACE STREAMLIT
# ───────────────────────────────────────────────

st.set_page_config(
    page_title='Esteganografia LSB',
    page_icon='🔐',
    layout='centered',
)

st.title('🔐 Esteganografia LSB')
st.caption('Esconda mensagens secretas dentro de imagens manipulando o bit menos significativo (LSB) de cada pixel.')

aba_esconder, aba_revelar = st.tabs(['Esconder mensagem', 'Revelar mensagem'])

# ── ABA ESCONDER ──────────────────────────────
with aba_esconder:
    st.subheader('1. Imagem de cobertura')
    arquivo = st.file_uploader(
        'Escolha uma imagem (PNG recomendado)',
        type=['png', 'bmp', 'tiff', 'jpg', 'jpeg'],
        key='enc_upload'
    )
    if arquivo:
        st.caption('⚠️ JPEG não recomendado — a compressão pode destruir os bits LSB')

    st.subheader('2. Mensagem secreta')
    mensagem = st.text_area('Digite a mensagem que deseja ocultar', height=100, key='enc_msg')

    if arquivo and mensagem:
        imagem = Image.open(arquivo)
        cap = capacidade_maxima(imagem.convert('RGB'))
        pct = min(100, int(len(mensagem) / cap * 100))
        st.caption(f'Capacidade usada: {len(mensagem)} / {cap} caracteres ({pct}%)')
        st.progress(pct)

    if st.button('▶ Executar algoritmo', type='primary', key='enc_btn'):
        if not arquivo:
            st.warning('Escolha uma imagem primeiro.')
        elif not mensagem:
            st.warning('Digite uma mensagem secreta.')
        else:
            imagem = Image.open(arquivo)

            with st.spinner('Processando...'):
                imagem_resultado, log = esconder_mensagem(imagem, mensagem)

            st.subheader('Log do processo')
            renderizar_log(log)

            if imagem_resultado:
                st.subheader('Resultado')
                col1, col2 = st.columns(2)
                with col1:
                    st.image(imagem, caption='Original', use_container_width=True)
                with col2:
                    st.image(imagem_resultado, caption='Com mensagem oculta', use_container_width=True)

                largura, altura = imagem_resultado.size
                bits_usados = len(texto_para_bits(mensagem + DELIMITADOR))
                col_a, col_b, col_c = st.columns(3)
                col_a.metric('Caracteres ocultos', len(mensagem))
                col_b.metric('Bits gravados', bits_usados)
                col_c.metric('Pixels alterados', f'{(bits_usados+2)//3:,}')

                st.download_button(
                    label='⬇ Baixar imagem com mensagem oculta',
                    data=imagem_para_bytes(imagem_resultado),
                    file_name='imagem_oculta.png',
                    mime='image/png',
                )

# ── ABA REVELAR ───────────────────────────────
with aba_revelar:
    st.subheader('Imagem com mensagem oculta')
    arquivo_dec = st.file_uploader(
        'Escolha a imagem gerada por esta ferramenta',
        type=['png', 'bmp', 'tiff'],
        key='dec_upload'
    )

    if st.button('▶ Extrair mensagem', type='primary', key='dec_btn'):
        if not arquivo_dec:
            st.warning('Escolha uma imagem primeiro.')
        else:
            imagem_dec = Image.open(arquivo_dec)

            with st.spinner('Analisando pixels...'):
                mensagem_revelada, log_dec = revelar_mensagem(imagem_dec)

            st.subheader('Log do processo')
            renderizar_log(log_dec)

            st.subheader('Mensagem revelada')
            if mensagem_revelada:
                st.success('Mensagem encontrada com sucesso!')
                st.code(mensagem_revelada, language=None)
            else:
                st.error('Nenhuma mensagem encontrada nesta imagem.')
