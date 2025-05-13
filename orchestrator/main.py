from fastapi import FastAPI
from agents import api_agent, analysis_agent, language_agent, retriever_agent
from data_ingestion.document_loader import load_txt_documents, chunk_text
import random

app = FastAPI()

# Load and embed market news
texts = load_txt_documents("data/news/")
chunks = [c for t in texts for c in chunk_text(t)]
index, source_texts = retriever_agent.embed_and_store(chunks)

def get_earnings_surprise(actual_eps, estimated_eps):
    return ((actual_eps - estimated_eps) / estimated_eps) * 100

@app.get("/brief")
def morning_brief():
    try:
        companies = ["TSMC", "005930.KS", "AAPL", "GOOGL"]
        company_data = {}

        for company in companies:
            try:
                stock_data = api_agent.get_stock_summary(company)
                actual_eps = random.uniform(5, 10)
                estimated_eps = random.uniform(4, 9)
                surprise = get_earnings_surprise(actual_eps, estimated_eps)
                company_data[company] = {
                    'stock_data': stock_data,
                    'earnings_surprise': surprise
                }
            except Exception as e:
                print(f"[ERROR] Failed to fetch data for {company}: {e}")
                continue

        today_risk = analysis_agent.compute_asia_tech_exposure({
            "AsiaTech_TSM": 2000000,
            "US_Tech_MSFT": 5000000
        })
        yesterday_risk = today_risk + random.uniform(-5, 5)
        direction = "up from" if today_risk > yesterday_risk else "down from"

        retrieved_docs = retriever_agent.retrieve_top_k("Asia tech earnings", index, source_texts)
        news_summary = " ".join(retrieved_docs)

        sentiment = analysis_agent.get_sentiment(news_summary)
        sentiment_label = sentiment.get("label", "neutral")
        sentiment_reason = sentiment.get("reason", "mixed factors")

        earnings_lines = []
        for company, data in company_data.items():
            change = data['earnings_surprise']
            if change >= 0:
                line = f"{company} beat estimates by {change:.2f}%"
            else:
                line = f"{company} missed by {abs(change):.2f}%"
            earnings_lines.append(line)

        prompt = (
            f"Today, your Asia tech allocation is {today_risk:.2f}% of AUM, "
            f"{direction} {abs(yesterday_risk):.2f}%.\n"
            f"{'; '.join(earnings_lines)}.\n"
            f"Regional sentiment is {sentiment_label} due to {sentiment_reason}."
        )

        brief = language_agent.generate_brief(prompt)
        return {"brief": brief or prompt}

    except Exception as e:
        print(f"[SERVER ERROR] {e}")
        return {"error": str(e)}
