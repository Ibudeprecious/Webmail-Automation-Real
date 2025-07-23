import smtplib as sm
import imaplib
import os
import time
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import formatdate
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed


load_dotenv()

subject_template = 'Pre-seed Investment Opportunity for {name}: AI-Powered Neobank Built in Spain.'

body_template = '''
<!DOCTYPE html>
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
    <p>Dear {name} team,</p>
    <p>As a Europe-based fintech startup, we’ve long admired your role in shaping Europe’s tech ecosystem. With {investments}+ investments and {exits}+ exits, your track record of backing bold innovation has been a real inspiration to us at Montreux Financial.</p>
    <p> However, we noticed a gap in the European Banking System. </p>
    <p> Did you know that despite having 4,886 traditional banks in Europe, there are only 77 neobanks that are serving a rapidly growing segment of digital-native consumers, freelancers, and SMEs? </p>
    <p> This leaves users juggling multiple disconnected apps for banking, crypto, and investing—an outdated experience in a digital-first world. </p>
    <p> We are determined to fill this gap. Montreux Financial is a next-gen, AI-powered neobank built in Spain for Europe. We unify: </p>
    <ul>
      <strong> <li> Instant IBAN accounts + debit cards </li></strong>
      <strong> <li> Real-time crypto trading with AI portfolio optimization </li></strong>
      <strong> <li> Fractional investing in stocks, commodities, and digital assets </li></strong>
    </ul>
    <p>
      This is an all-in-one unified, <strong> mobile-first platform. </strong>
    </p>
    <p>
      We’re targeting a €500B+ converging market and are already in discussions with EU regulators. Our team has fintech expertise —including a previous exit—and we’re currently raising a €380K pre-seed round to complete development and launch.
    </p>
    <p>
      We’d love to explore if Montreux aligns with Wayra’s thesis. Would you be open to a 15-minute call next week?
    <p>
    <p>👉 <a href="https://drive.google.com/drive/folders/12xlbSW1g_1zuKzQMf6T68PjBbb6Zt3bJ"> View our Deck </a> </p>
    <p> Looking forward to hearing your thoughts. </p>
    <p>
      Best regards,<br>
      <b>Pavel Pravosud</b> <br>
      Founder & CEO - Montreux Financial<br>
      📞 +34 650 374 849 (Signal and WhatsApp)<br>
      ✉️ investors@fintechsdev.com <br>
      <br>
    </p> 
  </div>
</body>
</html>
'''
MAX_EMAILS_PER_CONNECTION = 10  # Adjust based on your provider's limits
emails_sent_in_connection = 0

def connect_smtp():
    server = sm.SMTP_SSL('smtp.fatcow.com', 465)
    server.login(os.getenv('EMAIL_BOLU_EMAIL'), os.getenv('EMAIL_BOLU_PASS'))
    return server

# server = connect_smtp()

# imap = imaplib.IMAP4_SSL('imap.fatcow.com')
# imap.login(os.getenv('EMAIL_BOLU_EMAIL'), os.getenv('EMAIL_BOLU_PASS'))

# def send_email(subject, body, to_email, attachments):
#     msg = MIMEMultipart()
#     msg['From'] = os.getenv('EMAIL_BOLU_EMAIL')
#     msg['To'] = to_email
#     msg['Subject'] = subject
#     msg['Date'] = formatdate(localtime=True)

#     msg.attach(MIMEText(body, 'html'))

#     for filepath in attachments:
#         if os.path.isfile(filepath):
#             with open(filepath, 'rb') as f:
#                 part = MIMEApplication(f.read(), Name=os.path.basename(filepath))
#                 part['Content-Disposition'] = f'attachment; filename="{os.path.basename(filepath)}"'
#                 msg.attach(part)
#         else:
#             print(f"⚠️ Attachment not found: {filepath}")

#     server.sendmail(
#         from_addr=os.getenv('EMAIL_BOLU_EMAIL'),
#         to_addrs=to_email,
#         msg=msg.as_string()
#     )
#     print('✅ Email sent to:', to_email)

#     try:
#         imap.append('INBOX.Sent', '', imaplib.Time2Internaldate(time.time()), msg.as_bytes())
#     except Exception as e:
#         print('⚠️ Could not append to Sent folder:', e)

sent_info = []

# --- Function to send individual emails ---
def send_individual_email(row, attachments):
    name = row['Organization/Person Name']
    email = row['Contact Email']
    website = row['Website'] # Adjust column name if needed
    subject = subject_template.format(name=name)
    body = body_template.format(
        name=name,
        investments=row['Number of Investments'],
        exits=row['Number of Exits']
    )

    start = time.time()
    try:
        smtp = connect_smtp()
        imap_local = imaplib.IMAP4_SSL('imap.fatcow.com')
        imap_local.login(os.getenv('EMAIL_BOLU_EMAIL'), os.getenv('EMAIL_BOLU_PASS'))

        msg = MIMEMultipart()
        msg['From'] = os.getenv('EMAIL_BOLU_EMAIL')
        msg['To'] = email
        msg['Subject'] = subject
        msg['Date'] = formatdate(localtime=True)

        msg.attach(MIMEText(body, 'html'))

        for filepath in attachments:
            if os.path.isfile(filepath):
                with open(filepath, 'rb') as f:
                    part = MIMEApplication(f.read(), Name=os.path.basename(filepath))
                    part['Content-Disposition'] = f'attachment; filename="{os.path.basename(filepath)}"'
                    msg.attach(part)

        smtp.sendmail(msg['From'], msg['To'], msg.as_string())
        imap_local.append('INBOX.Sent', '', imaplib.Time2Internaldate(time.time()), msg.as_bytes())
        smtp.quit()
        imap_local.logout()
        elapsed = time.time() - start
        print(f"✅ Email sent to: {email}")
        print(f"⏱ Sent to {email} in {elapsed:.2f} seconds")
        sent_info.append({'Name': name, 'Website': website})
        return True

    except Exception as e:
        elapsed = time.time() - start
        print(f"❌ Failed to send to {email}: {e}")
        print(f"⏱ Attempted in {elapsed:.2f} seconds")
        return False

# Load recipient data
df = pd.read_csv('spain-seed-investors-23-07-2025.csv')

# Send only to first 100 emails
df = df.head(100)

attachments = ['Montreux Financial Pitch.pdf']
total_email_sent = 0
start_time = time.time()

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(send_individual_email, row, attachments) for _, row in df.iterrows()]
    for i, future in enumerate(as_completed(futures)):
        if future.result():
            total_email_sent += 1

# Save sent info to new CSV
pd.DataFrame(sent_info).to_csv('sent_names_websites.csv', index=False)

total_time = time.time() - start_time
print(f"\n📨 Total emails sent: {total_email_sent}")
print(f"⏱ Total time taken: {total_time:.2f} seconds")

