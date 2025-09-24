# 💰 Personal Finance Manager (Python + MySQL)
### Track, Analyze, and Visualize Your Finances

A **command-line Personal Finance Manager** that helps users manage their **income, expenses, categories, and reports** with MySQL as the backend and Python (Pandas, Matplotlib) for data analysis and visualization.

---

## 🚀 Features
- 👤 User management (Add/List users with duplicate email checks)
- 📂 Category management (Add/List categories)
- 💵 Income & Expense tracking with validation
- 📊 Reports & Insights:
  - Monthly summaries
  - Income vs Expenses trend line chart
  - Expense pie chart by category
  - Top 3 expense categories
  - Filter records by day, month, year
  - Compare income & expenses across months

---

## 🛠️ Tech Stack
- **Python 3.12**
- **MySQL** (database storage)
- **Pandas** (data handling)
- **Matplotlib** (visualization)

---

## 📂 Repository Structure
personal-finance-manager/  
│  
├── main.py   
├── README.md   
├── LICENSE   
├── .gitignore  
│  
├── docs/  
│   └── video tutorial  
│  
├── sql/  
│   └── schema.sql  

---

## 📥 Setup Instructions
1. Clone the repo:
   ```bash
   git clone https://github.com/your-username/personal-finance-manager.git
   cd personal-finance-manager
   ```  
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```  
3. Setup MySQL database:
    ```bash
    mysql -u root -p < sql/schema.sql
    mysql -u root -p < sql/sample_data.sql
    ```  
4. Run the program:
    ```bash
    python main.py
    ```

---

## 📝 License
This project is licensed under the MIT License. See the LICENSE file for details.
