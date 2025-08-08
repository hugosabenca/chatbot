# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
from datetime import datetime

# -----------------------------------------------------------------------------
# <<< INTERRUPTOR PRINCIPAL DO APLICATIVO >>>
# Altere para False para desativar o site e mostrar uma mensagem de manutenção.
# Altere para True para o site funcionar normalmente.
# -----------------------------------------------------------------------------
APP_ATIVO = True

# --- INÍCIO DA INTERFACE ---
st.set_page_config(page_title="Consulta de Prazos", page_icon="⏳", layout="centered")
st.title("Consulta de Prazos de Produção ⏳")

# --- LÓGICA DE ATIVAÇÃO ---
if APP_ATIVO:
    # Se o app estiver ATIVO, define a função e mostra a interface de consulta.
    
    def buscar_prazo_streamlit(numero_pedido, caminho_planilha):
        """
        Busca o prazo de um pedido em uma planilha Excel e retorna uma string formatada.
        """
        abas_maquinas = [
            "Fagor", "Esquadros", "Marafon",
            "Divimec (Slitter)", "Divimec (Rebaixamento)"
        ]
        respostas_encontradas = []
        num_pedido_normalizado = str(numero_pedido).strip().lstrip("0")

        try:
            for aba in abas_maquinas:
                df = pd.read_excel(caminho_planilha, sheet_name=aba, engine='openpyxl')
                
                coluna_pedido_principal = pd.to_numeric(df["Número do Pedido"], errors="coerce").fillna(0).astype(int).astype(str)
                condicao_principal = (coluna_pedido_principal == num_pedido_normalizado)

                if "Número do Pedido SF" in df.columns:
                    coluna_pedido_sf = pd.to_numeric(df["Número do Pedido SF"], errors="coerce").fillna(0).astype(int).astype(str)
                    condicao_final = condicao_principal | (coluna_pedido_sf == num_pedido_normalizado)
                else:
                    condicao_final = condicao_principal

                resultados = df.loc[condicao_final]

                if not resultados.empty:
                    for index, linha in resultados.iterrows():
                        produto = str(linha.get("Produto", "N/A")).strip()
                        quantidade = float(linha.get("Quantidade", 0))
                        quantidade_str = f"{quantidade:.3f}".replace(".", ",")
                        prazo_valor = linha.get("Prazo")

                        # Lógica de data corrigida para incluir a verificação do dia atual
                        try:
                            data_do_prazo = pd.to_datetime(prazo_valor).date()
                            hoje = datetime.now().date()
                            if data_do_prazo == hoje:
                                prazo_formatado = "entre hoje e o próximo dia útil"
                            else:
                                prazo_formatado = data_do_prazo.strftime("%d/%m/%Y")
                        except (ValueError, TypeError):
                            prazo_formatado = str(prazo_valor)

                        texto_formatado = (
                            f"**Máquina/Processo:** {aba}\n\n"
                            f"**Produto:** {produto} – {quantidade_str} tons\n\n"
                            f"**Previsão de Produção:** {prazo_formatado}"
                        )
                        respostas_encontradas.append(texto_formatado)
            
            if not respostas_encontradas:
                return (f"❌ **Pedido `{numero_pedido}` não encontrado.**\n\nTalvez já tenha sido produzido ou ainda não programei. Qualquer coisa me envie um e-mail que verifico pra você.")
            
            if len(respostas_encontradas) == 1:
                return f"#### ➡️ Pedido `{str(numero_pedido).strip()}`\n\n---\n\n{respostas_encontradas[0]}"
            
            cabecalho = f"#### ➡️ O pedido `{str(numero_pedido).strip()}` possui múltiplos itens:\n\n---\n\n"
            return cabecalho + "\n\n---\n\n".join(respostas_encontradas)

        except FileNotFoundError:
            return f"❌ **ERRO CRÍTICO:**\n\nA planilha de pedidos (`{caminho_planilha}`) não foi encontrada. Certifique-se de que o arquivo foi enviado para o GitHub junto com o script."
        except Exception as e:
            st.error(f"Ocorreu um erro técnico inesperado ao ler a planilha: {e}")
            return "❌ **ERRO AO PROCESSAR:**\n\nNão foi possível ler a planilha. Verifique se alguma aba está com o nome errado ou se o arquivo não está corrompido."

    # ----- Interface de consulta (continuação do if APP_ATIVO) -----
    st.info("Digite o número do pedido e clique em 'Buscar Prazo' para ver a previsão de produção.")
    
    CAMINHO_PLANILHA_PEDIDOS = "pedidos.xlsx"
    
    numero_pedido_input = st.text_input(
        "Número do Pedido:", 
        placeholder="Digite o número aqui...",
        help="Insira o número do pedido de venda ou da solicitação de faturamento."
    )

    if st.button("Buscar Prazo", type="primary"):
        if numero_pedido_input:
            with st.spinner("Buscando informações na planilha... Por favor, aguarde."):
                resultado = buscar_prazo_streamlit(numero_pedido_input, CAMINHO_PLANILHA_PEDIDOS)
                st.markdown(resultado)
        else:
            st.warning("Por favor, digite um número de pedido antes de buscar.", icon="⚠️")

else:
    # Se o app estiver DESATIVADO (APP_ATIVO = False), mostra apenas uma mensagem de aviso.
    st.warning(
        "**Site temporariamente em manutenção.**\n\n"
        "A consulta de prazos está desativada no momento. Por favor, tente novamente mais tarde.",
        icon="🛠️"
    )