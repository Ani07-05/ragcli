# 1) Tiered Allocation Approach:

Chapters were ranked by importance and allocated marks as follows:

- Top 10% of chapters: 12 marks each
- Next 20% of chapters: 8 marks each
- Next 30% of chapters: 4 marks each
- Bottom 40% of chapters: 0 marks

# 2) Balancing Mechanism:

To ensure each subject totals exactly 100 marks:

- If total exceeds 100: Reduce marks from less important chapters
- If total is below 100: Add marks to more important chapters
- Adjustments made in 4-mark increments to match JEE format

# 3) Domain-Specific Allocation:

We performed allocation separately for each subject:

- Each subject maintains exactly 100 marks
- Subject-specific patterns are preserved
- Allocation reflects both historical and recent patterns

This method combines data analysis with domain knowledge to create a reliable framework for predicting JEE chapter weightage. By integrating historical analysis with ML techniques, we provide insights into chapter importance to guide JEE preparation.

# IV. RESULTS AND ANALYSIS

Our comparison showed Random Forest performed best. Table I shows performance metrics for all tested models.

**TABLE I PERFORMANCE COMPARISON OF MACHINE LEARNING MODELS**
|Model|Mean RMSE|Std RMSE|Test RMSE|Test R²|Test MAE|
|---|---|---|---|---|---|
|Random Forest|1.669|0.080|1.651|0.196|0.938|
|SVM|1.766|0.095|1.671|0.176|0.805|
|Gradient Boosting|1.775|0.048|1.768|0.077|0.977|
|XGBoost|1.751|0.087|1.708|0.140|0.986|

# C CONFUSION MATRIX FOR RANDOM FOREST MODEL

**TABLE II**
|Actual/Pred.|Low|Med.|High|
|---|---|---|---|
|Low|114|141|3|
|Medium|0|59|6|
|High|0|4|0|

Random Forest achieved the lowest Test RMSE (1.651) and highest R² (0.196) among all models. The confusion matrix shows good performance for medium-importance chapters (91% accuracy) but lower accuracy for low-importance (44%).

# V. CONCLUSION

This research presents a data-driven approach to predicting chapter weightage for JEE examinations using machine learning. By analyzing historical patterns from 2002 to 2024, we developed a framework that provides insights into chapter importance across Physics, Chemistry, and Mathematics. Our findings show that ensemble learning methods, particularly Random Forest, effectively capture the complex relationships in chapter importance. The model processes multiple features to identify patterns that might be missed in traditional analysis.

The tiered allocation strategy derived from our predictions offers practical benefits for JEE aspirants:

- Strategic focus on high-weightage chapters for efficient study time use
- Subject-specific prioritization across all three domains
- Balanced preparation considering both historical and recent patterns

While our model shows promising results, we acknowledge limitations in accuracy, especially for high-importance chapters. Future research could address these by adding features like conceptual relationships between chapters, question complexity metrics, and syllabus changes over time.

This research contributes to educational data mining by showing how machine learning can provide valuable insights for exam preparation. By making chapter weightage predictions more objective and data-driven, we help JEE aspirants optimize their study strategies and improve their chances in this competitive examination.

# REFERENCES

1. A. Algarni, "Data mining and education," International Journal of Advanced Computer Science and Applications, vol. 7, no. 6, pp. 456-461, 2016.
2. C. A. Nwafor and I. E. Onyenwe, "Automatic Question Generation for Multiple Choice Questions Using NLP Techniques," International Journal of Computer Applications, vol. 182, no. 32, pp. 1-7, 2018.
3. D. V. Carvalho, E. M. Pereira, and J. S. Cardoso, "Machine Learning Interpretability: A Survey on Methods and Metrics," Electronics, vol. 8, no. 8, p. 832, 2019.
4. National Testing Agency, "JEE Main Information Bulletin," 2024. [Online]. Available: https://jeemain.nta.nic.in/