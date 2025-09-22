## Importing libraries and files
from crewai import Task

from agents import financial_analyst, verifier,investment_advisor,risk_assessor

## Creating a task to help solve user's query
analyze_financial_document = Task(
    description="Analyze the provided financial document and address the user's query: {query}.\n\
Conduct thorough analysis of financial statements, market data, and economic indicators.\n\
Provide data-driven insights based on actual financial information from the document.\n\
Identify key financial metrics, trends, and relevant market factors.\n\
Ensure all analysis is factual, evidence-based, and follows regulatory compliance standards.",

    expected_output="""Provide a comprehensive financial analysis including:
- Summary of key financial findings from the document
- Detailed analysis of financial metrics and ratios
- Identification of trends and patterns in the data
- Objective assessment of financial performance
- Data-driven insights relevant to the user's query
- Clear, factual recommendations based on the analysis
- Proper citations of data sources from the financial document""",

    agent=financial_analyst,
    async_execution=False,
)

## Creating an investment analysis task
investment_analysis = Task(
    description="Conduct professional investment analysis based on verified financial data and the user's query: {query}.\n\
Analyze financial statements, market conditions, and investment opportunities objectively.\n\
Consider risk tolerance, investment goals, and time horizons in the analysis.\n\
Provide balanced investment recommendations following regulatory compliance standards.\n\
Ensure all advice is based on factual data and sound investment principles.",

    expected_output="""Provide a comprehensive investment analysis including:
- Objective assessment of investment opportunities based on financial data
- Risk-adjusted investment recommendations
- Diversification strategies appropriate to the financial situation
- Clear explanation of investment rationale and expected outcomes
- Consideration of market conditions and economic factors
- Regulatory compliance disclosures where applicable
- Transparent fee structures and potential conflicts of interest""",

    agent=investment_advisor,
    async_execution=False,
)

## Creating a risk assessment task
risk_assessment = Task(
    description="Conduct comprehensive risk assessment based on the financial document and user query: {query}.\n\
Analyze various risk factors including market risk, credit risk, operational risk, and liquidity risk.\n\
Use established risk assessment methodologies and industry best practices.\n\
Provide balanced risk ratings and practical mitigation strategies.\n\
Ensure all risk analysis follows regulatory standards and compliance requirements.",

    expected_output="""Provide a thorough risk assessment including:
- Detailed analysis of identified risk factors and their potential impact
- Risk ratings using established methodologies (e.g., low, medium, high)
- Specific risk mitigation strategies and recommendations
- Stress testing scenarios and their potential outcomes
- Compliance with regulatory risk management requirements
- Clear risk tolerance guidelines and monitoring recommendations
- Documentation of risk assessment methodology and assumptions""",

    agent=risk_assessor,
    async_execution=False,
)

    
verification = Task(
    description="Verify that the uploaded document is a valid financial document and ensure data integrity.\n\
Conduct thorough examination of document structure, content, and formatting.\n\
Check for compliance with financial reporting standards and regulations.\n\
Validate data accuracy and identify any inconsistencies or anomalies.\n\
Provide detailed verification results with specific findings and recommendations.",

    expected_output="""Provide comprehensive document verification including:
- Document type classification and validation
- Assessment of data integrity and accuracy
- Identification of any formatting or structural issues
- Compliance check with financial reporting standards
- Detailed list of any anomalies or inconsistencies found
- Clear verification status (approved/rejected/requires review)
- Specific recommendations for addressing any identified issues""",

    agent=verifier,
    async_execution=False
)