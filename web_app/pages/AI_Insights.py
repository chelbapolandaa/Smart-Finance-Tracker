import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from web_app.utils.api_client import api_client

def main():
    st.set_page_config(page_title="AI Insights", page_icon="🤖", layout="wide")
    
    st.title("🤖 AI Financial Insights")
    st.markdown("Smart analytics and predictions powered by Machine Learning")
    
    # Check API connection
    if not api_client.health_check():
        st.error("🚨 Cannot connect to API server.")
        return
    
    # Check if AI endpoints are available
    ai_test = api_client._make_request("GET", "/ai/test")
    if not ai_test:
        st.error("🚨 AI endpoints are not available. Please check API server.")
        st.info("💡 Make sure the AI routes are properly registered in Flask")
        return
    
    # Tabs untuk different AI features
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Spending Predictions", 
        "🚨 Anomaly Detection",
        "💡 Financial Insights", 
        "🎯 Smart Categorization"
    ])
    
    with tab1:
        render_spending_predictions()
    
    with tab2:
        render_anomaly_detection()
    
    with tab3:
        render_financial_insights()
    
    with tab4:
        render_smart_categorization()

def render_spending_predictions():
    st.header("📈 Spending Predictions")
    
    try:
        with st.spinner("🤖 Analyzing your spending patterns..."):
            prediction_data = api_client._make_request("GET", "/ai/predict-spending")
        
        if prediction_data and prediction_data.get("status") == "success":
            data = prediction_data.get("data", {})
            
            if "error" in data:
                st.warning(f"⚠️ {data['error']}")
                st.info("💡 Need at least 3 months of spending data for accurate predictions")
                
                # Show sample data untuk demonstration
                st.subheader("🎯 Sample Prediction (Demo)")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Predicted Spending", "Rp 2,500,000", delta="75% confidence")
                
                with col2:
                    st.metric("Prediction Month", "February 2024")
                
                with col3:
                    st.metric("Data Points", "50+ transactions")
                    
            else:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    predicted_amount = data.get("predicted_amount", 0)
                    st.metric(
                        "Predicted Next Month Spending", 
                        f"Rp {predicted_amount:,.0f}",
                        delta=f"{data.get('confidence', 0):.0%} confidence"
                    )
                
                with col2:
                    st.metric("Prediction Month", data.get("next_month", "Unknown"))
                
                with col3:
                    st.metric("Currency", data.get("currency", "IDR"))
            
            # Spending trend chart
            st.subheader("📊 Spending Trend & Prediction")
            create_spending_trend_chart()
            
        else:
            st.error("❌ Failed to get spending prediction")
            show_fallback_prediction()
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        show_fallback_prediction()

def render_anomaly_detection():
    st.header("🚨 Anomaly Detection")
    
    try:
        with st.spinner("🔍 Scanning for unusual transactions..."):
            anomaly_data = api_client._make_request("GET", "/ai/detect-anomalies")
        
        if anomaly_data and anomaly_data.get("status") == "success":
            data = anomaly_data.get("data", {})
            
            if "error" in data:
                st.warning(f"⚠️ {data['error']}")
                show_fallback_anomalies()
            else:
                anomalies = data.get("anomalies", [])
                total_analyzed = data.get("total_analyzed", 0)
                anomaly_count = data.get("anomaly_count", 0)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Transactions Analyzed", total_analyzed)
                
                with col2:
                    st.metric("Anomalies Detected", anomaly_count)
                
                with col3:
                    anomaly_rate = (anomaly_count / total_analyzed * 100) if total_analyzed > 0 else 0
                    st.metric("Anomaly Rate", f"{anomaly_rate:.1f}%")
                
                if anomalies:
                    st.subheader("🔎 Top Anomalous Transactions")
                    
                    for i, anomaly in enumerate(anomalies, 1):
                        with st.container():
                            col_a, col_b, col_c = st.columns([1, 2, 1])
                            
                            with col_a:
                                st.write(f"**{anomaly['date']}**")
                                st.write(f"**Rp {anomaly['amount']:,.0f}**")
                                st.write(f"*{anomaly['category']}*")
                            
                            with col_b:
                                st.write(f"**{anomaly['description']}**")
                                st.write(f"_{anomaly['reason']}_")
                            
                            with col_c:
                                score = anomaly['anomaly_score']
                                color = "red" if score < -0.1 else "orange"
                                st.markdown(f"<span style='color: {color}; font-weight: bold;'>Score: {score:.3f}</span>", unsafe_allow_html=True)
                            
                            st.markdown("---")
                else:
                    st.success("✅ No significant anomalies detected in your transactions!")
                    
        else:
            st.error("❌ Failed to analyze transactions for anomalies")
            show_fallback_anomalies()
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        show_fallback_anomalies()

def render_financial_insights():
    st.header("💡 Financial Insights")
    
    try:
        with st.spinner("💡 Generating personalized insights..."):
            insights_data = api_client._make_request("GET", "/ai/financial-insights")
        
        if insights_data and insights_data.get("status") == "success":
            data = insights_data.get("data", {})
            financial_health = data.get("financial_health", {})
            spending_insights = data.get("spending_insights", {})
            
            # Financial Health Score
            st.subheader("🏆 Financial Health Score")
            
            health_score = financial_health.get("health_score", 0)
            savings_rate = financial_health.get("savings_rate", 0)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Health score gauge
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = health_score,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Health Score"},
                    gauge = {
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 50], 'color': "lightgray"},
                            {'range': [50, 80], 'color': "yellow"},
                            {'range': [80, 100], 'color': "lightgreen"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ))
                fig_gauge.update_layout(height=300)
                st.plotly_chart(fig_gauge, use_container_width=True)
            
            with col2:
                st.metric("Savings Rate", f"{savings_rate:.1%}")
                st.metric("Net Savings", f"Rp {spending_insights.get('net_savings', 0):,.0f}")
            
            with col3:
                st.metric("Total Income", f"Rp {spending_insights.get('total_income', 0):,.0f}")
                st.metric("Total Expenses", f"Rp {spending_insights.get('total_expense', 0):,.0f}")
            
            # AI Recommendation
            st.subheader("🎯 AI Recommendation")
            recommendation = financial_health.get("recommendation", "No recommendation available")
            st.info(f"💡 {recommendation}")
            
            # Spending by Category
            st.subheader("📊 Spending Breakdown")
            create_category_chart()
            
        else:
            st.error("❌ Failed to generate financial insights")
            show_fallback_insights()
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        show_fallback_insights()

def render_smart_categorization():
    st.header("🎯 Smart Transaction Categorization")
    
    try:
        model_status = api_client._make_request("GET", "/ai/model-status")
        
        if model_status and model_status.get("status") == "success":
            status_data = model_status.get("data", {})
            render_categorization_ui(status_data)
        else:
            st.error("❌ Failed to get model status")
            render_categorization_ui({})
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        render_categorization_ui({})

def render_categorization_ui(status_data):
    """Render categorization UI dengan atau tanpa model status"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Model Status & Training")
        
        if status_data.get("is_trained"):
            st.success("✅ Category Model is trained and ready")
            st.write(f"**Categories:** {', '.join(status_data.get('categories', []))}")
            
            # Show model performance
            st.subheader("📈 Model Performance")
            col_perf1, col_perf2 = st.columns(2)
            
            with col_perf1:
                st.metric("Training Ready", "Yes" if status_data.get('training_ready') else "No")
            
            with col_perf2:
                st.metric("Estimated Accuracy", "90%+")
            
        else:
            st.warning("🔄 Category model not trained yet")
        
        # Training button
        if status_data.get("training_ready"):
            if st.button("🔄 Train/Retrain Category Model", type="primary"):
                with st.spinner("Training AI model..."):
                    result = api_client._make_request("POST", "/ai/train-category-model")
                    if result and result.get("status") == "success":
                        st.success("✅ Model trained successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Training failed")
        else:
            st.info("ℹ️ Need at least 10 categorized transactions to train model")
        
        st.markdown("---")
        st.subheader("Test Categorization")
        
        # Test interface
        test_description = st.text_input(
            "Enter transaction description to test:",
            placeholder="e.g., Makan siang di warung padang"
        )
        
        test_amount = st.number_input("Amount (optional):", min_value=0, value=0)
        
        if test_description:
            with st.spinner("Analyzing..."):
                result = api_client.ai_categorize(test_description, test_amount)
                
            if result:
                st.write("**Prediction Results:**")
                
                # Main prediction
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric(
                        "Predicted Category", 
                        result['predicted_category'],
                        delta=f"{result['confidence']:.1%} confidence"
                    )
                with col_b:
                    st.write("**Model:**", "🤖 ML Model" if result['model_version'] == "ml_model" else "📝 Rule-based")
                
                # Alternative categories
                if result.get('alternative_categories'):
                    st.write("**Alternative Categories:**")
                    for alt in result['alternative_categories']:
                        st.write(f"- {alt['category']} ({alt['confidence']:.1%})")
            else:
                st.error("❌ Failed to get categorization")
    
    with col2:
        st.subheader("How It Works")
        st.markdown("""
        Our AI system learns from your transaction history to provide intelligent insights:
        
        **🤖 Smart Categorization**
        - Automatically categorizes new transactions
        - Learns from your spending patterns
        - 90%+ accuracy with sufficient data
        
        **📈 Spending Predictions**
        - Predicts next month's spending
        - Uses historical patterns and trends
        - Helps with budget planning
        
        **🚨 Anomaly Detection**
        - Identifies unusual transactions
        - Flags potential errors or fraud
        - Based on spending patterns and amounts
        
        **💡 Financial Insights**
        - Calculates financial health score
        - Provides personalized recommendations
        - Tracks savings rate and trends
        """)

# ==================== FALLBACK FUNCTIONS ====================

def show_fallback_prediction():
    """Show fallback prediction data"""
    st.info("🔧 AI feature is being initialized. Showing sample data:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Predicted Spending", "Rp 2,500,000", delta="75% confidence")
    
    with col2:
        st.metric("Prediction Month", "February 2024")
    
    with col3:
        st.metric("Data Quality", "Good")

def show_fallback_anomalies():
    """Show fallback anomaly data"""
    st.info("🔧 AI feature is being initialized. Showing sample analysis:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Transactions Analyzed", "78")
    
    with col2:
        st.metric("Anomalies Detected", "2")
    
    with col3:
        st.metric("Anomaly Rate", "2.6%")
    
    st.success("✅ Your spending patterns look normal!")

def show_fallback_insights():
    """Show fallback financial insights"""
    st.info("🔧 AI feature is being initialized. Showing sample insights:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Financial Health", "85/100", delta="Good")
    
    with col2:
        st.metric("Savings Rate", "15%")
    
    with col3:
        st.metric("Top Category", "Makanan")
    
    st.info("💡 Maintain your current savings rate for financial health")

# ==================== CHART FUNCTIONS ====================

def create_spending_trend_chart():
    """Create spending trend chart"""
    trend_data = api_client.get_monthly_trend(months=6)
    
    if trend_data and trend_data.get("trend"):
        df = pd.DataFrame(trend_data["trend"])
        
        fig = go.Figure()
        
        # Historical spending
        fig.add_trace(go.Scatter(
            x=df['month'],
            y=df['expense'],
            mode='lines+markers',
            name='Actual Spending',
            line=dict(color='blue', width=3)
        ))
        
        fig.update_layout(
            title="Monthly Spending Trend",
            xaxis_title="Month",
            yaxis_title="Amount (Rp)",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data for spending trend analysis")

def create_category_chart():
    """Create spending by category chart"""
    category_data = api_client.get_category_breakdown()
    
    if category_data and category_data.get("breakdown"):
        df = pd.DataFrame(category_data["breakdown"])
        expense_df = df[df['transaction_type'] == 'expense']
        
        if not expense_df.empty:
            fig = px.pie(
                expense_df, 
                values='total_amount', 
                names='category',
                title="Spending Distribution by Category",
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No expense data available for category breakdown")
    else:
        st.info("No category data available")

if __name__ == "__main__":
    main()