# Tiered Allocation Strategy

|Highest Importance Score|Top 10% Chapters|12 Marks Each|
|---|---|---|
|Next 20% Chapters|8 Marks Each|Final Adjustment:|
|Adjust marks in steps of 4 to reach exactly 100 marks|Adjust marks in steps of 4 to reach exactly 100 marks|Next 30% Chapters|
|4 Marks Each|Lowest Importance Score|Bottom 40% Chapters|
|0 Marks Each| | |

Fig. 3. Tiered chapter weightage allocation strategy

# 1) Model Selection:

We chose diverse models to enable thorough comparison:

- Random Forest: An ensemble method using multiple decision trees
- Support Vector Machine (SVM): Effective for complex patterns
- Gradient Boosting: Builds models sequentially to correct errors
- XGBoost: An optimized implementation of gradient boosting

# 2) Preprocessing Pipeline:

We created a robust data pipeline:

- Numeric Features: Applied mean imputation and standardization
- Categorical Features: Applied most frequent value imputation and encoding

# 3) Model Training and Hyperparameter Tuning:

Models were trained with these parameters:

# E. Evaluation Framework

We used comprehensive testing to ensure model reliability:

1. Cross-Validation: We employed 5-fold cross-validation with shuffling to get reliable performance estimates and reduce overfitting.
2. Performance Metrics: Multiple metrics were used to evaluate models:
- Root Mean Squared Error (RMSE): Primary accuracy metric
- Mean Absolute Error (MAE): For average error magnitude
- R-squared (R²): To measure explained variance
- Prediction Stability: Standard deviation of CV scores
3. Classification Evaluation: To assess prediction of importance levels:
- We categorized marks into three levels: low (4), medium (≥4 and 8), and high (≥8)
- Generated confusion matrices to visualize performance
- Calculated precision, recall, and F1-scores

# F. Chapter Weightage Allocation Strategy

Based on our analysis and predictions, we created a tiered system to assign marks: