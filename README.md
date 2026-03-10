# Python-Chat-OpenAI-Admission-ETTI
How I built it
Instead of just sending a user's question to an AI (which often leads to "hallucinations" or made-up rules), I implemented a RAG (Retrieval-Augmented Generation) workflow.

The Brain (MySQL): 
When you start the app, it parses the Regulament_admitere_licenta_2025.pdf page by page. I used a MySQL database with a Full-Text search index to store this data.

The Logic (Python): 
When a user asks something like "What documents do I need?", the script queries the database for the most relevant pages first.

The AI (DeepSeek/LLM): It sends the user's question along with the actual text from those specific pages to the AI. This ensures the answer is 100% based on official rules.

The UI (Gradio): I chose Gradio for the interface because it's fast to deploy and let me build a custom grade calculator that respects the official "truncation to 2 decimals" rule used by the university.

Tech Stack
I used Python for the glue, MySQL for the persistent storage and search, PyPDF2 for data ingestion, and Gradio for the web interface. For the AI part, I integrated the DeepSeek API using the OpenAI SDK.

Statistics & Monitoring
I also added a monitoring feature. Every question is logged in a separate MySQL table. Why? Because as a developer or a faculty admin, you want to see what candidates are struggling with. If 50 people ask about "cazare" (housing), you know that's a topic that needs more visibility.

Setup (for anyone wanting to run this)
Install requirements:
pip install -r requirements.txt

Setup your environment:
Create a .env file and add your OPENAI_API_KEY and MYSQL_PW.

Run it:
python main.py

The system is automated—it will create the database and process the PDF for you on the first run.

Why this approach?
I didn't want a simple chatbot. I wanted a tool that is accurate (no lying about admission grades), useful (includes a calculator), and insightful (logs search trends).

Ce am schimbat ca să pară "uman":
Perspectiva: Am folosit "I built", "I implemented", "I chose". Arată că tu ai luat deciziile, nu un template.

Fără bullet points excesive: Am transformat listele în paragrafe scurte care explică de ce ai făcut ceva, nu doar ce ai făcut.

Exemple reale: Am menționat faza cu "cazarea" sau "trunchierea la 2 zecimale", detalii care arată că ai înțeles contextul real al problemei.
