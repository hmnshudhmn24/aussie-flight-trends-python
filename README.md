
# ✈️ Aussie Flight Trends – Market Demand Analysis Web App

This is a Python-based Flask web app that analyzes and visualizes flight market demand trends across Australian cities. It processes sample flight pricing data and uses OpenAI's GPT model to generate smart insights on pricing trends, popular routes, and high-demand periods.

## 🔍 Features

- ✅ Clean, filterable UI for entering date range, origin, and destination
- 📊 Interactive Plotly charts showing:
  - Average demand per route
  - Price trends over time
- 🤖 AI-generated insights via OpenAI’s GPT-4 API based on route popularity and price data
- 📦 Self-contained demo using sample data (no paid APIs required)

## 🖥 Tech Stack

| Layer        | Tech Used             |
|--------------|------------------------|
| Backend      | Python, Flask          |
| Frontend     | HTML, CSS, Plotly.js   |
| AI Insights  | OpenAI GPT-4 API       |
| Data         | Sample data (scraped/fake) |
| Visuals      | Plotly charts          |
| Styling      | Custom responsive CSS  |

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/aussie-flight-trends.git
cd aussie-flight-trends
```

### 2. Set Up a Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows
```

### 3. Install Required Packages
```bash
pip install -r requirements.txt
```

### 4. Set Your OpenAI API Key
You can either:
- **Option A:** Edit `app.py` directly:
```python
openai.api_key = 'sk-your-openai-key-here'
```
- **Option B:** Use an `.env` file:
```bash
pip install python-dotenv
```
Then create a `.env` file with:
```
OPENAI_API_KEY=sk-your-openai-key-here
```
And update `app.py` to:
```python
from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
```

## 💡 Usage

1. Run the app locally:
```bash
python app.py
```

2. Visit [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

3. Apply filters, view insights, and explore the interactive charts.

## 📂 Folder Structure

```
.
├── app.py                 # Main application logic
├── templates/
│   └── index.html         # Frontend UI with filters and chart containers
├── static/                # (Optional) for additional CSS or JS files
├── requirements.txt       # Python dependencies
├── README.md              # You're reading it!
```

## 📌 Notes

- The app uses sample hardcoded data for demonstration purposes.
- Can be extended with real airline APIs like Skyscanner, AviationStack, etc.
- Built as part of a technical assessment task, but scalable into a production tool.

## 👨‍💻 Author

**Himanshu Kumar**  
[GitHub](https://github.com/yourusername) • [Email](mailto:your@email.com)

## 📜 License

MIT License - feel free to use and modify.
