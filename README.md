# URL Scraping System

This project is a **URL scraping system** built with **FastAPI, PostgreSQL, Redis, and Celery**. Users can upload a CSV file containing a list of URLs, and the system will scrape each URL, extract meta tags (**title, description, keywords**), and store the results. The system is designed to be **secure, scalable, and automated** using free tools.

## 🌟 Features

✅ **User Authentication**: Users must register and authenticate to access the scraping endpoints.
✅ **CSV Upload**: Users can upload a CSV file containing a list of URLs to be scraped.
✅ **Asynchronous Scraping**: Uses **Celery** to scrape URLs in the background.
✅ **Task Queue**: Uses **Redis** as a task queue.
✅ **Metadata Storage**: Stores extracted metadata in **PostgreSQL**.
✅ **Error Handling**: Handles errors gracefully (invalid URLs, timeouts, and failed requests).
✅ **CI/CD Pipeline**: Automates deployment using **GitHub Actions**.
✅ **Containerization**: Fully containerized with **Docker**.
✅ **Deployment**: Deployed on **Render.com**.
✅ **Monitoring**: Monitored using **Prometheus and Grafana**.

## 🚀 Live Demo

The project is deployed on **Render.com** and accessible at:
👉 **[Live URL](https://assignment-pcho.onrender.com/docs#/)**

## 📌 API Endpoints

### 1️⃣ Register (POST `/register`)

**Description:** Registers a new user.

- **Request Body:** `UserSchema`
- **Response:** Access token and user creation message.

### 2️⃣ Login (POST `/login`)

**Description:** Authenticates a user and returns a JWT token.

- **Request Body:** `UserLoginSchema`
- **Response:** JWT Access token.

### 3️⃣ Upload CSV (POST `/upload-csv`)

**Description:** Uploads a CSV file containing URLs to be scraped.

- **Request Body:** CSV file
- **Response:** Task ID for tracking progress.

### 4️⃣ Check Status (GET `/check-status/{task_id}`)

**Description:** Checks the status of a scraping task.

- **Path Parameter:** `task_id`
- **Response:** Task status (`PENDING`, `IN_PROGRESS`, `COMPLETED`, `FAILED`).

### 5️⃣ Download Scraped Data (GET `/download-scraped-data/{task_id}`)

**Description:** Downloads the scraped metadata for a given task.

- **Path Parameter:** `task_id`
- **Response:** JSON/CSV file containing metadata.

## 🛠️ Technologies Used

- **Backend:** FastAPI
- **Database:** PostgreSQL (Use **Render PostgreSQL** for managed service)
- **Task Queue:** Redis (Use **Upstash Redis** for better scalability)
- **Asynchronous Processing:** Celery
- **Containerization:** Docker
- **Deployment:** Render.com
- **CI/CD:** GitHub Actions
- **Monitoring:** Prometheus and Grafana

## 📖 Setup and Installation

### 🔹 1. Clone the Repository

```bash
git https://github.com/Mr-JackSparrow/Url-Scrapper-System.git
cd Url-Scrapper-System
```

### 🔹 2. Set Up Environment Variables

Create a `.env` file in the root directory and add the following:

```env
DATABASE_URL=postgresql://user:password@localhost/dbname  # Use Render PostgreSQL URL
REDIS_URL=redis://localhost:6379/0  # Use Upstash Redis URL
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 🔹 3. Build and Run Docker Containers

```bash
docker-compose up --build
```

### 🔹 4. Run Database Migrations

```bash
docker-compose exec web alembic upgrade head
```

### 🔹 5. Access the Application

The application will be available at **http://localhost:8000**.

## 📡 Deployment

The project is deployed on **Render.com**, and the Docker image is built and pushed to **Docker Hub** using **GitHub Actions**.

**Steps:**

1. **Build the Docker image**
   ```bash
   docker build -t jacksparrow3133/assignment .
   ```
2. **Push the image to Docker Hub**
   ```bash
   docker push jacksparrow3133/assignment
   ```
3. **Deploy to Render.com** using the provided service settings.

## 📊 Monitoring

Prometheus and Grafana are used for monitoring the application. The dashboards are set up to monitor request/processing time and log API activity for debugging.

### 1️⃣ Start Prometheus

```sh
docker run -d --name=prometheus -p 9090:9090 prom/prometheus
```

### 2️⃣ Start Grafana

```sh
docker run -d --name=grafana -p 3000:3000 grafana/grafana
```

### 3️⃣ Configure Dashboards

- Add **Prometheus** as a data source in Grafana.
- Set up dashboards for API request count and response time tracking.

#### Example Metrics:

- **http_requests_total for handler /**:

  - `instance="assignment-app:8000"`
  - `method="GET"`
  - `status="2xx"`
- **http_requests_total for handler /docs**:

  - `instance="assignment-app:8000"`
  - `method="GET"`
  - `status="2xx"`

### 🔹 Collected Metrics

- **http_requests_total for handler /**:
  - `instance="assignment-app:8000"`
  - `job="assignment-prometheus"`
  - `method="GET"`
  - `status="2xx"`
- **http_requests_total for handler /docs**:
  - `instance="assignment-app:8000"`
  - `job="assignment-prometheus"`
  - `method="GET"`
  - `status="2xx"`

📊 **Grafana Dashboard Screenshot:**

![Grafana Dashboard](monitoring/monitoring.png)

## 📜 License

This project is licensed under the **MIT License**.
