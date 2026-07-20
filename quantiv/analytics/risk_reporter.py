import os
from typing import Dict, Any
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


class LLMRiskReporter:
    """
    Automates risk reporting by utilizing the OpenAI API via LangChain
    to translate complex volatility surface metrics into readable natural language summaries.
    """
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        self.model_name = model_name
        self.api_key = os.environ.get("OPENAI_API_KEY", "")
        
        if LANGCHAIN_AVAILABLE and self.api_key:
            self.llm = ChatOpenAI(
                model=self.model_name, 
                temperature=0.3,
                api_key=self.api_key
            )
            
            self.prompt = PromptTemplate(
                input_variables=["spot", "rate", "min_iv", "max_iv", "mean_iv", "skew"],
                template=(
                    "You are a quantitative risk analyst.\n"
                    "Given the following implied volatility (IV) surface metrics for an underlying asset, "
                    "provide a concise, professional risk summary (2-3 paragraphs).\n\n"
                    "Market Data:\n"
                    "- Spot Price: {spot}\n"
                    "- Risk-Free Rate: {rate}%\n"
                    "- Min IV: {min_iv}%\n"
                    "- Max IV: {max_iv}%\n"
                    "- Average IV: {mean_iv}%\n"
                    "- Volatility Skew (Max - Min): {skew}%\n\n"
                    "Please analyze what these numbers suggest about market sentiment, potential tail risks, "
                    "and the shape of the volatility surface (e.g., steepness of the smile/smirk). "
                    "Do not include generic warnings; focus on interpreting the given metrics."
                )
            )
            self.chain = self.prompt | self.llm | StrOutputParser()
        else:
            self.llm = None
            self.chain = None

    def generate_surface_report(self, df: pd.DataFrame, spot: float, rate: float) -> str:
        """
        Extracts metrics from the volatility surface DataFrame and returns a natural language report.
        """
        if df.empty:
            return "No volatility surface data available to analyze."
            
        if not self.chain:
            return (
                "⚠️ OpenAI / LangChain is not configured properly or OPENAI_API_KEY is missing.\n\n"
                "To enable automated risk reporting, ensure the 'openai' and 'langchain' packages are installed "
                "and the OPENAI_API_KEY environment variable is set."
            )
            
        try:
            # Extract key metrics
            iv_values = df["iv"] * 100  # Convert to percentage
            min_iv = round(iv_values.min(), 2)
            max_iv = round(iv_values.max(), 2)
            mean_iv = round(iv_values.mean(), 2)
            skew = round(max_iv - min_iv, 2)
            
            # Generate report
            response = self.chain.invoke({
                "spot": spot,
                "rate": round(rate * 100, 2),
                "min_iv": min_iv,
                "max_iv": max_iv,
                "mean_iv": mean_iv,
                "skew": skew
            })
            return response
        except Exception as e:
            return f"❌ Error generating risk report: {str(e)}"
