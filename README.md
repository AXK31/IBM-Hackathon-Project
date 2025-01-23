# IBM-Hackathon-Project

Welcome to the IBM Hackathon Project repository! This project was developed as part of a hackathon challenge where the goal was to design and develop a solution using IBM Cloud services. The solution leverages modern technologies to address real-world challenges in the health and wellness domain.

## Project Overview
The project aims to create a **Virtual Health Assistant** that provides personalized dietary and lifestyle recommendations based on user-submitted medical reports or symptoms. This is achieved by integrating IBM Cloud services and advanced technologies to analyze user inputs and generate actionable insights.

### Key Features
- **User Authentication:** Secure login and registration system.
- **Symptom Analysis:** Accepts symptoms provided by users and generates personalized dietary and lifestyle recommendations.
- **Medical Report Analysis:** Uploads and analyzes medical reports in PDF format to provide detailed recommendations.
- **Natural Language Explanations:** Utilizes a Retrieval-Augmented Generation (RAG) model with *Harrison's Principles of Internal Medicine* as the knowledge base for medical explanations.
- **IBM Cloud Integration:** Leverages IBM Cloud services, including IBM Db2, AI models, and storage services.

## Technologies Used
- **Frontend:** HTML, CSS, JavaScript (for forms and UI)
- **Backend:** Flask (Python web framework)
- **Database:** IBM Db2
- **Cloud Services:** IBM Cloud (AI/ML models, cloud storage, etc.)
- **Other Tools:** PDF parsing and natural language processing libraries

## Installation and Setup
Follow these steps to set up the project locally:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/AXK31/IBM-Hackathon-Project.git
   cd IBM-Hackathon-Project
   ```

2. **Set Up a Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up IBM Cloud Services:**
   - Create an IBM Cloud account if you don't have one.
   - Set up IBM Db2 and obtain the credentials.
   - Configure AI services and add necessary credentials to the environment variables or configuration file.

5. **Run the Application:**
   ```bash
   flask run
   ```

6. **Access the Application:**
   Open your browser and go to `http://127.0.0.1:5000`.

## Project Structure
```
IBM-Hackathon-Project/
├── static/                # Static assets (CSS, JS, images)
├── templates/             # HTML templates for Flask
├── app.py                 # Main application file
├── models/                # Backend models and utilities
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
└── ...                    # Additional files and folders
```

## Contribution
Contributions are welcome! If you'd like to contribute:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a clear description of your changes.

## License
This project is licensed under the [MIT License](LICENSE).

## Acknowledgments
- **Hackathon Organizers:** For the opportunity and resources.
- **IBM Cloud:** For providing the tools and services that made this project possible.
- **Team Members:** For their collaboration and efforts.

---

Feel free to explore the repository and provide feedback or suggestions!

