import google.generativeai as genai
import json
import os
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
import streamlit as st
from typing import Dict, List, Optional
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIHandler:
    def __init__(self):
        self.configured = False
        self.model_name = "gemini-2.5-flash"  # Correct stable model name
        self.api_key = None
        self.last_error = None
        # --- Add attributes for separate models ---
        self.analysis_model = None # Keep analysis on flash
        # If you wanted separate search model:
        # self.search_model_name = "gemini-1.5-flash-lite"
        # self.search_model = None
        # ------------------------------------------
        self.configure_api()

    def configure_api(self):
        """Simple and robust API configuration."""
        try:
            # Method 1: Streamlit secrets
            if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
                self.api_key = st.secrets['GEMINI_API_KEY'].strip()
                logger.info("📁 Found API key in Streamlit secrets")

            # Method 2: Environment variable
            elif 'GEMINI_API_KEY' in os.environ:
                self.api_key = os.environ['GEMINI_API_KEY'].strip()
                logger.info("🌐 Found API key in environment variable")

            else:
                logger.warning("❌ No API key found in secrets or environment")
                self.configured = False
                self.last_error = "No API key found"
                return

            # Validate API key
            if not self.api_key:
                self.last_error = "API key is empty"; logger.error(self.last_error); self.configured = False; return
            if len(self.api_key) < 20:
                self.last_error = f"API key too short: {len(self.api_key)} chars"; logger.error(self.last_error); self.configured = False; return

            genai.configure(api_key=self.api_key)

            # Quick test and initialize models
            try:
                list(genai.list_models()) # Test connection
                # --- Initialize model objects ---
                self.analysis_model = genai.GenerativeModel(self.model_name)
                # If using separate search model:
                # self.search_model = genai.GenerativeModel(self.search_model_name)
                # --------------------------------
                self.configured = True
                logger.info("✅ API configuration successful & models initialized!")

            except Exception as test_error:
                self.last_error = f"API test/model init failed: {str(test_error)}"
                logger.error(f"❌ {self.last_error}")
                self.configured = False

        except Exception as e:
            self.last_error = f"Configuration error: {str(e)}"
            logger.error(f"❌ Configuration failed: {e}")
            self.configured = False

    def get_api_status(self):
        """Get API status for debugging."""
        return {
            "configured": self.configured,
            "model": self.model_name, # Or report both if using two models
            "has_api_key": bool(self.api_key),
            "api_key_length": len(self.api_key) if self.api_key else 0,
            "last_error": self.last_error
        }


   # In ai_handler.py

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def find_new_product_with_ai(self, query: str) -> Dict:
        """AI product search, aiming to fetch ALL ingredients for accuracy."""
        logger.info(f"🔍 AI Searching for: '{query}'")

        if not self.configured:
            logger.info("🔄 Using mock data - API not configured")
            return self._mock_product_search(query)

        # Use the correct model object (assuming analysis_model handles search)
        model_to_use = self.analysis_model
        if not model_to_use:
                logger.error("❌ Search model not initialized.")
                return self._mock_product_search(query)

        try:
            # --- REVERTED PROMPT ---
            prompt = f"""
            Find information about this skincare product: "{query}"

            IMPORTANT: Return ONLY valid JSON with this exact structure:
            {{
                "name": "Full product name",
                "brand": "Brand name",
                "category": "skincare category",
                "ingredients": ["ingredient1", "ingredient2", "ingredient3", "... list ALL ingredients found ..."]
            }}

            Guidelines:
            - If you cannot find the exact product, provide the most likely match.
            - Category should be one of: cleanser, serum, moisturizer, sunscreen, toner, treatment.
            - **Crucially, list ALL ingredients you can find for the product, in the correct order if possible.**
            - Return only the JSON object, no other text.
            """
            # --- END REVERTED PROMPT ---

            # Keep timeout slightly higher for potentially longer lists
            response = model_to_use.generate_content(prompt, request_options={'timeout': 30})
            result = self._parse_ai_response(response.text)

            if "error" not in result and all(key in result for key in ['name', 'brand', 'category', 'ingredients']):
                logger.info(f"✅ AI found: {result.get('name', 'Unknown')} with {len(result.get('ingredients', []))} ingredients.")
                if not isinstance(result.get('ingredients'), list):
                    logger.warning("AI returned non-list for ingredients, using empty list.")
                    result['ingredients'] = []
                return result
            else:
                logger.warning(f"❌ AI returned incomplete data: {result.get('error')}, using mock")
                return self._mock_product_search(query)

        except Exception as e:
            logger.error(f"❌ AI search failed: {e}, using mock data")
            self.last_error = str(e)
            return self._mock_product_search(query)
        
    # --- THIS FUNCTION IS UPDATED ---
    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=2, max=5))
    def get_deep_analysis_from_ai(self, products: List[Dict]) -> Dict:
        """CONCISE AI analysis focusing on key actionable insights."""
        logger.info(f"🔬 Concise AI Analyzing {len(products)} products")

        if not self.configured:
            logger.info("🔄 Using mock analysis - API not configured")
            return self._mock_deep_analysis(products, concise=True) # Use concise mock

        if not self.analysis_model:
                logger.error("❌ Analysis model not initialized.")
                return self._mock_deep_analysis(products, concise=True)

        try:
            product_details = self._prepare_product_analysis_data(products)

            # --- UPDATED CONCISE PROMPT with SEPARATE CONFLICTS/WARNINGS ---
            prompt = f"""
            Analyze this skincare routine concisely, focusing on critical issues and actions:

            {product_details}

            Provide a FOCUSED analysis with this EXACT JSON structure:
            {{
                "rating": 1-5,
                "summary": "Brief overall assessment (1-2 sentences MAX)",
                "conflicts": ["List ONLY specific ingredient-vs-ingredient conflicts (e.g., 'Retinol conflicts with Benzoyl Peroxide'). If none, return an empty list []."],
                "warnings": ["List critical usage warnings NOT related to specific conflicts (e.g., 'Risk of over-exfoliation', 'Missing daily sunscreen'). If none, return an empty list []."],
                "gap_analysis": "Identify the most important missing product category or type. Phrase it as a user-friendly suggestion in one sentence (e.g., 'Consider adding a hydrating moisturizer for better barrier support.' or 'Your routine appears complete regarding essential steps.'). Use 'None' only if truly complete.",
                "recommendations": ["List ONLY the TOP 3-5 most crucial action steps (e.g., add SPF, reduce exfoliation, add moisturizer). Be very direct."],
                "routine": {{
                    "am": "Step-by-step morning routine order (product names only, use ' -> ' separator)",
                    "pm": "Step-by-step evening routine order (product names only, use ' -> ' separator)"
                }}
            }}

            Requirements:
            - Be extremely concise and to the point.
            - Differentiate between specific `conflicts` (ingredient vs. ingredient) and general `warnings` (usage advice).
            - Ensure 'gap_analysis' is a single, helpful sentence.
            - Do NOT include detailed explanations, pairings, or synergies unless part of a CRITICAL conflict/warning.
            - Return ONLY valid JSON, no additional text.
            """
            # --- END UPDATED PROMPT ---

            response = self.analysis_model.generate_content(prompt, request_options={'timeout': 45}) # Timeout 45s
            result = self._parse_ai_response(response.text)

            if "error" not in result:
                logger.info(f"✅ Concise AI analysis completed")
                # Ensure structure matches concise request
                return self._ensure_concise_analytical_features(result) # Use concise ensure helper
            else:
                logger.error(f"❌ Concise AI analysis failed to parse: {result.get('error')}, using mock")
                return self._mock_deep_analysis(products, concise=True)

        except Exception as e:
            logger.error(f"❌ Concise AI analysis failed: {e}, using mock")
            self.last_error = str(e)
            return self._mock_deep_analysis(products, concise=True)
    # --- END OF UPDATED FUNCTION ---

    def _prepare_product_analysis_data(self, products: List[Dict]) -> str:
        """Prepare product data string for analysis prompt."""
        # (This function remains unchanged)
        product_details = [f"Analyzing Routine ({len(products)} products):"]
        product_details.append("=" * 30)
        for i, product in enumerate(products):
            ingredients = product.get('ingredients', [])
            key_ingredients_str = ', '.join(map(str, ingredients[:8])) + ('...' if len(ingredients) > 8 else '')
            product_details.append(
                f"P{i+1}: {product.get('name', 'Unknown')}\n"
                f"  Brand: {product.get('brand', 'N/A')}\n"
                f"  Category: {product.get('category', 'N/A')}\n"
                f"  Key Ingredients: {key_ingredients_str or 'None listed'}"
            )
        return "\n".join(product_details)

    def _parse_ai_response(self, response_text: str) -> Dict:
        """Clean and parse AI JSON response."""
        # (This function remains unchanged)
        response_text = response_text.strip()
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        cleaned_text = None
        if json_match:
            cleaned_text = json_match.group()
        else:
            if response_text.startswith('```json'):
                cleaned_text = response_text[7:].rstrip('` \n')
            elif response_text.startswith('{'):
                cleaned_text = response_text
        if not cleaned_text:
            logger.error(f"No JSON found in AI response: {response_text[:100]}...")
            return {"error": "No JSON content found in AI response"}
        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {e} in text: {cleaned_text[:100]}...")
            cleaned_text_fixed = re.sub(r",\s*([\}\]])", r"\1", cleaned_text)
            try:
                logger.info("Attempting parse after fixing trailing comma...")
                return json.loads(cleaned_text_fixed)
            except json.JSONDecodeError:
                logger.error("Still failed after fixing trailing comma.")
                return {"error": f"Failed to parse AI JSON response: {e}"}

    # --- THIS ORIGINAL FUNCTION IS NO LONGER USED BY CONCISE ANALYSIS ---
    def _ensure_analytical_features(self, result: Dict) -> Dict:
        """Ensure all features for FULL analysis are present."""
        # (This function remains unchanged but is now only relevant if you revert)
        defaults = { "rating": 3, "summary": "Analysis completed.", "deep_analysis": "Detailed analysis not provided by AI.", "gap_analysis": "Gap analysis not provided.", "routine": {"am": "Not specified.", "pm": "Not specified."}, "warnings": ["Check warnings."], "recommendations": ["Follow recommendations."], "ingredient_interactions": {"conflicts": ["Check conflicts."],"synergies": ["Check synergies."]} }
        for key, default in defaults.items(): result.setdefault(key, default)
        if not isinstance(result.get("routine"), dict): result["routine"] = defaults["routine"]
        result["routine"].setdefault("am", defaults["routine"]["am"])
        result["routine"].setdefault("pm", defaults["routine"]["pm"])
        return result
    # -------------------------------------------------------------

    # --- UPDATED CONCISE DEFAULTS HELPER ---
    def _ensure_concise_analytical_features(self, result: Dict) -> Dict:
        """Ensure core features for CONCISE analysis are present."""
        defaults = {
            "rating": 3,
            "summary": "Routine analysis complete.",
            "conflicts": [], # <-- NEW: Default to no conflicts
            "warnings": ["No critical usage warnings identified."], # <-- NEW: Default for warnings
            "gap_analysis": "Your routine appears complete regarding essential steps.", # Updated default
            "recommendations": ["Continue routine, monitor skin.", "Use SPF daily."],
            "routine": {
                "am": "Cleanse -> Moisturize -> SPF",
                "pm": "Cleanse -> Treat -> Moisturize"
            }
        }
        for key, default in defaults.items(): result.setdefault(key, default)
        if not isinstance(result.get("routine"), dict): result["routine"] = defaults["routine"]
        result["routine"].setdefault("am", defaults["routine"]["am"])
        result["routine"].setdefault("pm", defaults["routine"]["pm"])
        # Ensure list types
        if not isinstance(result.get("conflicts"), list): result["conflicts"] = defaults["conflicts"] # <-- NEW
        if not isinstance(result.get("warnings"), list): result["warnings"] = defaults["warnings"]
        if not isinstance(result.get("recommendations"), list): result["recommendations"] = defaults["recommendations"]
        # Ensure gap_analysis is a string
        if not isinstance(result.get("gap_analysis"), str): result["gap_analysis"] = defaults["gap_analysis"]
        return result
    # --- END UPDATED HELPER ---

    def _mock_product_search(self, query: str) -> Dict:
        """Mock product search."""
        # (This function remains unchanged)
        mock_products = { "minimalist": {"name": "Minimalist 10% Niacinamide", "brand": "Minimalist", "category": "serum", "ingredients": ["Aqua", "Niacinamide"]}, "cerave": {"name": "CeraVe Cleanser", "brand": "CeraVe", "category": "cleanser", "ingredients": ["Aqua", "Glycerin"]}}
        query_lower = query.lower()
        for key, product in mock_products.items():
            if key in query_lower: return product
        category = "serum"
        if "cleanser" in query_lower: category = "cleanser"
        elif "sunscreen" in query_lower: category = "sunscreen"
        return {"name": f"{query.title()} (Mock)", "brand": "Mock Brand", "category": category, "ingredients": ["Aqua", "Glycerin"]}

    # --- UPDATED MOCK ANALYSIS ---
    def _mock_deep_analysis(self, products: List[Dict], concise: bool = False) -> Dict:
        """Mock analysis, optionally concise."""
        product_names = [p.get('name', 'Unknown') for p in products]
        num_prod = len(products)

        if concise:
            # Concise mock output with user-friendly gap
            return {
                "rating": 4,
                "summary": f"Mock concise analysis: Routine with {num_prod} products looks reasonable.",
                "conflicts": [], # <-- NEW: Mock no conflicts
                "warnings": ["Mock: Patch test actives."], # <-- NEW: Mock general warning
                "gap_analysis": "Mock: Consider adding a hydrating serum if skin feels dry.", # User-friendly mock gap
                "recommendations": ["Mock: Use SPF daily.", "Mock: Moisturize AM/PM."],
                "routine": {"am": "Cleanse -> SPF (Mock)", "pm": "Cleanse -> Moisturize (Mock)"}
            }
        else:
            # Original detailed mock output (remains unchanged)
            return {
                "rating": 4,
                "summary": f"Mock detailed analysis: Good routine with {num_prod} products.",
                "deep_analysis": f"Detailed mock analysis covering {', '.join(product_names)}. Looks compatible...",
                "gap_analysis": "Mock: Consider antioxidant serum.",
                "routine": {"am": "Cleanse -> Serum -> SPF (Mock)", "pm": "Cleanse -> Treat -> Moisturize (Mock)"},
                "warnings": ["Mock: Patch test new items."],
                "recommendations": ["Mock: Use sunscreen.", "Mock: Introduce slowly."],
                "ingredient_interactions": {"conflicts": ["Mock: None found."], "synergies": ["Mock: Looks compatible."]}
            }
    # --- END UPDATED MOCK ---

# Global instance
ai_handler = AIHandler()

# Public functions (remain unchanged)
def find_new_product_with_ai(query: str) -> Dict:
    return ai_handler.find_new_product_with_ai(query)

def get_deep_analysis_from_ai(products: List[Dict]) -> Dict:
    return ai_handler.get_deep_analysis_from_ai(products)

def is_ai_configured() -> bool:
    return ai_handler.configured

def get_api_status_details() -> Dict:
    return ai_handler.get_api_status() # Corrected typo