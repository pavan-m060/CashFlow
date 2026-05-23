import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from greedy_algorithm import greedy_minimize
from graph_flow_algorithm import graph_flow_minimize

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from fpdf import FPDF
from datetime import datetime
import os


# EMAIL CONFIG
SENDER_EMAIL = "lokeshwarvarma09@gmail.com"
APP_PASSWORD = "vbozvbeattbpdpzu"


st.set_page_config(page_title="Cash Flow Minimizer", layout="wide", page_icon="💸")

st.markdown("""
<style>
    /* Premium Modern Dark Theme */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    :root {
        --primary: #6366f1;
        --primary-hover: #4f46e5;
        --secondary: #10b981;
        --bg-grad: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        --text-main: #f8fafc;
        --text-muted: #94a3b8;
        --danger: #ef4444;
    }

    .stApp {
        background: var(--bg-grad);
        color: var(--text-main);
    }
    
    h2, h3, h4 {
        color: var(--text-main) !important;
        font-weight: 600 !important;
    }

    /* Expense Item Styling */
    .expense-item {
        background: rgba(15, 23, 42, 0.6);
        border-left: 4px solid var(--primary);
        padding: 18px 20px;
        margin-bottom: 12px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        transition: all 0.2s ease;
    }
    .expense-item:hover {
        background: rgba(30, 41, 59, 0.8);
        border-left: 4px solid #c084fc;
    }

    /* Buttons */
    div.stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, rgba(139, 92, 246, 1) 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 14px 0 rgba(99, 102, 241, 0.39);
        width: 100%;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5);
        color: white;
    }
    div.stButton > button:active {
        transform: translateY(0);
    }
    
    /* Input Fields */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
        background-color: rgba(15, 23, 42, 0.5) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 8px !important;
        color: white !important;
        transition: border 0.2s ease;
    }
    div[data-baseweb="input"] > div:focus-within, div[data-baseweb="select"] > div:focus-within {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 1px var(--primary) !important;
    }

    hr {
        border-color: rgba(255,255,255,0.1);
        margin: 2rem 0;
    }
    
    /* Badges */
    .badge {
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        background: rgba(99, 102, 241, 0.15);
        color: #818cf8;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
</style>
""", unsafe_allow_html=True)


st.markdown("""
<h1 style="text-align: center; color: #f8fafc; text-shadow: 0px 4px 20px rgba(139, 92, 246, 0.6); font-weight: 800; font-size: 3.5rem; margin-bottom: 2rem;">
    💸 Cash Flow Minimizer
</h1>
""", unsafe_allow_html=True)


# SESSION STATE
if "members" not in st.session_state:
    st.session_state.members = {} # name -> {email}

if "expenses" not in st.session_state:
    st.session_state.expenses = []

if "results_ready" not in st.session_state:
    st.session_state.results_ready = False


# LAYOUT: Main application structure (Two Columns: Setup/Input vs Summary)
main_col1, main_col2 = st.columns([1.2, 1])

with main_col1:
    # ─── ADD MEMBERS CARD ───────────────
    st.subheader("👥 Add Group Members")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name", placeholder="e.g. Alice")
    with col2:
        email = st.text_input("Email", placeholder="alice@example.com")
        
    if st.button("Add Member", key="add_mem"):
        if name and email:
            st.session_state.members[name] = {"email": email}
            st.success(f"✨ **{name}** added successfully!")
        else:
            st.warning("Please provide both Name and Email.")


    # ─── ADD EXPENSE CARD ───────────────
    if st.session_state.members:
        st.write("---")
        st.subheader("💳 Add Expense")

        place = st.text_input("Expense / Place Description", placeholder="e.g. Dinner, Movie, Rent...")

        col1, col2 = st.columns(2)
        with col1:
            payer = st.selectbox("Who Paid?", list(st.session_state.members.keys()))
        with col2:
            split_type = st.radio("How to Split?", ["Equally", "Exact Amounts"], horizontal=True)

        participants = st.multiselect("Participants involved", list(st.session_state.members.keys()), default=list(st.session_state.members.keys()))

        amount = 0.0
        exact_amounts = {}

        if participants:
            if split_type == "Equally":
                amount = st.number_input("Total Amount Paid", min_value=1.0, value=100.0, step=10.0)
            else:
                st.markdown("<p style='color:var(--text-muted); font-size:0.9rem;'>Enter exact amounts for each participant:</p>", unsafe_allow_html=True)
                for p in participants:
                    val = st.number_input(f"Amount {p} spent", min_value=0.0, value=0.0, step=10.0, key=f"exact_{p}_{place}")
                    exact_amounts[p] = val
                amount = sum(exact_amounts.values())
                if amount > 0:
                    st.info(f"**Calculated Total:** Rs. {amount:.2f}")

        if st.button("💾 Save Expense", key="save_exp"):
            if place and participants and amount > 0:
                if split_type == "Equally":
                    per_person = amount / len(participants)
                    exact_amounts = {p: per_person for p in participants}
                else:
                    s = sum(exact_amounts.values())
                    if s <= 0:
                        st.error("Total amount must be greater than zero.")
                        st.stop()
                    per_person = amount / len(participants)

                st.session_state.expenses.append({
                    "place": place,
                    "payer": payer,
                    "participants": participants,
                    "split_type": split_type,
                    "exact_amounts": exact_amounts,
                    "per_person": exact_amounts[participants[0]] if split_type == "Equally" else per_person,
                    "total": amount
                })
                st.success(f"Expense '{place}' saved successfully!")
                st.rerun()
            else:
                st.warning("Please fill out the description and ensure positive amounts.")

        # ─── MINIMIZE TRANSACTIONS ───────────────
        if st.session_state.expenses:
            st.markdown('<div style="margin-top:20px;">', unsafe_allow_html=True)
            if st.button("🚀 Minimize All Transactions", use_container_width=True):
                all_tx = []
                for e in st.session_state.expenses:
                    for p in e["participants"]:
                        if p != e["payer"]:
                            owed = e.get("exact_amounts", {}).get(p, e.get("per_person", 0))
                            if owed > 0:
                                all_tx.append((p, e["payer"], owed))

                st.session_state.transactions = all_tx
                st.session_state.greedy_result = greedy_minimize(all_tx)
                st.session_state.flow_result = graph_flow_minimize(all_tx)
                st.session_state.results_ready = True
            st.markdown('</div>', unsafe_allow_html=True)


with main_col2:
    # ─── OVERVIEW: MEMBERS & EXPENSES ───────────────
    if st.session_state.members:
        st.subheader("📋 Group Members")
        for n, details in st.session_state.members.items():
            st.markdown(f"<div style='margin-bottom:6px;'>🔹 <strong>{n}</strong> <span style='color:var(--text-muted); font-size:0.9em;'>({details['email']})</span></div>", unsafe_allow_html=True)
        st.write("")

    if st.session_state.expenses:
        st.subheader("🧾 Registered Expenses")

        for e in st.session_state.expenses:
            html = f'''
            <div class="expense-item">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <h4 style="margin:0 0 4px 0;">{e['place']}</h4>
                        <span class="badge">{e.get('split_type', 'Equally')}</span>
                    </div>
                    <div style="text-align: right;">
                        <span style="color: #10b981; font-weight: 800; font-size:1.1rem;">Rs. {e['total']:.2f}</span>
                        <div style="color: #94a3b8; font-size:0.85rem; margin-top:4px;">Paid by: <strong>{e['payer']}</strong></div>
                    </div>
                </div>
            '''
            
            # Show sub-owed amounts
            for p in e["participants"]:
                if p != e["payer"]:
                    owed = e.get("exact_amounts", {}).get(p, e.get("per_person", 0))
                    if owed > 0:
                        html += f"<div style='margin-top:6px; font-size:0.9rem; color:#cbd5e1;'>↳ <strong>{p}</strong> owes <strong>{e['payer']}</strong>: Rs. {owed:.2f}</div>"
            
            html += "</div>"
            st.markdown(html, unsafe_allow_html=True)


# ==========================================
# GRAPH DISPLAY FUNCTION
# ==========================================
def draw_graph(data, title, node_color="#6366f1", edge_color="#a855f7"):
    if not data:
        st.info(f"[{title}] No transactions needed. Already Balanced!")
        return None

    G = nx.DiGraph()
    combined = {}

    for a, b, w in data:
        combined[(a, b)] = combined.get((a, b), 0) + w

    for (a, b), w in combined.items():
        G.add_edge(a, b, weight=round(w, 2))

    pos = nx.circular_layout(G)

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('#0f172a')  # Match dark theme
    ax.set_facecolor('#0f172a')

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=4000, node_color=node_color, edgecolors="white", linewidths=1.5)

    # Draw node labels
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=13, font_weight="bold", font_color="white")

    # Draw edges
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color=edge_color, width=3.0, arrowsize=35, arrowstyle="-|>", connectionstyle="arc3,rad=0.15", alpha=0.85, node_size=4000)

    # Draw edge labels
    labels={(u,v):f"Rs. {d['weight']:.2f}" for u,v,d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, ax=ax, font_size=12, font_weight="bold", font_color="#f8fafc", bbox=dict(facecolor="#1e293b", edgecolor=edge_color, alpha=0.9, boxstyle="round,pad=0.4"))

    ax.set_title(title, fontsize=18, fontweight="bold", color="#f8fafc", pad=20)
    ax.axis("off")
    fig.tight_layout()

    st.pyplot(fig)
    return fig


# ==========================================
# PDF GENERATION
# ==========================================
def generate_pdf_report(members, expenses, transactions, greedy_result, flow_result, filename):

    pdf = FPDF()
    pdf.add_page()
    
    # Colors
    DARK_BLUE = (44, 62, 80)
    LIGHT_GRAY = (245, 245, 245)
    GREEN = (39, 174, 96)
    PURPLE = (142, 68, 173)

    pdf.set_font("Arial","B",16)
    pdf.set_text_color(*DARK_BLUE)
    pdf.cell(0,10,"Cash Flow Minimization Report",0,1,"C")
    pdf.line(10, 20, 200, 20)
    pdf.ln(5)

    # GROUP MEMBERS
    pdf.set_font("Arial","B",12)
    pdf.cell(0,8,"1. Group Members",0,1)

    pdf.set_font("Arial","B",11)
    pdf.set_fill_color(*LIGHT_GRAY)
    pdf.cell(95,8,"Name",1,0,"C", True)
    pdf.cell(95,8,"Email ID",1,1,"C", True)

    pdf.set_font("Arial","",11)
    for name, details in members.items():
        pdf.cell(95,8,name,1,0,"C")
        pdf.cell(95,8,details['email'],1,1,"C")

    pdf.ln(5)

    # SAVED EXPENSES
    pdf.set_font("Arial","B",12)
    pdf.cell(0,8,"2. Registered Expenses",0,1)

    pdf.set_font("Arial","",11)
    for e in expenses:
        pdf.set_font("Arial","B",11)
        pdf.cell(0,8,f"{e['place']} (Total: Rs. {e['total']:.2f}) - Paid by {e['payer']}",0,1)
        pdf.set_font("Arial","",11)
        for p in e["participants"]:
            if p != e["payer"]:
                owed = e.get("exact_amounts", {}).get(p, e.get("per_person", 0))
                if owed > 0:
                    pdf.cell(10, 6, "", 0, 0)
                    pdf.cell(0,6,f"-> {p} owes {e['payer']} Rs. {owed:.2f}",0,1)
        pdf.ln(2)

    pdf.ln(3)

    # ORIGINAL TRANSACTIONS
    pdf.set_font("Arial","B",12)
    pdf.cell(0,8,"3. Initial Debt Network (Before Minimization)",0,1)

    pdf.set_font("Arial","B",11)
    pdf.set_fill_color(*LIGHT_GRAY)
    pdf.cell(65,8,"Payer (Owes)",1,0,"C", True)
    pdf.cell(60,8,"Payee (Receives)",1,0,"C", True)
    pdf.cell(65,8,"Amount",1,1,"C", True)

    pdf.set_font("Arial","",11)
    if not transactions:
        pdf.cell(190, 8, "No debts.", 1, 1, "C")
    for a,b,amt in transactions:
        pdf.cell(65,8,a,1,0,"C")
        pdf.cell(60,8,b,1,0,"C")
        pdf.cell(65,8,f"Rs. {amt:.2f}",1,1,"R")

    pdf.ln(5)

    # GREEDY RESULT
    pdf.set_font("Arial","B",12)
    pdf.cell(0,8,"4. Minimized Debts (Greedy Algorithm)",0,1)
    pdf.set_font("Arial","",11)
    if not greedy_result:
        pdf.set_text_color(*GREEN)
        pdf.cell(0,8,"Accounts are fully balanced. No transactions needed.",0,1)
        pdf.set_text_color(*DARK_BLUE)
    else:
        for a,b,amt in greedy_result:
            pdf.cell(10, 6, "", 0, 0)
            pdf.cell(0,8,f"-> {a} must pay {b} : Rs. {amt:.2f}",0,1)

    pdf.ln(5)
    
    # FLOW RESULT
    pdf.set_font("Arial","B",12)
    pdf.cell(0,8,"5. Minimized Debts (Graph Flow Algorithm)",0,1)
    pdf.set_font("Arial","",11)
    if not flow_result:
        pdf.set_text_color(*GREEN)
        pdf.cell(0,8,"Accounts are fully balanced. No transactions needed.",0,1)
        pdf.set_text_color(*DARK_BLUE)
    else:
        for a,b,amt in flow_result:
            pdf.cell(10, 6, "", 0, 0)
            pdf.cell(0,8,f"-> {a} must pay {b} : Rs. {amt:.2f}",0,1)
            
    reduction_greedy = len(transactions) - len(greedy_result) if transactions else 0
    reduction_flow = len(transactions) - len(flow_result) if transactions else 0
    
    pdf.ln(5)
    pdf.set_font("Arial","B",11)
    pdf.set_text_color(*GREEN)
    pdf.cell(0,8,f"Optimization Summary: Greedy reduced {reduction_greedy} edges. Flow reduced {reduction_flow} edges.",0,1)
    pdf.set_text_color(*DARK_BLUE)
    
    # GRAPH ANALYTICS
    pdf.add_page()
    pdf.set_font("Arial","B",14)
    pdf.cell(0,10,"Analytics & Visualizations",0,1,"C")
    pdf.ln(5)
    
    if os.path.exists("greedy_graph_temp.png"):
        pdf.set_font("Arial","B",12)
        pdf.cell(0,10,"Greedy Algorithm Network:",0,1)
        pdf.image("greedy_graph_temp.png", x=15, w=180)
        pdf.ln(5)
        
    if os.path.exists("flow_graph_temp.png"):
        pdf.set_font("Arial","B",12)
        pdf.cell(0,10,"Graph Flow Algorithm Network:",0,1)
        pdf.image("flow_graph_temp.png", x=15, w=180)
        pdf.ln(5)

    pdf.set_y(-20)
    pdf.set_font("Arial","I",10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0,8,f"Generated securely on {datetime.now().strftime('%d %b %Y %H:%M')}",0,0,"C")

    pdf.output(filename)
    return filename


# ==========================================
# DISPLAY ALGORITHM RESULTS
# ==========================================
if st.session_state.get("results_ready"):
    st.write("---")
    st.markdown("<h2 style='text-align:center;'>📊 Settlement Analysis</h2>", unsafe_allow_html=True)
    
    col_out1, col_out2 = st.columns(2)
    
    # --- GREEDY ---
    with col_out1:
        st.subheader("Greedy Algorithm")
        if not st.session_state.greedy_result:
            st.success("✅ No transactions left (Already Balanced!)")
        else:
            for fr,to,amt in st.session_state.greedy_result:
                st.markdown(f"**{fr}** ➔ **{to}** : <span style='color:var(--secondary);'>Rs. {amt:.2f}</span>", unsafe_allow_html=True)
        
        fig1 = draw_graph(st.session_state.greedy_result, "Greedy Graph", node_color="#f43f5e", edge_color="#fb7185")
        if fig1:
            fig1.savefig("greedy_graph_temp.png", facecolor='#0f172a', bbox_inches='tight')

    # --- FLOW ---
    with col_out2:
        st.subheader("Graph Flow Algorithm")
        if not st.session_state.flow_result:
            st.success("✅ No transactions left (Already Balanced!)")
        else:
            for fr,to,amt in st.session_state.flow_result:
                st.markdown(f"**{fr}** ➔ **{to}** : <span style='color:var(--secondary);'>Rs. {amt:.2f}</span>", unsafe_allow_html=True)
                
        fig2 = draw_graph(st.session_state.flow_result, "Graph Flow Graph", node_color="#3b82f6", edge_color="#60a5fa")
        if fig2:
            fig2.savefig("flow_graph_temp.png", facecolor='#0f172a', bbox_inches='tight')


    # ==========================================
    # EMAIL REPORT SENDER
    # ==========================================
    st.write("---")
    cols_btn = st.columns([1, 2, 1])
    with cols_btn[1]:
        if st.button("📧 Send Settlement Report to All Members", use_container_width=True):
            with st.spinner("Generating PDF and sending emails..."):
                try:
                    pdf_path = "Settlement_Report.pdf"

                    generate_pdf_report(
                        st.session_state.members,
                        st.session_state.expenses,
                        st.session_state.transactions,
                        st.session_state.greedy_result,
                        st.session_state.flow_result,
                        pdf_path
                    )

                    try:
                        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
                        server.starttls()
                        server.login(SENDER_EMAIL,APP_PASSWORD)
                    except Exception:
                        server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10)
                        server.login(SENDER_EMAIL,APP_PASSWORD)

                    success = 0

                    for name, details in st.session_state.members.items():
                        email = details['email']
                        msg = MIMEMultipart()
                        msg["From"] = SENDER_EMAIL
                        msg["To"] = email
                        msg["Subject"] = "Cash Flow Settlement Report"

                        msg.attach(MIMEText("Hi there,\n\nPlease find attached the automated Cash Flow Settlement Report.\n\nThank you,\nCash Flow Minimizer App","plain"))

                        with open(pdf_path,"rb") as f:
                            part = MIMEApplication(f.read(),Name="Settlement_Report.pdf")
                            part['Content-Disposition'] = 'attachment; filename="Settlement_Report.pdf"'
                            msg.attach(part)

                        server.sendmail(SENDER_EMAIL,email,msg.as_string())
                        success += 1

                    server.quit()
                    st.success(f"🎉 Settlement Report successfully sent to {success} members via Email!")
                except Exception as e:
                    st.error(f"Failed to generate or send email: {e}")