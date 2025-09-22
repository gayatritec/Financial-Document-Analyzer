## Importing libraries and files
import os
import asyncio
from typing import Optional, List, Any
from conf import settings
from crewai.tools import BaseTool
from crewai_tools import SerperDevTool
from pydantic import BaseModel, Field
import fitz  # PyMuPDF for PDF processing with image and table support

from PIL import Image
import io
import pandas as pd
import numpy as np
import re

## Creating search tool
search_tool = SerperDevTool(api_key=settings.SERPER_API_KEY)

## Input models for tools
class PDFInput(BaseModel):
    path: str = Field(description="Path to the PDF file to analyze")

class FinancialDataInput(BaseModel):
    financial_document_data: str = Field(description="Financial document data to analyze")

## Creating custom PDF reader tool
class FinancialDocumentTool(BaseTool):
    name: str = "financial_document_reader"
    description: str = "Read and extract content from PDF files including text, tables, and images"
    args_schema: type[BaseModel] = PDFInput

    def _run(self, path: str) -> str:
        """Read data from a PDF file including text, tables, and images

        Args:
            path (str): Path to the PDF file

        Returns:
            str: Extracted content from the PDF including text, tables, and image descriptions
        """
        try:
            if not os.path.exists(path):
                return f"Error: File not found at path: {path}"
            
            # Open the PDF file
            doc = fitz.open(path)
            full_content = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_content = f"\n=== Page {page_num + 1} ===\n"
                
                # Extract text
                text = page.get_text()
                if text.strip():
                    page_content += f"\n--- Text Content ---\n{text}\n"
                
                # Extract tables
                tables = page.find_tables()
                if tables:
                    page_content += f"\n--- Tables Found ({len(tables.tables)}) ---\n"
                    for i, table in enumerate(tables):
                        try:
                            df = table.to_pandas()
                            page_content += f"\nTable {i+1}:\n{df.to_string()}\n"
                        except Exception as e:
                            page_content += f"\nTable {i+1} (raw data): {table.extract()}\n"
                
                # Extract and process images
                image_list = page.get_images(full=True)
                if image_list:
                    page_content += f"\n--- Images Found ({len(image_list)}) ---\n"
                    for img_index, img in enumerate(image_list):
                        try:
                            # Get image data
                            xref = img[0]
                            pix = fitz.Pixmap(doc, xref)
                            
                            if pix.n - pix.alpha < 4:  # Check if image is in color or grayscale
                                img_data = pix.tobytes("ppm")
                                img_pil = Image.open(io.BytesIO(img_data))
                                
                                # Use OCR to extract text from image
                                ocr_text = pytesseract.image_to_string(img_pil)
                                if ocr_text.strip():
                                    page_content += f"\nImage {img_index+1} (OCR Text):\n{ocr_text}\n"
                                else:
                                    page_content += f"\nImage {img_index+1}: [Image contains no readable text]\n"
                            else:
                                page_content += f"\nImage {img_index+1}: [Complex image format - cannot process]\n"
                            
                            pix = None  # Free memory
                        except Exception as e:
                            page_content += f"\nImage {img_index+1}: [Error processing image: {str(e)}]\n"
                
                full_content.append(page_content)
            
            doc.close()
            
            # Clean and format the final content
            final_content = "\n".join(full_content)
            
            # Remove excessive whitespace while preserving structure
            final_content = re.sub(r'\n{3,}', '\n\n', final_content)
            final_content = re.sub(r' {2,}', ' ', final_content)
            
            return final_content if final_content.strip() else "No extractable content found in the PDF."
            
        except Exception as e:
            return f"Error reading PDF file: {str(e)}"


## Creating Investment Analysis Tool
class InvestmentTool(BaseTool):
    name: str = "investment_analyzer"
    description: str = "Analyze financial data and provide investment recommendations"
    args_schema: type[BaseModel] = FinancialDataInput

    def _run(self, financial_document_data: str) -> str:
        """Analyze financial document data and provide investment analysis

        Args:
            financial_document_data (str): Financial document data to analyze

        Returns:
            str: Investment analysis and recommendations
        """
        try:
            # Clean the input data
            cleaned_data = re.sub(r'\s+', ' ', financial_document_data.strip())
            
            # Extract key financial metrics using regex patterns
            analysis_results = []
            
            # Look for revenue/profit patterns
            revenue_patterns = [
                r'(?:revenue|sales|income)\s*[:\$]?\s*([\d,]+\.?\d*)\s*(?:million|billion|thousand)?',
                r'(?:net\s*income|profit|earnings)\s*[:\$]?\s*([\d,]+\.?\d*)\s*(?:million|billion|thousand)?',
                r'(?:EBITDA|operating\s*income)\s*[:\$]?\s*([\d,]+\.?\d*)\s*(?:million|billion|thousand)?'
            ]
            
            financial_metrics = {}
            for pattern in revenue_patterns:
                matches = re.findall(pattern, cleaned_data, re.IGNORECASE)
                if matches:
                    financial_metrics[pattern] = matches
            
            # Look for risk indicators
            risk_indicators = [
                r'(?:debt|liability)\s*[:\$]?\s*([\d,]+\.?\d*)',
                r'(?:risk|volatility|uncertainty)',
                r'(?:loss|decline|decrease)'
            ]
            
            risk_found = []
            for pattern in risk_indicators:
                if re.search(pattern, cleaned_data, re.IGNORECASE):
                    risk_found.append(pattern)
            
            # Generate analysis report
            analysis_report = "\n=== INVESTMENT ANALYSIS REPORT ===\n\n"
            
            if financial_metrics:
                analysis_report += "**Financial Metrics Identified:**\n"
                for metric, values in financial_metrics.items():
                    analysis_report += f"- {metric}: {', '.join(values)}\n"
                analysis_report += "\n"
            
            if risk_found:
                analysis_report += "**Risk Indicators Found:**\n"
                for risk in risk_found:
                    analysis_report += f"- {risk}\n"
                analysis_report += "\n"
            
            # Provide general investment guidance
            analysis_report += "**Investment Recommendations:**\n"
            analysis_report += "1. Conduct thorough due diligence before making any investment decisions\n"
            analysis_report += "2. Consider diversification to mitigate risk\n"
            analysis_report += "3. Consult with a qualified financial advisor\n"
            analysis_report += "4. Review the complete financial documents for comprehensive analysis\n"
            analysis_report += "5. Monitor market conditions and economic indicators\n"
            
            if risk_found:
                analysis_report += "\n**Risk Management Considerations:**\n"
                analysis_report += "- Higher risk indicators suggest need for conservative approach\n"
                analysis_report += "- Consider hedging strategies for risk mitigation\n"
                analysis_report += "- Regular portfolio review and rebalancing recommended\n"
            
            return analysis_report
            
        except Exception as e:
            return f"Error in investment analysis: {str(e)}"


## Creating Risk Assessment Tool
class RiskTool(BaseTool):
    name: str = "risk_assessor"
    description: str = "Assess financial risks and provide risk management strategies"
    args_schema: type[BaseModel] = FinancialDataInput

    def _run(self, financial_document_data: str) -> str:
        """Assess financial risks and provide risk management recommendations

        Args:
            financial_document_data (str): Financial document data to assess

        Returns:
            str: Risk assessment and management recommendations
        """
        try:
            # Clean the input data
            cleaned_data = financial_document_data.lower()
            
            # Define risk categories and keywords
            risk_categories = {
                'Market Risk': ['market', 'volatility', 'fluctuation', 'price', 'value', 'trading'],
                'Credit Risk': ['credit', 'debt', 'loan', 'borrower', 'default', 'payment'],
                'Operational Risk': ['operational', 'process', 'system', 'technology', 'fraud'],
                'Liquidity Risk': ['liquidity', 'cash', 'funding', 'capital', 'assets'],
                'Regulatory Risk': ['regulatory', 'compliance', 'legal', 'government', 'policy']
            }
            
            # Assess risk levels
            risk_assessment = {}
            for category, keywords in risk_categories.items():
                risk_score = 0
                found_keywords = []
                for keyword in keywords:
                    count = cleaned_data.count(keyword)
                    if count > 0:
                        risk_score += count
                        found_keywords.append(keyword)
                
                if risk_score > 0:
                    risk_level = 'High' if risk_score > 5 else 'Medium' if risk_score > 2 else 'Low'
                    risk_assessment[category] = {
                        'score': risk_score,
                        'level': risk_level,
                        'keywords': found_keywords
                    }
            
            # Generate risk assessment report
            risk_report = "\n=== RISK ASSESSMENT REPORT ===\n\n"
            
            if risk_assessment:
                risk_report += "**Identified Risk Categories:**\n"
                for category, assessment in risk_assessment.items():
                    risk_report += f"\n{category} ({assessment['level']} Risk):\n"
                    risk_report += f"- Risk Score: {assessment['score']}\n"
                    risk_report += f"- Keywords Found: {', '.join(assessment['keywords'])}\n"
                
                # Overall risk assessment
                total_risk_score = sum(assessment['score'] for assessment in risk_assessment.values())
                overall_risk = 'High' if total_risk_score > 15 else 'Medium' if total_risk_score > 8 else 'Low'
                
                risk_report += f"\n**Overall Risk Assessment: {overall_risk} Risk**\n"
                risk_report += f"Total Risk Score: {total_risk_score}\n\n"
                
                # Risk mitigation strategies
                risk_report += "**Risk Mitigation Strategies:**\n"
                risk_report += "1. Implement comprehensive risk monitoring system\n"
                risk_report += "2. Develop contingency plans for high-risk areas\n"
                risk_report += "3. Regular risk assessment and reporting\n"
                risk_report += "4. Diversification to spread risk exposure\n"
                risk_report += "5. Maintain adequate capital reserves\n"
                risk_report += "6. Stay updated with regulatory changes\n"
                risk_report += "7. Implement internal controls and audits\n"
                
                if overall_risk == 'High':
                    risk_report += "\n**High Risk Alert:**\n"
                    risk_report += "- Immediate attention required\n"
                    risk_report += "- Consider risk reduction strategies\n"
                    risk_report += "- Increase monitoring frequency\n"
                    
            else:
                risk_report += "No significant risk indicators found in the document.\n"
                risk_report += "Continue regular monitoring and assessment.\n"
            
            return risk_report
            
        except Exception as e:
            return f"Error in risk assessment: {str(e)}"


## Create tool instances for use in agents
financial_document_tool = FinancialDocumentTool()
investment_tool = InvestmentTool()
risk_tool = RiskTool()