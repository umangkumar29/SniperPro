# Price-Drop Sniper Pro 🎯📉

**Price-Drop Sniper Pro** is an advanced e-commerce price tracking and analysis tool designed to help you buy at the absolute lowest price. It monitors products, detects fake sales using historical data algorithms, and notifies you instantly via Telegram when a *true* price drop occurs.

## ✨ Key Features

- **🚀 Real-time Price Tracking**: Automatically scrapes and updates product prices at scheduled intervals.
- **🕵️ Fake Sale Detector**: Analyzes historical price trends to identify if a "sale" is genuine or just a markup-then-drop scam.
- **📊 Interactive Dashboard**:
  - **Buy Gauge**: Visual recommendation engine (Buy/Wait/Don't Buy).
  - **Price History Charts**: Beautiful, interactive graphs powered by Recharts.
  - **Product Insights**: Detailed metrics on lowest price, highest price, and volatility.
- **🔔 Instant Notifications**: Get Telegram alerts properly formatted with product details and direct links.
- **⚡ High Performance**: Built with a modern tech stack ensuring speed and reliability.

---

## 🛠️ Tech Stack

### Backend
- **Framework**: Python (FastAPI/Celery)
- **Database**: PostgreSQL
- **Task Queue**: Celery + Redis
- **Scraping**: Custom Python Scrapers
- **Containerization**: Docker & Docker Compose

### Frontend
- **Framework**: React (Vite)
- **Styling**: Tailwind CSS, Framer Motion (for animations)
- **Visualization**: Recharts
- **Icons**: Lucide React

---

## 🚀 Getting Started

### Prerequisites
- [Docker](https://www.docker.com/) and Docker Compose installed.
- [Node.js](https://nodejs.org/) (for local frontend development).

### 1. Clone the Repository
```bash
git clone https://github.com/umangkumar29/SniperPro.git
cd SniperPro
```

### 2. Setup Environment Variables
Create a `.env` file in the `backend/` directory (or root, depending on your setup) with the following:
```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=pricedrop
```

### 3. Run with Docker (Recommended)
This will start the Database, Redis, Backend API, Worker, and Scheduler.
```bash
docker-compose up --build
```

### 4. Run Frontend Locally
Open a new terminal:
```bash
cd frontend-react
npm install
npm run dev
```
The frontend will run at `http://localhost:5173`.

---

## 🔮 Roadmap
- [ ] Support for more e-commerce sites (Amazon, Flipkart, etc.).
- [ ] User authentication system.
- [ ] Email notifications.
- [ ] AI-powered price prediction.

---

## 🤝 Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

## 📄 License
This project is licensed under the MIT License.
<img width="1344" height="507" alt="image" src="https://github.com/user-attachments/assets/e33d8f50-477e-4e9d-92a9-fb6f23024459" />

<img width="1384" height="548" alt="image" src="https://github.com/user-attachments/assets/5da42b8a-2661-468a-b4c7-62d90ab78e92" />


