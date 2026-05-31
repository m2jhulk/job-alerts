const form = document.getElementById('alertForm');
const statusMsg = document.getElementById('statusMsg');
const submitBtn = document.getElementById('submitBtn');

// i dont have back end so... 
const GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwgCl4deP-e6_pPFDKM1x5_KOlO4GWUAvSqK0AfDQIcd-opsERhMHN_PKYAS8sDRqvYkw/exec"; 

form.addEventListener('submit', e => {
    e.preventDefault();
    
    

    // लोडिंग स्टेट
    submitBtn.innerText = "Subscribing...";
    submitBtn.disabled = true;
    statusMsg.innerText = "";
    
    const formData = new FormData(form);

    fetch(GOOGLE_SCRIPT_URL, {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(data => {
        if(data.includes("Success")) {
            statusMsg.innerText = "🎉 बधाई हो! आपने सफलतापूर्वक सब्सक्राइब कर लिया है।";
            statusMsg.style.color = "#10b981"; // हरा रंग
            form.reset();
        } else if(data.includes("already subscribed")) {
            statusMsg.innerText = "ℹ️ यह ईमेल पहले से ही सब्सक्राइब है!";
            statusMsg.style.color = "#fbbf24"; // पीला रंग
        } else {
            statusMsg.innerText = "❌ कुछ गलत हुआ। कृपया दोबारा प्रयास करें।";
            statusMsg.style.color = "#ef4444"; // लाल रंग
        }
    })
    .catch(error => {
        statusMsg.innerText = "❌ नेटवर्क एरर! कृपया अपना इंटरनेट चेक करें।";
        statusMsg.style.color = "#ef4444";
    })
    .finally(() => {
        // बटन को वापस नॉर्मल करना
        submitBtn.innerText = "Subscribe Now";
        submitBtn.disabled = false;
    });
});
