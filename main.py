# main.py
from datetime import datetime
import matplotlib.pyplot as plt
import networkx as nx
from greedy_algorithm import greedy_minimize
from graph_flow_algorithm import graph_flow_minimize
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Gmail credentials – CHANGE THESE!
GMAIL_USER = "lokeshwarvarma09@gmail.com"           # your Gmail address
GMAIL_PASSWORD = "kdli zozl ngpn gxax"         # app password (generate at https://myaccount.google.com/apppasswords)

def draw_debts(transactions, title):
    if not transactions:
        print(f"[{title}] No transactions")
        return

    G = nx.DiGraph()
    for a, b, amt in transactions:
        G.add_edge(a, b, weight=amt)

    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, node_color='lightblue',
            node_size=2200, font_size=10, font_weight='bold',
            arrows=True, arrowstyle='->', arrowsize=20)
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9)
    plt.title(title)
    plt.axis('off')
    plt.show()

def generate_pdf_report(members, transactions, greedy_result, flow_result, filename="settlement_report.pdf"):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()

    # Colors (RGB)
    BLUE = (78, 115, 223)
    DARK_BLUE = (44, 62, 80)
    GRAY = (108, 117, 125)
    LIGHT_GRAY = (248, 249, 252)

    # Header
    pdf.set_fill_color(*BLUE)
    pdf.rect(0, 0, 210, 30, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 20)
    pdf.cell(0, 15, "Cash Flow Minimization Report", 0, 1, "C")
    pdf.ln(5)

    # Subtitle
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, "M.Gowtham (24018) & N.Lokeshwar (24020)", 0, 1, "C")
    pdf.ln(10)

    # Reset text color
    pdf.set_text_color(*DARK_BLUE)

    # Group Members Table
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Group Members", 0, 1)
    pdf.set_font("Arial", "", 11)
    pdf.set_fill_color(*LIGHT_GRAY)
    pdf.cell(90, 8, "Name", 1, 0, "C", True)
    pdf.cell(100, 8, "Email ID", 1, 1, "C", True)

    pdf.set_font("Arial", "", 11)
    for name, details in members.items():
        pdf.cell(90, 8, name, 1, 0, "C")
        pdf.cell(100, 8, details['email'], 1, 1, "C")

    pdf.ln(5)

    # Original Transactions Table
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Original Transactions", 0, 1)
    pdf.set_font("Arial", "", 11)
    pdf.set_fill_color(*LIGHT_GRAY)
    pdf.cell(60, 8, "Payer", 1, 0, "C", True)
    pdf.cell(60, 8, "Payee", 1, 0, "C", True)
    pdf.cell(70, 8, "Amount", 1, 1, "C", True)

    pdf.set_font("Arial", "", 11)
    for a, b, amt in transactions:
        pdf.cell(60, 8, a, 1)
        pdf.cell(60, 8, b, 1)
        pdf.cell(70, 8, f"Rs.{amt}", 1, 1, "R")  # Safe fallback

    pdf.ln(5)

    # Greedy Result Table
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Greedy Algorithm Result", 0, 1)
    pdf.set_font("Arial", "", 11)
    pdf.set_fill_color(*LIGHT_GRAY)
    pdf.cell(60, 8, "From", 1, 0, "C", True)
    pdf.cell(60, 8, "To", 1, 0, "C", True)
    pdf.cell(70, 8, "Amount", 1, 1, "C", True)

    pdf.set_font("Arial", "", 11)
    if not greedy_result:
        pdf.set_text_color(39, 174, 96)
        pdf.cell(190, 8, "No transactions left (Already balanced)", 1, 1, "C")
        pdf.set_text_color(*DARK_BLUE)
    else:
        for a, b, amt in greedy_result:
            pdf.cell(60, 8, a, 1)
            pdf.cell(60, 8, b, 1)
            pdf.cell(70, 8, f"Rs.{amt}", 1, 1, "R")

    pdf.ln(5)

    # Flow Result Table
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Graph Flow Algorithm Result", 0, 1)
    pdf.set_font("Arial", "", 11)
    pdf.set_fill_color(*LIGHT_GRAY)
    pdf.cell(60, 8, "From", 1, 0, "C", True)
    pdf.cell(60, 8, "To", 1, 0, "C", True)
    pdf.cell(70, 8, "Amount", 1, 1, "C", True)

    pdf.set_font("Arial", "", 11)
    if not flow_result:
        pdf.set_text_color(39, 174, 96)
        pdf.cell(190, 8, "No transactions left (Already balanced)", 1, 1, "C")
        pdf.set_text_color(*DARK_BLUE)
    else:
        for a, b, amt in flow_result:
            pdf.cell(60, 8, a, 1)
            pdf.cell(60, 8, b, 1)
            pdf.cell(70, 8, f"Rs.{amt}", 1, 1, "R")
            
    pdf.ln(5)
    
    # GRAPH ANALYTICS
    pdf.add_page()
    pdf.set_font("Arial","B",14)
    pdf.cell(0,10,"Analytic Graphs",0,1,"C")
    
    import os
    if os.path.exists("greedy_graph_cli.png"):
        pdf.set_font("Arial","B",12)
        pdf.cell(0,10,"Greedy Algorithm Network:",0,1)
        pdf.image("greedy_graph_cli.png", x=20, w=140)
        pdf.ln(5)
        
    if os.path.exists("flow_graph_cli.png"):
        pdf.set_font("Arial","B",12)
        pdf.cell(0,10,"Graph Flow Network:",0,1)
        pdf.image("flow_graph_cli.png", x=20, w=140)
        pdf.ln(5)

    # Summary
    reduction_greedy = len(transactions) - len(greedy_result) if transactions else 0
    reduction_flow = len(transactions) - len(flow_result) if transactions else 0
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(39, 174, 96)  # Green
    pdf.cell(0, 10, f"Optimization Summary: Greedy reduced {reduction_greedy} edges. Flow reduced {reduction_flow} edges.", 0, 1)

    # Footer
    pdf.set_y(-15)
    pdf.set_font("Arial", "I", 8)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 10, f"Generated on {datetime.now().strftime('%d %b %Y %H:%M')} | Project by M.Gowtham & N.Lokeshwar", 0, 0, "C")

    # Save PDF (fixed mode)
    pdf.output(filename, 'F')
    print(f"\nProfessional PDF Report generated: {filename}")
    return filename

def send_email_report(to_email, pdf_file, name):
    msg = MIMEMultipart()
    msg['From'] = GMAIL_USER
    msg['To'] = to_email
    msg['Subject'] = "Cash Flow Minimization Report"

    body = f"Hi {name},\nYour personalized settlement report is attached.\n\nThank you for using Cash Flow Minimizer!"
    msg.attach(MIMEText(body, 'plain'))

    # Attach PDF
    with open(pdf_file, "rb") as attachment:
        p = MIMEBase('application', 'octet-stream')
        p.set_payload(attachment.read())
        encoders.encode_base64(p)
        p.add_header('Content-Disposition', f"attachment; filename= {pdf_file}")
        msg.attach(p)

    try:
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
            server.starttls()
            server.login(GMAIL_USER, GMAIL_PASSWORD)
        except Exception:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10)
            server.login(GMAIL_USER, GMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(GMAIL_USER, to_email, text)
        server.quit()
        print(f"✅ Report sent to {name} ({to_email})")
    except Exception as e:
        print(f"Failed to send to {name}: {e}")

# ────────────────────── MAIN PROGRAM ──────────────────────

print("=== Cash Flow Minimization Project ===")
print("Enter group members with names and email IDs")
print("Format : name email_address")
print("Examples:")
print("  Alice alice@example.com")
print("  Bob bob@example.com")
print("When finished type: done\n")

members = {}  # name → {email}

while True:
    line = input("→ ").strip()
    if line.lower() in ['done', 'd', 'exit', 'q']:
        break

    parts = line.split()
    if len(parts) < 2:
        print("Invalid format → use: Name email@example.com")
        continue

    name, email = parts[0], parts[1]
    if '@' not in email or '.' not in email:
        print("Invalid email format")
        continue

    members[name] = {"email": email}
    print(f"Added: {name} ({email})")

if len(members) < 2:
    print("\nAt least 2 members required. Goodbye.")
else:
    print("\n" + "="*50)
    print("Group Members")
    print("="*50)
    for name, details in members.items():
        print(f"{name:10} : {details['email']}")

    print("\nEnter transactions mode:")
    print("1. Direct Transactions (payer payee amount)")
    print("2. Group Expense (enter who paid, then exact amounts spent by others)")
    choice = input("Choice (1 or 2): ").strip()

    transactions = []

    if choice == '2':
        while True:
            print("\n--- Add Group Expense ---")
            payer = input("Who Paid? (or type 'done' to finish): ").strip()
            if payer.lower() in ['done', 'd', 'exit', 'q']:
                break
            if payer not in members:
                print("Name not in group members.")
                continue

            parts = input("Enter all participants separated by space: ").strip().split()
            valid_parts = [p for p in parts if p in members]
            if not valid_parts:
                print("No valid participants given.")
                continue

            for p in valid_parts:
                if p != payer:
                    amt_str = input(f"Exactly how much did {p} spend? ").strip()
                    try:
                        amt = float(amt_str)
                        if amt > 0:
                            transactions.append((p, payer, amt))
                    except ValueError:
                        print("Invalid amount skipped.")
            print("Expense recorded.")
    else:
        print("\nEnter transactions one by one")
        print("Format : payer payee amount")
        print("Examples:")
        print("  Alice Bob 1200")
        print("When finished type: done\n")

        while True:
            line = input("→ ").strip()
            if line.lower() in ['done', 'd', 'exit', 'q']:
                break

            parts = line.split()
            if len(parts) != 3:
                print("Invalid format → use: Name1 Name2 123")
                continue

            payer, payee, amt_str = parts
            if payer not in members or payee not in members:
                print("Payer or payee not in group members")
                continue

            try:
                amount = float(amt_str)
                if amount <= 0:
                    print("Amount must be positive")
                    continue
                transactions.append((payer, payee, amount))
            except ValueError:
                print("Amount must be a number")
                continue

    if not transactions:
        print("\nNo transactions entered. Goodbye.")
    else:
        print("\n" + "="*50)
        print("INPUT TRANSACTIONS")
        print("="*50)
        for a, b, amt in transactions:
            print(f"{a:10} owes {b:10} Rs.{amt:>6}")

        # Greedy
        greedy_result = greedy_minimize(transactions)
        print("\n" + "="*50)
        print("GREEDY ALGORITHM RESULT")
        print("="*50)
        if not greedy_result:
            print("No transactions left (Already Balanced)")
        else:
            for a, b, amt in greedy_result:
                print(f"{a:10} -> {b:10} : Rs.{amt:>6}")
        print(f"→ Reduced to {len(greedy_result)} transactions")
        
        # Graph Flow
        flow_result = graph_flow_minimize(transactions)
        print("\n" + "="*50)
        print("GRAPH FLOW ALGORITHM RESULT")
        print("="*50)
        if not flow_result:
            print("No transactions left (Already Balanced)")
        else:
            for a, b, amt in flow_result:
                print(f"{a:10} -> {b:10} : Rs.{amt:>6}")
        print(f"→ Reduced to {len(flow_result)} transactions")
        
        # Save graph image before PDF generates
        import networkx as nx
        if greedy_result:
            G_temp = nx.DiGraph()
            for a, b, amt in greedy_result:
                G_temp.add_edge(a, b, weight=amt)
            pos_temp = nx.spring_layout(G_temp, seed=42)
            plt.figure(figsize=(6, 4))
            nx.draw(G_temp, pos_temp, with_labels=True, node_color='lightgreen', node_size=1500)
            nx.draw_networkx_edge_labels(G_temp, pos_temp, edge_labels=nx.get_edge_attributes(G_temp, 'weight'))
            plt.savefig("greedy_graph_cli.png")
            plt.close()
            
        if flow_result:
            G_flow = nx.DiGraph()
            for a, b, amt in flow_result:
                G_flow.add_edge(a, b, weight=amt)
            pos_flow = nx.spring_layout(G_flow, seed=42)
            plt.figure(figsize=(6, 4))
            nx.draw(G_flow, pos_flow, with_labels=True, node_color='lightblue', node_size=1500)
            nx.draw_networkx_edge_labels(G_flow, pos_flow, edge_labels=nx.get_edge_attributes(G_flow, 'weight'))
            plt.savefig("flow_graph_cli.png")
            plt.close()

        # Generate PDF Report
        pdf_file = generate_pdf_report(members, transactions, greedy_result, flow_result)

        # Send email report to each person
        print("\nSending personalized report via email...")
        print("="*50)
        for name, details in members.items():
            email = details['email']
            send_email_report(email, pdf_file, name)

        # Visualizations
        print("\nShowing graphs... (close each window to continue)")
        draw_debts(transactions, "Original Debts")
        draw_debts(greedy_result, "After Greedy Minimization")

print("\nThank you for using the Cash Flow Minimizer!")