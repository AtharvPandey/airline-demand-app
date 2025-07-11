from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_gpt_summary(df):
    if df.empty:
        return "No data available to summarize."

    summary = f"""
    Top Airlines: {df['Airline'].value_counts().head(3).to_dict()}.
    Top Routes: {df['Route'].value_counts().head(3).to_dict()}.
    Flight Status Counts: {df['Status'].value_counts().to_dict()}.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional data analyst."},
                {"role": "user", "content": f"Please summarize this airline market data in simple terms: {summary}"}
            ],
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"GPT Error: {e}")
        return "Could not generate GPT summary."

