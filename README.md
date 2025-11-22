# 🤖 Veract AI Sales Assistant

> An intelligent sales chatbot powered by LangGraph, Groq AI, and natural language understanding for product management, sales tracking, analytics, and vendor management.



## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Database Schema](#database-schema)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## 🎯 Overview

The Veract AI Sales Assistant is an enterprise-grade conversational AI system designed for retail and sales operations. It uses advanced natural language processing to understand user queries and execute complex operations across products, sales, analytics, and vendor management.

**Built by:** Veract Consultancy Pvt Ltd  
**Location:** Chennai, Tamil Nadu, India  
**Technology Stack:** Python, LangGraph, Groq AI (Llama 3.3), Streamlit

---

## ✨ Features

### 🔍 **Product Management**
- Natural language product search with fuzzy matching
- Filter by category, brand, price range, and ratings
- View detailed product information including variants
- Create and update products with validation
- Stock level tracking across multiple locations
- Pricing tiers (retail, wholesale, floor prices)

### 💰 **Sales Management**
- Search and filter sales records
- Track payment status (PAID, PENDING, CANCELLED)
- Create new sales with multi-item support
- Update existing sales records
- Customer-specific sales history
- Payment method tracking (CASH, CARD, UPI)

### 📊 **Analytics & Insights**
- Real-time sales summary dashboard
- Top-selling products analysis
- Revenue tracking and trends
- Payment completion rates
- Average transaction values
- Category-wise performance metrics

### 🏢 **Vendor Management**
- Vendor directory with contact information
- Search vendors by name or ID
- Track vendor relationships
- Supplier performance metrics

### 🧠 **Intelligent Features**
- **Conversation Memory:** Remembers context, preferences, and previous queries
- **Intent Recognition:** Understands natural language queries
- **Entity Extraction:** Automatically identifies products, categories, IDs, prices
- **Input Validation:** Ensures data quality with smart validation
- **Confirmation Workflow:** Requires explicit confirmation for create/update operations
- **Smart Recommendations:** Suggests products based on ratings, sales, and user preferences

### 🎨 **User Interface**
- Modern Streamlit web interface
- Real-time chat experience
- Stats dashboard with key metrics
- Quick action buttons
- Mobile-responsive design
- Message history with timestamps

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Web UI                          │
│  (Chat Interface, Dashboard, Quick Actions)                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              Enhanced Chatbot Controller                     │
│        (Session Memory, Context Management)                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  LangGraph Orchestration                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Understand │→ │   Validate   │→ │  Route Agent │     │
│  └──────────────┘  └──────────────┘  └──────┬───────┘     │
│                                              │              │
│  ┌────────────────────────────────────────────┼──────────┐ │
│  │                                            ▼          │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐│ │
│  │  │ Product  │ │  Sales   │ │Analytics │ │ Vendor  ││ │
│  │  │  Agent   │ │  Agent   │ │  Agent   │ │ Agent   ││ │
│  │  └──────────┘ └──────────┘ └──────────┘ └─────────┘│ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              Natural Language Understanding                  │
│        (Groq AI - Llama 3.3 70B Versatile)                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  Database Layer (JSON)                       │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │ products.json│ │  sales.json  │ │ vendors.json │       │
│  └──────────────┘ └──────────────┘ └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### LangGraph Flow

```
User Input → Understand → Validate → Route → Execute → Response
              ↓            ↓          ↓       ↓
           Extract     Check      Choose    Run
           Intent      Rules      Agent     Tools
```

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Groq API key ([Get one here](https://console.groq.com))

### Step-by-Step Installation

1. **Clone the repository**
```bash
git clone https://github.com/veract/ai-sales-assistant.git
cd ai-sales-assistant
```

2. **Create virtual environment** (recommended)
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
# Create .env file
echo "GROQ_API_KEY=your_api_key_here" > .env
```

5. **Initialize database** (optional - auto-initializes on first run)
```bash
python chatbot.py
# Type 'quit' to exit after initialization
```

---

## 📦 Dependencies

Create a `requirements.txt` file with:

```txt
streamlit==1.28.0
groq==0.4.0
langgraph==0.0.19
typing-extensions==4.8.0
python-dotenv==1.0.0
```

Install all at once:
```bash
pip install -r requirements.txt
```

---

## 💻 Usage

### Running the Streamlit Web App

```bash
streamlit run app.py
```

The app will automatically open at `http://localhost:8501`

### Running the CLI Version

```bash
python chatbot.py
```

### Example Conversations

**Search Products:**
```
You: Show me all electronics
Bot: I found 3 products in Electronics category...

You: Find iPhone
Bot: Here are the iPhone models we have...
```

**Check Sales:**
```
You: Show recent sales
Bot: I found 5 recent sales...

You: Show sales for customer cust_001
Bot: Here are all sales for customer cust_001...
```

**Get Analytics:**
```
You: Show me analytics
Bot: 📊 Sales Analytics Summary
     • Total Sales: 89
     • Total Revenue: ₹24,56,789
     ...
```

**Create Product:**
```
You: Create a new product
Bot: I'll help you create a product. Please provide:
     • Product ID
     • Product Name
     • Category
     ...
```

**Get Recommendations:**
```
You: Recommend products
Bot: ⭐ Here are my top recommendations:
     1. Apple iPhone 15 Pro
     ...
```

---

## 📁 Project Structure

```
veract-ai-sales-assistant/
│
├── app.py                      # Streamlit web application
├── chatbot.py                  # Core chatbot logic with LangGraph
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (API keys)
├── README.md                   # This file
│
├── Database Files/
│   ├── products.json           # Products database
│   ├── sales.json             # Sales records database
│   └── vendors.json           # Vendors database
│
├── docs/
│   ├── API.md                 # API documentation
│   ├── ARCHITECTURE.md        # System architecture details
│   └── Chatbot_scope_document.pdf  # Original requirements
│
└── tests/
    ├── test_chatbot.py        # Unit tests for chatbot
    ├── test_tools.py          # Tests for database tools
    └── test_agents.py         # Tests for agent nodes
```

---

## 🔧 Configuration

### Groq API Configuration

Edit the API key in `chatbot.py`:

```python
client = Groq(api_key="YOUR_API_KEY_HERE")
```

Or use environment variables:

```python
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
```

### Database Configuration

Database file paths are defined in `chatbot.py`:

```python
PRODUCTS_DB = "products.json"
SALES_DB = "sales.json"
VENDORS_DB = "vendors.json"
```

### Model Configuration

Change the AI model:

```python
completion = client.chat.completions.create(
    model="llama-3.3-70b-versatile",  # Change model here
    messages=[...],
    temperature=0.1,  # Adjust creativity (0.0 - 1.0)
)
```

Available Groq models:
- `llama-3.3-70b-versatile` (recommended)
- `llama-3.1-70b-versatile`
- `mixtral-8x7b-32768`
- `gemma2-9b-it`

---

## 🗄️ Database Schema

### Products Schema

```json
{
  "id": "prod_001",
  "company_id": "comp_001",
  "name": "Apple iPhone 15 Pro",
  "category": "Electronics",
  "description": "Latest flagship smartphone",
  "brand": "Apple",
  "rating": 4.8,
  "variants": [
    {
      "id": "var_001",
      "variant_name": "128GB - Black",
      "sku": "IP15-BLK-128",
      "pricing": {
        "retail_price": 79999,
        "wholesale_price": 72000,
        "floor_price": 70000
      },
      "locations": [
        {
          "location_id": "loc_001",
          "stock": 12,
          "reorder_level": 3
        }
      ]
    }
  ]
}
```

### Sales Schema

```json
{
  "id": "sale_001",
  "company_id": "comp_001",
  "customer_id": "cust_001",
  "invoice_number": "INV-2025-001",
  "total": 79999,
  "discount": 0,
  "payment_status": "PAID",
  "created_at": "2025-02-15T14:22:00Z",
  "items": [
    {
      "variant_id": "var_001",
      "qty": 1,
      "unit_price": 79999
    }
  ],
  "payments": [
    {
      "method": "CARD",
      "amount": 79999,
      "ref_number": "TXN-123456"
    }
  ]
}
```

### Vendors Schema

```json
{
  "id": "vendor_001",
  "name": "Tech Supplies India",
  "contact": "Rajesh Kumar",
  "email": "rajesh@techsupplies.in",
  "phone": "+91-9876543210"
}
```

---

## 🎨 Customization

### Adding New Categories

In `chatbot.py`, update the valid categories:

```python
valid_categories = ["Electronics", "Grocery", "Fashion", "Home", "Sports", "Books", "Toys"]
```

### Adding New Intents

1. Add intent to `AgentType` enum:
```python
class AgentType(Enum):
    YOUR_NEW_AGENT = "your_new_agent"
```

2. Create agent node:
```python
def your_agent_node(self, state: ConversationState) -> ConversationState:
    # Your logic here
    pass
```

3. Update routing:
```python
def route_to_agent(self, state: ConversationState) -> str:
    if intent == "your_new_intent":
        return "your_new_agent"
```

### Customizing UI Colors

In `app.py`, modify the CSS:

```python
st.markdown("""
<style>
    .user-message {
        background: linear-gradient(135deg, #YOUR_COLOR1, #YOUR_COLOR2);
    }
</style>
""", unsafe_allow_html=True)
```

---

## 🐛 Troubleshooting

### Common Issues

**1. ImportError: No module named 'groq'**
```bash
pip install groq
```

**2. API Key Error**
```
Error: API key is required
```
Solution: Set your Groq API key in the code or environment variables

**3. JSON Decode Error**
```
Error loading products.json: Expecting value
```
Solution: Delete corrupted JSON files - they'll auto-regenerate

**4. Port Already in Use (Streamlit)**
```bash
streamlit run app.py --server.port 8502
```

**5. Memory Issues with Large Databases**
- Limit search results to 10-20 items
- Implement pagination
- Use database indices

### Debug Mode

Enable debug logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
```

---

## 🧪 Testing

### Run Unit Tests

```bash
python -m pytest tests/
```

### Run Specific Test

```bash
python -m pytest tests/test_chatbot.py::test_search_products
```

### Manual Testing Checklist

- [ ] Product search with various keywords
- [ ] Create product with validation
- [ ] Update existing product
- [ ] Search sales by customer
- [ ] Create sale with confirmation
- [ ] View analytics summary
- [ ] Get product recommendations
- [ ] Search vendors
- [ ] Reset conversation memory
- [ ] Handle invalid inputs gracefully

---

## 🚀 Deployment

### Deploy to Streamlit Cloud

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repository
4. Add secrets (API keys) in settings
5. Deploy!

### Deploy to Heroku

```bash
# Create Procfile
echo "web: streamlit run app.py --server.port $PORT" > Procfile

# Deploy
heroku create your-app-name
git push heroku main
```

### Deploy to AWS/GCP/Azure

Use Docker:

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

---

## 📈 Performance Optimization

### Tips for Production

1. **Caching:** Use Streamlit's `@st.cache_data` for database reads
2. **API Rate Limits:** Implement request throttling
3. **Database:** Migrate to PostgreSQL/MongoDB for scale
4. **Async Operations:** Use async/await for API calls
5. **Load Balancing:** Deploy multiple instances behind a load balancer

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Coding Standards

- Follow PEP 8 style guide
- Add docstrings to all functions
- Write unit tests for new features
- Update README with new features

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Contact

**Veract Consultancy Pvt Ltd**

- 📍 Address: 17, First Street, Tansi Nagar, Velachery, Chennai – 600042
- 📧 Email: info@veract.io
- 🌐 Website: www.veract.io
- 📱 Phone: +91-9789991565, +91-9962837650

---

## 🙏 Acknowledgments

- [Groq](https://groq.com/) for lightning-fast AI inference
- [LangGraph](https://python.langchain.com/docs/langgraph) for agent orchestration
- [Streamlit](https://streamlit.io/) for the amazing UI framework
- [Meta AI](https://ai.meta.com/) for Llama 3.3 model

---

## 📊 Project Status

- ✅ Phase 1: Core chatbot functionality - **Complete**
- ✅ Phase 2: Streamlit UI - **Complete**
- 🔄 Phase 3: Advanced analytics - **In Progress**
- 📋 Phase 4: Multi-user support - **Planned**
- 📋 Phase 5: Real-time notifications - **Planned**

---

## 🎯 Roadmap

### Version 2.0 (Q2 2025)
- [ ] Multi-language support (Hindi, Tamil, Telugu)
- [ ] Voice interface integration
- [ ] WhatsApp bot integration
- [ ] Advanced inventory management
- [ ] Predictive analytics

### Version 3.0 (Q3 2025)
- [ ] Mobile app (iOS/Android)
- [ ] Integration with payment gateways
- [ ] Automated reordering system
- [ ] Customer sentiment analysis
- [ ] AR product visualization

---



---

**Made with ❤️ by Veract Consultancy**

*Last Updated: November 22, 2025*