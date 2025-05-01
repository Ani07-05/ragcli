# D. Research Gap and Our Contribution

While there is substantial work on educational data mining and exam pattern prediction, a gap exists for competitive exams like JEE. Most research addresses general question prediction without considering the specific challenges of competitive exams and their evolving patterns. Our work addresses this gap by focusing on recent patterns while incorporating historical context.

# III. METHODOLOGY

Here is our approach to predicting JEE chapter weightage, from data collection through model building and testing.

# Model Architecture for Chapter Weightage Prediction

|Chapter frequency|Historical avg. marks|Predicted marks|
|---|---|---|
|Recent importance|Random Forest Regressor|Chapter weightage allocation|
|Chapter trend (200 estimators)|Evaluation metrics:|RMSE = 1.651|
|Consistency| |R² = 0.196|
|Training data|(80%)|Test data (20%)|

Note: Random Forest processes features through decision trees to predict mark values, which become chapter weightage allocations.

Fig. 1. Model architecture for JEE chapter weightage prediction

# A. Data Collection

We compiled JEE exam questions from 2002 to 2024. Our dataset contains 1,632 data points. Each entry shows the year, chapter, subject (Physics, Chemistry, or Mathematics), and marks allocated. This gives us over 20 years of exam patterns to analyze.

We collected data from official JEE papers, academic sources, and public datasets. We started with over 13,000 question records, then filtered them for consistency. The final dataset has a balanced distribution: 584 entries for Mathematics, 546 for Chemistry, and 502 for Physics.

# B. Data Preprocessing

We prepared the raw data through several steps:

1. Data Cleaning: We performed thorough cleaning:
- Removed duplicates to prevent bias
- Standardized chapter names across years
- Verified mark allocations against original papers
- Checked for missing values (our final dataset had none)
2. Temporal Segmentation: Recent exams are more relevant for future predictions, so we divided the data:
- Recent years (2015-2024): Given higher weight
- Earlier years (2002-2014): Provided context but with reduced influence

We assigned 75% weight to recent patterns and 25% to historical patterns.
3. Categorical Encoding: For ML model compatibility, we transformed categorical variables:
- Text features (chapter and subject) were one-hot encoded
- We kept original categorical values for easier analysis

# C. Feature Engineering

We created informative features to capture different aspects of chapter importance:

|Historical Metrics|Temporal Metrics|
|---|---|
|Average Marks|Chapter Trend|
|Frequency|Recent Importance|
|Importance Score|Maximum Marks|
|Chapter Consistency|Variation|

Fig. 2. Feature engineering framework for chapter importance calculation

1. Historical Importance Metrics: For each chapter, we calculated:
- Average Marks: Mean marks allocated to the chapter across all years
- Frequency: How often the chapter appears in examinations
- Maximum Marks: The highest marks ever allocated to the chapter
- Variation: Standard deviation of marks, showing volatility
2. Temporal Trend Features: To capture changes in chapter importance over time:
- Chapter Trend: Whether marks are increasing or decreasing over years
- Recent Importance: Average marks in recent years (2015-2024)
- Chapter Consistency: Proportion of years the chapter appeared
3. Derived Indicators: Additional features we created:
- High Marks Indicator: Whether the chapter ever received 8+ marks
- Importance Score: Combined measure using this formula:
Importance Score = 0.3×Avg Marks + 0.3×Frequency + 0.4×Max Marks + 0.5×Variation

# D. Model Development

We implemented and compared four regression models: