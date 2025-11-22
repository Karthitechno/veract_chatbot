import streamlit as st
import json
import os
from datetime import datetime
from typing import Optional, Dict, List, Any
from chatbot import EnhancedChatbot, initialize_sample_data
import time

# Import the chatbot (assuming the main code is in chatbot.py)
# from chatbot import EnhancedChatbot, initialize_sample_data, load_json

# For demo purposes, we'll create a simplified version
class SimplifiedChatbot:
    def __init__(self):
        self.memory = []
        self.context = {}
    
    def process_message(self, user_input: str) -> str:
        """Simplified message processing for demo"""
        lower_input = user_input.lower()
        
        if 'search' in lower_input or 'find' in lower_input or 'product' in lower_input:
            return """🔍 **Product Search Results**

I found 3 products matching your search:

1. **Apple iPhone 15 Pro**
   • ID: prod_001
   • Category: Electronics
   • Brand: Apple
   • Rating: ⭐⭐⭐⭐⭐
   • Price: ₹79,999
   • Stock: 12 units available

2. **Samsung Galaxy S24 Ultra**
   • ID: prod_002
   • Category: Electronics  
   • Brand: Samsung
   • Rating: ⭐⭐⭐⭐⭐
   • Price: ₹89,999
   • Stock: 7 units available

3. **Sony WH-1000XM5**
   • ID: prod_004
   • Category: Electronics
   • Brand: Sony
   • Rating: ⭐⭐⭐⭐⭐
   • Price: ₹24,999
   • Stock: 15 units available

Would you like more details on any of these products?"""
        
        elif 'sale' in lower_input or 'transaction' in lower_input:
            return """💰 **Sales Records**

I found 2 recent sales:

1. **Sale INV-2025-001**
   • Customer: cust_001
   • Total: ₹1,59,998
   • Status: ✅ PAID
   • Date: Feb 12, 2025
   • Items: 2 products

2. **Sale INV-2025-002**
   • Customer: cust_002
   • Total: ₹24,999
   • Status: ⏳ PENDING
   • Date: Feb 16, 2025
   • Items: 1 product

Would you like to see more details or filter by customer?"""
        
        elif 'analytics' in lower_input or 'report' in lower_input:
            return """📊 **Sales Analytics Summary**

• Total Sales: 89
• Total Revenue: ₹24,56,789
• Paid Sales: 77
• Pending Sales: 12
• Average Transaction: ₹27,604
• Payment Completion Rate: 86.5%

🔥 **Top Selling Products:**
1. Apple iPhone 15 Pro - 23 units
2. Samsung Galaxy S24 - 18 units
3. Sony WH-1000XM5 - 15 units
4. Nike Air Max 270 - 12 units
5. Levi's 501 Jeans - 10 units

📈 Trend: Sales are up 15% from last month!"""
        
        elif 'recommend' in lower_input or 'suggest' in lower_input:
            return """⭐ **Product Recommendations**

Based on your preferences, here are my top recommendations:

1. **Apple iPhone 15 Pro** ⭐⭐⭐⭐⭐
   • Latest flagship with A17 Pro chip
   • Price: ₹79,999
   • High customer satisfaction

2. **Sony WH-1000XM5** ⭐⭐⭐⭐⭐
   • Industry-leading noise cancellation
   • Price: ₹24,999
   • Perfect for audiophiles

3. **Samsung Galaxy S24 Ultra** ⭐⭐⭐⭐⭐
   • 200MP camera + S Pen
   • Price: ₹89,999
   • Best Android flagship"""
        
        elif 'vendor' in lower_input:
            return """🏢 **Vendor Information**

Here are our registered vendors:

1. **Tech Supplies India**
   • ID: vendor_001
   • Contact: Rajesh Kumar
   • Email: rajesh@techsupplies.in
   • Phone: +91-9876543210

2. **Fashion Wholesale Co**
   • ID: vendor_002
   • Contact: Priya Sharma
   • Email: priya@fashionwholesale.com
   • Phone: +91-9876543211"""
        
        elif 'hello' in lower_input or 'hi' in lower_input:
            return """👋 Hello! I'm your Veract AI Sales Assistant.

I can help you with:
• 🔍 Search products
• 💰 Check sales records
• 📊 View analytics
• ⭐ Get recommendations
• 🏢 Manage vendors

What would you like to do today?"""
        
        else:
            return """I'm here to help! I can assist you with:

🔍 **Search** - Find products or sales
📦 **Product Details** - View complete information
💰 **Sales Management** - Track records
📊 **Analytics** - Get insights
🏢 **Vendors** - Manage vendor info

What would you like to explore?"""

# Page configuration
st.set_page_config(
    page_title="Veract AI Sales Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stApp {
        background: linear-gradient(to bottom right, #f0f4ff, #ffffff, #f8f0ff);
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 20%;
    }
    .assistant-message {
        background-color: #f7f7f8;
        color: #1f2937;
        margin-right: 20%;
    }
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        text-align: center;
    }
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }
    .stat-label {
        color: #6b7280;
        font-size: 0.875rem;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": """🤖 **Welcome to Veract AI Sales Assistant!**

I can help you with:
• 🔍 Search and filter products
• 📦 View product details and variants
• 💰 Check sales records and transactions
• 📊 Get analytics and insights
• 🏢 Manage vendor information
• ➕ Create and update products/sales

Just chat naturally - I'll understand what you need!""",
            "timestamp": datetime.now().isoformat()
        }
    ]

if 'chatbot' not in st.session_state:
    st.session_state.chatbot = SimplifiedChatbot()

if 'stats' not in st.session_state:
    st.session_state.stats = {
        'total_products': 150,
        'total_sales': 89,
        'revenue': 2456789,
        'pending_sales': 12
    }

# Header
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.title("🤖 Veract AI Sales Assistant")
    st.caption("Powered by LangGraph & Groq AI")

# Sidebar
with st.sidebar:
    st.header("📊 Dashboard")
    
    # Stats
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{st.session_state.stats['total_products']}</div>
            <div class="stat-label">📦 Total Products</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{st.session_state.stats['total_sales']}</div>
            <div class="stat-label">💰 Total Sales</div>
        </div>
        """, unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">₹{st.session_state.stats['revenue']/100000:.1f}L</div>
            <div class="stat-label">📈 Revenue</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{st.session_state.stats['pending_sales']}</div>
            <div class="stat-label">⏳ Pending</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick Actions
    st.header("⚡ Quick Actions")
    
    if st.button("🔍 Search Products", use_container_width=True):
        st.session_state.messages.append({
            "role": "user",
            "content": "Show me all products",
            "timestamp": datetime.now().isoformat()
        })
        response = st.session_state.chatbot.process_message("Show me all products")
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        st.rerun()
    
    if st.button("📊 View Analytics", use_container_width=True):
        st.session_state.messages.append({
            "role": "user",
            "content": "Show analytics",
            "timestamp": datetime.now().isoformat()
        })
        response = st.session_state.chatbot.process_message("Show analytics")
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        st.rerun()
    
    if st.button("⭐ Get Recommendations", use_container_width=True):
        st.session_state.messages.append({
            "role": "user",
            "content": "Recommend products",
            "timestamp": datetime.now().isoformat()
        })
        response = st.session_state.chatbot.process_message("Recommend products")
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        st.rerun()
    
    if st.button("💰 Recent Sales", use_container_width=True):
        st.session_state.messages.append({
            "role": "user",
            "content": "Show recent sales",
            "timestamp": datetime.now().isoformat()
        })
        response = st.session_state.chatbot.process_message("Show recent sales")
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        st.rerun()
    
    st.markdown("---")
    
    # Settings
    st.header("⚙️ Settings")
    if st.button("🔄 Reset Conversation", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "🔄 **Memory Reset!**\n\nStarting a fresh conversation. How can I help you today?",
                "timestamp": datetime.now().isoformat()
            }
        ]
        st.rerun()
    
    st.markdown("---")
    st.caption("© 2025 Veract Consultancy Pvt Ltd")
    st.caption("Chennai, Tamil Nadu, India")

# Main chat area
chat_container = st.container()

with chat_container:
    # Display messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <div><strong>You</strong></div>
                <div>{message["content"]}</div>
                <div style="font-size: 0.75rem; opacity: 0.7; margin-top: 0.5rem;">
                    {datetime.fromisoformat(message["timestamp"]).strftime("%I:%M %p")}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <div><strong>🤖 Assistant</strong></div>
                <div>{message["content"]}</div>
                <div style="font-size: 0.75rem; opacity: 0.7; margin-top: 0.5rem;">
                    {datetime.fromisoformat(message["timestamp"]).strftime("%I:%M %p")}
                </div>
            </div>
            """, unsafe_allow_html=True)

# Input area
st.markdown("---")
col1, col2 = st.columns([6, 1])

with col1:
    user_input = st.text_input(
        "Message",
        placeholder="Ask me anything about products, sales, analytics...",
        key="user_input",
        label_visibility="collapsed"
    )

with col2:
    send_button = st.button("Send 📤", use_container_width=True)

# Process input
if send_button and user_input:
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().isoformat()
    })
    
    # Get bot response
    with st.spinner("Thinking..."):
        time.sleep(0.5)  # Simulate processing
        response = st.session_state.chatbot.process_message(user_input)
    
    # Add assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "timestamp": datetime.now().isoformat()
    })
    
    # Rerun to update chat
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6b7280; font-size: 0.875rem;">
    <p>AI-powered chatbot with LangGraph orchestration | Natural language understanding</p>
    <p>Features: Product search, Sales tracking, Analytics, Vendor management, Smart recommendations</p>
</div>
""", unsafe_allow_html=True)