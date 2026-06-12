# 🏏 IPL Analytics Dashboard

An interactive data analytics dashboard built with **Streamlit** and **Plotly** for analyzing Indian Premier League (IPL) match data from 2008 to 2022.

## 🔗 Live Demo
[View on Streamlit Cloud →](https://rishi-360-chaudhary-ipl-dashboard-app-fjgs3n.streamlit.app/)

## 📊 Features

- **Team Analysis** — All-time win leaderboard, season-wise win distribution, toss decision trends, toss-win to match-win correlation
- **Batting Intelligence** — Top 15 run scorers, boundary analysis (4s vs 6s), average runs per over by match phase
- **Bowling Intelligence** — Top wicket takers, dismissal type breakdown, best economy rates
- **Venue Analysis** — Most-hosted venues, bat-first vs field-first win rates, city-wise match distribution treemap

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python | Core language |
| Pandas | Data wrangling & analysis |
| Plotly | Interactive visualizations |
| Streamlit | Web app framework |
| Streamlit Cloud | Deployment |

## 🚀 Run Locally

```bash
git clone https://github.com/YOUR_USERNAME/ipl-dashboard
cd ipl-dashboard
pip install -r requirements.txt
streamlit run app.py
```

## 📁 Dataset

Download from Kaggle: [IPL Complete Dataset](https://www.kaggle.com/datasets/ramjidoolla/ipl-data-set)

Place `matches.csv` and `deliveries.csv` inside the `data/` folder.

```
ipl-dashboard/
├── app.py
├── requirements.txt
├── README.md
└── data/
    ├── matches.csv
    └── deliveries.csv
```

## 📈 Key Insights Covered

- Mumbai Indians have the highest win count in IPL history
- Teams winning the toss and choosing to field win ~52% of matches
- Death overs (16–20) consistently produce the highest run rates
- Wankhede Stadium and Eden Gardens are the most frequently used venues