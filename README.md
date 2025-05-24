# 🥗 NutriFit: AI-Based Food Nutrition Analyzer

> Your intelligent partner for decoding the nutrition in every bite.

---

## 🚀 What is NutriFit?

**NutriFit** is an AI-powered, Streamlit-based web app that helps you analyze food nutrition using real USDA data. Whether you're meal prepping, tracking macros, or just curious — NutriFit gives you instant insights into the health content of foods like oats, bananas, eggs, and more.

---

## 🎯 Key Features

* **Analyze Foods Instantly**
    Enter any food name (e.g., *banana*, *oats*, *egg*) and get a detailed nutrition breakdown.
* **Macronutrient Visualizations**
    Beautiful bar charts to understand your **calories**, **protein**, **carbs**, **fats**, **fiber**, and more.
* **Nutrition AI Assistant**
    Ask natural language questions (e.g., *Which foods are high in potassium?*) and get smart answers.
* **Quantity & Unit Scaling**
    Choose between **small, medium, large**, **grams**, or **cups** and instantly adjust the nutrient data.

---
## 🧠 How It Works

* **🗃️ USDA Integration**: Uses USDA's FoodData Central API for real nutrition data.
* **🧠 Ollama NLP Engine**: Leverages Ollama AI to parse nutrition info and answer user questions.
* **📦 Streamlit Frontend**: Provides a responsive, interactive UI for easy analysis.
## 💻 How to Run Locally
---

```bash
# 1. Clone the repository
git clone https://github.com/harshadpy/NutriFit-AI-Based-Food-Nutrition-Analyzer.git
cd NutriFit-AI-Based-Food-Nutrition-Analyzer

# 2. (Optional) Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the Streamlit app
streamlit run app.py
```

---

## 📸 Screenshots

| Food Analysis |
| :-----------: |
| ![image](https://github.com/user-attachments/assets/416a9544-caf4-4adf-af49-356800007056)
|![image](https://github.com/user-attachments/assets/b99118aa-0609-403e-bba4-e5b5a953eb02)
| ![image](https://github.com/user-attachments/assets/6c8417bb-cf43-47a0-86e9-bd8611a3e010)
|![image](https://github.com/user-attachments/assets/36ea6019-6b43-4612-8b4b-be7362c53274)
|![image](https://github.com/user-attachments/assets/0a45cf3c-5164-4d21-94f6-1a8265f0b16d)


---


## 🛠 Tech Stack

* **Frontend**: Streamlit
* **Backend**: Python, FastAPI 
* **Data Source**: USDA FoodData Central, Ollama
* **Visualization**: Matplotlib, Pandas
* **Deployment**: Streamlit
---

## 📦 Folder Structure

```
NutriFit/
├── app.py              # Streamlit frontend
├── requirements.txt    # Python dependencies
├── .gitignore
├── README.md
└── backend/ (Optional) # FastAPI or server logic
```

---

## 🤝 Contributing

Contributions are welcome! Feel free to open issues, suggest improvements, or submit pull requests.

* 🍴 Fork the repo
* 📥 Clone your forked repo
* 💡 Create a new branch: `git checkout -b feature-name`
* ✅ Commit your changes: `git commit -m 'Added feature'`
* 🚀 Push and open a PR

---

## 🧠 AI Prompt Examples

```plaintext
🍌 "What is the nutritional value of a banana?"
🥣 "Is oats high in protein?"
💬 "Which fruits are high in potassium?"
```

---

## 📄 License

This project is licensed under the MIT License — feel free to use, fork, and build on it!

---

## 💬 Let's Connect

Made with ❤️ by @harshadpy

“You are what you eat. Track it smart with NutriFit.” 🚀
