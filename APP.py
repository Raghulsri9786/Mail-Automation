import streamlit as st
import smtplib
from email.message import EmailMessage
import re
import google.generativeai as genai
import datetime


# Configure Page
st.set_page_config(page_title="Aptean EDI Automation Portal", layout="wide")
st.sidebar.image(r"C:\Users\rs1\OneDrive - Aptean-online\Desktop\AI\idAUq6R9ng.jpeg", width=1500)
st.sidebar.markdown("## 📌 About Mail Automation")

st.sidebar.write(
    "### 🔹 Introduction\n"
    "The **Aptean EDI Automation Portal** is designed to simplify email communication for EDI-related transactions. "
    "It automates the process of generating professional emails and sending them with minimal manual effort."
)

st.sidebar.write("### 🔹 Problem Statement\n"
    "Manual email communication for EDI-related queries is time-consuming and error-prone. "
    "This tool helps generate structured emails efficiently."
)

st.sidebar.write("### 📜 Email History")
if "email_history" not in st.session_state:
    st.session_state["email_history"] = []

if st.session_state["email_history"]:
    for i, history in enumerate(reversed(st.session_state["email_history"][-5:])):  # Show last 5 emails
        if st.sidebar.button(f"{history['subject']} - {history['timestamp']}"):
            st.session_state["subject"] = history["subject"]
            st.session_state["body"] = history["body"]
            st.session_state["email_generated"] = True
else:
    st.sidebar.write("No history available.")




# Gemini AI Setup
genai.configure(api_key="AIzaSyC8Is-_d6cBqDg2gPzu3Iw1T2SbT0sszXI")
model = genai.GenerativeModel("gemini-pro")

# Function to Generate Email Content using AI
def enhance_email_content(user_prompt):
    prompt_text = f"""
    Write a professional email based on the following details:
    
    Recipient: Manager  
    Key Details: {user_prompt}  
    Tone: Polite  
    Provide the subject and body separately.
    Sincerely,
    [Raghul M S]
    """
    
    response = model.generate_content(prompt_text)
    email_text = re.sub(r"\*\*", "", response.text)
    
    # Extract subject and body
   # Extract subject and body
    email_lines = email_text.split("\n")
    subject, body = "", []
    capture_body = False

    for line in email_lines:
        if line.lower().startswith("subject:"):
            subject = line.replace("Subject:", "").strip()
            capture_body = True  # Start capturing body after the subject
        elif capture_body:
            if line.lower().startswith("body:"):  # Remove "Body:" if present
                continue
            body.append(line)

    # Join body lines into a string
    body_text = "\n".join(body).strip()
    return subject, body_text

       

# Function to Send Email
def send_email(sender, password, recipient_str, cc_str, subject, body,file=None):
    msg = EmailMessage()
    recipients = [email.strip() for email in recipient_str.split(',') if email.strip()]
    cc_list = [email.strip() for email in cc_str.split(',') if email.strip()]
    
    msg['From'] = sender
    msg['To'] = ", ".join(recipients)
    if cc_list:
        msg['Cc'] = ", ".join(cc_list)
    msg['Subject'] = subject
    msg.set_content(body)
    
    if file is not None:
        file_data = file.getvalue()
        msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=file.name)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg, from_addr=sender, to_addrs=recipients + cc_list)
        server.quit()
        return "✅ Email Sent Successfully!"
    except Exception as e:
        return f"❌ An error occurred: {e}"

# Layout: Two Columns (Left - AI, Right - Email)
col1, col2 = st.columns([1, 1])

# 🔹 Left Side (AI Section)
with col1:
    # st.image(r"C:\Users\rs1\OneDrive - Aptean-online\Desktop\AI\Aptean_idIi4XDGmj_0.png", use_column_width=True,width=50)
    st.image(r"C:\Users\rs1\OneDrive - Aptean-online\Desktop\AI\Aptean_idIi4XDGmj_0.png", width=250)

    st.header("AI Email Generator")
    
    user_prompt = st.text_area("Enter your email request details:")
    
    if st.button("Generate Email"):
        subject, body = enhance_email_content(user_prompt)
        st.session_state['subject'] = subject
        st.session_state['body'] = body
        st.session_state['email_generated'] = True
    
    # Show AI-Generated Email
    if 'email_generated' in st.session_state and st.session_state['email_generated']:
        st.subheader("Generated Email")
        st.text_input("Subject:", st.session_state['subject'])
        st.text_area("Body:", st.session_state['body'], height=200)
        
        col1a, col1b = st.columns(2)
        with col1a:
            if st.button("Regenerate"):
                st.session_state['email_generated'] = False
                st.rerun()
        with col1b:
            if st.button("Approve & Send"):
                st.session_state['approved'] = True

# 🔹 Right Side (Email Information)
with col2:
    # st.image(r"C:\Users\rs1\OneDrive - Aptean-online\Desktop\AI\idAUq6R9ng.jpeg", use_column_width=True)
    st.header("Email Information")
    
    if 'approved' in st.session_state and st.session_state['approved']:
        sender_email = st.text_input("Your Email:")
        sender_password = "znve dnzr qlcj dips"  # Store safely in production
        recipient_emails = st.text_input("Recipient Email(s) (comma-separated):")
        cc_emails = st.text_input("CC Email(s) (comma-separated):")
        
        uploaded_file = st.file_uploader("📎 Attach a file (images, PDFs, docs)", type=["png", "jpg", "jpeg", "pdf", "docx","xslt","py","xmd"])
        
        if uploaded_file is not None:
            st.success(f"Uploaded: {uploaded_file.name}")

            # Show preview if it's an image
            if uploaded_file.type.startswith("image"):
                st.image(uploaded_file, caption="Preview", use_container_width=True)


        if st.button("Send Email"):
            result = send_email(sender_email, sender_password, recipient_emails, cc_emails, st.session_state['subject'], st.session_state['body'],uploaded_file)
            st.success(result)
            # After sending email, store it in session state history
            st.session_state["email_history"].append({
                "subject": st.session_state["subject"],
                "body": st.session_state["body"],
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

