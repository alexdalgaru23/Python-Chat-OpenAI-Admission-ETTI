# Admission Assistant ETTI-UPB 🎓

I built this project to turn a static, 40-page admission PDF into an interactive AI assistant. It helps candidates get instant, accurate answers about the 2025 admission rules at ETTI (Politehnica Bucharest).

---

### **Why I made this**

University regulations are usually a nightmare to read. I wanted a tool that:
1. **Never lies**: By using RAG, the AI only answers based on the official PDF.
2. **Calculates exactly**: It includes a grade calculator that follows the university's specific "truncation to 2 decimals" rule.
3. **Identifies trends**: It logs what people search for, so faculty admins can see common "pain points".

---

### **How it works (The Tech Part)**

The system doesn't just "chat"—it follows a specific pipeline to ensure accuracy:

* **Storage**: On the first run, the script parses the PDF and stores it in a **MySQL** database with a `FULLTEXT` index.
* **Retrieval**: When you ask a question, Python fetches the 3 most relevant pages from the database.
* **Generation**: The **DeepSeek LLM** receives your question + the official text as context to generate the final answer.
* **Interface**: I used **Gradio** for a clean web UI that works on both desktop and mobile.

---

### **Quick Setup**

1. **Install**: `pip install -r requirements.txt`
2. **Config**: Create a `.env` file with your `OPENAI_API_KEY` and `MYSQL_PW`.
3. **Run**: `python main.py` (The DB and PDF processing are fully automated).

---
*Personal project developed to demonstrate AI integration with SQL databases.*
