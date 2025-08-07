# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
# CONSULTA DE PRAZOS WEB - VERSÃO STREAMLIT
# -----------------------------------------------------------------------------
# Desenvolvido por: Hugo Sabença (via assistente de IA)
# Descrição: Uma interface web simples para consultar prazos de produção
#            a partir da planilha de pedidos, sem a necessidade do bot.
# -----------------------------------------------------------------------------

import streamlit as st
import pandas as pd
from datetime import datetime

# --- LÓGICA DE BUSCA DE PRAZO ---
# Função adaptada do bot original para ser robusta e autônoma.
def buscar_prazo_streamlit(numero_pedido, caminho_planilha):
    """
    Busca o prazo de um pedido em uma planilha Excel e retorna uma string formatada
    para exibição no Streamlit.
    """
    # Lista de abas a serem pesquisadas na planilha.
    # Se novas máquinas/processos forem adicionados, basta atualizar esta lista.
    abas_maquinas = [
        "Fagor",
        "Esquadros",
        "Marafon",
        "Divimec (Slitter)",
        "Divimec (Rebaixamento)"
    ]
    
    respostas_encontradas = []
    # Remove zeros à esquerda e garante que o número do pedido seja uma string para comparação
    num_pedido_normalizado = str(numero_pedido).strip().lstrip("0")

    try:
        # Itera sobre cada aba (representando uma máquina/processo)
        for aba in abas_maquinas:
            # Lê a aba específica da planilha
            df = pd.read_excel(caminho_planilha, sheet_name=aba)
            
            # Condição 1: Busca na coluna "Número do Pedido"
            # Converte a coluna para texto para garantir uma comparação correta, tratando erros
            coluna_pedido_principal = pd.to_numeric(df["Número do Pedido"], errors="coerce").fillna(0).astype(int).astype(str)
            condicao_principal = (coluna_pedido_principal == num_pedido_normalizado)

            # Condição 2: Busca na coluna "Número do Pedido SF", se ela existir
            if "Número do Pedido SF" in df.columns:
                coluna_pedido_sf = pd.to_numeric(df["Número do Pedido SF"], errors="coerce").fillna(0).astype(int).astype(str)
                # A condição final é: pedido encontrado em uma OU outra coluna
                condicao_final = condicao_principal | (coluna_pedido_sf == num_pedido_normalizado)
            else:
                condicao_final = condicao_principal

            # Filtra o DataFrame para encontrar as linhas que correspondem ao pedido
            resultados = df.loc[condicao_final]

            # Se encontrou algum resultado, formata a mensagem
            if not resultados.empty:
                for index, linha in resultados.iterrows():
                    produto = str(linha.get("Produto", "N/A")).strip()
                    quantidade = float(linha.get("Quantidade", 0))
                    quantidade_str = f"{quantidade:.3f}".replace(".", ",")
                    prazo_valor = linha.get("Prazo")

                    # Tenta formatar a data. Se não for uma data válida, mostra como texto.
                    try:
                        prazo_formatado = pd.to_datetime(prazo_valor).strftime("%d/%m/%Y")
                    except (ValueError, TypeError):
                        prazo_formatado = str(prazo_valor)

                    texto_formatado = (
                        f"**Máquina/Processo:** {aba}\n\n"
                        f"**Produto:** {produto} – {quantidade_str} tons\n\n"
                        f"**Previsão de Produção:** {prazo_formatado}"
                    )
                    respostas_encontradas.append(texto_formatado)
        
        # --- Monta a Resposta Final para o Usuário ---
        if not respostas_encontradas:
            return (f"❌ **Pedido `{numero_pedido}` não encontrado.**\n\nVerifique o número digitado ou se o pedido já foi programado.")
        
        if len(respostas_encontradas) == 1:
            return f"#### ➡️ Pedido `{str(numero_pedido).strip()}`\n\n---\n\n{respostas_encontradas[0]}"
        
        # Se o pedido tem múltiplos itens em máquinas diferentes
        cabecalho = f"#### ➡️ O pedido `{str(numero_pedido).strip()}` possui múltiplos itens:\n\n---\n\n"
        return cabecalho + "\n\n---\n\n".join(respostas_encontradas)

    except FileNotFoundError:
        return f"❌ **ERRO CRÍTICO:**\n\nA planilha de pedidos (`{caminho_planilha}`) não foi encontrada. Certifique-se de que o arquivo está na mesma pasta que o script."
    except Exception as e:
        st.error(f"Ocorreu um erro técnico inesperado ao ler a planilha: {e}")
        return "❌ **ERRO AO PROCESSAR:**\n\nNão foi possível ler a planilha. Verifique se alguma aba está com o nome errado ou se o arquivo não está corrompido."


# --- INTERFACE GRÁFICA DA APLICAÇÃO COM STREAMLIT ---

# Configurações da página (título na aba do navegador, ícone e layout)
st.set_page_config(page_title="Consulta de Prazos", page_icon="⏳", layout="centered")

# Título principal da página
st.title("Consulta de Prazos de Produção ⏳")

# Caixa de informação para o usuário
st.info("Digite o número do pedido e clique em 'Buscar Prazo' para ver a previsão de produção.")

# CAMINHO DO ARQUIVO DE DADOS
# O arquivo 'pedidos.xlsx' DEVE estar na mesma pasta que este script.
CAMINHO_PLANILHA_PEDIDOS = "pedidos.xlsx"

# Campo de texto para o usuário inserir o número do pedido
numero_pedido_input = st.text_input(
    "Número do Pedido:", 
    placeholder="Digite o número aqui...",
    help="Insira o número do pedido de venda ou da solicitação de faturamento."
)

# Botão para iniciar a busca
if st.button("Buscar Prazo", type="primary"):
    if numero_pedido_input:
        # Mostra uma mensagem de "carregando" enquanto a busca é feita
        with st.spinner("Buscando informações na planilha... Por favor, aguarde."):
            resultado = buscar_prazo_streamlit(numero_pedido_input, CAMINHO_PLANILHA_PEDIDOS)
            # st.markdown() é usado para renderizar o texto com formatação (negrito, etc.)
            st.markdown(resultado)
    else:
        # Alerta para o caso do usuário clicar no botão sem digitar nada
        st.warning("Por favor, digite um número de pedido antes de buscar.", icon="⚠️")