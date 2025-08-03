# 🔧 Use Python 3.10 specifically
FROM python:3.10-slim

# 🛠 Set working directory
WORKDIR /app

# 📦 Copy dependencies first (cache optimization)
COPY requirements.txt .

# 📥 Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# 📁 Copy all project files
COPY . .

# 🚀 Run your bot
CMD ["python", "main.py"]
