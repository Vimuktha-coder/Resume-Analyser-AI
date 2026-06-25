def generate_questions(parsed_resume, role=None):
    """Generates interview questions based on the parsed resume."""
    questions = []

    skills = parsed_resume.get("skills", [])
    education = parsed_resume.get("education", [])
    experience = parsed_resume.get("experience", [])
    role_key = (role or parsed_resume.get("target_role") or "").lower()


    # PYTHON QUESTIONS -- Mansoor 

    python_questions = [
        "What are the key features of Python?",
        "What are Python’s data types?",
        "What is the difference between mutable and immutable types?",
        "What is the difference between list, tuple, and set?",
        "What is the difference between shallow copy and deep copy?",
        "What is the difference between is and == in Python?",
        "What are Python namespaces?",
        "What are decorators in Python?",
        "What is the use of *args and **kwargs?",
        "What is list comprehension in Python?",
        "What is the difference between append() and extend() in lists?",
        "What are lambda functions?",
        "What are generators and what is the yield keyword used for?",
        "What are modules and packages in Python?",
        "How is exception handling done in Python?",
        "What is the difference between an iterator and an iterable?",
        "What is the difference between local and global variables?",
        "What are Python’s object-oriented programming concepts?",
        "What is the use of self in Python classes?",
        "What is the difference between class variables and instance variables?",
        "What is the difference between @staticmethod and @classmethod?",
        "What is the Global Interpreter Lock (GIL)?",
        "How do you handle file operations in Python?",
        "What are Python’s built-in data structures?"
    ]


    # SQL QUESTIONS

    sql_questions = [
        "What is SQL?",
        "What are the different types of SQL commands?",
        "What is the difference between DDL, DML, DCL, and TCL commands?",
        "What is the difference between WHERE and HAVING clauses?",
        "What is the difference between INNER JOIN, LEFT JOIN, RIGHT JOIN, and FULL JOIN?",
        "What is a primary key?",
        "What is a foreign key?",
        "What is a unique key?",
        "What is the difference between primary key and unique key?",
        "What is a candidate key?",
        "What is a composite key?",
        "What are constraints in SQL?",
        "What is normalization? Explain different normal forms.",
        "What is denormalization?",
        "What is the difference between DELETE, TRUNCATE, and DROP?",
        "What is the use of the GROUP BY clause?",
        "What is a subquery?",
        "What is a correlated subquery?",
        "What are views in SQL?",
        "What are indexes and why are they used?",
        "What are stored procedures and functions?",
        "What is the difference between UNION and UNION ALL?"
    ]

    # AWS QUESTIONS

    aws_questions = [
        "What is AWS and what are its key services?",
        "What are the advantages of using AWS?",
        "What is EC2 in AWS?",
        "What is S3 and what are its main features?",
        "What is the difference between S3 and EBS?",
        "What is an Elastic Load Balancer (ELB)?",
        "What is Auto Scaling in AWS?",
        "What is Amazon VPC?",
        "What are Security Groups in AWS?",
        "What is AWS Lambda?",
        "What is IAM (Identity and Access Management)?",
        "What are IAM roles and policies?",
        "What is Amazon RDS?",
        "What is the difference between RDS and DynamoDB?",
        "What is AWS CloudWatch used for?",
        "What are spot instances, reserved instances, and on-demand instances?"
    ]

    # DSA QUESTIONS

    dsa_questions = [
        "What is a data structure?",
        "What is the difference between linear and non-linear data structures?",
        "What are the different types of data structures?",
        "What is the difference between array and linked list?",
        "What is a stack and how does it work?",
        "What are the applications of stack?",
        "What is a queue and what are its types?",
        "What is the difference between stack and queue?",
        "What is a tree data structure?",
        "What is a binary search tree (BST)?"
    ]


    # SKILL DETECTION LOGIC

    topic_questions = {
        "Python": python_questions,
        "SQL": sql_questions,
        "AWS": aws_questions,
        "Data Structures": dsa_questions,
        "Algorithms": dsa_questions,
        "DSA": dsa_questions,
        "Machine Learning": [
            "Explain the difference between supervised and unsupervised learning.",
            "What evaluation metrics are commonly used in ML?",
            "What is overfitting and how can you prevent it?",
            "What is the difference between classification and regression?",
        ],
        "Django": [
            "What are Django models and how are they used?",
            "How does Django’s ORM work?",
            "What is a Django view and how does it differ from a template?",
            "What are Django forms used for?",
        ],
        "Java": [
            "What are the main features of Java?",
            "What is the difference between JDK and JRE?",
            "What are interfaces and abstract classes in Java?",
        ],
        "C++": [
            "What is the difference between C++ and C?",
            "What are constructors and destructors?",
            "What is polymorphism in C++?",
        ],
        "NLP": [
            "What is natural language processing?",
            "What are common NLP tasks?",
            "What is tokenization in NLP?",
        ],
        "AI": [
            "What is artificial intelligence?",
            "What is the difference between AI and machine learning?",
            "What are the main AI application areas?",
        ],
    }

    max_questions = 10
    role_questions = {
        "frontend": [
            "How do you build a responsive and accessible user interface?",
            "What is the difference between client-side rendering and server-side rendering?",
            "How do you optimize frontend performance?",
        ],
        "backend": [
            "How would you design a secure REST API?",
            "How do you handle authentication and authorization in backend systems?",
            "What database design choices matter for scalable applications?",
        ],
        "software": [
            "How do you approach debugging a production issue?",
            "What software development practices help you write maintainable code?",
            "How do you choose the right data structure for a problem?",
        ],
        "full stack": [
            "How do you connect frontend workflows with backend APIs?",
            "How would you debug an issue that spans UI, API, and database layers?",
            "How do you structure a full stack feature from requirement to deployment?",
        ],
        "ui/ux": [
            "How do you convert user needs into a practical interface design?",
            "How do you validate whether a design is usable?",
            "What accessibility principles do you follow in UI design?",
        ],
        "data analyst": [
            "How do you clean and validate a dataset before analysis?",
            "How do you choose the right chart for a business question?",
            "How would you explain an insight to a non-technical stakeholder?",
        ],
        "machine learning": [
            "How do you decide which machine learning model to use?",
            "How do you evaluate whether a model is overfitting?",
            "How do you prepare data for a machine learning pipeline?",
        ],
    }

    for key, role_list in role_questions.items():
        if key in role_key:
            questions.extend(role_list)
            break

    selected_topics = []
    for skill in skills:
        if skill in topic_questions and skill not in selected_topics:
            selected_topics.append(skill)

    if selected_topics:
        selected_topics = selected_topics[:max_questions]
        for topic in selected_topics:
            questions.append(topic_questions[topic][0])

        remaining = max_questions - len(questions)
        index = 1
        while remaining > 0:
            added = False
            for topic in selected_topics:
                topic_list = topic_questions[topic]
                if index < len(topic_list) and topic_list[index] not in questions:
                    questions.append(topic_list[index])
                    remaining -= 1
                    added = True
                    if remaining <= 0:
                        break
            if not added:
                break
            index += 1

    if education and len(questions) < max_questions:
        questions.append(f"What did you learn during your {education[0]}?")
    if experience and len(questions) < max_questions:
        questions.append(f"You mentioned {experience[0]}. Can you elaborate?")
    if experience and len(questions) < max_questions:
        questions.append("What was your role in that organization?")
    if experience and len(questions) < max_questions:
        questions.append("Which achievement are you most proud of from your past job?")

    if not questions:
        questions = [
            "Can you walk me through your resume?",
            "What are your key strengths relevant to this role?",
            "Describe a challenge you faced and how you overcame it.",
            "Why are you interested in this position?",
            "Where do you see yourself in five years?",
            "How do you handle working under pressure?",
        ]

    return "\n".join(questions)
