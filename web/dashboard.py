"""
🚀 Sistema Distribuido de Cripto-Inversiones
Dashboard con patrón CQRS y PostgreSQL Master-Slave Replication
"""
import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ============================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================
st.set_page_config(
    page_title="Sistema Distribuido Crypto",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# CONFIGURACIÓN DE LA API
# ============================================
API_BASE_URL = "http://localhost:8000"

# ============================================
# ESTILOS CSS PERSONALIZADOS
# ============================================
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(120deg, #1f77b4, #17a2b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .architecture-badge {
        text-align: center;
        font-size: 1.2rem;
        color: #28a745;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1.5rem;
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-left: 5px solid #28a745;
        border-radius: 10px;
        color: #155724;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .node-badge-write {
        display: inline-block;
        padding: 0.8rem 1.5rem;
        background: linear-gradient(135deg, #dc3545, #c82333);
        color: white;
        border-radius: 8px;
        font-weight: bold;
        font-size: 0.95rem;
        margin: 1rem 0;
        box-shadow: 0 3px 5px rgba(220,53,69,0.3);
    }
    .node-badge-read {
        display: inline-block;
        padding: 0.8rem 1.5rem;
        background: linear-gradient(135deg, #17a2b8, #138496);
        color: white;
        border-radius: 8px;
        font-weight: bold;
        font-size: 0.95rem;
        margin: 1rem 0;
        box-shadow: 0 3px 5px rgba(23,162,184,0.3);
    }
    .stButton>button {
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# CABECERA INFORMATIVA
# ============================================
st.markdown('<h1 class="main-header">🚀 Sistema Distribuido de Cripto-Inversiones</h1>', unsafe_allow_html=True)
st.markdown('<div class="architecture-badge">⚙️ Arquitectura: Master-Slave Replication</div>', unsafe_allow_html=True)
st.markdown("---")

# ============================================
# CONTENIDO PRINCIPAL - DOS COLUMNAS
# ============================================
col1, col2 = st.columns([1, 1])

# ============================================
# PANEL IZQUIERDO - SIMULACIÓN DE ESCRITURA
# ============================================
with col1:
    st.markdown("### ✍️ Simulación de Escritura")
    st.markdown('<div class="node-badge-write">🎯 TARGET: NODO MAESTRO (172.20.0.10)</div>', unsafe_allow_html=True)
    
    with st.form("investment_form", clear_on_submit=True):
        st.markdown("#### 💰 Registrar Inversión")
        
        # Lista de criptomonedas populares
        crypto_options = [
            "bitcoin",
            "ethereum",
            "binancecoin",
            "cardano",
            "solana",
            "ripple",
            "dogecoin",
            "polkadot",
            "avalanche-2",
            "chainlink",
            "matic-network",
            "litecoin",
            "shiba-inu",
            "tron",
            "uniswap"
        ]
        
        # Select input
        coin_name = st.selectbox(
            "Selecciona la Criptomoneda",
            options=crypto_options,
            index=0,  # Bitcoin por defecto
            format_func=lambda x: x.upper().replace("-", " ")
        )
        
        amount = st.number_input(
            "Cantidad",
            min_value=0.0001,
            value=1.5,
            step=0.1,
            format="%.4f"
        )
        
        # Submit button
        submit_button = st.form_submit_button("🚀 Registrar Inversión", use_container_width=True, type="primary")
        
        if submit_button:
            with st.spinner("📤 Enviando a NODO MAESTRO..."):
                try:
                    # POST request to API
                    response = requests.post(
                        f"{API_BASE_URL}/invest",
                        json={"coin": coin_name, "amount": amount},
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Success message - VERDE LLAMATIVO
                        st.markdown(
                            f"""
                            <div class="success-box">
                                <h3 style="margin:0; font-size:1.5rem;">✅ Datos escritos en NODO MAESTRO (172.20.0.10)</h3>
                                <p style="margin:0.5rem 0; font-size:1.1rem;"><strong>Inversión registrada exitosamente</strong></p>
                                <hr style="margin:1rem 0;">
                                <p><strong>🪙 Moneda:</strong> {data['investment']['coin'].upper()}</p>
                                <p><strong>📊 Cantidad:</strong> {data['investment']['amount']}</p>
                                <p><strong>💵 Precio:</strong> ${data['investment']['price_per_coin_usd']:,.2f} USD</p>
                                <p><strong>💰 Total:</strong> ${data['investment']['total_value_usd']:,.2f} USD</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                        # Auto-refresh después de 2 segundos
                        import time
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {response.json().get('detail', 'Error desconocido')}")
                
                except requests.exceptions.ConnectionError:
                    st.error("❌ **No se puede conectar a la API.** Verifica que FastAPI esté corriendo en http://localhost:8000")
                except Exception as e:
                    st.error(f"❌ Error inesperado: {str(e)}")

# ============================================
# PANEL DERECHO - LECTURA DE LA RÉPLICA
# ============================================
with col2:
    st.markdown("### 📖 Lectura de la Réplica")
    st.markdown('<div class="node-badge-read">� Leyendo datos del NODO RÉPLICA (172.20.0.11)</div>', unsafe_allow_html=True)
    
    # Botón para actualizar datos
    if st.button("🔄 Actualizar Datos", use_container_width=True, type="secondary"):
        st.rerun()
    
    st.markdown("#### 📋 Historial de Inversiones")
    
    try:
        # GET request to API (reads from Replica)
        response = requests.get(f"{API_BASE_URL}/history", timeout=5)
        
        if response.status_code == 200:
            history_data = response.json()
            
            if history_data:
                # Convert to DataFrame
                df = pd.DataFrame(history_data)
                
                # Format columns
                df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
                df['purchase_price_usd'] = df['purchase_price_usd'].apply(lambda x: f"${x:,.2f}")
                df['total_value_usd'] = df['total_value_usd'].apply(lambda x: f"${x:,.2f}")
                
                # Rename columns for display
                df_display = df.rename(columns={
                    'id': 'ID',
                    'coin_name': 'Moneda',
                    'amount': 'Cantidad',
                    'purchase_price_usd': 'Precio',
                    'total_value_usd': 'Total',
                    'timestamp': 'Fecha'
                })
                
                # Display table
                st.dataframe(
                    df_display,
                    use_container_width=True,
                    hide_index=True,
                    height=400
                )
                
                st.info(f"📊 Total de {len(history_data)} inversión(es) leída(s) desde RÉPLICA")
            else:
                st.warning("📭 No hay inversiones registradas todavía")
        else:
            st.error("❌ Error al obtener el historial")
    
    except requests.exceptions.ConnectionError:
        st.error("❌ **Error de conexión con la API**")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

# ============================================
# GRÁFICO DE EVOLUCIÓN
# ============================================
st.markdown("---")
st.markdown("## 📈 Evolución del Portafolio")

try:
    # Get history for chart
    response = requests.get(f"{API_BASE_URL}/history", timeout=5)
    
    if response.status_code == 200:
        history_data = response.json()
        
        if history_data and len(history_data) > 0:
            # Create DataFrame for chart
            df_chart = pd.DataFrame(history_data)
            df_chart['timestamp'] = pd.to_datetime(df_chart['timestamp'])
            df_chart = df_chart.sort_values('timestamp')
            
            # Calculate cumulative value
            df_chart['Valor Acumulado USD'] = df_chart['total_value_usd'].cumsum()
            
            # Create beautiful line chart
            chart_data = df_chart.set_index('timestamp')[['Valor Acumulado USD']]
            st.line_chart(
                data=chart_data,
                use_container_width=True,
                height=400
            )
            
            # Summary metrics
            col_met1, col_met2, col_met3 = st.columns(3)
            with col_met1:
                st.metric("💰 Total Invertido", f"${df_chart['Valor Acumulado USD'].iloc[-1]:,.2f}")
            with col_met2:
                st.metric("📊 Total Operaciones", len(history_data))
            with col_met3:
                unique_coins = df_chart['coin_name'].nunique()
                st.metric("🪙 Monedas Diferentes", unique_coins)
        else:
            st.info("📊 No hay suficientes datos para mostrar el gráfico. ¡Registra tu primera inversión!")
except Exception as e:
    st.warning("⚠️ No se pudo generar el gráfico de evolución")

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 1.5rem;'>
        <p style='font-size: 1.1rem;'><strong>🎓 Proyecto de Sistemas Distribuidos</strong></p>
        <p>PostgreSQL Master-Slave Replication | FastAPI CQRS Pattern | Streamlit Dashboard</p>
    </div>
    """,
    unsafe_allow_html=True
)
