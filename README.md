# 📚 Paper Hunter (DBLP Paper Finder)

Paper Hunter is a fast, interactive web application built with Streamlit that allows researchers to directly scrape, filter, and discover academic papers from the DBLP computer science bibliography. 

Instead of manually browsing through massive conference proceedings, you can build a search queue of specific venues and years, apply boolean keyword filters (AND/OR), and extract direct links to the papers you need.

## ✨ Features

* **Targeted Scraping:** Fetch papers directly from DBLP conference pages using their consistent schema.
* **Search Queue:** Queue up multiple venues and years (e.g., USENIX Security 2023 + NDSS 2024) to search across them simultaneously.
* **Dynamic Database:** Add or remove custom conference venues and their DBLP acronyms on the fly.
* **Advanced Filtering:** Filter scraped results using comma-separated keywords with `AND`/`OR` logic applied to both titles and author lists.
* **Exportable Results:** Results are displayed in a clean, interactive dataframe with direct paper links.

## 🛠 Tech Stack

* **Frontend & UI:** [Streamlit](https://streamlit.io/)
* **Scraping:** [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/), `requests`
* **Data Handling:** `pandas`, `json`

## 🚀 Getting Started

### Prerequisites
* Python 3.8+

### Installation

1. **Clone the repository:**
```bash
git clone [https://github.com/EdoardoAllegrini/paper_hunter.git](https://github.com/EdoardoAllegrini/paper_hunter.git)
cd paper_hunter
```

2. **Create and activate a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

### Running the App
Execute the following command to start the Streamlit server:

```bash
streamlit run app.py
```
The application will open automatically in your default web browser at http://localhost:8501.

### 📁 Project Structure
- `app.py`: Main Streamlit application, UI layout, state management, and keyword filtering logic.

- `scraper.py`: Core web scraping functions using BeautifulSoup to extract data from DBLP HTML structure.

- `venues.json`: Local JSON database storing your saved conference venues and their respective DBLP acronyms.

### 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the [https://github.com/EdoardoAllegrini/paper_hunter/issues](issues) page.

### 📝 License
This project is licensed under the MIT License - see the `LICENSE` file for details.