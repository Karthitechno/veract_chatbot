import json
import os
from groq import Groq
from datetime import datetime
from typing import Optional, Dict, List, Any, Annotated
from dataclasses import dataclass, field
from enum import Enum
import operator

# LangGraph imports
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict

# Initialize Groq client

import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Database paths
PRODUCTS_DB = "products.json"
SALES_DB = "sales.json"
VENDORS_DB = "vendors.json"

# Agent types
class AgentType(Enum):
    CONVERSATION_MANAGER = "conversation_manager"
    PRODUCT_AGENT = "product_agent"
    SALES_AGENT = "sales_agent"
    ANALYTICS_AGENT = "analytics_agent"
    VENDOR_AGENT = "vendor_agent"

# LangGraph State
class ConversationState(TypedDict):
    """State passed between nodes in the graph"""
    user_input: str
    agent_response: str
    intent: Optional[str]
    entities: Dict[str, Any]
    conversation_history: Annotated[List[Dict], operator.add]
    context: Dict[str, Any]
    pending_confirmation: Optional[Dict[str, Any]]
    validation_errors: List[str]
    tool_calls: List[Dict[str, Any]]
    requires_followup: bool

class SessionMemory:
    """Enhanced memory with context tracking"""
    def __init__(self):
        self.messages = []
        self.context = {
            "last_product": None,
            "last_product_id": None,
            "last_filters": {},
            "last_search_results": [],
            "current_topic": None,
            "user_preferences": {
                "price_range": None,
                "preferred_categories": [],
                "preferred_brands": []
            },
            "session_start": datetime.now().isoformat(),
            "customer_id": None,
            "last_sale": None,
            "conversation_count": 0
        }
        self.pending_actions = []
    
    def add_message(self, role: str, content: str):
        """Add message with timestamp"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.context["conversation_count"] += 1
    
    def update_context(self, key: str, value: Any):
        """Update specific context key"""
        self.context[key] = value
    
    def update_user_preferences(self, preference_type: str, value: Any):
        """Update user preferences"""
        if preference_type in self.context["user_preferences"]:
            self.context["user_preferences"][preference_type] = value
    
    def get_context_string(self) -> str:
        """Get formatted context"""
        return json.dumps(self.context, indent=2)
    
    def get_recent_messages(self, n: int = 5) -> List[Dict]:
        """Get last n messages"""
        return self.messages[-n:]
    
    def add_pending_action(self, action: Dict[str, Any]):
        """Add action that requires confirmation"""
        self.pending_actions.append(action)
    
    def get_pending_action(self) -> Optional[Dict[str, Any]]:
        """Get most recent pending action"""
        return self.pending_actions[-1] if self.pending_actions else None
    
    def clear_pending_actions(self):
        """Clear all pending actions"""
        self.pending_actions = []
    
    def reset(self):
        """Reset memory"""
        self.messages = []
        self.context = {
            "last_product": None,
            "last_product_id": None,
            "last_filters": {},
            "last_search_results": [],
            "current_topic": None,
            "user_preferences": {
                "price_range": None,
                "preferred_categories": [],
                "preferred_brands": []
            },
            "session_start": datetime.now().isoformat(),
            "customer_id": None,
            "last_sale": None,
            "conversation_count": 0
        }
        self.pending_actions = []

# Database utilities
def load_json(filepath: str) -> dict:
    """Load JSON database"""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
        except (json.JSONDecodeError, Exception) as e:
            print(f"Warning: Error loading {filepath}: {e}")
    return {"products": [], "sales": [], "vendors": []}

def save_json(filepath: str, data: dict) -> bool:
    """Save JSON database"""
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving {filepath}: {e}")
        return False

# Enhanced Tool functions
class ProductTools:
    """Enhanced product tools with fuzzy matching"""
    
    @staticmethod
    def search_products(query: str, category: Optional[str] = None, 
                       min_price: Optional[float] = None, 
                       max_price: Optional[float] = None,
                       min_rating: Optional[float] = None) -> List[dict]:
        """Enhanced search with flexible matching"""
        db = load_json(PRODUCTS_DB)
        results = []
        query_lower = query.lower() if query else ""
        
        for product in db.get("products", []):
            # Fuzzy matching
            name_match = query_lower in product.get("name", "").lower()
            brand_match = query_lower in product.get("brand", "").lower()
            category_match = query_lower in product.get("category", "").lower()
            desc_match = query_lower in product.get("description", "").lower()
            
            if name_match or brand_match or category_match or desc_match:
                if category and product.get("category") != category:
                    continue
                
                # Apply filters
                if min_rating and product.get("rating", 0) < min_rating:
                    continue
                
                results.append(product)
        
        return results
    
    @staticmethod
    def get_product_by_id(product_id: str) -> dict:
        """Get product with validation"""
        db = load_json(PRODUCTS_DB)
        for product in db.get("products", []):
            if product.get("id") == product_id:
                return product
        return {}
    
    @staticmethod
    def list_products_by_category(category: str) -> List[dict]:
        """List products with category validation"""
        valid_categories = ["Electronics", "Grocery", "Fashion", "Home", "Sports"]
        if category not in valid_categories:
            return []
        
        db = load_json(PRODUCTS_DB)
        return [p for p in db.get("products", []) if p.get("category") == category]
    
    @staticmethod
    def validate_product_data(product_data: dict) -> tuple[bool, List[str]]:
        """Validate product data before creation"""
        errors = []
        
        if not product_data.get("id"):
            errors.append("Product ID is required")
        if not product_data.get("name"):
            errors.append("Product name is required")
        if not product_data.get("category"):
            errors.append("Category is required")
        
        valid_categories = ["Electronics", "Grocery", "Fashion", "Home", "Sports"]
        if product_data.get("category") not in valid_categories:
            errors.append(f"Category must be one of: {', '.join(valid_categories)}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def create_product(product_data: dict) -> tuple[bool, str, List[str]]:
        """Create product with validation"""
        # Validate first
        is_valid, errors = ProductTools.validate_product_data(product_data)
        if not is_valid:
            return False, "Validation failed", errors
        
        db = load_json(PRODUCTS_DB)
        
        # Check duplicates
        if any(p.get("id") == product_data.get("id") for p in db.get("products", [])):
            return False, "Product ID already exists", ["Duplicate ID"]
        
        db.setdefault("products", []).append(product_data)
        success = save_json(PRODUCTS_DB, db)
        
        return success, "Product created successfully" if success else "Failed to save", []
    
    @staticmethod
    def update_product(product_id: str, updates: dict) -> tuple[bool, str]:
        """Update product with validation"""
        db = load_json(PRODUCTS_DB)
        
        for product in db.get("products", []):
            if product.get("id") == product_id:
                product.update(updates)
                success = save_json(PRODUCTS_DB, db)
                return success, "Product updated successfully" if success else "Failed to update"
        
        return False, "Product not found"
    
    @staticmethod
    def get_top_rated_products(limit: int = 5, category: Optional[str] = None) -> List[dict]:
        """Get top rated products"""
        db = load_json(PRODUCTS_DB)
        products = db.get("products", [])
        
        if category:
            products = [p for p in products if p.get("category") == category]
        
        return sorted(products, key=lambda p: p.get("rating", 0), reverse=True)[:limit]

class SalesTools:
    """Enhanced sales tools"""
    
    @staticmethod
    def search_sales(customer_id: Optional[str] = None, 
                    status: Optional[str] = None,
                    date_from: Optional[str] = None,
                    date_to: Optional[str] = None) -> List[dict]:
        """Enhanced sales search"""
        db = load_json(SALES_DB)
        results = []
        
        for sale in db.get("sales", []):
            if customer_id and sale.get("customer_id") != customer_id:
                continue
            if status and sale.get("payment_status") != status:
                continue
            results.append(sale)
        
        return results
    
    @staticmethod
    def get_sale_by_id(sale_id: str) -> dict:
        """Get sale details"""
        db = load_json(SALES_DB)
        for sale in db.get("sales", []):
            if sale.get("id") == sale_id:
                return sale
        return {}
    
    @staticmethod
    def validate_sale_data(sale_data: dict) -> tuple[bool, List[str]]:
        """Validate sale data"""
        errors = []
        
        if not sale_data.get("id"):
            errors.append("Sale ID is required")
        if not sale_data.get("customer_id"):
            errors.append("Customer ID is required")
        if not sale_data.get("total") or sale_data.get("total") <= 0:
            errors.append("Total amount must be greater than 0")
        
        valid_statuses = ["PAID", "PENDING", "CANCELLED"]
        if sale_data.get("payment_status") not in valid_statuses:
            errors.append(f"Payment status must be one of: {', '.join(valid_statuses)}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def create_sale(sale_data: dict) -> tuple[bool, str, List[str]]:
        """Create sale with validation"""
        is_valid, errors = SalesTools.validate_sale_data(sale_data)
        if not is_valid:
            return False, "Validation failed", errors
        
        db = load_json(SALES_DB)
        
        # Add timestamp
        sale_data["created_at"] = datetime.now().isoformat()
        
        db.setdefault("sales", []).append(sale_data)
        success = save_json(SALES_DB, db)
        
        return success, "Sale created successfully" if success else "Failed to save", []
    
    @staticmethod
    def update_sale(sale_id: str, updates: dict) -> tuple[bool, str]:
        """Update sale"""
        db = load_json(SALES_DB)
        
        for sale in db.get("sales", []):
            if sale.get("id") == sale_id:
                sale.update(updates)
                success = save_json(SALES_DB, db)
                return success, "Sale updated successfully" if success else "Failed to update"
        
        return False, "Sale not found"

class AnalyticsTools:
    """Enhanced analytics tools"""
    
    @staticmethod
    def get_top_products(limit: int = 5) -> List[Dict[str, Any]]:
        """Get top selling products with details"""
        db_sales = load_json(SALES_DB)
        db_products = load_json(PRODUCTS_DB)
        
        product_sales = {}
        for sale in db_sales.get("sales", []):
            for item in sale.get("items", []):
                variant_id = item.get("variant_id")
                qty = item.get("qty", 0)
                product_sales[variant_id] = product_sales.get(variant_id, 0) + qty
        
        sorted_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)
        
        # Get product details
        result = []
        for variant_id, qty in sorted_products[:limit]:
            result.append({"variant_id": variant_id, "quantity_sold": qty})
        
        return result
    
    @staticmethod
    def get_sales_summary() -> dict:
        """Comprehensive sales summary"""
        db = load_json(SALES_DB)
        sales = db.get("sales", [])
        
        total_sales = len(sales)
        total_revenue = sum(s.get("total", 0) for s in sales)
        paid_sales = len([s for s in sales if s.get("payment_status") == "PAID"])
        pending_sales = len([s for s in sales if s.get("payment_status") == "PENDING"])
        
        return {
            "total_sales": total_sales,
            "total_revenue": total_revenue,
            "paid_sales": paid_sales,
            "pending_sales": pending_sales,
            "cancelled_sales": total_sales - paid_sales - pending_sales,
            "average_transaction": total_revenue / total_sales if total_sales > 0 else 0,
            "payment_completion_rate": (paid_sales / total_sales * 100) if total_sales > 0 else 0
        }
    
    @staticmethod
    def recommend_products(category: Optional[str] = None, 
                          based_on: str = "rating",
                          limit: int = 5) -> List[dict]:
        """Enhanced product recommendations"""
        db = load_json(PRODUCTS_DB)
        products = db.get("products", [])
        
        if category:
            products = [p for p in products if p.get("category") == category]
        
        if based_on == "rating":
            return sorted(products, key=lambda p: p.get("rating", 0), reverse=True)[:limit]
        elif based_on == "sales":
            return AnalyticsTools.get_top_products(limit)
        
        return products[:limit]

class VendorTools:
    """Vendor management tools"""
    
    @staticmethod
    def list_vendors() -> List[dict]:
        """List all vendors"""
        db = load_json(VENDORS_DB)
        return db.get("vendors", [])
    
    @staticmethod
    def get_vendor_by_id(vendor_id: str) -> dict:
        """Get vendor details"""
        db = load_json(VENDORS_DB)
        for vendor in db.get("vendors", []):
            if vendor.get("id") == vendor_id:
                return vendor
        return {}
    
    @staticmethod
    def search_vendors(query: str) -> List[dict]:
        """Search vendors by name"""
        db = load_json(VENDORS_DB)
        query_lower = query.lower()
        return [v for v in db.get("vendors", []) 
                if query_lower in v.get("name", "").lower()]

# Enhanced NLU for intent and entity extraction
class NaturalLanguageUnderstanding:
    """Extract intent and entities from user input"""
    
    @staticmethod
    def extract_intent_and_entities(user_input: str, session_memory: SessionMemory) -> Dict[str, Any]:
        """Use LLM to extract intent and entities"""
        
        system_prompt = f"""You are an intent classifier for a sales chatbot. Analyze the user's message and extract:
1. Intent (one of: search_product, get_product_details, create_product, update_product, search_sales, 
   create_sale, update_sale, get_analytics, get_recommendations, vendor_query, general_chat)
2. Entities (product names, categories, IDs, prices, dates, customer IDs, statuses)

Valid categories: Electronics, Grocery, Fashion, Home, Sports
Valid payment statuses: PAID, PENDING, CANCELLED

Current conversation context:
{session_memory.get_context_string()}

User message: {user_input}

Respond ONLY with a JSON object in this format:
{{
  "intent": "intent_name",
  "entities": {{
    "product_name": "...",
    "category": "...",
    "product_id": "...",
    "price_min": number,
    "price_max": number,
    "rating_min": number,
    "customer_id": "...",
    "sale_id": "...",
    "status": "...",
    "limit": number
  }},
  "requires_clarification": false,
  "clarification_needed": []
}}"""

        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": system_prompt}],
                temperature=0.1,
                
            )
            
            response = completion.choices[0].message.content
            
            # Clean response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            result = json.loads(response)
            return result
        
        except Exception as e:
            print(f"NLU Error: {e}")
            # Fallback to basic keyword matching
            return NaturalLanguageUnderstanding._fallback_intent_detection(user_input)
    
    @staticmethod
    def _fallback_intent_detection(user_input: str) -> Dict[str, Any]:
        """Fallback intent detection"""
        user_lower = user_input.lower()
        
        intent = "general_chat"
        entities = {}
        
        if any(word in user_lower for word in ["search", "find", "show", "look", "product"]):
            intent = "search_product"
        elif any(word in user_lower for word in ["sale", "order", "purchase", "transaction"]):
            intent = "search_sales"
        elif any(word in user_lower for word in ["recommend", "suggest", "best", "top"]):
            intent = "get_recommendations"
        elif any(word in user_lower for word in ["analytics", "report", "summary", "stats"]):
            intent = "get_analytics"
        elif any(word in user_lower for word in ["vendor", "supplier"]):
            intent = "vendor_query"
        elif any(word in user_lower for word in ["create", "add"]):
            if "product" in user_lower:
                intent = "create_product"
            elif "sale" in user_lower:
                intent = "create_sale"
        
        return {
            "intent": intent,
            "entities": entities,
            "requires_clarification": False,
            "clarification_needed": []
        }

# LangGraph Nodes
class ChatbotNodes:
    """Node functions for LangGraph"""
    
    def __init__(self, session_memory: SessionMemory):
        self.session_memory = session_memory
        self.nlu = NaturalLanguageUnderstanding()
        self.product_tools = ProductTools()
        self.sales_tools = SalesTools()
        self.analytics_tools = AnalyticsTools()
        self.vendor_tools = VendorTools()
    
    def understand_input(self, state: ConversationState) -> ConversationState:
        """Node: Extract intent and entities"""
        user_input = state["user_input"]
        
        # Check for confirmation keywords
        if any(word in user_input.lower() for word in ["yes", "confirm", "ok", "proceed", "sure"]):
            pending = self.session_memory.get_pending_action()
            if pending:
                state["intent"] = "confirm_action"
                state["entities"] = pending
                return state
        
        if any(word in user_input.lower() for word in ["no", "cancel", "abort"]):
            state["intent"] = "cancel_action"
            return state
        
        # Extract intent and entities
        nlu_result = self.nlu.extract_intent_and_entities(user_input, self.session_memory)
        
        state["intent"] = nlu_result.get("intent", "general_chat")
        state["entities"] = nlu_result.get("entities", {})
        state["requires_followup"] = nlu_result.get("requires_clarification", False)
        
        return state
    
    def validate_input(self, state: ConversationState) -> ConversationState:
        """Node: Validate extracted entities"""
        intent = state["intent"]
        entities = state["entities"]
        errors = []
        
        # Category validation
        if "category" in entities and entities["category"]:
            valid_categories = ["Electronics", "Grocery", "Fashion", "Home", "Sports"]
            if entities["category"] not in valid_categories:
                errors.append(f"Invalid category. Choose from: {', '.join(valid_categories)}")
        
        # Status validation
        if "status" in entities and entities["status"]:
            valid_statuses = ["PAID", "PENDING", "CANCELLED"]
            if entities["status"] not in valid_statuses:
                errors.append(f"Invalid status. Choose from: {', '.join(valid_statuses)}")
        
        state["validation_errors"] = errors
        return state
    
    def route_to_agent(self, state: ConversationState) -> str:
        """Routing function for graph"""
        intent = state["intent"]
        
        if state.get("validation_errors"):
            return "handle_validation_errors"
        
        if intent in ["search_product", "get_product_details", "create_product", "update_product"]:
            return "product_agent"
        elif intent in ["search_sales", "create_sale", "update_sale"]:
            return "sales_agent"
        elif intent in ["get_analytics", "get_recommendations"]:
            return "analytics_agent"
        elif intent in ["vendor_query"]:
            return "vendor_agent"
        elif intent in ["confirm_action"]:
            return "execute_confirmation"
        elif intent in ["cancel_action"]:
            return "handle_cancellation"
        else:
            return "general_agent"
    
    def product_agent_node(self, state: ConversationState) -> ConversationState:
        """Node: Handle product operations"""
        intent = state["intent"]
        entities = state["entities"]
        
        if intent == "search_product":
            results = self.product_tools.search_products(
                query=entities.get("product_name", ""),
                category=entities.get("category"),
                min_rating=entities.get("rating_min")
            )
            
            self.session_memory.update_context("last_search_results", results)
            self.session_memory.update_context("last_filters", entities)
            
            if results:
                response = self._format_product_results(results)
            else:
                response = "I couldn't find any products matching your search. Could you try different keywords or specify a category?"
            
            state["agent_response"] = response
        
        elif intent == "get_product_details":
            product_id = entities.get("product_id")
            if not product_id:
                # Try to get from context
                product_id = self.session_memory.context.get("last_product_id")
            
            if product_id:
                product = self.product_tools.get_product_by_id(product_id)
                if product:
                    response = self._format_product_details(product)
                else:
                    response = f"I couldn't find a product with ID '{product_id}'. Please check the ID and try again."
            else:
                response = "Could you please provide the product ID? You can say something like 'show details for prod_001'."
            
            state["agent_response"] = response
        
        elif intent == "create_product":
            # Prepare pending action for confirmation
            product_data = {
                "id": entities.get("product_id"),
                "name": entities.get("product_name"),
                "category": entities.get("category"),
                "brand": entities.get("brand"),
                "description": entities.get("description", ""),
                "rating": entities.get("rating_min", 0),
                "company_id": "comp_001",
                "variants": []
            }
            
            # Validate
            is_valid, errors = self.product_tools.validate_product_data(product_data)
            
            if not is_valid:
                response = f"I need some more information to create this product:\n"
                for error in errors:
                    response += f"• {error}\n"
                response += "\nPlease provide the missing details."
                state["agent_response"] = response
            else:
                # Store for confirmation
                self.session_memory.add_pending_action({
                    "action": "create_product",
                    "data": product_data
                })
                
                response = f"I'm ready to create a new product with these details:\n\n"
                response += f"• Product ID: {product_data['id']}\n"
                response += f"• Name: {product_data['name']}\n"
                response += f"• Category: {product_data['category']}\n"
                response += f"• Brand: {product_data.get('brand', 'N/A')}\n\n"
                response += "Would you like me to proceed with creating this product? (Yes/No)"
                
                state["agent_response"] = response
                state["pending_confirmation"] = product_data
        
        elif intent == "get_recommendations":
            category = entities.get("category")
            limit = entities.get("limit", 5)
            
            recommendations = self.analytics_tools.recommend_products(
                category=category,
                based_on="rating",
                limit=limit
            )
            
            if recommendations:
                response = "Here are my top recommendations"
                if category:
                    response += f" for {category}"
                response += ":\n\n"
                response += self._format_product_results(recommendations)
            else:
                response = "I don't have enough data to make recommendations right now."
            
            state["agent_response"] = response
        
        return state
    
    def sales_agent_node(self, state: ConversationState) -> ConversationState:
        """Node: Handle sales operations"""
        intent = state["intent"]
        entities = state["entities"]
        
        if intent == "search_sales":
            results = self.sales_tools.search_sales(
                customer_id=entities.get("customer_id"),
                status=entities.get("status")
            )
            
            self.session_memory.update_context("last_sale", results[0] if results else None)
            
            if results:
                response = self._format_sales_results(results)
            else:
                response = "I couldn't find any sales records matching your criteria. Try adjusting your search parameters."
            
            state["agent_response"] = response
        
        elif intent == "create_sale":
            sale_data = {
                "id": entities.get("sale_id", f"sale_{datetime.now().strftime('%Y%m%d%H%M%S')}"),
                "customer_id": entities.get("customer_id"),
                "total": entities.get("total", 0),
                "discount": entities.get("discount", 0),
                "payment_status": entities.get("status", "PENDING"),
                "company_id": "comp_001",
                "items": []
            }
            
            is_valid, errors = self.sales_tools.validate_sale_data(sale_data)
            
            if not is_valid:
                response = "I need more information to create this sale:\n"
                for error in errors:
                    response += f"• {error}\n"
                response += "\nPlease provide the missing details."
                state["agent_response"] = response
            else:
                self.session_memory.add_pending_action({
                    "action": "create_sale",
                    "data": sale_data
                })
                
                response = f"I'm ready to create a new sale:\n\n"
                response += f"• Sale ID: {sale_data['id']}\n"
                response += f"• Customer ID: {sale_data['customer_id']}\n"
                response += f"• Total: ₹{sale_data['total']}\n"
                response += f"• Status: {sale_data['payment_status']}\n\n"
                response += "Shall I proceed with creating this sale? (Yes/No)"
                
                state["agent_response"] = response
                state["pending_confirmation"] = sale_data
        
        return state
    
    def analytics_agent_node(self, state: ConversationState) -> ConversationState:
        """Node: Handle analytics queries"""
        intent = state["intent"]
        
        if intent == "get_analytics":
            summary = self.analytics_tools.get_sales_summary()
            top_products = self.analytics_tools.get_top_products(limit=5)
            
            response = "📊 **Sales Analytics Summary**\n\n"
            response += f"• Total Sales: {summary['total_sales']}\n"
            response += f"• Total Revenue: ₹{summary['total_revenue']:,.2f}\n"
            response += f"• Paid Sales: {summary['paid_sales']}\n"
            response += f"• Pending Sales: {summary['pending_sales']}\n"
            response += f"• Average Transaction: ₹{summary['average_transaction']:,.2f}\n"
            response += f"• Payment Completion Rate: {summary['payment_completion_rate']:.1f}%\n\n"
            
            if top_products:
                response += "🔥 **Top Selling Products:**\n"
                for idx, prod in enumerate(top_products, 1):
                    response += f"{idx}. Variant ID: {prod['variant_id']} - Sold: {prod['quantity_sold']} units\n"
            
            state["agent_response"] = response
        
        return state
    
    def vendor_agent_node(self, state: ConversationState) -> ConversationState:
        """Node: Handle vendor queries"""
        entities = state["entities"]
        
        if entities.get("vendor_id"):
            vendor = self.vendor_tools.get_vendor_by_id(entities["vendor_id"])
            if vendor:
                response = self._format_vendor_details(vendor)
            else:
                response = f"I couldn't find a vendor with ID '{entities['vendor_id']}'."
        else:
            vendors = self.vendor_tools.list_vendors()
            if vendors:
                response = "Here are all our vendors:\n\n"
                response += self._format_vendor_list(vendors)
            else:
                response = "No vendors found in the database."
        
        state["agent_response"] = response
        return state
    
    def general_agent_node(self, state: ConversationState) -> ConversationState:
        """Node: Handle general conversation"""
        user_input = state["user_input"]
        
        system_prompt = f"""You are a friendly sales assistant for Veract Consultancy. 
The user said: {user_input}

Respond naturally and helpfully. You can help with:
- Searching products
- Viewing sales records
- Getting analytics and recommendations
- Managing vendors

Context: {self.session_memory.get_context_string()}

Keep your response conversational and under 100 words."""

        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.7,
                
            )
            
            response = completion.choices[0].message.content
            state["agent_response"] = response
        except Exception as e:
            state["agent_response"] = "I'm here to help! You can ask me to search for products, check sales, get analytics, or manage vendors. What would you like to do?"
        
        return state
    
    def execute_confirmation_node(self, state: ConversationState) -> ConversationState:
        """Node: Execute confirmed actions"""
        pending = self.session_memory.get_pending_action()
        
        if not pending:
            state["agent_response"] = "There's nothing pending to confirm. How else can I help you?"
            return state
        
        action = pending.get("action")
        data = pending.get("data")
        
        if action == "create_product":
            success, message, errors = self.product_tools.create_product(data)
            if success:
                response = f"✅ Great! I've successfully created the product '{data['name']}' (ID: {data['id']}).\n\n"
                response += "The product is now in your inventory. What would you like to do next?"
            else:
                response = f"❌ Sorry, I couldn't create the product: {message}\n"
                if errors:
                    for error in errors:
                        response += f"• {error}\n"
            
            self.session_memory.clear_pending_actions()
            state["agent_response"] = response
        
        elif action == "create_sale":
            success, message, errors = self.sales_tools.create_sale(data)
            if success:
                response = f"✅ Perfect! I've created the sale record (ID: {data['id']}).\n\n"
                response += f"• Customer: {data['customer_id']}\n"
                response += f"• Total: ₹{data['total']}\n"
                response += f"• Status: {data['payment_status']}\n\n"
                response += "Is there anything else you need help with?"
            else:
                response = f"❌ I couldn't create the sale: {message}\n"
                if errors:
                    for error in errors:
                        response += f"• {error}\n"
            
            self.session_memory.clear_pending_actions()
            state["agent_response"] = response
        
        elif action == "update_product":
            product_id = data.get("product_id")
            updates = data.get("updates")
            success, message = self.product_tools.update_product(product_id, updates)
            
            if success:
                response = f"✅ Done! I've updated the product (ID: {product_id}).\n\n"
                response += "The changes have been saved. Anything else?"
            else:
                response = f"❌ Sorry, I couldn't update the product: {message}"
            
            self.session_memory.clear_pending_actions()
            state["agent_response"] = response
        
        elif action == "update_sale":
            sale_id = data.get("sale_id")
            updates = data.get("updates")
            success, message = self.sales_tools.update_sale(sale_id, updates)
            
            if success:
                response = f"✅ All set! I've updated the sale (ID: {sale_id}).\n\n"
                response += "The changes are now saved. What's next?"
            else:
                response = f"❌ I couldn't update the sale: {message}"
            
            self.session_memory.clear_pending_actions()
            state["agent_response"] = response
        
        return state
    
    def handle_cancellation_node(self, state: ConversationState) -> ConversationState:
        """Node: Handle action cancellation"""
        self.session_memory.clear_pending_actions()
        state["agent_response"] = "No problem! I've cancelled that action. What else can I help you with?"
        return state
    
    def handle_validation_errors_node(self, state: ConversationState) -> ConversationState:
        """Node: Handle validation errors"""
        errors = state.get("validation_errors", [])
        
        response = "I noticed some issues with your request:\n\n"
        for error in errors:
            response += f"• {error}\n"
        response += "\nCould you please provide the correct information?"
        
        state["agent_response"] = response
        return state
    
    # Formatting helpers
    def _format_product_results(self, products: List[dict]) -> str:
        """Format product list"""
        if not products:
            return "No products found."
        
        response = f"I found {len(products)} product(s):\n\n"
        for idx, product in enumerate(products[:10], 1):  # Limit to 10
            response += f"{idx}. **{product.get('name', 'Unknown')}**\n"
            response += f"   • ID: {product.get('id')}\n"
            response += f"   • Category: {product.get('category', 'N/A')}\n"
            response += f"   • Brand: {product.get('brand', 'N/A')}\n"
            response += f"   • Rating: {'⭐' * int(product.get('rating', 0))}\n"
            response += f"   • Description: {product.get('description', 'No description')}\n\n"
        
        if len(products) > 10:
            response += f"...and {len(products) - 10} more products.\n"
        
        return response
    
    def _format_product_details(self, product: dict) -> str:
        """Format detailed product info"""
        response = f"📦 **Product Details**\n\n"
        response += f"**{product.get('name', 'Unknown')}**\n\n"
        response += f"• ID: {product.get('id')}\n"
        response += f"• Category: {product.get('category', 'N/A')}\n"
        response += f"• Brand: {product.get('brand', 'N/A')}\n"
        response += f"• Rating: {product.get('rating', 0)}/5 {'⭐' * int(product.get('rating', 0))}\n"
        response += f"• Description: {product.get('description', 'No description available')}\n"
        
        if product.get('variants'):
            response += f"\n**Available Variants:** {len(product['variants'])}\n"
        
        return response
    
    def _format_sales_results(self, sales: List[dict]) -> str:
        """Format sales list"""
        if not sales:
            return "No sales found."
        
        response = f"I found {len(sales)} sale(s):\n\n"
        for idx, sale in enumerate(sales[:10], 1):
            response += f"{idx}. **Sale {sale.get('id')}**\n"
            response += f"   • Customer: {sale.get('customer_id')}\n"
            response += f"   • Total: ₹{sale.get('total', 0):,.2f}\n"
            response += f"   • Status: {sale.get('payment_status', 'UNKNOWN')}\n"
            response += f"   • Date: {sale.get('created_at', 'N/A')}\n\n"
        
        if len(sales) > 10:
            response += f"...and {len(sales) - 10} more sales.\n"
        
        return response
    
    def _format_vendor_list(self, vendors: List[dict]) -> str:
        """Format vendor list"""
        response = ""
        for idx, vendor in enumerate(vendors, 1):
            response += f"{idx}. **{vendor.get('name', 'Unknown')}**\n"
            response += f"   • ID: {vendor.get('id')}\n"
            response += f"   • Contact: {vendor.get('contact', 'N/A')}\n\n"
        return response
    
    def _format_vendor_details(self, vendor: dict) -> str:
        """Format vendor details"""
        response = f"🏢 **Vendor Details**\n\n"
        response += f"**{vendor.get('name', 'Unknown')}**\n\n"
        response += f"• ID: {vendor.get('id')}\n"
        response += f"• Contact: {vendor.get('contact', 'N/A')}\n"
        response += f"• Email: {vendor.get('email', 'N/A')}\n"
        response += f"• Phone: {vendor.get('phone', 'N/A')}\n"
        return response

# Build LangGraph
def build_conversation_graph(session_memory: SessionMemory) -> StateGraph:
    """Build the conversation flow graph"""
    
    nodes = ChatbotNodes(session_memory)
    
    # Create graph
    workflow = StateGraph(ConversationState)
    
    # Add nodes
    workflow.add_node("understand", nodes.understand_input)
    workflow.add_node("validate", nodes.validate_input)
    workflow.add_node("product_agent", nodes.product_agent_node)
    workflow.add_node("sales_agent", nodes.sales_agent_node)
    workflow.add_node("analytics_agent", nodes.analytics_agent_node)
    workflow.add_node("vendor_agent", nodes.vendor_agent_node)
    workflow.add_node("general_agent", nodes.general_agent_node)
    workflow.add_node("execute_confirmation", nodes.execute_confirmation_node)
    workflow.add_node("handle_cancellation", nodes.handle_cancellation_node)
    workflow.add_node("handle_validation_errors", nodes.handle_validation_errors_node)
    
    # Set entry point
    workflow.set_entry_point("understand")
    
    # Add edges
    workflow.add_edge("understand", "validate")
    
    # Conditional routing from validate
    workflow.add_conditional_edges(
        "validate",
        nodes.route_to_agent,
        {
            "product_agent": "product_agent",
            "sales_agent": "sales_agent",
            "analytics_agent": "analytics_agent",
            "vendor_agent": "vendor_agent",
            "general_agent": "general_agent",
            "execute_confirmation": "execute_confirmation",
            "handle_cancellation": "handle_cancellation",
            "handle_validation_errors": "handle_validation_errors"
        }
    )
    
    # All agents end
    workflow.add_edge("product_agent", END)
    workflow.add_edge("sales_agent", END)
    workflow.add_edge("analytics_agent", END)
    workflow.add_edge("vendor_agent", END)
    workflow.add_edge("general_agent", END)
    workflow.add_edge("execute_confirmation", END)
    workflow.add_edge("handle_cancellation", END)
    workflow.add_edge("handle_validation_errors", END)
    
    return workflow.compile()

# Main Chatbot Class
class EnhancedChatbot:
    """Main chatbot with LangGraph orchestration"""
    
    def __init__(self):
        self.session_memory = SessionMemory()
        self.graph = build_conversation_graph(self.session_memory)
    
    def process_message(self, user_input: str) -> str:
        """Process user message through graph"""
        
        # Add to memory
        self.session_memory.add_message("user", user_input)
        
        # Initialize state
        initial_state: ConversationState = {
            "user_input": user_input,
            "agent_response": "",
            "intent": None,
            "entities": {},
            "conversation_history": [{"role": "user", "content": user_input}],
            "context": self.session_memory.context,
            "pending_confirmation": None,
            "validation_errors": [],
            "tool_calls": [],
            "requires_followup": False
        }
        
        # Run through graph
        try:
            result = self.graph.invoke(initial_state)
            response = result.get("agent_response", "I'm not sure how to help with that. Could you rephrase?")
            
            # Add to memory
            self.session_memory.add_message("assistant", response)
            
            return response
        
        except Exception as e:
            error_msg = f"I encountered an error: {str(e)}. Could you try again?"
            print(f"Graph Error: {e}")
            return error_msg
    
    def reset(self):
        """Reset chatbot memory"""
        self.session_memory.reset()
        self.graph = build_conversation_graph(self.session_memory)

# Initialize sample data
def initialize_sample_data():
    """Initialize sample data if needed"""
    products_db = load_json(PRODUCTS_DB)
    if not products_db.get("products") or len(products_db.get("products", [])) < 3:
        print("Initializing products database...")
        sample_products = {
            "products": [
                {
                    "id": "prod_001",
                    "company_id": "comp_001",
                    "name": "Apple iPhone 15 Pro",
                    "category": "Electronics",
                    "description": "Latest flagship smartphone with A17 Pro chip and titanium design",
                    "brand": "Apple",
                    "rating": 4.8,
                    "variants": []
                },
                {
                    "id": "prod_002",
                    "company_id": "comp_001",
                    "name": "Samsung Galaxy S24 Ultra",
                    "category": "Electronics",
                    "description": "Premium Android smartphone with S Pen and 200MP camera",
                    "brand": "Samsung",
                    "rating": 4.7,
                    "variants": []
                },
                {
                    "id": "prod_003",
                    "company_id": "comp_001",
                    "name": "Nike Air Max 270",
                    "category": "Sports",
                    "description": "Comfortable running shoes with Max Air cushioning",
                    "brand": "Nike",
                    "rating": 4.5,
                    "variants": []
                },
                {
                    "id": "prod_004",
                    "company_id": "comp_001",
                    "name": "Sony WH-1000XM5",
                    "category": "Electronics",
                    "description": "Premium noise-cancelling wireless headphones",
                    "brand": "Sony",
                    "rating": 4.9,
                    "variants": []
                },
                {
                    "id": "prod_005",
                    "company_id": "comp_001",
                    "name": "Levi's 501 Original Jeans",
                    "category": "Fashion",
                    "description": "Classic straight fit denim jeans",
                    "brand": "Levi's",
                    "rating": 4.6,
                    "variants": []
                }
            ]
        }
        save_json(PRODUCTS_DB, sample_products)
        print("✅ Products database initialized!\n")
    
    sales_db = load_json(SALES_DB)
    if not sales_db.get("sales") or len(sales_db.get("sales", [])) < 2:
        print("Initializing sales database...")
        sample_sales = {
            "sales": [
                {
                    "id": "sale_001",
                    "company_id": "comp_001",
                    "customer_id": "cust_001",
                    "invoice_number": "INV-2025-001",
                    "total": 79999,
                    "discount": 0,
                    "payment_status": "PAID",
                    "created_at": "2025-02-15T14:22:00Z",
                    "items": []
                },
                {
                    "id": "sale_002",
                    "company_id": "comp_001",
                    "customer_id": "cust_002",
                    "invoice_number": "INV-2025-002",
                    "total": 24999,
                    "discount": 1000,
                    "payment_status": "PENDING",
                    "created_at": "2025-02-16T10:15:00Z",
                    "items": []
                }
            ]
        }
        save_json(SALES_DB, sample_sales)
        print("✅ Sales database initialized!\n")
    
    vendors_db = load_json(VENDORS_DB)
    if not vendors_db.get("vendors"):
        print("Initializing vendors database...")
        sample_vendors = {
            "vendors": [
                {
                    "id": "vendor_001",
                    "name": "Tech Supplies India",
                    "contact": "Rajesh Kumar",
                    "email": "rajesh@techsupplies.in",
                    "phone": "+91-9876543210"
                },
                {
                    "id": "vendor_002",
                    "name": "Fashion Wholesale Co",
                    "contact": "Priya Sharma",
                    "email": "priya@fashionwholesale.com",
                    "phone": "+91-9876543211"
                }
            ]
        }
        save_json(VENDORS_DB, sample_vendors)
        print("✅ Vendors database initialized!\n")

# Main application
def main():
    """Main application loop"""
    print("=" * 60)
    print("🤖 Veract AI Sales Assistant - Enhanced with LangGraph")
    print("=" * 60)
    print("\nHello! I'm your intelligent sales assistant. I can help you with:")
    print("  • 🔍 Search and find products")
    print("  • 📦 View product details and recommendations")
    print("  • 💰 Check sales records and transactions")
    print("  • 📊 Get analytics and insights")
    print("  • 🏢 Manage vendor information")
    print("  • ➕ Create and update products and sales")
    print("\nJust chat naturally - I'll understand what you need!")
    print("\nCommands: 'quit' to exit | 'reset' to start fresh")
    print("=" * 60 + "\n")
    
    try:
        initialize_sample_data()
    except Exception as e:
        print(f"⚠️  Error initializing data: {e}\n")
    
    chatbot = EnhancedChatbot()
    
    while True:
        try:
            user_input = input("\n💬 You: ").strip()
            
            if user_input.lower() in ["quit", "exit", "bye"]:
                print("\n👋 Thanks for using Veract AI! Have a great day!")
                break
            
            if user_input.lower() == "reset":
                chatbot.reset()
                print("\n✅ Memory reset! Starting fresh conversation.")
                continue
            
            if not user_input:
                continue
            
            print("\n🤖 Assistant: ", end="")
            response = chatbot.process_message(user_input)
            print(response)
        
        except KeyboardInterrupt:
            print("\n\n👋 Chat interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again or type 'reset' to start fresh.")
            continue

if __name__ == "__main__":
    main()