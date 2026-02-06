# 🧪 How to Test the Web Form

Yes! You can use the web form to test sample messages.

### Steps:
1.  **Open Dashboard**: [http://localhost:5173](http://localhost:5173)
2.  **Locate Form**: Find the **"Report a Crisis"** box on the left sidebar.
3.  **Input Message**: Type a sample crisis message.
    *   *Example:* "Medical emergency at Bandra Station, need ambulance immediately."
4.  **Submit**: Click **"Submit Report"**. 
    *   *(Note: If the confirmation modal gets stuck, just refresh the page. The request is submitted!)*
5.  **Verify Queue**: Scroll down to the **Crisis Queue** to see your new item.
6.  **Check Analysis**: Click on the card to see the **Confidence Score** (e.g., 57%).
7.  **Find Matches**: Click **"Find Resources"**.
    *   You should see real Mumbai resources like **Lilavati Hospital** (~1.4 km) or **Sion Hospital** (~2.9 km).

### Expected Results (Demo Data)
- **Input**: "Medical emergency at Bandra Station..."
- **Urgency**: Medium (U3)
- **Matches**: Lilavati Hospital (1.4 km) - *Verified Haversine Accuracy* ✅
