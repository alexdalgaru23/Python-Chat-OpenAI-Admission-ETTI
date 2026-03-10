import os
import mysql.connector
import PyPDF2
import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url="https://api.deepseek.com/v1")
MODEL = "deepseek-chat"

MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": os.getenv("MYSQL_PW"),
    "database": "admitere"
}
PDF_FILE = "Regulament_admitere_licenta_2025.pdf"


def setup_mysql():
    conn = mysql.connector.connect(
        host=MYSQL_CONFIG["host"],
        user=MYSQL_CONFIG["user"],
        password=MYSQL_CONFIG["password"]
    )
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_CONFIG['database']}")
    cursor.execute(f"USE {MYSQL_CONFIG['database']}")
    cursor.execute("DROP TABLE IF EXISTS regulament")
    cursor.execute("""
        CREATE TABLE regulament (
            id INT AUTO_INCREMENT PRIMARY KEY,
            text LONGTEXT,
            pagina INT,
            FULLTEXT(text)
        ) ENGINE=InnoDB
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monitorizare (
            id INT AUTO_INCREMENT PRIMARY KEY,
            intrebare TEXT,
            data_ora DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def pdf_to_mysql(pdf_path):
    if not os.path.exists(pdf_path): return
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                cursor.execute("INSERT INTO regulament (text, pagina) VALUES (%s, %s)", (" ".join(text.split()), i + 1))
    conn.commit()
    conn.close()


def get_context(query):
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT text, pagina FROM regulament WHERE MATCH(text) AGAINST(%s IN NATURAL LANGUAGE MODE) LIMIT 3",
            (query,))
        rows = cursor.fetchall()
        conn.close()
        return "\n\n".join([f"[Pagina {r[1]}] {r[0]}" for r in rows]) if rows else ""
    except:
        return ""


def respond(user_message, history):
    if not user_message:
        return "", history

    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO monitorizare (intrebare) VALUES (%s)", (user_message,))
        conn.commit()
        conn.close()
    except:
        pass

    context = get_context(user_message)

    system_prompt = (
            "Ești asistentul ETTI. Răspunde prietenos la saluturi. "
            "Folosește contextul de mai jos DOAR dacă ești întrebat despre regulament. "
            "Pentru calcule, respectă regula trunchierii la 2 zecimale.\n\n"
            "CONTEXT REGULAMENT:\n" + context
    )

    api_msgs = [{"role": "system", "content": system_prompt}]

    for msg in history:
        if isinstance(msg, dict):
            api_msgs.append({"role": msg["role"], "content": msg["content"]})
        elif isinstance(msg, (list, tuple)):
            api_msgs.append({"role": "user", "content": msg[0]})
            api_msgs.append({"role": "assistant", "content": msg[1]})

    api_msgs.append({"role": "user", "content": user_message})

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=api_msgs,
            temperature=0.3
        )
        answer = resp.choices[0].message.content
    except Exception as e:
        answer = f"Eroare: {str(e)}"

    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": answer})

    return "", history


def calculeaza_mg(sesiune, nc1, nc2, nb_val):
    def tr(v):
        return int(v * 100) / 100.0

    n1, n2, n3 = tr(nc1), tr(nc2), tr(nb_val)
    mc = tr((n1 + n2) / 2.0)
    if sesiune == "Sesiunea I (Admitere anticipată)":
        mg_brut = (4.0 * mc + n3) / 5.0
        formula = "MG = (4 * MC + NB) / 5"
    else:
        mg_brut = (0.8 * mc + 0.2 * n3)
        formula = "MG = 0,8 * MC + 0,2 * NB"

    mg_final = tr(mg_brut)
    status = "✅ ADMISIBIL" if mg_final >= 5.0 else "❌ RESPINS"
    return f"### {status}\n**Media Generală: {mg_final:.2f}**"


def get_stats():
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT intrebare, COUNT(*) as nr FROM monitorizare GROUP BY intrebare ORDER BY nr DESC LIMIT 10")
        data = cursor.fetchall()
        conn.close()
        return data
    except:
        return []


with gr.Blocks(title="Admitere ETTI - Chat Suport") as demo:
    gr.Markdown("# 🎓 Admitere ETTI - UPB")

    with gr.Tabs():
        with gr.TabItem("💬 Asistent Chat"):
            chatbot = gr.Chatbot(label="Chatbot Regulament")
            with gr.Row():
                txt = gr.Textbox(placeholder="Scrie aici...", show_label=False, scale=4)
                btn = gr.Button("Trimite", variant="primary")

            btn.click(respond, [txt, chatbot], [txt, chatbot])
            txt.submit(respond, [txt, chatbot], [txt, chatbot])

        with gr.TabItem("Calculator"):
            s = gr.Radio(["Sesiunea I (Admitere anticipată)", "Sesiunea II (Admitere)"], label="Sesiune",
                         value="Sesiunea I (Admitere anticipată)")
            with gr.Row():
                c1 = gr.Number(label="P1", value=9.0)
                c2 = gr.Number(label="P2", value=9.0)
                b = gr.Number(label="P3 / NB", value=9.0)
            c_btn = gr.Button("Calculează")
            out = gr.Markdown()
            c_btn.click(calculeaza_mg, [s, c1, c2, b], out)

        with gr.TabItem("Statistici"):
            r_btn = gr.Button("Refresh")
            st = gr.Dataframe(headers=["Întrebare", "Nr. Căutări"])
            r_btn.click(get_stats, outputs=st)

if __name__ == "__main__":
    setup_mysql()
    pdf_to_mysql(PDF_FILE)
    demo.launch(theme=gr.themes.Soft())