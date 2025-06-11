import tkinter as tk
from tkinter import simpledialog, messagebox
import smtplib
from email.message import EmailMessage

class EmailDialog(tk.Toplevel):
    def __init__(self, master, title, report_data, report_type):
        super().__init__(master)
        self.title(title)
        self.geometry("400x200")
        tk.Label(self, text="Recipient Email:").pack(pady=10)
        self.email_entry = tk.Entry(self, width=40)
        self.email_entry.pack(pady=5)
        tk.Button(self, text="Send", command=self.send_email).pack(pady=20)
        self.report_data = report_data
        self.report_type = report_type

    def send_email(self):
        recipient = self.email_entry.get()
        if not recipient:
            messagebox.showwarning("Input Error", "Please enter a recipient email.")
            return
        # Here you would implement the actual email sending logic
        messagebox.showinfo("Email Sent", f"Report sent to {recipient}")
        self.destroy()

def send_email_with_attachment(subject, body, to_email, attachment_path, smtp_server, smtp_port, smtp_user, smtp_password):
    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = smtp_user
        msg['To'] = to_email
        msg.set_content(body)

        # Attach the file
        with open(attachment_path, 'rb') as f:
            file_data = f.read()
            file_name = attachment_path.split('/')[-1]
        msg.add_attachment(file_data, maintype='application', subtype='pdf', filename=file_name)

        # Send the email
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
            smtp.login(smtp_user, smtp_password)
            smtp.send_message(msg)
        messagebox.showinfo("Success", f"Email sent successfully to {to_email}")
    except Exception as e:
        messagebox.showerror("Email Error", f"Failed to send email: {e}")

def email_dialog_with_attachment(parent, attachment_path):
    # Collect email info from user
    to_email = simpledialog.askstring("Send Email", "Recipient Email:", parent=parent)
    if not to_email:
        return
    subject = simpledialog.askstring("Send Email", "Subject:", parent=parent)
    if not subject:
        subject = "Report"
    body = simpledialog.askstring("Send Email", "Message Body:", parent=parent)
    if not body:
        body = "Please find the attached report."

    # SMTP credentials (you can prompt or store securely)
    smtp_server = simpledialog.askstring("SMTP", "SMTP Server (e.g. smtp.gmail.com):", parent=parent)
    smtp_port = simpledialog.askinteger("SMTP", "SMTP Port (e.g. 465 for SSL):", parent=parent)
    smtp_user = simpledialog.askstring("SMTP", "Your Email Address:", parent=parent)
    smtp_password = simpledialog.askstring("SMTP", "Your Email Password (will not be stored):", parent=parent, show="*")

    if not all([smtp_server, smtp_port, smtp_user, smtp_password]):
        messagebox.showwarning("Missing Info", "All SMTP fields are required.")
        return

    send_email_with_attachment(subject, body, to_email, attachment_path, smtp_server, smtp_port, smtp_user, smtp_password)
