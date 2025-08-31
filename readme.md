# AI Travel Agent

This project is a simple AI-powered travel agent web app. It uses a conversational agent built with **LangGraph** to assist users in planning their trips. The application is a backend service using **Django** to handle web requests and an agentic framework to manage the conversation flow.


---

### Agent Workflow Graph

<p align="center">
  <img src="graph.png" alt="AI Travel Agent Graph">
</p>


---

### Setup and Running the Application

1.  **Clone the Repository:** First, clone the repository to your local machine.
    
    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```

2.  **Create a Virtual Environment:** It is best practice to create a virtual environment to manage project dependencies.

    ```bash
    python -m venv venv
    ```

3.  **Activate the Virtual Environment:** Activate the environment based on your operating system.

    * On Windows: `venv\Scripts\activate`
    * On macOS/Linux: `source venv/bin/activate`

4.  **Install Dependencies:** Install all the required packages listed in `requirements.txt`.

    ```bash
    pip install -r requirements.txt
    ```

5.  **Create a `.env` file:** In the root directory of your project (where `manage.py` is located) and add the following api keys in the following format.

    ```ini
    GOOGLE_API_KEY=your_google_api_key_here
    SERPER_API_KEY=your_serper_api_key_here
    ```

6.  **Start the Development Server:** 

    ```bash
    python manage.py runserver
    ```

Your travel agent web app should now be running locally at `http://127.0.0.1:8000/`.