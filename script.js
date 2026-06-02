// --- 1. ईमेल सब्सक्रिप्शन लॉजिक ---
const form = document.getElementById('alertForm');
const statusMsg = document.getElementById('statusMsg');
const submitBtn = document.getElementById('submitBtn');

// google sc url
const GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwgCl4deP-e6_pPFDKM1x5_KOlO4GWUAvSqK0AfDQIcd-opsERhMHN_PKYAS8sDRqvYkw/exec"; 

form.addEventListener('submit', e => {
    e.preventDefault();
    

    submitBtn.innerText = "Subscribing...";
    submitBtn.disabled = true;
    statusMsg.innerText = "";
    
    fetch(GOOGLE_SCRIPT_URL, { method: 'POST', body: new FormData(form) })
    .then(response => response.text())
    .then(data => {
        if(data.includes("Success")) {
            statusMsg.innerText = "🎉 सफलतापूर्वक सब्सक्राइब कर लिया गया है।";
            statusMsg.style.color = "#10b981"; form.reset();
        } else if(data.includes("already subscribed")) {
            statusMsg.innerText = "ℹ️ यह ईमेल पहले से ही सब्सक्राइब है!";
            statusMsg.style.color = "#fbbf24";
        } else { throw new Error('Failed'); }
    })
    .catch(() => {
        statusMsg.innerText = "❌ एरर! कृपया दोबारा प्रयास करें।";
        statusMsg.style.color = "#ef4444";
    })
    .finally(() => {
        submitBtn.innerText = "Subscribe Now";
        submitBtn.disabled = false;
    });
});

// --- 2. लाइव जॉब्स दिखाने का लॉजिक ---
function loadLatestJobs() {
    const jobsList = document.getElementById('liveJobsList');
    
    // jobs.json फाइल से डेटा फैच करना
    fetch('jobs.json')
        .then(response => response.json())
        .then(jobs => {
            jobsList.innerHTML = ''; // लोडिंग टेक्स्ट हटाएं
            
            jobs.forEach(job => {
                // हर जॉब के लिए एक <li> और <a> टैग बनाना
                const li = document.createElement('li');
                const a = document.createElement('a');
                a.href = job.link;
                a.target = "_blank"; // नए टैब में खोलने के लिए
                a.innerText = "📌 " + job.title;
                
                li.appendChild(a);
                jobsList.appendChild(li);
            });
        })
        .catch(error => {
            jobsList.innerHTML = '<li style="color: #ef4444;">⚠️ जॉब्स लोड नहीं हो पाईं।</li>';
        });
}

// पेज लोड होते ही जॉब्स वाला फंक्शन चलाएं
loadLatestJobs();
