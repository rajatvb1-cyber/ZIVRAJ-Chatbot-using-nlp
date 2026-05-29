from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
import sqlite3
import json
import os
import re
from io import BytesIO
from database import init_db

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "your_secret_key_here")

# Initialize database
init_db()

# ---------------------------
# Data Loading
# ---------------------------
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

DOMAIN_FILES = {
    "python": "python_questions.json",
    "ml": "ml_questions.json",
    "sql": "sql_questions.json",
    "cloud": "cloud_questions.json",
    "interview": "interview_questions.json"
}

DOMAIN_DATA = {}

def load_all_domains():
    """Load all domain JSON datasets into memory."""
    global DOMAIN_DATA
    for key, filename in DOMAIN_FILES.items():
        filepath = os.path.join(DATA_DIR, filename)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                DOMAIN_DATA[key] = json.load(f)

load_all_domains()

# ---------------------------
# Helper Functions
# ---------------------------
def get_db_connection():
    conn = sqlite3.connect("chatbot.db")
    conn.row_factory = sqlite3.Row
    return conn


def get_domain_response(domain_key, user_message):
    """Generate a domain-specific chatbot response."""
    msg = user_message.lower().strip()
    domain = DOMAIN_DATA.get(domain_key)

    if not domain:
        return "Domain not found. Please select a valid domain from the sidebar."

    domain_name = domain["domain"]

    # Greetings (use word boundary to avoid matching 'hi' inside 'machine' etc.)
    if any(re.search(r'\b' + w + r'\b', msg) for w in ["hello", "hi", "hey", "greetings"]):
        return f"Hello! 👋 Welcome to the {domain_name} module. I'm your AI tutor here to help you learn. Ask me anything about {domain_name}, or start a learning module!"

    # Help
    if "help" in msg:
        return f"I can help you with:\n• {domain_name} concepts and theory\n• Practice MCQs\n• Interview preparation\n• Coding exercises\n\nTry asking me a specific question or start a module from the right panel!"

    # Module info
    if "module" in msg:
        modules_info = ""
        for mod in domain["modules"]:
            modules_info += f"\n📘 {mod['name']} — {mod['description']}"
        return f"Available {domain_name} modules:{modules_info}\n\nClick on a module in the right panel to get started!"

    # Domain-specific keyword responses
    responses = _get_keyword_responses(domain_key, msg)
    if responses:
        return responses

    # Check for "what is [domain]" intro questions
    domain_intro = _get_domain_intro_response(msg)
    if domain_intro:
        return domain_intro

    # Default
    return f"Great question about {domain_name}! 🤔 I'm focused on {domain_name} topics. Try asking about specific concepts, or start a learning module for structured practice!"


def get_general_response(user_message):
    """Generate a response by searching across ALL domains."""
    msg = user_message.lower().strip()

    # --- Domain-level questions (check FIRST, before greetings) ---
    domain_intro = _get_domain_intro_response(msg)
    if domain_intro:
        return domain_intro

    # Greetings (use word boundary to avoid matching 'hi' inside 'machine' etc.)
    if any(re.search(r'\b' + w + r'\b', msg) for w in ["hello", "hi", "hey", "greetings"]):
        return "Hello! 👋 I'm ZIVRAJ, your AI learning assistant. I can help you with:\n\n🐍 Python Programming\n🤖 Machine Learning\n🗃️ SQL & Databases\n☁️ Cloud Computing\n🎯 Interview Preparation\n\nAsk me anything, or select a domain from the sidebar for structured learning!"

    # Help
    if "help" in msg:
        return "Here's how I can help:\n\n• Ask me any question — I'll search across all domains\n• Select a domain from the sidebar for structured modules\n• Practice MCQs, coding, and interview questions\n\nDomains available: Python, ML, SQL, Cloud Computing, Interview Guidance"

    # Search across all domains for keyword matches
    for domain_key in DOMAIN_DATA:
        response = _get_keyword_responses(domain_key, msg)
        if response:
            domain_name = DOMAIN_DATA[domain_key]["domain"]
            return f"📚 {domain_name}\n\n{response}\n\n💡 Select '{domain_name}' from the sidebar for structured learning modules!"

    # Default
    return "I'm not sure about that one! 🤔 Try asking about:\n\n• Python (variables, loops, functions, OOP)\n• ML (supervised learning, neural networks)\n• SQL (joins, queries, normalization)\n• Cloud (AWS, Docker, Kubernetes)\n• Interview tips (STAR method, strengths)\n\nOr select a domain from the sidebar for guided learning!"


def _get_domain_intro_response(msg):
    """Handle high-level 'what is X' questions about entire domains."""

    # --- Python ---
    if any(kw in msg for kw in ["what is python", "about python", "tell me about python", "explain python", "define python"]):
        return "📚 Python Programming\n\n🐍 Python is a high-level, interpreted, general-purpose programming language created by Guido van Rossum in 1991.\n\nKey features:\n• Easy to learn with clean, readable syntax\n• Dynamically typed — no need to declare variable types\n• Supports multiple paradigms: OOP, functional, procedural\n• Huge ecosystem of libraries (NumPy, Pandas, Flask, Django)\n• Used in: web development, data science, AI/ML, automation, scripting\n\nExample:\nprint('Hello, World!')\n\n💡 Select 'Python' from the sidebar for structured learning modules!"

    # --- Machine Learning ---
    if any(kw in msg for kw in ["what is ml", "what is machine learning", "about ml", "about machine learning",
                                 "tell me about ml", "tell me about machine learning", "explain ml",
                                 "explain machine learning", "define ml", "define machine learning",
                                 "what's ml", "what's machine learning",
                                 "machine learning", "ml"]) or msg.strip() == "ml":
        return "📚 Machine Learning\n\n🤖 Machine Learning (ML) is a branch of Artificial Intelligence that enables computers to learn from data and improve their performance without being explicitly programmed.\n\nTypes of ML:\n• Supervised Learning — learns from labeled data (e.g., spam detection, price prediction)\n• Unsupervised Learning — finds hidden patterns in unlabeled data (e.g., customer segmentation)\n• Reinforcement Learning — learns through rewards and penalties (e.g., game-playing AI)\n\nPopular algorithms: Linear Regression, Decision Trees, Random Forest, Neural Networks, SVM, K-Means\n\nCommon libraries: Scikit-learn, TensorFlow, PyTorch, Keras\n\n💡 Select 'Machine Learning' from the sidebar for structured learning modules!"

    # --- AI ---
    if any(kw in msg for kw in ["what is ai", "what is artificial intelligence", "about ai",
                                 "tell me about ai", "explain ai", "define ai"]):
        return "📚 Machine Learning\n\n🧠 Artificial Intelligence (AI) is the simulation of human intelligence by machines. It enables computers to perform tasks that typically require human intelligence such as:\n\n• Learning from experience\n• Understanding natural language\n• Recognizing patterns and images\n• Making decisions\n\nSubfields of AI:\n• Machine Learning — learning from data\n• Deep Learning — neural networks with multiple layers\n• NLP — understanding human language\n• Computer Vision — understanding images/videos\n• Robotics — physical AI agents\n\n💡 Select 'Machine Learning' from the sidebar to dive deeper into AI/ML!"

    # --- SQL ---
    if any(kw in msg for kw in ["what is sql", "about sql", "tell me about sql", "explain sql", "define sql",
                                 "what's sql", "what is structured query language"]) or msg.strip() == "sql":
        return "📚 SQL\n\n🗃️ SQL (Structured Query Language) is a standard programming language used to manage and manipulate relational databases.\n\nWhat you can do with SQL:\n• CREATE tables and databases\n• INSERT, UPDATE, DELETE data\n• SELECT and query data with powerful filters\n• JOIN multiple tables together\n• Use aggregate functions (COUNT, SUM, AVG)\n\nSQL command types:\n• DDL — CREATE, ALTER, DROP (structure)\n• DML — SELECT, INSERT, UPDATE, DELETE (data)\n• DCL — GRANT, REVOKE (permissions)\n• TCL — COMMIT, ROLLBACK (transactions)\n\nPopular databases: MySQL, PostgreSQL, SQLite, SQL Server, Oracle\n\n💡 Select 'SQL' from the sidebar for structured learning modules!"

    # --- Database ---
    if any(kw in msg for kw in ["what is database", "what is a database", "about database",
                                 "tell me about database", "explain database", "define database",
                                 "what is dbms", "what is rdbms"]):
        return "📚 SQL\n\n🗄️ A Database is an organized collection of structured data stored electronically. A DBMS (Database Management System) is the software used to manage it.\n\nTypes:\n• Relational (RDBMS) — MySQL, PostgreSQL, Oracle (uses tables & SQL)\n• NoSQL — MongoDB, Redis (flexible schema)\n• In-memory — Redis, Memcached (fast, cached data)\n\nKey concepts:\n• Tables, rows, columns\n• Primary keys & foreign keys\n• Normalization (reducing redundancy)\n• ACID properties (reliable transactions)\n\n💡 Select 'SQL' from the sidebar for structured learning modules!"

    # --- Cloud Computing ---
    if any(kw in msg for kw in ["what is cloud computing", "about cloud computing", "tell me about cloud computing",
                                 "explain cloud computing", "define cloud computing", "what's cloud computing",
                                 "what is cloud", "about cloud", "tell me about cloud", "explain cloud",
                                 "what is cc", "about cc", "what's cloud",
                                 "cloud computing"]) or msg.strip() in ["cc", "cloud computing"]:
        return "📚 Cloud Computing\n\n☁️ Cloud Computing is the delivery of computing services — including servers, storage, databases, networking, software, and analytics — over the internet (\"the cloud\").\n\nService models:\n• IaaS (Infrastructure as a Service) — Virtual machines, storage (AWS EC2)\n• PaaS (Platform as a Service) — Development platforms (Heroku, Google App Engine)\n• SaaS (Software as a Service) — Ready-to-use apps (Gmail, Google Docs)\n\nDeployment models:\n• Public Cloud — Available to everyone (AWS, Azure, GCP)\n• Private Cloud — Dedicated to one organization\n• Hybrid Cloud — Combination of both\n\nBenefits: Cost savings, scalability, reliability, global reach, pay-as-you-go\n\n💡 Select 'Cloud Computing' from the sidebar for structured learning modules!"

    # --- Interview ---
    if any(kw in msg for kw in ["what is interview preparation", "about interview", "tell me about interview",
                                 "interview tips", "how to prepare for interview", "interview preparation",
                                 "interview guidance", "what is interview"]):
        return "📚 Interview Preparation\n\n🎯 Interview Preparation involves getting ready to present your skills, experience, and personality effectively to potential employers.\n\nKey areas:\n• Self-introduction — concise, confident, structured\n• Technical questions — domain-specific knowledge\n• Behavioral questions — STAR method (Situation, Task, Action, Result)\n• HR questions — strengths, weaknesses, goals\n• Communication skills — clarity, confidence, body language\n\nTips:\n• Research the company beforehand\n• Practice common questions out loud\n• Prepare specific examples from your projects\n• Ask thoughtful questions to the interviewer\n\n💡 Select 'Interview Preparation' from the sidebar for structured learning modules!"

    return None


def _get_keyword_responses(domain_key, msg):
    """Return keyword-based responses specific to each domain."""
    if domain_key == "python":
        if "variable" in msg:
            return "Variables store data values in Python.\nExample:\nname = 'Raj'\nage = 20\n\nPython is dynamically typed — no need to declare types!"
        elif "data type" in msg or "datatype" in msg:
            return "Python data types:\n• int — Integers (10, -5)\n• float — Decimals (3.14)\n• str — Strings ('hello')\n• bool — True/False\n• list — Ordered mutable collection\n• tuple — Ordered immutable collection\n• dict — Key-value pairs"
        elif "loop" in msg or "for loop" in msg or "while loop" in msg:
            return "Python loops:\n\nfor loop:\nfor i in range(5):\n    print(i)\n\nwhile loop:\nwhile x > 0:\n    x -= 1\n\nUse 'break' to exit, 'continue' to skip iteration."
        elif "function" in msg or "def " in msg:
            return "Functions are reusable code blocks:\n\ndef greet(name):\n    return f'Hello, {name}!'\n\nresult = greet('Raj')  # 'Hello, Raj!'"
        elif "class" in msg or "oop" in msg or "object oriented" in msg or "inheritance" in msg:
            return "Python OOP:\n\nclass Student:\n    def __init__(self, name):\n        self.name = name\n\n    def greet(self):\n        return f'Hi, I am {self.name}'\n\ns = Student('Raj')\nprint(s.greet())\n\nOOP Pillars: Encapsulation, Inheritance, Polymorphism, Abstraction"
        elif "list" in msg and "comprehension" in msg:
            return "List comprehension creates lists concisely:\n\nsquares = [x**2 for x in range(10)]\neven = [x for x in range(20) if x % 2 == 0]\n\nEquivalent to a for loop but more Pythonic!"
        elif "list" in msg:
            return "Lists are ordered, mutable collections:\n\nfruits = ['apple', 'banana', 'cherry']\nfruits.append('mango')\nfruits[0]  # 'apple'\nlen(fruits)  # 4"
        elif "dictionary" in msg or "dict" in msg:
            return "Dictionaries store key-value pairs:\n\nstudent = {'name': 'Raj', 'age': 20}\nstudent['name']  # 'Raj'\nstudent['grade'] = 'A'  # Add new key"
        elif "tuple" in msg:
            return "Tuples are ordered, immutable collections:\n\ncoords = (10, 20)\ncolors = ('red', 'green', 'blue')\n\nTuples cannot be modified after creation.\nUse them for fixed data like coordinates or RGB values."
        elif "string" in msg or "str " in msg:
            return "Strings are sequences of characters:\n\nname = 'Raj'\nname.upper()    # 'RAJ'\nname.lower()    # 'raj'\nname.replace('R', 'M')  # 'Maj'\nlen(name)       # 3\n\nStrings are immutable — operations return new strings."
        elif "exception" in msg or "try" in msg or "error handling" in msg:
            return "Python exception handling:\n\ntry:\n    result = 10 / 0\nexcept ZeroDivisionError:\n    print('Cannot divide by zero!')\nfinally:\n    print('This always runs')\n\nCommon exceptions: ValueError, TypeError, KeyError, IndexError"
        elif "file" in msg and ("read" in msg or "write" in msg or "open" in msg or "handling" in msg):
            return "File handling in Python:\n\n# Reading\nwith open('file.txt', 'r') as f:\n    content = f.read()\n\n# Writing\nwith open('file.txt', 'w') as f:\n    f.write('Hello!')\n\nModes: 'r' (read), 'w' (write), 'a' (append), 'rb' (binary read)"
        elif "module" in msg or "import" in msg or "library" in msg:
            return "Python modules are reusable code files:\n\nimport math\nmath.sqrt(16)  # 4.0\n\nfrom random import randint\nrandint(1, 10)\n\nPopular libraries: NumPy, Pandas, Flask, Django, Requests, Matplotlib"
        elif "pip" in msg or "install" in msg:
            return "pip is Python's package manager:\n\npip install flask\npip install numpy pandas\npip list  # Show installed packages\npip freeze > requirements.txt  # Save dependencies\npip install -r requirements.txt  # Install from file"
        elif "lambda" in msg:
            return "Lambda functions are small anonymous functions:\n\nsquare = lambda x: x ** 2\nsquare(5)  # 25\n\nadd = lambda a, b: a + b\nadd(3, 4)  # 7\n\nOften used with map(), filter(), sorted()."
        elif "decorator" in msg:
            return "Decorators modify function behavior:\n\ndef my_decorator(func):\n    def wrapper():\n        print('Before function')\n        func()\n        print('After function')\n    return wrapper\n\n@my_decorator\ndef say_hello():\n    print('Hello!')\n\nsay_hello()"
        elif "generator" in msg or "yield" in msg:
            return "Generators produce values lazily using yield:\n\ndef countdown(n):\n    while n > 0:\n        yield n\n        n -= 1\n\nfor num in countdown(5):\n    print(num)  # 5, 4, 3, 2, 1\n\nGenerators are memory-efficient for large datasets."
        elif "set" in msg:
            return "Sets are unordered collections of unique elements:\n\ncolors = {'red', 'green', 'blue'}\ncolors.add('yellow')\ncolors.discard('red')\n\nSet operations: union (|), intersection (&), difference (-)"

    elif domain_key == "ml":
        if "supervised" in msg:
            return "Supervised Learning uses labeled data to train models.\nThe model learns input→output mapping.\n\nExamples:\n• Classification (spam detection)\n• Regression (price prediction)\n\nAlgorithms: Linear Regression, Random Forest, SVM"
        elif "unsupervised" in msg:
            return "Unsupervised Learning finds hidden patterns in unlabeled data.\n\nExamples:\n• Clustering (customer segmentation)\n• Dimensionality reduction (PCA)\n\nAlgorithms: K-Means, DBSCAN, Hierarchical Clustering"
        elif "neural network" in msg or "deep learning" in msg:
            return "Neural Networks are inspired by the human brain.\n\nLayers: Input → Hidden → Output\nActivation functions: ReLU, Sigmoid, Softmax\n\nDeep Learning = Neural networks with multiple hidden layers.\nUsed in: image recognition, NLP, autonomous vehicles."
        elif "overfitting" in msg:
            return "Overfitting: Model learns noise in training data.\n\nSigns: High training accuracy, low test accuracy.\n\nSolutions:\n• More training data\n• Regularization (L1/L2)\n• Cross-validation\n• Dropout\n• Early stopping"
        elif "underfitting" in msg:
            return "Underfitting: Model is too simple to capture data patterns.\n\nSigns: Low training accuracy AND low test accuracy.\n\nSolutions:\n• Use a more complex model\n• Add more features\n• Reduce regularization\n• Train longer"
        elif "regression" in msg:
            return "Regression predicts continuous numerical values.\n\nTypes:\n• Linear Regression — straight-line relationship\n• Polynomial Regression — curved relationships\n• Ridge/Lasso — regularized regression\n\nExamples: predicting house prices, temperature, stock prices.\n\nMetrics: MSE, RMSE, MAE, R-squared"
        elif "classification" in msg:
            return "Classification predicts discrete categories/labels.\n\nTypes:\n• Binary — two classes (spam/not spam)\n• Multi-class — multiple classes (digit recognition)\n\nAlgorithms: Logistic Regression, Decision Trees, SVM, KNN, Random Forest\n\nMetrics: Accuracy, Precision, Recall, F1-Score"
        elif "decision tree" in msg:
            return "Decision Trees split data into branches based on feature values.\n\n• Easy to interpret and visualize\n• Can handle both classification and regression\n• Prone to overfitting (use pruning or Random Forest)\n\nKey terms: Root node, leaf node, splitting, information gain, Gini impurity"
        elif "random forest" in msg:
            return "Random Forest is an ensemble of many decision trees.\n\n• Reduces overfitting compared to single trees\n• Uses bagging (bootstrap aggregating)\n• Each tree votes; majority wins\n• Works for both classification and regression\n\nAdvantages: Robust, handles missing data, provides feature importance"
        elif "k-means" in msg or "kmeans" in msg or "clustering" in msg:
            return "K-Means Clustering groups data into K clusters.\n\nSteps:\n1. Choose K (number of clusters)\n2. Initialize K centroids randomly\n3. Assign each point to nearest centroid\n4. Update centroids to cluster means\n5. Repeat until convergence\n\nUse the Elbow Method to find optimal K."
        elif "training" in msg or "testing" in msg or "train" in msg or "test" in msg:
            return "Train-Test Split divides data for model evaluation:\n\n• Training set (70-80%) — model learns patterns\n• Testing set (20-30%) — evaluates model performance\n\nfrom sklearn.model_selection import train_test_split\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)\n\nNever evaluate on training data — it leads to overly optimistic results!"
        elif "model" in msg:
            return "An ML Model is a mathematical representation that learns patterns from data.\n\nWorkflow:\n1. Collect & prepare data\n2. Choose an algorithm\n3. Train the model on training data\n4. Evaluate on test data\n5. Tune hyperparameters\n6. Deploy for predictions\n\nPopular models: Linear Regression, SVM, Random Forest, Neural Networks"
        elif "nlp" in msg or "natural language" in msg or "text" in msg:
            return "NLP (Natural Language Processing) enables machines to understand human language.\n\nTasks:\n• Text classification (sentiment analysis)\n• Named Entity Recognition (NER)\n• Machine Translation\n• Text summarization\n• Chatbots\n\nLibraries: NLTK, spaCy, Hugging Face Transformers"
        elif "cnn" in msg or "convolutional" in msg:
            return "CNN (Convolutional Neural Network) is designed for image processing.\n\nLayers:\n• Convolutional — detects features (edges, textures)\n• Pooling — reduces dimensions\n• Fully Connected — makes predictions\n\nUsed in: image classification, object detection, facial recognition."
        elif "rnn" in msg or "recurrent" in msg or "lstm" in msg:
            return "RNN (Recurrent Neural Network) processes sequential data.\n\n• Maintains hidden state (memory)\n• LSTM (Long Short-Term Memory) solves vanishing gradient problem\n\nUsed in: text generation, speech recognition, time series prediction, machine translation."
        elif "feature" in msg:
            return "Feature Engineering improves ML model performance:\n\n• Feature creation — derive new features from existing data\n• Feature selection — pick the most relevant features\n• Encoding — convert categorical to numerical (one-hot, label encoding)\n• Scaling — normalize/standardize numerical features\n\nGood features = better model performance!"
        elif "accuracy" in msg or "precision" in msg or "recall" in msg or "f1" in msg:
            return "ML Evaluation Metrics:\n\n• Accuracy — % of correct predictions\n• Precision — % of positive predictions that are correct\n• Recall — % of actual positives found\n• F1-Score — harmonic mean of precision & recall\n\nUse F1-Score for imbalanced datasets.\nUse confusion matrix to visualize all four metrics."

    elif domain_key == "sql":
        if "join" in msg:
            return "SQL JOINs combine rows from two or more tables:\n\n• INNER JOIN — Only matching rows\n• LEFT JOIN — All left + matching right\n• RIGHT JOIN — All right + matching left\n• FULL JOIN — All rows from both tables"
        elif "select" in msg:
            return "SELECT retrieves data from tables:\n\nSELECT * FROM students;\nSELECT name, age FROM students WHERE grade = 'A';\nSELECT COUNT(*) FROM students GROUP BY grade;"
        elif "primary key" in msg:
            return "A Primary Key uniquely identifies each row:\n\nCREATE TABLE students (\n    id INT PRIMARY KEY,\n    name VARCHAR(100)\n);\n\nRules: Must be unique, cannot be NULL."
        elif "foreign key" in msg:
            return "A Foreign Key links two tables together:\n\nCREATE TABLE orders (\n    id INT PRIMARY KEY,\n    student_id INT,\n    FOREIGN KEY (student_id) REFERENCES students(id)\n);\n\nIt enforces referential integrity between tables."
        elif "index" in msg:
            return "Indexes speed up data retrieval:\n\nCREATE INDEX idx_name ON students(name);\n\nTypes: Clustered (one per table), Non-clustered (multiple allowed).\nTrade-off: Faster reads, slower writes."
        elif "normalization" in msg or "normal form" in msg:
            return "Normalization organizes data to reduce redundancy:\n\n• 1NF — Atomic values, no repeating groups\n• 2NF — No partial dependencies (all non-key columns depend on full primary key)\n• 3NF — No transitive dependencies\n• BCNF — Every determinant is a candidate key\n\nBenefits: Less redundancy, better data integrity."
        elif "query" in msg or "queries" in msg:
            return "SQL Queries are commands to interact with databases:\n\n• SELECT — retrieve data\n• INSERT INTO — add new rows\n• UPDATE — modify existing data\n• DELETE — remove rows\n\nExample:\nSELECT name, age FROM students WHERE age > 18 ORDER BY name;"
        elif "table" in msg:
            return "Tables are the basic unit of data storage in SQL:\n\nCREATE TABLE students (\n    id INT PRIMARY KEY,\n    name VARCHAR(100),\n    age INT,\n    grade CHAR(2)\n);\n\nTables have columns (fields) and rows (records)."
        elif "where" in msg or "filter" in msg:
            return "WHERE clause filters rows based on conditions:\n\nSELECT * FROM students WHERE age > 18;\nSELECT * FROM students WHERE grade = 'A' AND age < 25;\nSELECT * FROM students WHERE name LIKE 'R%';\n\nOperators: =, >, <, >=, <=, <>, LIKE, IN, BETWEEN"
        elif "group by" in msg or "aggregate" in msg or "having" in msg:
            return "GROUP BY groups rows with same values:\n\nSELECT grade, COUNT(*) FROM students GROUP BY grade;\nSELECT grade, AVG(age) FROM students GROUP BY grade HAVING AVG(age) > 20;\n\nAggregate functions: COUNT, SUM, AVG, MIN, MAX\nHAVING filters groups (used after GROUP BY)."
        elif "insert" in msg:
            return "INSERT adds new rows to a table:\n\nINSERT INTO students (name, age, grade)\nVALUES ('Raj', 20, 'A');\n\nINSERT INTO students VALUES (1, 'Raj', 20, 'A');\n\nYou can insert multiple rows at once too."
        elif "update" in msg:
            return "UPDATE modifies existing data:\n\nUPDATE students SET grade = 'A' WHERE name = 'Raj';\nUPDATE students SET age = age + 1;\n\n⚠️ Always use WHERE — without it, ALL rows get updated!"
        elif "delete" in msg or "truncate" in msg or "drop" in msg:
            return "Removing data in SQL:\n\n• DELETE — removes specific rows (can rollback)\nDELETE FROM students WHERE grade = 'F';\n\n• TRUNCATE — removes all rows, keeps table structure\nTRUNCATE TABLE students;\n\n• DROP — removes the entire table\nDROP TABLE students;"
        elif "subquery" in msg or "nested" in msg:
            return "A Subquery is a query inside another query:\n\nSELECT name FROM students\nWHERE age = (SELECT MAX(age) FROM students);\n\nTypes:\n• Scalar — returns single value\n• Row — returns single row\n• Table — returns multiple rows\n• Correlated — references outer query"
        elif "view" in msg:
            return "A View is a virtual table based on a query:\n\nCREATE VIEW top_students AS\nSELECT name, grade FROM students WHERE grade = 'A';\n\nSELECT * FROM top_students;\n\nViews simplify complex queries and add security."
        elif "stored procedure" in msg or "procedure" in msg:
            return "Stored Procedures are saved SQL programs:\n\nCREATE PROCEDURE GetStudents()\nBEGIN\n    SELECT * FROM students;\nEND;\n\nCALL GetStudents();\n\nBenefits: Reusable, faster execution, better security."
        elif "transaction" in msg or "commit" in msg or "rollback" in msg:
            return "Transactions group SQL operations:\n\nBEGIN TRANSACTION;\nUPDATE accounts SET balance = balance - 100 WHERE id = 1;\nUPDATE accounts SET balance = balance + 100 WHERE id = 2;\nCOMMIT;\n\nACID properties: Atomicity, Consistency, Isolation, Durability\nUse ROLLBACK to undo changes."

    elif domain_key == "cloud":
        if "aws" in msg:
            return "AWS (Amazon Web Services) is the leading cloud provider.\n\nKey services:\n• EC2 — Virtual servers\n• S3 — Object storage\n• Lambda — Serverless compute\n• RDS — Managed databases\n• CloudFront — CDN"
        elif "docker" in msg or "container" in msg:
            return "Docker containerizes applications:\n\n• Lightweight alternative to VMs\n• Packages app + dependencies\n• Consistent across environments\n\nCommands:\ndocker build -t myapp .\ndocker run -p 5000:5000 myapp"
        elif "serverless" in msg or "lambda" in msg:
            return "Serverless computing:\n\n• No server management\n• Auto-scaling\n• Pay per execution\n• Event-driven\n\nExamples: AWS Lambda, Azure Functions, Google Cloud Functions"
        elif "kubernetes" in msg or "k8s" in msg:
            return "Kubernetes (K8s) is a container orchestration platform:\n\n• Automates deployment, scaling, and management of containers\n• Self-healing — restarts failed containers\n• Load balancing & service discovery\n• Rolling updates & rollbacks\n\nKey concepts: Pods, Nodes, Clusters, Services, Deployments"
        elif "azure" in msg:
            return "Microsoft Azure is a major cloud platform:\n\nKey services:\n• Azure VMs — Virtual machines\n• Azure Blob Storage — Object storage\n• Azure Functions — Serverless compute\n• Azure SQL — Managed databases\n• Azure DevOps — CI/CD pipelines"
        elif "gcp" in msg or "google cloud" in msg:
            return "Google Cloud Platform (GCP) offers cloud services:\n\nKey services:\n• Compute Engine — Virtual machines\n• Cloud Storage — Object storage\n• Cloud Functions — Serverless compute\n• BigQuery — Data analytics\n• GKE — Managed Kubernetes"
        elif "iaas" in msg:
            return "IaaS (Infrastructure as a Service) provides virtualized computing resources:\n\n• Virtual machines, storage, networking\n• You manage: OS, middleware, applications\n• Provider manages: hardware, networking, data centers\n\nExamples: AWS EC2, Azure VMs, Google Compute Engine"
        elif "paas" in msg:
            return "PaaS (Platform as a Service) provides a development platform:\n\n• You focus on coding, provider handles infrastructure\n• Includes: runtime, middleware, OS, servers\n• Easy deployment and scaling\n\nExamples: Heroku, Google App Engine, Azure App Service"
        elif "saas" in msg:
            return "SaaS (Software as a Service) delivers complete applications:\n\n• Accessed via web browser\n• No installation or maintenance needed\n• Subscription-based pricing\n\nExamples: Gmail, Google Docs, Slack, Salesforce, Dropbox"
        elif "devops" in msg or "ci/cd" in msg or "cicd" in msg:
            return "DevOps combines development and operations:\n\nPractices:\n• CI/CD — Continuous Integration & Deployment\n• Infrastructure as Code (IaC)\n• Monitoring & logging\n• Automated testing\n\nTools: Jenkins, GitHub Actions, Docker, Kubernetes, Terraform, Ansible"
        elif "virtual machine" in msg or "vm " in msg:
            return "Virtual Machines (VMs) are software-based computers:\n\n• Run a full OS on a hypervisor\n• Isolated from host system\n• Heavier than containers but more isolated\n\nCloud VMs: AWS EC2, Azure VMs, Google Compute Engine\n\nVMs vs Containers: VMs run full OS; containers share host OS kernel (lighter, faster)."
        elif "scaling" in msg or "auto-scaling" in msg or "autoscaling" in msg:
            return "Cloud Scaling adjusts resources based on demand:\n\n• Vertical Scaling (Scale Up) — More CPU/RAM to existing server\n• Horizontal Scaling (Scale Out) — Add more servers\n• Auto-scaling — Automatic adjustment based on rules\n\nBenefits: Cost optimization, handle traffic spikes, high availability"
        elif "s3" in msg:
            return "Amazon S3 (Simple Storage Service) is cloud object storage:\n\n• Store unlimited files (objects) in buckets\n• 99.999999999% durability\n• Storage classes: Standard, Infrequent Access, Glacier\n• Use for: backups, static websites, data lakes, media storage"
        elif "ec2" in msg:
            return "Amazon EC2 (Elastic Compute Cloud) provides virtual servers:\n\n• Choose instance types based on CPU/RAM needs\n• Multiple OS options (Linux, Windows)\n• Pay per hour/second\n• Auto-scaling groups for dynamic capacity\n\nInstance types: General Purpose, Compute Optimized, Memory Optimized, Storage Optimized"
        elif "load balancing" in msg or "load balancer" in msg:
            return "Load Balancing distributes traffic across servers:\n\nTypes:\n• Round Robin — equal distribution\n• Least Connections — send to least busy server\n• IP Hash — consistent routing based on client IP\n\nAWS: Elastic Load Balancer (ALB, NLB, CLB)"

    elif domain_key == "interview":
        if "introduce" in msg or "tell me about yourself" in msg or "self introduction" in msg:
            return "Self-introduction template:\n\n'My name is [Name]. I am pursuing [Degree] from [College]. I have skills in [Technologies]. I've worked on projects like [Project]. My goal is to [Career Goal].'\n\nKeep it under 2 minutes. Be confident!"
        elif "strength" in msg:
            return "How to answer 'What are your strengths?':\n\n1. Choose relevant strengths\n2. Give specific examples\n3. Show impact\n\nExample: 'I'm a strong problem solver. In my recent project, I optimized a database query that reduced load time by 40%.'"
        elif "weakness" in msg:
            return "How to answer 'What are your weaknesses?':\n\n1. Choose a real but non-critical weakness\n2. Show self-awareness\n3. Explain improvement steps\n\nExample: 'I sometimes overthink solutions, but I've been setting time limits to make faster decisions.'"
        elif "star" in msg or "behavioral" in msg:
            return "STAR Method for behavioral questions:\n\n• Situation — Set the context\n• Task — Describe your responsibility\n• Action — Explain what you did\n• Result — Share the outcome\n\nExample: 'Tell me about a time you solved a difficult problem...'\nUse STAR to structure every behavioral answer!"
        elif "resume" in msg or "cv " in msg:
            return "Resume/CV Tips:\n\n• Keep it 1-2 pages\n• Use action verbs (developed, optimized, implemented)\n• Quantify achievements (increased performance by 30%)\n• Tailor to each job description\n• Include: Education, Skills, Projects, Experience\n• Use clean formatting with consistent fonts"
        elif "hr " in msg or "hr question" in msg:
            return "Common HR Questions:\n\n• Why do you want to work here?\n• Where do you see yourself in 5 years?\n• Why should we hire you?\n• Tell me about a challenge you faced.\n• What's your expected salary?\n\nTip: Research the company, be honest, and show enthusiasm!"
        elif "salary" in msg or "negotiat" in msg:
            return "Salary Negotiation Tips:\n\n• Research market rates (Glassdoor, LinkedIn)\n• Let the employer mention numbers first\n• Focus on your value, not your needs\n• Consider total compensation (benefits, growth)\n• Be confident but flexible\n\nExample: 'Based on my research and skills, I'm looking for a range of [X-Y].'"
        elif "project" in msg:
            return "How to Present Your Projects:\n\n1. Name and purpose of the project\n2. Technologies used\n3. Your specific role and contributions\n4. Challenges faced and how you solved them\n5. Results or impact\n\nTip: Practice explaining your top 2-3 projects fluently."
        elif "communication" in msg or "body language" in msg:
            return "Interview Communication Tips:\n\n• Maintain eye contact\n• Sit upright with open body language\n• Speak clearly and at a moderate pace\n• Listen before answering\n• Ask clarifying questions\n• Smile and be friendly\n• Avoid filler words (um, uh, like)"
        elif "fresher" in msg or "first job" in msg or "no experience" in msg:
            return "Tips for Freshers:\n\n• Focus on academic projects and internships\n• Highlight skills learned through coursework\n• Show eagerness to learn\n• Mention hackathons, certifications, or online courses\n• Be honest about what you know and don't know\n\nStrengths to highlight: quick learner, adaptable, team player, passionate"

    return None


# ---------------------------
# Routes
# ---------------------------

@app.route("/")
def home():
    return redirect(url_for("login"))

# ---------------------------
# Register
# ---------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except:
            conn.close()
            return "Username already exists. Try another one."

    return render_template("register.html")

# ---------------------------
# Login
# ---------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session["username"] = username
            return redirect(url_for("dashboard"))
        else:
            return "Invalid username or password."

    return render_template("login.html")

# ---------------------------
# Dashboard
# ---------------------------
@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    domains = []
    for key, data in DOMAIN_DATA.items():
        domains.append({
            "key": key,
            "name": data["domain"],
            "icon": data["icon"],
            "description": data["description"]
        })

    return render_template("dashboard.html", username=username, domains=domains)

# ---------------------------
# API: Get Domain Data
# ---------------------------
@app.route("/api/domain/<domain_key>")
def get_domain(domain_key):
    if "username" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    domain = DOMAIN_DATA.get(domain_key)
    if not domain:
        return jsonify({"error": "Domain not found"}), 404

    return jsonify(domain)

# ---------------------------
# API: Chat Response (Domain-Specific)
# ---------------------------
@app.route("/get_response", methods=["POST"])
def get_response():
    if "username" not in session:
        return jsonify({"reply": "Session expired. Please login again."})

    username = session["username"]
    user_message = request.json.get("message", "")
    domain_key = request.json.get("domain", "general")

    if domain_key == "general":
        bot_reply = get_general_response(user_message)
    else:
        bot_reply = get_domain_response(domain_key, user_message)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chats (username, sender, message) VALUES (?, ?, ?)", (username, "user", user_message))
    cursor.execute("INSERT INTO chats (username, sender, message) VALUES (?, ?, ?)", (username, "bot", bot_reply))
    conn.commit()
    conn.close()

    return jsonify({"reply": bot_reply})

# ---------------------------
# API: Get Module Questions
# ---------------------------
@app.route("/api/module/<domain_key>/<int:module_index>")
def get_module(domain_key, module_index):
    if "username" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    domain = DOMAIN_DATA.get(domain_key)
    if not domain:
        return jsonify({"error": "Domain not found"}), 404

    if module_index < 0 or module_index >= len(domain["modules"]):
        return jsonify({"error": "Module not found"}), 404

    module = domain["modules"][module_index]
    return jsonify(module)

# ---------------------------
# API: Save Progress
# ---------------------------
@app.route("/api/save_progress", methods=["POST"])
def save_progress():
    if "username" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    username = session["username"]
    domain = data.get("domain", "")
    module_id = data.get("module_id", "")
    score = data.get("score", 0)
    total = data.get("total", 0)
    accuracy = data.get("accuracy", 0)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO progress (username, domain, module_id, score, total, accuracy)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (username, domain, module_id, score, total, accuracy))
    conn.commit()
    conn.close()

    return jsonify({"status": "success"})

# ---------------------------
# API: Get Progress
# ---------------------------
@app.route("/api/get_progress")
def get_progress():
    if "username" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    username = session["username"]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM progress WHERE username=?", (username,))
    rows = cursor.fetchall()
    conn.close()

    progress = {}
    for row in rows:
        progress[row["module_id"]] = {
            "domain": row["domain"],
            "score": row["score"],
            "total": row["total"],
            "accuracy": row["accuracy"]
        }

    return jsonify(progress)

# ---------------------------
# API: Leaderboard
# ---------------------------
@app.route("/api/leaderboard")
def leaderboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT username, SUM(score) as total_score, 
               ROUND(AVG(accuracy), 1) as avg_accuracy,
               COUNT(DISTINCT module_id) as modules_completed
        FROM progress 
        GROUP BY username 
        ORDER BY total_score DESC 
        LIMIT 10
    """)
    rows = cursor.fetchall()
    conn.close()

    result = []
    for i, row in enumerate(rows):
        result.append({
            "rank": i + 1,
            "username": row["username"],
            "total_score": row["total_score"],
            "avg_accuracy": row["avg_accuracy"],
            "modules_completed": row["modules_completed"]
        })

    return jsonify(result)

# ---------------------------
# Clear Chat
# ---------------------------
@app.route("/clear_chat", methods=["POST"])
def clear_chat():
    if "username" not in session:
        return jsonify({"status": "error"})

    username = session["username"]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chats WHERE username=?", (username,))
    conn.commit()
    conn.close()

    return jsonify({"status": "success"})

# ---------------------------
# Download Chat
# ---------------------------
@app.route("/download_chat")
def download_chat():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT sender, message FROM chats WHERE username=?", (username,))
    chats = cursor.fetchall()
    conn.close()

    content = ""
    for chat in chats:
        sender = "You" if chat["sender"] == "user" else "ZIVRAJ"
        content += f"{sender}: {chat['message']}\n"

    buffer = BytesIO()
    buffer.write(content.encode("utf-8"))
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="chat_history.txt", mimetype="text/plain")

# ---------------------------
# Logout
# ---------------------------
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

# ---------------------------
# Run App
# ---------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)