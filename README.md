# 🏙️ UrbanLens — AI City Intelligence Agent

UrbanLens is an AI-powered city assistant that provides real-time weather updates and latest city news using intelligent tool-calling workflows powered by Mistral AI, LangChain, and Streamlit.

---

# ✨ Features

* 🌦️ Real-time weather updates
* 📰 Latest city news search
* 🤖 AI-powered city assistant
* ⚡ LangChain tool calling
* 🧠 Human approval before tool execution
* 💬 Interactive chat interface
* 🎨 Modern Streamlit UI
* 🔐 Secure API key handling using environment secrets
* 🚀 Deployable on Streamlit Cloud

---

# 🛠️ Tech Stack

| Technology      | Purpose                    |
| --------------- | -------------------------- |
| Python          | Backend                    |
| Streamlit       | Web Interface              |
| LangChain       | Tool Calling & Agent Logic |
| Mistral AI      | Large Language Model       |
| Tavily API      | News Search                |
| OpenWeather API | Weather Data               |

---

# 📂 Project Structure

```text id="yjlwm2"
urbanlens-ai/
│
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
└── .env.example
```

---

# 🔑 Environment Variables

Create a `.env` file locally:

```env id="jlwmr0"
MISTRAL_API_KEY=your_mistral_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
TAVILY_API_KEY=your_tavily_api_key
```

---

# ▶️ Run Locally

```bash id="y3udxw"
python -m streamlit run app.py
```

---

# 🌍 Example Queries

```text id="jjlwm2"
What's the weather in Ahmedabad?
```

```text id="7jlwm1"
Latest news in Mumbai
```

```text id="jlwmt0"
Tell me weather and news in Delhi
```

---

# 🚀 Deployment

The application can be deployed using Streamlit Cloud and connected securely with environment secrets for API management.
---

# 🧠 How It Works

1. User sends a query
2. LLM decides whether tools are required
3. UrbanLens pauses for human approval
4. Approved tools execute securely
5. Tool results are returned to the model
6. AI generates final response

---


# 👨‍💻 Author

Built by YUG KHATRI

---

# ⭐ Support

If you liked this project:

* Star the repository
* Fork the project
* Share feedback

---

# 📜 License

This project is licensed under the MIT License.
