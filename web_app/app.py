import streamlit as st
import pandas as pd
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# Add parent directory to path untuk import utils
sys.path.append(str(Path(__file__).parent.parent))

from config.config import APP_CONFIG
from web_app.utils.api_client import api_client

# ===============================================
# PAGE CONFIGURATION
# ===============================================
st.set_page_config(
    page_title="Smart Finance Tracker",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================================
# DATABASE FUNCTIONS
# ===============================================
def init_database():
    """Initialize database via API - simple version"""
    pass

# ===============================================
# STREAMLIT COMPONENTS - SIMPLIFIED
# ===============================================
def render_sidebar():
    """Render sidebar navigation - simplified version""" 
    with st.sidebar:
        st.title("💸 Smart Finance")
        st.markdown("---")
        
        # API Status Indicator
        if api_client.health_check():
            st.success("✅ API Connected")
        else:
            st.error("❌ API Disconnected")
        
        # Simple menu tanpa radio (pakai selectbox saja)
        menu_options = ["📊 Dashboard", "💳 Input Transaksi", "📋 Data Transaksi", "🎯 Budget Management", "🤖 AI Insights"]
        
        selected_menu = st.selectbox(
            "Navigasi Menu",
            menu_options
        )
        
        st.markdown("---")
        st.markdown("### Quick Stats")
        
        # Show quick stats from API
        try:
            summary_data = api_client.get_financial_summary()
            if summary_data:
                overall = summary_data.get("overall", {})
                balance = overall.get("balance", 0)
                total_income = overall.get("total_income", 0)
                total_expense = overall.get("total_expense", 0)
                
                # HAPUS KEY dari metric() - tidak support di versi lama
                st.metric("Balance", f"Rp {balance:,.0f}")
                st.metric("Pemasukan", f"Rp {total_income:,.0f}")
                st.metric("Pengeluaran", f"Rp {total_expense:,.0f}")
        except:
            st.info("Belum ada data transaksi")
        
        st.markdown("---")
        st.caption("Smart Finance Tracker v1.0")
    
    return selected_menu

def render_dashboard():
    """Render main dashboard using API data"""
    st.header("📊 Financial Dashboard")
    
    # Check API connection
    if not api_client.health_check():
        st.error("🚨 Cannot connect to API server. Please make sure the Flask API is running on port 5000.")
        st.info("💡 Run this command in another terminal: `python api/app.py`")
        return
    
    try:
        # Get data from API
        summary_data = api_client.get_financial_summary()
        category_data = api_client.get_category_breakdown()
        trend_data = api_client.get_monthly_trend(months=6)
        
        if not summary_data:
            st.warning("📝 Belum ada data transaksi. Silakan input transaksi terlebih dahulu.")
            return
        
        # ==================== SUMMARY CARDS ====================
        st.subheader("Ringkasan Keuangan")
        
        overall = summary_data.get("overall", {})
        current_month = summary_data.get("current_month", {})
        
        total_income = overall.get("total_income", 0)
        total_expense = overall.get("total_expense", 0)
        balance = overall.get("balance", 0)
        transaction_count = overall.get("total_transactions", 0)
        
        monthly_income = current_month.get("income", 0)
        monthly_expense = current_month.get("expense", 0)
        monthly_balance = current_month.get("balance", 0)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Balance", f"Rp {balance:,.0f}")
        
        with col2:
            st.metric("Total Pemasukan", f"Rp {total_income:,.0f}")
        
        with col3:
            st.metric("Total Pengeluaran", f"Rp {total_expense:,.0f}")
        
        with col4:
            st.metric("Jumlah Transaksi", transaction_count)
        
        # Current month summary
        st.subheader("Bulan Ini")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Pemasukan Bulan Ini", f"Rp {monthly_income:,.0f}")
        with col2:
            st.metric("Pengeluaran Bulan Ini", f"Rp {monthly_expense:,.0f}")
        with col3:
            st.metric("Balance Bulan Ini", f"Rp {monthly_balance:,.0f}")
        
        # ==================== MONTHLY TREND CHART ====================
        st.subheader("📈 Trend Bulanan")
        
        if trend_data and trend_data.get("trend"):
            trend_df = pd.DataFrame(trend_data["trend"])
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=trend_df['month'], 
                y=trend_df['income'],
                name='Pemasukan',
                line=dict(color='#00FF00', width=3),
                fill='tozeroy',
                fillcolor='rgba(0, 255, 0, 0.1)'
            ))
            
            fig.add_trace(go.Scatter(
                x=trend_df['month'], 
                y=trend_df['expense'],
                name='Pengeluaran',
                line=dict(color='#FF0000', width=3),
                fill='tozeroy',
                fillcolor='rgba(255, 0, 0, 0.1)'
            ))
            
            fig.update_layout(
                title="Trend Pemasukan vs Pengeluaran (6 Bulan Terakhir)",
                xaxis_title="Bulan",
                yaxis_title="Amount (Rp)",
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Belum ada data cukup untuk trend analysis")
        
        # ==================== CATEGORY BREAKDOWN ====================
        st.subheader("🍕 Breakdown Kategori")
        
        if category_data and category_data.get("breakdown"):
            category_df = pd.DataFrame(category_data["breakdown"])
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Expense by category
                expense_df = category_df[category_df['transaction_type'] == 'expense']
                if not expense_df.empty:
                    fig_pie = px.pie(
                        expense_df, 
                        values='total_amount', 
                        names='category',
                        title="Pengeluaran per Kategori",
                        hole=0.4
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.info("Belum ada data pengeluaran")
            
            with col2:
                # Income by category
                income_df = category_df[category_df['transaction_type'] == 'income']
                if not income_df.empty:
                    fig_bar = px.bar(
                        income_df,
                        x='category',
                        y='total_amount',
                        title="Pemasukan per Kategori",
                        color='total_amount',
                        color_continuous_scale='greens'
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.info("Belum ada data pemasukan")
                
    except Exception as e:
        st.error(f"Error loading dashboard data: {str(e)}")

def render_transaction_form():
    """Render transaction input form dengan AI terpisah"""
    st.header("💳 Input Transaksi Baru")
    
    # Check API connection
    if not api_client.health_check():
        st.error("🚨 Cannot connect to API server. Please start the Flask API first.")
        return
    
    # Initialize session state untuk category
    if 'selected_category' not in st.session_state:
        st.session_state.selected_category = "Makanan"
    
    # ==================== AI CATEGORIZATION HELPER ====================
    st.subheader("🤖 AI Categorization Helper")
    st.write("Gunakan AI untuk mendapatkan kategori otomatis berdasarkan deskripsi transaksi:")
    
    col_ai1, col_ai2 = st.columns([3, 1])
    
    with col_ai1:
        ai_description = st.text_input(
            "Deskripsi transaksi:",
            placeholder="Contoh: Makan siang di warung padang",
            key="ai_description_input"
        )
    
    with col_ai2:
        ai_amount = st.number_input(
            "Jumlah (optional):",
            min_value=0,
            value=0,
            key="ai_amount_input"
        )
    
    # AI Prediction Button - DI LUAR FORM
    if ai_description and st.button("🎯 Dapatkan Kategori AI", type="primary", key="ai_predict_btn"):
        with st.spinner("🤖 Menganalisis..."):
            ai_result = api_client.ai_categorize(ai_description, ai_amount)
            if ai_result:
                predicted_category = ai_result.get("predicted_category")
                confidence = ai_result.get("confidence", 0)
                
                st.success(f"**AI Prediction:** {predicted_category} (confidence: {confidence:.0%})")
                
                # Simpan ke session state
                st.session_state.selected_category = predicted_category
                st.session_state.ai_suggestion = f"✅ Kategori di-set ke: **{predicted_category}**"
            else:
                st.error("❌ Gagal mendapatkan prediksi AI")
    
    # Tampilkan AI suggestion jika ada
    if 'ai_suggestion' in st.session_state:
        st.info(st.session_state.ai_suggestion)
    
    st.markdown("---")
    
    # ==================== TRANSACTION FORM ====================
    st.subheader("📝 Detail Transaksi")
    
    with st.form("transaction_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            transaction_date = st.date_input(
                "Tanggal Transaksi*",
                value=date.today()
            )
            
            amount = st.number_input(
                "Jumlah (Rp)*",
                min_value=0.0,
                step=1000.0,
                value=0.0,
                help="Masukkan jumlah transaksi dalam Rupiah"
            )
            
            transaction_type = st.selectbox(
                "Tipe Transaksi*",
                ["expense", "income"],
                format_func=lambda x: "💸 Pengeluaran" if x == "expense" else "💰 Pemasukan"
            )
        
        with col2:
            categories = ["Makanan", "Transportasi", "Hiburan", "Belanja", "Kesehatan", "Pendidikan", "Gaji", "Investasi", "Lainnya"]
            
            # Gunakan category dari AI jika ada, otherwise default
            default_index = categories.index(st.session_state.selected_category) if st.session_state.selected_category in categories else 0
            
            category = st.selectbox(
                "Kategori*",
                categories,
                index=default_index
            )
            
            description = st.text_input(
                "Keterangan*",
                placeholder="Contoh: Makan siang di warung, Gaji bulan Januari, dll.",
                help="Deskripsi singkat tentang transaksi"
            )
        
        # ✅ FIX: Hanya st.form_submit_button() di dalam form
        submitted = st.form_submit_button("💾 Simpan Transaksi")
        
        # ✅ FIX: Define transaction_data di outer scope
        transaction_data = None
        
        if submitted:
            # Validation
            validation_errors = []
            
            if amount <= 0:
                validation_errors.append("❌ Jumlah transaksi harus lebih dari 0")
            
            if not description.strip():
                validation_errors.append("❌ Keterangan transaksi harus diisi")
            
            if validation_errors:
                for error in validation_errors:
                    st.error(error)
                return
            
            # Prepare data for API - ✅ FIX: Assign ke variable di outer scope
            transaction_data = {
                "date": transaction_date.isoformat(),
                "amount": amount,
                "description": description,
                "type": transaction_type,
                "category": category
            }
            
            # Save via API
            try:
                result = api_client.create_transaction(transaction_data)
                if result:
                    st.success("✅ Transaksi berhasil disimpan!")
                    
                    # Show preview
                    with st.expander("📋 Preview Transaksi yang Disimpan", expanded=True):
                        col_preview1, col_preview2 = st.columns(2)
                        
                        with col_preview1:
                            st.write(f"**Tanggal:** {transaction_date}")
                            st.write(f"**Jumlah:** Rp {amount:,.0f}")
                            st.write(f"**Tipe:** {'💸 Pengeluaran' if transaction_type == 'expense' else '💰 Pemasukan'}")
                        
                        with col_preview2:
                            st.write(f"**Kategori:** {category}")
                            st.write(f"**Keterangan:** {description}")
                    
                    # Clear AI suggestion setelah berhasil simpan
                    if 'ai_suggestion' in st.session_state:
                        del st.session_state.ai_suggestion
                    
                    # Reset selected category
                    st.session_state.selected_category = "Makanan"
                    
                    # Auto-refresh form
                    st.rerun()
                    
                else:
                    st.error("❌ Gagal menyimpan transaksi")
                    
            except Exception as e:
                # ✅ FIX: Sekarang transaction_data accessible
                error_msg = f"❌ Error menyimpan transaksi: {str(e)}"
                if transaction_data:
                    error_msg += f"\n\nData yang gagal disimpan:\n- Deskripsi: {transaction_data['description']}\n- Jumlah: Rp {transaction_data['amount']:,.0f}\n- Kategori: {transaction_data['category']}"
                st.error(error_msg)
    
    # ==================== QUICK ACTION BUTTONS ====================
    st.markdown("---")
    st.subheader("⚡ Quick Actions")
    
    col_quick1, col_quick2, col_quick3 = st.columns(3)
    
    with col_quick1:
        if st.button("🍕 Contoh: Makan Siang", key="quick_food"):
            st.session_state.selected_category = "Makanan"
            st.rerun()
    
    with col_quick2:
        if st.button("⛽ Contoh: Isi Bensin", key="quick_transport"):
            st.session_state.selected_category = "Transportasi"
            st.rerun()
    
    with col_quick3:
        if st.button("🛒 Contoh: Belanja", key="quick_shopping"):
            st.session_state.selected_category = "Belanja"
            st.rerun()

def render_transaction_list():
    """Render transaction data table using API"""
    st.header("📋 Data Transaksi")
    
    # Check API connection
    if not api_client.health_check():
        st.error("🚨 Cannot connect to API server. Please start the Flask API first.")
        return
    
    try:
        # Get transactions from API
        transactions = api_client.get_transactions()
        
        if not transactions:
            st.warning("Belum ada data transaksi")
            return
        
        df = pd.DataFrame(transactions)
        
        # Show summary
        total_income = df[df['transaction_type'] == 'income']['amount'].sum()
        total_expense = df[df['transaction_type'] == 'expense']['amount'].sum()
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"Total Pemasukan: **Rp {total_income:,.0f}**")
        with col2:
            st.info(f"Total Pengeluaran: **Rp {total_expense:,.0f}**")
        
        # Show data
        st.subheader(f"Data Transaksi ({len(df)} records)")
        
        # Format the dataframe for display
        display_df = df.copy()
        display_df['amount'] = display_df['amount'].apply(lambda x: f"Rp {x:,.0f}")
        display_df['transaction_type'] = display_df['transaction_type'].apply(
            lambda x: "💰 Pemasukan" if x == "income" else "💸 Pengeluaran"
        )
        
        st.dataframe(
            display_df[['date', 'amount', 'transaction_type', 'category', 'description']],
            use_container_width=True
        )
        
        # Export option
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Export ke CSV",
            data=csv,
            file_name=f"transactions_{date.today()}.csv",
            mime="text/csv"
        )
        
    except Exception as e:
        st.error(f"Error loading transactions: {str(e)}")

def render_budget_management():
    """Render budget management page"""
    st.header("🎯 Budget Management")
    st.info("Fitur budget management akan segera hadir di versi berikutnya!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Coming Soon Features:")
        st.write("✅ Set monthly budget per kategori")
        st.write("✅ Budget vs actual spending alerts")
        st.write("✅ Spending recommendations")
        st.write("✅ Savings goals tracking")
    
    with col2:
        st.subheader("API-Powered Features:")
        st.write("🚀 Real-time data sync")
        st.write("📱 Future mobile app ready")
        st.write("🔌 Third-party integrations")
        st.write("🌐 Multi-user support")

# ===============================================
# MAIN APPLICATION
# ===============================================
def main():
    """Main application function"""
    
    # Initialize database
    init_database()
    
    # Render sidebar and get selected menu
    selected_menu = render_sidebar()
    
    # Render selected page
    if selected_menu == "📊 Dashboard":
        render_dashboard()
    elif selected_menu == "💳 Input Transaksi":
        render_transaction_form()
    elif selected_menu == "📋 Data Transaksi":
        render_transaction_list()
    elif selected_menu == "🎯 Budget Management":
        render_budget_management()
    elif selected_menu == "🤖 AI Insights":
        # Simple AI page
        st.header("🤖 AI Insights")
        st.info("AI Features are working in the background!")
        st.write("Our AI model has been trained and can categorize transactions automatically.")
        st.write("Try adding a transaction in the 'Input Transaksi' page to see AI categorization in action!")

if __name__ == "__main__":
    main()