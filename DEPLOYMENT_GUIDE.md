# Deployment Guide for Render.com

This guide provides step-by-step instructions on how to deploy your FastAPI application to Render.com to get a public URL for your project submission.

---

### **Step 1: Sign Up for a Free Render Account**

1.  Go to the website: **render.com**
2.  Sign up for a new account. The easiest way is to **sign up using your GitHub account**, as this will automatically link them and make the next steps much simpler.

---

### **Step 2: Create a New "Web Service"**

1.  Once you are logged into your Render dashboard, click the **"New +"** button (usually at the top right).
2.  From the menu that appears, select **"Web Service"**.

---

### **Step 3: Connect Your GitHub Repository**

1.  Render will ask you to connect your GitHub account if you haven't already.
2.  It will then show a list of your repositories. Select your project repository (e.g., `tds-project-1`).

---

### **Step 4: Configure Your Web Service**

This is the most important part. You need to tell Render how to build and run your application. Fill in the form with these exact settings:

*   **Name:** Give your service a unique name. For example: `iitm-tds-project-nishchay`.
*   **Region:** Choose a location (Singapore is a good choice if you're in India).
*   **Branch:** Make sure this is set to `main`.
*   **Runtime:** Render should automatically detect `Python 3`.
*   **Build Command:** Set this to the following command:
    ```
    pip install -r requirements.txt
    ```
*   **Start Command:** This is critical. Set it to:
    ```
    uvicorn main:app --host 0.0.0.0 --port $PORT
    ```
    *(The `--host 0.0.0.0` part is essential for the server to be accessible online. Render provides the `$PORT` value for you.)*

---

### **Step 5: Add Your Secret Keys (Environment Variables)**

1.  Scroll down the page until you find the "Environment" or "Advanced" section.
2.  Click on **"Add Environment Variable"**. You must add your three secrets here, one by one:
    *   **Key:** `SECRET`
        **Value:** `your-secret-key` (or whatever secret you are using)
    *   **Key:** `GITHUB_TOKEN`
        **Value:** (your real GitHub token)
    *   **Key:** `AIPIPE_API_KEY`
        **Value:** (your real AIPipe key)

---

### **Step 6: Deploy the Application**

1.  Scroll to the very bottom of the page.
2.  Click the **"Create Web Service"** button.
3.  Render will now start building and deploying your application. You can watch the progress in the logs on the screen. This may take a few minutes.

---

### **Step 7: Get Your Public URL**

Once the deployment is complete, you will see a "Live" status. At the top of your service's dashboard page, Render will display your public URL. It will look something like this:

`https://iitm-tds-project-nishchay.onrender.com`

This is the public address of your running application.

---

### **Final Step: Filling Out the Submission Form**

The form asks for your **Endpoint URL**. This is your public Render URL with `/handle_task` added to the end.

**Example:**
`https://iitm-tds-project-nishchay.onrender.com/handle_task`

This is the URL you need to submit in the Google Form. Good luck!