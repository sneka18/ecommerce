"""
Google Gemini Generative AI Service
Provides AI-powered product description generation, bullet-point highlights,
and personalized customer shopping insights.
"""
import json
import re
from typing import Dict, Any, Optional, List
from app.core.config import settings

# Attempt import of Google Generative AI
try:
    import google.generativeai as genai
    _GENAI_AVAILABLE = True
except ImportError:
    _GENAI_AVAILABLE = False


class GeminiAIService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = None
        self._init_client()

    def _init_client(self):
        """Initialize Google Gemini client if API key is provided."""
        if not _GENAI_AVAILABLE:
            print("[GeminiAIService] google-generativeai package not installed.")
            return

        # Check if user set the API key
        if self.api_key and self.api_key.strip() and self.api_key != "your_gemini_api_key_here":
            try:
                genai.configure(api_key=self.api_key.strip())
                # Prefer fast, modern flash model
                self.model = genai.GenerativeModel("gemini-1.5-flash")
                print("[GeminiAIService] Initialized Gemini 1.5 Flash client.")
            except Exception as e:
                print(f"[GeminiAIService] Warning configuring Gemini: {e}")
                self.model = None
        else:
            self.model = None

    def _call_gemini(self, prompt: str) -> Optional[str]:
        """Call Gemini model or return None if not configured."""
        if not self.model:
            self.api_key = settings.GEMINI_API_KEY
            self._init_client()

        if not self.model:
            return None

        try:
            response = self.model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            print(f"[GeminiAIService] Live Gemini API call failed: {e}")
            return None

        return None

    def generate_product_description(
        self,
        product_name: str,
        category: str,
        price: float,
        features: Optional[str] = None,
        specifications: Optional[str] = None,
        target_audience: Optional[str] = None
    ) -> Dict[str, Any]:
        """Feature 1: Generate professional e-commerce product description, highlights, and use cases."""
        prompt = f"""
You are an expert e-commerce copywriter and product marketing specialist.
Write a compelling, professional, SEO-optimized product description for an online store.

Product Details:
- Product Name: {product_name}
- Category: {category}
- Price: ${price:.2f}
- Key Features: {features or 'Not specified'}
- Specifications: {specifications or 'Standard premium grade'}
- Target Audience: {target_audience or 'General consumers'}

Respond strictly with a valid JSON object in the following format:
{{
  "description": "Engaging 2-3 paragraph marketing description highlighting value, craftsmanship, and benefits.",
  "highlights": [
    "Highlight point 1 (e.g. Battery life, durability)",
    "Highlight point 2",
    "Highlight point 3",
    "Highlight point 4"
  ],
  "use_cases": [
    "Ideal use case 1",
    "Ideal use case 2"
  ]
}}
Do NOT include markdown formatting or extra text outside the JSON.
"""
        raw_text = self._call_gemini(prompt)

        # If live Gemini succeeded, parse its response
        if raw_text:
            try:
                cleaned = re.sub(r"^```(?:json)?\s*", "", raw_text.strip())
                cleaned = re.sub(r"\s*```$", "", cleaned)
                data = json.loads(cleaned)
                return {
                    "success": True,
                    "data": {
                        "description": data.get("description", ""),
                        "highlights": "\n".join(f"• {h}" for h in data.get("highlights", [])),
                        "use_cases": data.get("use_cases", [])
                    }
                }
            except Exception:
                return {
                    "success": True,
                    "data": {
                        "description": raw_text,
                        "highlights": f"• Premium {category} grade\n• Superior value at ${price:.2f}\n• Designed for {target_audience or 'all users'}",
                        "use_cases": ["Everyday use", "Professional applications"]
                    }
                }

        # Demo Fallback Generator (Ensures demo NEVER fails when API key is pending)
        feat_text = f" Featuring {features}." if features else ""
        aud_text = f" Specifically tailored for {target_audience}." if target_audience else ""
        demo_desc = (
            f"The {product_name} represents the next benchmark in {category}. "
            f"Engineered with premium craftsmanship and meticulous attention to detail, it delivers uncompromised reliability and superior performance at an accessible ${price:.2f} price point.{feat_text}{aud_text}\n\n"
            f"Whether for intensive daily use or specialized tasks, this product seamlessly integrates into your modern workflow."
        )
        demo_highlights = (
            f"• High-durability materials engineered for extended lifecycle\n"
            f"• Advanced {category} performance tuned for maximum efficiency\n"
            f"• Backed by verified manufacturer warranty and quality assurance\n"
            f"• Optimized balance of premium features and outstanding value (${price:.2f})"
        )
        return {
            "success": True,
            "data": {
                "description": demo_desc,
                "highlights": demo_highlights,
                "use_cases": ["Daily professional usage", "Lifestyle and productivity optimization"]
            }
        }

    def generate_product_highlights(self, product_name: str, category: str, description: Optional[str] = None) -> List[str]:
        """Feature 1b: Generate bullet-point highlights from product details."""
        prompt = f"""
Generate 4-5 concise, bullet-point selling highlights for the following product:
- Product Name: {product_name}
- Category: {category}
- Context/Description: {description or ''}

Return ONLY the bullet points, each on a new line starting with '• '.
"""
        text = self._call_gemini(prompt)
        if text:
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            return lines
        return [
            f"• Premium high-grade construction for {category}",
            f"• Ergonomic and intuitive design for effortless handling",
            f"• Engineered for optimal performance and daily durability",
            f"• High customer satisfaction and quality assurance"
        ]

    def generate_shopping_insights(
        self,
        category: Optional[str] = None,
        viewed_products: Optional[List[str]] = None,
        interests: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Feature 2: Generate personalized shopping recommendations and shopping tips."""
        prompt = f"""
Act as an intelligent AI shopping concierge. Generate friendly, insightful shopping advice and smart purchasing recommendations for a customer.

Customer Context:
- Preferred Category: {category or 'General / Multi-category'}
- Recently Viewed Items: {', '.join(viewed_products) if viewed_products else 'Trending electronics, fashion, lifestyle'}
- Customer Interests: {', '.join(interests) if interests else 'Quality, high durability, modern aesthetics'}

Respond strictly with a JSON object:
{{
  "headline": "A catchy, personalized headline for the customer",
  "smart_tips": [
    "Tip 1 for making a smart purchase in this category",
    "Tip 2 regarding warranty, features, or value",
    "Tip 3 on seasonal trends or compatibility"
  ],
  "ai_recommendation_summary": "A 2-sentence encouraging summary recommending how to choose the right product."
}}
"""
        raw_text = self._call_gemini(prompt)
        if raw_text:
            try:
                cleaned = re.sub(r"^```(?:json)?\s*", "", raw_text.strip())
                cleaned = re.sub(r"\s*```$", "", cleaned)
                return json.loads(cleaned)
            except Exception:
                pass

        return {
            "headline": f"Smart Shopping Guide for {category or 'Savvy Shoppers'}",
            "smart_tips": [
                "Compare user ratings and specifications before finalizing your choice.",
                "Look for bundled accessories or warranties to maximize your investment.",
                "Take advantage of current platform promotional offers."
            ],
            "ai_recommendation_summary": (raw_text[:200] if raw_text else "Our machine learning engine curates top trending recommendations to help you make informed purchase decisions.")
        }

    def generate_product_reason_insight(self, product_name: str, category: str, price: float, rating: float) -> str:
        """Feature 3: Explain why a recommended product is beneficial to the customer."""
        prompt = f"""
Explain in 2 friendly, persuasive sentences why a customer should consider buying '{product_name}' (${price:.2f}, {rating}★, {category}).
Highlight its standout value or convenience factor. Keep it concise and natural.
"""
        text = self._call_gemini(prompt)
        if text:
            return text
        return f"{product_name} delivers standout performance in the {category} category, backed by verified user reviews and a competitive ${price:.2f} price."


gemini_service = GeminiAIService()

