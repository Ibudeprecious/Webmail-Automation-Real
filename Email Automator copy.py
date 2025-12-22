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

subject_template = 'Investment Opportunity: FintechsDev – The Omni-Channel Payment Gateway Transforming SME Banking'

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
    <p>Hi {name} team,</p>
    <p>I’m reaching out to introduce FintechsDev, an omni-channel payment and business banking platform built to solve a massive and persistent problem for European SMEs. </p>
    <p>Across the region, more than 25 million SMEs struggle with slow onboarding, fragmented tools, hidden banking fees, and outdated manual financial operations. With 65% dissatisfied with their current bank, the market is primed for a modern, integrated alternative. </p>
    <p> FintechsDev delivers that solution: </p>
    <ul>
      <strong> <li> Business accounts open in minutes, not weeks </li></strong>
      <strong> <li> Instant IBANs and physical/virtual cards </li></strong>
      <strong> <li> 120+ global and local payment methods </li></strong>
      <strong> <li> Real-time expense tracking and automated accounting </li></strong>
      <strong> <li> Multicurrency support with transparent, competitive FX </li></strong>
      <strong> <li> No hidden charges and a pay-for-what-you-use model </li></strong>
    </ul>
    <p> Our platform targets IT freelancers, startups, and SMEs with 2–150 employees, tapping into a €190B SME banking market with high churn and clear unmet needs. Competitors like Stripe, Moonpay, and Revolut each miss critical components we provide in one unified system. </p>
    <p> Our rollout plan is direct and execution-ready: </p>
    <ul>
      <strong> <li> Establish operations with a 20–25-person local team </li></strong>
      <strong> <li> Secure enterprise clients through existing partnerships </li></strong>
      <strong> <li> Onboard 800+ businesses and 25,000+ users locally </li></strong>
      <strong> <li> Expand EU-wide, then into the USA, EMEA, and APAC </li></strong>
      <strong> <li> Scale to 350–400 employees to support global growth </li></strong>
    </ul>
    <p>
      We are currently raising €450,000 in seed funding, allocated to licensing, product development, gateway launch, and a targeted marketing campaign. Our payment gateway is scheduled for rollout in 5–7 months.
    </p>
    <p>
      I’d welcome the chance to share our roadmap and discuss how we can align this opportunity with your investment thesis.
    </p>
    <p>
      Would you be available for a brief call this week or next?
    <p>
    <p> Here is a link to our pitch deck, do well to check it out. <a href="https://drive.google.com/drive/folders/1-AoKFaJ7-zvkGq4QhvIgAJdbEDrOYuHX">Click here</a>
    </p>

    <p>
      Best regards, <br>
      <strong> Pavel Pravosud </strong> <br>
      Founder & CEO – FintechsDev <br>
      +34 650 374 849 <br>
      WhatsApp at wa.me/+34650374849 <br>
      investors@fintechsdev.com <br>
      www.aldriv.com <br>
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

sent_info = []

smtp = connect_smtp()

# --- Function to send individual emails ---
def send_individual_email(row, smtp):
    name = row['Organization/Person Name']
    email = row['Contact Email']
    # website = row['Website'] # Adjust column name if needed
    subject = subject_template.format(name=name)
    body = body_template.format(
        name=name,
        # investments=row['Number of Investments'],
        # exits=row['Number of Exits']
    )

    start = time.time()
    try:
        imap_local = imaplib.IMAP4_SSL('imap.fatcow.com')
        imap_local.login(os.getenv('EMAIL_BOLU_EMAIL'), os.getenv('EMAIL_BOLU_PASS'))

        msg = MIMEMultipart()
        msg['From'] = os.getenv('EMAIL_BOLU_EMAIL')
        msg['To'] = email
        msg['Subject'] = subject
        msg['Date'] = formatdate(localtime=True)

        msg.attach(MIMEText(body, 'html'))

        # for filepath in attachments:
        #     if os.path.isfile(filepath):
        #         with open(filepath, 'rb') as f:
        #             part = MIMEApplication(f.read(), Name=os.path.basename(filepath))
        #             part['Content-Disposition'] = f'attachment; filename="{os.path.basename(filepath)}"'
        #             msg.attach(part)

        smtp.sendmail(msg['From'], msg['To'], msg.as_string())
        imap_local.append('INBOX.Sent', '', imaplib.Time2Internaldate(time.time()), msg.as_bytes())
        imap_local.logout()
        elapsed = time.time() - start
        print(f"✅ Email sent to: {email}")
        print(f"⏱ Sent to {email} in {elapsed:.2f} seconds")
        sent_info.append({'Name': name, 'Email': email})
        return True

    except Exception as e:
        elapsed = time.time() - start
        print(f"❌ Failed to send to {email}: {e}")
        print(f"⏱ Attempted in {elapsed:.2f} seconds")
        return False

# Load recipient data
df = pd.read_csv('newlist.csv')

# Send only to first 250 emails
df = df.head(226)


# attachments = ['FintechsDev+ Omni-Channel Payment Gateway 2024 (2).pptx']
total_email_sent = 0
start_time = time.time()

for _, row in df.iterrows():
    if send_individual_email(row, smtp):
        total_email_sent += 1

smtp.quit()
# Save sent info to new CSV
pd.DataFrame(sent_info).to_csv('sent_names_websites.csv', index=False)

total_time = time.time() - start_time
print(f"\n📨 Total emails sent: {total_email_sent}")
print(f"⏱ Total time taken: {total_time:.2f} seconds")

