import requests
from bs4 import BeautifulSoup
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# json फाइल का नाम (जो गिटहब पर अपडेट होगी)
# यह सुनिश्चित करेगा कि फाइल हमेशा सही फोल्डर में ही पढ़ी और सेव की जाए
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(BASE_DIR, "jobs.json")

# --- 1. f for ex data from site ---
def get_top_5_latest_jobs():
    url = "https://sarkariresult.com.cm/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 'Latest Jobs' हेडिंग खोजना
            heading = soup.find('p', string=lambda text: text and 'Latest Jobs' in text.strip())
            
            if heading:
                latest_jobs_list = heading.find_next('ul')
                if latest_jobs_list:
                    all_job_links = latest_jobs_list.find_all('a')
                    top_5_jobs = [] 
                    
                    for link in all_job_links[:5]: 
                        job_title = link.text.strip()
                        job_url = link.get('href', '')
                        top_5_jobs.append({"title": job_title, "link": job_url})
                        
                    return top_5_jobs
    except Exception as e:
        print(f"❌ स्क्रैपिंग में एरर: {e}")
    
    return []



# --- 2. f for sending emails ---
def send_email_alerts(new_jobs):
    # os.environ 
    SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
    APP_PASSWORD = os.environ.get("APP_PASSWORD")
    
    # google sc
    GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwgCl4deP-e6_pPFDKM1x5_KOlO4GWUAvSqK0AfDQIcd-opsERhMHN_PKYAS8sDRqvYkw/exec"

    print("🔄 गूगल शीट से सब्सक्राइबर्स की लिस्ट मंगा रहे हैं...")
    try:
        response = requests.get(GOOGLE_SCRIPT_URL)
        if response.status_code == 200:
            RECEIVERS = response.json() # गूगल शीट से ईमेल्स की लिस्ट आ गई
            print(f"✅ कुल {len(RECEIVERS)} सब्सक्राइबर्स मिले।")
        else:
            print("❌ गूगल शीट से जुड़ने में एरर।")
            return
    except Exception as e:
        print(f"❌ लिस्ट लाने में एरर: {e}")
        return

    # अगर शीट में कोई ईमेल नहीं है, तो वापस लौट जाएं
    if not RECEIVERS or len(RECEIVERS) == 0:
        print("⚠️ कोई सब्सक्राइबर नहीं मिला, ईमेल नहीं भेजा गया।")
        return

    if len(new_jobs) == 1:
        subject = f"🚨 नया अपडेट: {new_jobs[0]['title']}"
    else:
        subject = f"🚨 {len(new_jobs)} नए अपडेट्स: {new_jobs[0]['title']} और अन्य"

    jobs_html = ""
    for job in new_jobs:
        jobs_html += f"""
        <div style="background-color: #f8fafc; padding: 15px; border-left: 5px solid #10b981; margin: 15px 0; border-radius: 4px;">
            <h3 style="color: #0f172a; margin: 0 0 10px 0; font-size: 16px;">📌 {job['title']}</h3>
            <a href="{job['link']}" style="background-color: #10b981; color: white; padding: 8px 15px; text-decoration: none; border-radius: 4px; font-weight: bold; font-size: 14px; display: inline-block;">
                यहाँ क्लिक करके देखें
            </a>
        </div>
        """

    body = f"""
    <html>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; color: #333; background-color: #f4f4f9; padding: 20px;">
            <div style="background-color: #ffffff; border: 1px solid #ddd; padding: 20px; border-radius: 10px; max-width: 500px; margin: auto; box-shadow: 0 4px 8px rgba(0,0,0,0.05);">
                <h2 style="color: #0284c7; text-align: center; border-bottom: 2px solid #f0f0f0; padding-bottom: 10px;">
                    Sarkari Result Alert 🔔
                </h2>
                <p style="font-size: 16px;">नमस्कार,</p>
                <p style="font-size: 15px; line-height: 1.5;">वेबसाइट पर <b>{len(new_jobs)} नई सरकारी जॉब / रिज़ल्ट</b> के अपडेट आए हैं:</p>
                
                {jobs_html}
                
                <hr style="border: none; border-top: 1px solid #eee; margin-top: 30px;">
                <p style="font-size: 12px; color: #94a3b8; text-align: center; margin-bottom: 0;">
                    यह एक ऑटोमैटिक अलर्ट है।
                </p>
            </div>
        </body>
    </html>
    """

    try:
        print("\n📧 ईमेल सर्वर से कनेक्ट हो रहे हैं...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)

        for receiver in RECEIVERS:
            msg = MIMEMultipart()
            msg['From'] = f"Sarkari Alerts <{SENDER_EMAIL}>"
            msg['To'] = receiver
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))
            
            server.sendmail(SENDER_EMAIL, receiver, msg.as_string())
            print(f"✅ ईमेल सफलतापूर्वक भेजा गया: {receiver}")

        server.quit()
    except Exception as e:
        print(f"❌ ईमेल भेजने में एरर: {e}")
    # 👇 यहाँ अपना सेकेंडरी जीमेल और 16-अक्षरों वाला App Password डालें
    SENDER_EMAIL = ""
    APP_PASSWORD = "" 
    
    # 👇 अभी टेस्टिंग के लिए अपना पर्सनल (प्राइमरी) ईमेल डालें जहाँ आपको अलर्ट चाहिए
    RECEIVERS = [""] 

    
  # अगर 1 जॉब है तो सब्जेक्ट अलग, 1 से ज़्यादा हैं तो अलग
    if len(new_jobs) == 1:
        subject = f"🚨 नई भर्ती: {new_jobs[0]['title']}"
    else:
        subject = f"🚨 {len(new_jobs)} नई भर्तियां: {new_jobs[0]['title']} और अन्य"

    # लूप चलाकर HTML के अंदर सभी नई जॉब्स के बॉक्स तैयार करना
    jobs_html = ""
    for job in new_jobs:
        jobs_html += f"""
        <div style="border: 1px solid #e2e8f0; border-radius: 8px; margin-bottom: 20px; padding: 20px; border-left: 5px solid #0ea5e9; background-color: #f8fafc;">
            <h3 style="margin: 0 0 15px 0; color: #0f172a; font-size: 18px; line-height: 1.4;">{job['title']}</h3>
            <a href="{job['link']}" style="display: inline-block; background-color: #0ea5e9; color: #ffffff; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-weight: bold; font-size: 14px; text-align: center;">
                यहाँ क्लिक करके देखें &rarr;
            </a>
        </div>
        """

    # मुख्य ईमेल की बॉडी (सिर्फ नई भर्ती के लिए)
    body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f1f5f9; color: #334155;">
        <div style="max-width: 600px; margin: 40px auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.05);">
            
            <div style="background: linear-gradient(135deg, #1e293b, #0f172a); padding: 30px 20px; text-align: center;">
                <h1 style="margin: 0; color: #38bdf8; font-size: 28px; letter-spacing: 1px;">🔔 Sarkari Job Alerts</h1>
                <p style="margin: 10px 0 0 0; color: #94a3b8; font-size: 15px;">फ्री सरकारी जॉब अपडेट्स</p>
            </div>
            
            <div style="padding: 40px 30px;">
                <p style="margin: 0 0 15px 0; font-size: 16px;">नमस्कार,</p>
                <p style="margin: 0 0 30px 0; font-size: 15px; line-height: 1.6; color: #475569;">
                    वेबसाइट पर अभी-अभी <b>{len(new_jobs)} नई भर्तियों</b> के ताज़ा अपडेट्स आए हैं। कृपया नीचे दी गई जानकारी चेक करें:
                </p>
                
                {jobs_html}
                
            </div>
            
            <div style="background-color: #f8fafc; border-top: 1px solid #e2e8f0; padding: 25px 20px; text-align: center;">
                <p style="margin: 0 0 10px 0; font-size: 13px; color: #64748b;">
                    यह एक ऑटोमैटिक सिस्टम जनरेटेड अलर्ट है।
                </p>
                
                <p style="margin: 10px 0; font-size: 14px; color: #334155;">
                    Designed & Developed by <strong style="color: #0ea5e9;">m2j247</strong>
                </p>

                <p style="margin: 0; font-size: 12px; color: #94a3b8;">
                    © 2026 Sarkari Job Alerts. All rights reserved.<br>
                    अगर आप भविष्य में ये ईमेल नहीं पाना चाहते हैं, तो कृपया रिप्लाई करें।
                </p>
            </div>
            
        </div>
    </body>
    </html>
    """

    try:
        print("\n📧 ईमेल सर्वर से कनेक्ट हो रहे हैं...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)

        for receiver in RECEIVERS:
            msg = MIMEMultipart()
            msg['From'] = f"Sarkari Alerts <{SENDER_EMAIL}>"
            msg['To'] = receiver
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))
            
            server.sendmail(SENDER_EMAIL, receiver, msg.as_string())
            print(f"✅ ईमेल सफलतापूर्वक भेजा गया: {receiver}")

        server.quit()
    except Exception as e:
        print(f"❌ ईमेल भेजने में एरर: {e}")


# --- 3. नया अपडेट चेक करने और डेटाबेस (JSON) अपडेट करने का फंक्शन ---
def check_and_update_jobs():
    print("🔎 वेबसाइट चेक कर रहे हैं...")
    live_jobs = get_top_5_latest_jobs()
    
    if not live_jobs:
        print("⚠️ कोई जॉब नहीं मिली।")
        return

    # पुरानी jobs.json फाइल को पढ़ना
    old_jobs = []
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            try:
                old_jobs = json.load(f)
            except json.JSONDecodeError:
                old_jobs = []

    # पुरानी जॉब्स के 'नाम' की एक लिस्ट बनाना
    old_titles = [job['title'] for job in old_jobs]

    # खोजना कि live_jobs में से कौन सी जॉब old_titles में नहीं है
    new_updates = []
    for job in live_jobs:
        if job['title'] not in old_titles:
            new_updates.append(job)

    # अगर कोई नई जॉब मिली है तो JSON अपडेट करें और ईमेल भेजें
    if len(new_updates) > 0:
        print(f"\n🎉 {len(new_updates)} नए अपडेट मिले हैं!")
        
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(live_jobs, f, indent=4, ensure_ascii=False)
        print("✅ jobs.json फाइल अपडेट कर दी गई है।")
        
        # ईमेल फंक्शन कॉल करना
        send_email_alerts(new_updates)
        
    else:
        print("\n💤 कोई नया अपडेट नहीं है। पुरानी जॉब ही चल रही है।")


# --- स्क्रिप्ट रन करना ---
if __name__ == "__main__":
    check_and_update_jobs()
