import smtplib as sm
import imaplib
import os
import time
import dns.resolver
import pandas as pd
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import formatdate
from datetime import datetime as dt

load_dotenv()

# --- Email Setup ---
EMAIL_ADDRESS = os.getenv('EMAIL_BOLU_EMAIL')
EMAIL_PASSWORD = os.getenv('EMAIL_BOLU_PASS')
SMTP_SERVER = 'smtp.fatcow.com'
SMTP_PORT = 465
IMAP_SERVER = 'imap.fatcow.com'

# --- Body Template ---
subject = 'Exciting Pre-Seed Funding Opportunity: Bridging the Gap in Europe’s Digital Banking Space'

body_template = '''<!DOCTYPE html>
        <html>
            <head>
            <style>
                .email-content {{
                font-size: 15px;
                line-height: 1.15;
                font-family: Arial, sans-serif;
                }}
                .email-content b {{
                font-weight: bold;
                }}
                .email-content p {{
                margin-bottom: 1.15em;
                margin-top: 0;
                }}
            </style>
            </head>
            <body>
            <div class="email-content">
                <p>Dear {name},</p>
                <p>I hope this message finds you well.</p>
                <p>
                As you may know, the European banking landscape is experiencing a significant shift. Currently, we have 4,886 traditional banks catering to the market, but only 77 neo-banks are stepping up to meet the growing demands of digitally savvy consumers, freelancers, and SMEs.
                </p>
                <p>
                At Montreux Financial, we can bridge this gap with our innovative AI-driven neo-bank platform, specifically tailored for the modern economy.
                </p>
                <p>
                <b>Core Offerings:</b><br>
                <b>- Seamless Banking:</b> Instant IBAN account creation and debit card issuance.<br>
                <b>- Crypto Integration:</b> Real-time trading and AI-enhanced portfolio management.<br>
                <b>- Democratized Investing:</b> Enabling fractional ownership in stocks and commodities.
                </p>
                <p>
                <b>Investment Highlights:</b><br>
                <b>- Market Opportunity:</b> Digital assets are projected to soar to €448 billion by 2028, with a robust CAGR of 28%.<br>
                <b>- Revenue Trajectory:</b> We aim €8 million in Year 1, scaling to €300 million by Year 5.<br>
                <b>- Pre-Seed Round:</b> We are seeking €380K to complete our platform development, expand our talented team, and accelerate our market launch.
                </p>
                <p>
                With regulatory advancements in progress and a seasoned leadership team at the helm, Montreux Financial is well-positioned for rapid growth.
                </p>
                <p>
                I would love to discuss how you might engage with this exciting venture. Could we schedule a brief 15-minute call at your convenience? For your reference, I’ve attached our overview deck below.
                </p>
                <p>
                Please let me know your availability this week. I genuinely look forward to hearing your thoughts!
                </p>
                <p>
                Best regards,<br><br>
                Pavel Pravosud<br>
                Founder & CEO | Montreux Financial<br>
                📞 +34 650 374 849 (WhatsApp)<br>
                ✉️ Pavel.Pravosud@fintechsdev.com<br>
                <br>
                <b>Link to Supporting Documents:</b> <a href = 'https://drive.google.com/drive/folders/12xlbSW1g_1zuKzQMf6T68PjBbb6Zt3bJ'>https://drive.google.com/drive/folders/12xlbSW1g_1zuKzQMf6T68PjBbb6Zt3bJ</a><br>
                <br>
                <i>P.S. If now's not ideal, reply "LATER" – and I will reconnect at a later date. Prefer WhatsApp? Tap here: <a href='https://wa.me/34650374849'>Send a Quick Message</a></i>
                </p>
            </div>
            </body>
            </html>'''

# --- Validate Email Domain ---
def is_valid_email(email):
    try:
        domain = email.split('@')[-1]
        dns.resolver.resolve(domain, 'MX')
        return True
    except Exception:
        return False

# --- Send Email ---
def send_email(to_email, name, attachments, server, imap):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = subject
    msg['Date'] = formatdate(localtime=True)
    
    body = body_template.format(name=name)
    msg.attach(MIMEText(body, 'html'))

    for file in attachments:
        if os.path.isfile(file):
            with open(file, 'rb') as fr:
                part = MIMEApplication(fr.read(), Name=os.path.basename(file))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file)}"'
                msg.attach(part)

    server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())

    try:
        imap.append('INBOX.Sent', '', imaplib.Time2Internaldate(time.time()), msg.as_bytes())
    except:
        pass

# --- Load Data ---
df = pd.read_csv('investors-21-06-2025.csv')  # 👈 Change path as needed
attachments = ['Montreux Financial Pitch.pdf']

# --- Start Session Once ---
server = sm.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

imap = imaplib.IMAP4_SSL(IMAP_SERVER)
imap.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

log = []
start_time = time.time()

# --- Send Loop ---
for _, row in df.iterrows():
    name = row.get('Name').strip()
    email = row.get('Emails').strip()

    if not is_valid_email(email):
        log.append({'Name': name, 'Email': email, 'Status': 'Invalid email domain'})
        continue

    try:
        send_start = time.time()
        send_email(email, name, attachments, server, imap)
        duration = round(time.time() - send_start, 2)
        log.append({'Name': name, 'Email': email, 'Status': 'Sent', 'Time (s)': duration})
        print(f"✅ Sent to {email} in {duration}s")
    except Exception as e:
        log.append({'Name': name, 'Email': email, 'Status': f'Failed: {str(e)}'})
        print(f"❌ Failed to send to {email}: {e}")

# --- End Session ---
server.quit()
imap.logout()

# --- Save Logs ---
log_df = pd.DataFrame(log)
log_df.to_csv(f'email_log-{dt.now():%d-%m_%H-%M}_.csv', index=False)

total_time = round(time.time() - start_time, 2)
print("\n--- Summary ---")
print(f"📧 Total Emails: {sum(log['Email'])}")
print(f"📬 Total Sent: {sum(l['Status'] == 'Sent' for l in log)}")
print(f"🕒 Total Time: {total_time}s")
print("📂 Log saved to 'email_log.csv'")