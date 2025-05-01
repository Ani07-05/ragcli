# Predicting JEE Chapter Weightage Using Historical Data and Machine Learning

Anirudh, Akshith Anoop, Achyuth Anil Kumar, Kunal K

School of Computer Science and Engineering

RV University

Bangalore, India

1RVU23CSE058, 1RVU23CSE038, 1RVU23CSE019, 1RVU23CSE229

# Abstract

JEE is one of the toughest engineering entrance exams in India. Students need smart preparation to succeed. We studied JEE papers from 2002 to 2024 to predict which chapters will get more marks in the next exam. We tested Random Forest, SVM, and other ML models to find patterns. Random Forest performed best with a Test RMSE of 1.6508. Our results provide a breakdown of expected chapter marks for JEE 2025 across Physics, Chemistry, and Mathematics. This helps students focus their study time on high-value chapters. The research also shows how JEE patterns have changed over the years.

Index Terms—JEE, Chapter Weightage, Machine Learning, Random Forest, Test Preparation, Study Planning

# I. INTRODUCTION

JEE is very difficult. It opens doors to premier institutions like IITs and NITs. Each year, more than a million students compete for limited seats. Smart study plans are as important as understanding the concepts. Past papers show that some chapters consistently get more questions in Physics, Chemistry, and Mathematics. Yet this information is not clearly shared with students. Many end up with ineffective study plans based on uncertain information.

Traditional methods for predicting important chapters rely on teacher opinions or simple counting from past papers. These methods miss the complex patterns of how chapter importance changes over time. With better data tools now available, we can create more accurate prediction models.

Our project tests different ML models to predict chapter weightage for JEE. We used data spanning from 2002 to 2024. Our dataset contains detailed chapter marks for all three subjects over more than twenty years. This gives us a solid foundation to identify patterns and predict future trends. We compared various ML approaches to find the best model based on accuracy, interpretability, and stability. This research could transform JEE preparation by providing data-driven insights instead of guesswork.

# A. Educational Data Mining for Exam Patterns

Educational Data Mining (EDM) has proven useful for extracting insights from academic data. Algarni [1] applied EDM to predict future exam questions by analyzing student responses and past papers. They used regression and classification models to identify topics likely to reappear. Their results showed that EDM can predict exam content based on historical trends and student performance. This provided a framework for our JEE analysis.

# B. NLP and Automated Question Generation

In question analysis, Nwafor and Onyenwe [2] explored using NLP to automatically create multiple-choice questions from course materials. They identified key concepts from syllabus and past exams to generate questions. Using syntax parsing and other NLP techniques, they demonstrated it’s possible to create questions by analyzing curriculum content. While we aren’t generating questions, their work reveals connections between syllabus and question patterns. Their approach to identifying key concepts helped shape our feature engineering, especially in understanding chapter relationships in JEE.

# C. ML Model Interpretability in Education

When using ML in education, model clarity matters. Carvalho et al. [3] surveyed methods for explaining ML models, noting that transparent AI models (XAI) are important in education. They found that while “black box” models can be accurate, they are often too complex to understand, causing people to question the results. This influenced our model selection and evaluation criteria. We wanted both accuracy and clarity in our JEE chapter prediction models. By improving model interpretability, we created predictions that students and teachers can trust and use.

# II. RELATED WORK

Previous research in exam pattern prediction ranges from basic statistics to advanced ML methods. Here we review key studies that informed our approach. We wanted both accuracy and clarity in our JEE chapter prediction models. By improving model interpretability, we created predictions that students and teachers can trust and use.