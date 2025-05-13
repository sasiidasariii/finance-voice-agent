from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agents import api_agent, scraping_agent, retriever_agent, analysis_agent, language_agent
import logging

# Initialize FastAPI app
app = FastAPI()

# Middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for simplicity in development
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/")
def root():
    return {"message": "Finance Voice Agent is running. Use /brief?query=your-question"}

@app.get("/brief")
def morning_brief(query: str = "What’s our risk exposure in Asia tech stocks today?"):
    try:
        logger.info(f"🔍 Query received: {query}")

        # Fetch market data
        try:
            market_data = api_agent.fetch_market_data()
            logger.info(f"Fetched market data: {market_data}")
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            return {"error": f"Market data fetch failed: {str(e)}"}

        # Scrape earnings news
        try:
            earnings = scraping_agent.scrape_earnings_news()
            logger.info(f"Earnings news scraped: {earnings}")
        except Exception as e:
            logger.error(f"Error scraping earnings news: {e}")
            return {"error": f"Earnings scraping failed: {str(e)}"}

        # Retrieve relevant articles
        try:
            retrieval = retriever_agent.retrieve(query)
            logger.info(f"Retrieval results: {retrieval}")
        except Exception as e:
            logger.error(f"Error in retrieval: {e}")
            return {"error": f"Retrieval failed: {str(e)}"}

        # Perform risk analysis
        try:
            analysis = analysis_agent.analyze(market_data)
            logger.info(f"Risk analysis result: {analysis}")
        except Exception as e:
            logger.error(f"Error in analysis: {e}")
            return {"error": f"Analysis failed: {str(e)}"}

        # Combine all information for summary generation
        try:
            facts = f"{retrieval} | {str(analysis)} | {earnings}"
            summary = language_agent.generate_summary(facts)
            logger.info(f"Generated summary: {summary}")
        except Exception as e:
            logger.error(f"Error in generating summary: {e}")
            return {"error": f"Summary generation failed: {str(e)}"}

        return {"summary": summary}

    except Exception as e:
        logger.error(f"❌ General error: {e}")
        return {"error": f"An unexpected error occurred: {str(e)}"}
