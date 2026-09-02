// Static Data Module for Nandeeswaran B. Portfolio

export const personalInfo = {
  name: 'Nandeeswaran B',
  role: 'Aspiring Data Scientist | AI & Data Science Student',
  college: 'SNS College of Engineering',
  degree: 'B.Tech Artificial Intelligence and Data Science',
  careerObjective: 'Passionate about Data Science, Machine Learning, Artificial Intelligence, Predictive Analytics, and solving real-world problems using data-driven solutions.',
  email: 'nandeeswaran033@gmail.com',
  phone: '+91 88079 82288', // Placeholder/Typical phone format, customizable
  linkedin: 'https://linkedin.com/in/bnandeeswaran',
  github: 'https://github.com/Nandeeswaran-b',
  leetcode: 'https://leetcode.com/u/Nandeeswarn_45/',
  resumeFolder: 'https://drive.google.com/drive/folders/1sOftMSg_xfGdfZXYXgO9qcVkQnqCZqP8'
};

export const statistics = [
  { label: 'Internships', count: 2, icon: 'Briefcase' },
  { label: 'Certifications', count: 4, icon: 'Award' },
  { label: 'Live Projects', count: 3, icon: 'Database' },
  { label: 'LeetCode Problems', count: 412, icon: 'Code', suffix: '+' }
];

export const skills = [
  // Programming
  { name: 'Python', category: 'Programming', proficiency: 95 },
  { name: 'SQL', category: 'Programming', proficiency: 88 },
  
  // Machine Learning
  { name: 'Classification', category: 'Machine Learning', proficiency: 92 },
  { name: 'Regression', category: 'Machine Learning', proficiency: 90 },
  { name: 'Predictive Modeling', category: 'Machine Learning', proficiency: 90 },
  { name: 'Feature Engineering', category: 'Machine Learning', proficiency: 88 },
  { name: 'Model Evaluation', category: 'Machine Learning', proficiency: 85 },
  { name: 'EDA', category: 'Machine Learning', proficiency: 92 },
  { name: 'Statistical Analysis', category: 'Machine Learning', proficiency: 84 },
  
  // Data Analytics
  { name: 'Data Cleaning', category: 'Data Analytics', proficiency: 94 },
  { name: 'Data Wrangling', category: 'Data Analytics', proficiency: 90 },
  { name: 'Data Visualization', category: 'Data Analytics', proficiency: 92 },
  { name: 'Business Intelligence', category: 'Data Analytics', proficiency: 82 },
  
  // Libraries
  { name: 'Pandas', category: 'Libraries', proficiency: 95 },
  { name: 'NumPy', category: 'Libraries', proficiency: 92 },
  { name: 'Scikit-learn', category: 'Libraries', proficiency: 90 },
  { name: 'Matplotlib', category: 'Libraries', proficiency: 88 },
  { name: 'Seaborn', category: 'Libraries', proficiency: 90 },
  
  // Tools
  { name: 'Power BI', category: 'Tools', proficiency: 85 },
  { name: 'MySQL', category: 'Tools', proficiency: 88 },
  { name: 'Git', category: 'Tools', proficiency: 80 },
  { name: 'GitHub', category: 'Tools', proficiency: 85 },
  { name: 'Jupyter Notebook', category: 'Tools', proficiency: 95 },
  { name: 'VS Code', category: 'Tools', proficiency: 90 },
  { name: 'Google Colab', category: 'Tools', proficiency: 92 },

  // Soft Skills
  { name: 'Problem Solving', category: 'Soft Skills', proficiency: 95 },
  { name: 'Critical Thinking', category: 'Soft Skills', proficiency: 90 },
  { name: 'Effective Communication', category: 'Soft Skills', proficiency: 88 },
  { name: 'Team Collaboration', category: 'Soft Skills', proficiency: 92 },
  { name: 'Presentation Skills', category: 'Soft Skills', proficiency: 85 },
  { name: 'Adaptability & Learning', category: 'Soft Skills', proficiency: 94 }
];

export const internships = [
  {
    company: 'DeepByte Verxe',
    role: 'Machine Learning Intern',
    period: '2025 (Remote)',
    description: 'Developed neural network layers and classical classification architectures. Preprocessed raw image datasets, performed feature extraction, and built model evaluation pipelines to optimize validation margins.',
    skills: ['Neural Networks', 'Feature Engineering', 'Model Evaluation'],
    technologies: ['Python', 'TensorFlow', 'Scikit-Learn', 'Google Colab']
  },
  {
    company: 'Tamil Infotech',
    role: 'Data Scientist Intern',
    period: '2026 (Hybrid)',
    description: 'Conducted exploratory data analysis (EDA), data cleaning, and statistical modeling. Built dashboards to summarize sales distributions and helped refine data pipeline integrity.',
    skills: ['EDA', 'Data Cleaning', 'Data Visualization'],
    technologies: ['Python', 'Pandas', 'Matplotlib', 'MySQL']
  }
];

export const projects = [
  {
    title: 'Customer Churn Prediction',
    subtitle: 'Machine Learning Classification Model',
    description: 'A robust machine learning classification system designed to predict user retention. Handled severe class imbalance using SMOTE and evaluated with ROC-AUC scores.',
    category: 'Machine Learning',
    coverImage: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=600&auto=format&fit=crop',
    liveLink: 'https://customer-churn-prediction-sooty.vercel.app',
    githubLink: 'https://github.com/Nandeeswaran-b/customer-churn-prediction',
    tags: ['Python', 'Scikit-Learn', 'Pandas', 'SMOTE'],
    challenge: 'A leading bank experienced high annual subscriber churn, but the dataset was severely imbalanced (only 15% positive churn records), which skewed standard classifiers toward false negatives.',
    methodology: 'Implemented SMOTE (Synthetic Minority Over-sampling Technique) to rebalance the training cohort. Preprocessed features using standard scaling and encoded categorical variables. Trained a Random Forest Classifier and hyperparameter-tuned it using grid search.',
    impact: 'Achieved an ROC-AUC of 92.4% and boosted recall on positive churn class by 28%. Provided the marketing team with early churn warnings, helping them reduce attrition by an estimated 12% in testing cohorts.',
    details: {
      keyMetric: 'ROC-AUC Score',
      keyMetricVal: '92.4%',
      modelType: 'Random Forest + SMOTE',
      datasetSize: '10,000 customers'
    }
  },
  {
    title: 'Loan Approval Prediction',
    subtitle: 'Predictive Analytics Credit Risk Model',
    description: 'An analytical pipeline that evaluates and automates credit approvals. Compares random forests and boosted trees to minimize false approvals and credit losses.',
    category: 'Machine Learning',
    coverImage: 'https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?q=80&w=600&auto=format&fit=crop',
    liveLink: 'https://loan-approval-prediction.onrender.com',
    githubLink: 'https://github.com/Nandeeswaran-b/-loan-approval-prediction',
    tags: ['Python', 'XGBoost', 'Feature Engineering', 'EDA'],
    challenge: 'Automating credit risk evaluation while maintaining tight safety guardrails. Loan officers needed an interpretable yet highly accurate metric to approve applications instantly without human bottlenecking.',
    methodology: 'Conducted rigorous Exploratory Data Analysis (EDA) to isolate key determinants like credit history and debt-to-income ratio. Built an XGBoost predictive pipeline with robust feature engineering (income-to-loan ratios, credit-span factors).',
    impact: 'Reduced loan manual processing overheads by 65% with a false approval rate of less than 1.8%. The final model output showed a predictive F1-score of 89.2% on cross-validation testing.',
    details: {
      keyMetric: 'Validation F1-Score',
      keyMetricVal: '89.2%',
      modelType: 'XGBoost Classifier',
      datasetSize: '614 applicants'
    }
  },
  {
    title: 'Sales Intelligence Platform',
    subtitle: 'Full-Stack Data Analytics Dashboard',
    description: 'A full-stack Sales Intelligence Platform with a Python/Flask REST API backend, real-time SQLite analytics, polynomial regression forecasting, RFM customer segmentation, anomaly detection, Market Basket Analysis, and an interactive SQL Sandbox.',
    category: 'Data Analytics',
    coverImage: 'https://images.unsplash.com/photo-1543286386-713bdd548da4?q=80&w=600&auto=format&fit=crop',
    liveLink: 'https://sales-henna-beta.vercel.app',
    githubLink: 'https://github.com/Nandeeswaran-b/sales',
    tags: ['Python', 'Flask', 'SQLite', 'Chart.js', 'REST API'],
    challenge: 'Business teams needed a single, live platform to monitor KPIs, detect anomalies, segment customers by value, and explore raw data via SQL — without relying on expensive BI tools or manual spreadsheet analysis.',
    methodology: 'Built a Python/Flask REST API serving analytics endpoints for monthly trends, RFM cohort scoring, polynomial regression forecasting, and Apriori-based Market Basket Analysis. Frontend uses vanilla HTML/CSS/JS with Chart.js for real-time visualisations, deployed on Vercel (frontend) and Render (backend).',
    impact: 'Delivered real-time KPI monitoring, intelligent anomaly flagging, and data-driven product recommendations. The SQL Sandbox enables ad-hoc queries directly against the live sales database, reducing reporting time from hours to seconds.',
    details: {
      keyMetric: 'API Response Time',
      keyMetricVal: '< 200ms',
      modelType: 'Flask + SQLite + Chart.js',
      datasetSize: '50,000+ sales entries'
    }
  }
];

export const certifications = [
  {
    name: 'Oracle Cloud Infrastructure 2025 Certified AI Foundations Associate',
    issuer: 'Oracle',
    driveLink: 'https://drive.google.com/drive/folders/1A9CDodY46BaVaB0P1pl7GlaQNyp_Hbc-'
  },
  {
    name: 'Power BI for Beginners',
    issuer: 'Microsoft / Coursera',
    driveLink: 'https://drive.google.com/drive/folders/19A1jh7qAsFvF9IvFi3r6e0h6u_lEI944'
  },
  {
    name: 'Artificial Intelligence Fundamentals',
    issuer: 'IBM',
    driveLink: 'https://drive.google.com/drive/folders/1mW_QULUkYLTqLKdJHQk_4HtmD7967YCB'
  },
  {
    name: 'Microsoft Excel',
    issuer: 'Infosys Springboard',
    driveLink: 'https://drive.google.com/drive/folders/1nMetvyZAfsM8BZ-pfg9dbgpuu9rCIsF5'
  }
];

export const achievements = [
  {
    title: 'Solved 412+ LeetCode Problems',
    description: 'Demonstrated strong logic, writing algorithms and complex data structures (arrays, trees, searching).'
  },
  {
    title: 'Built Multiple Data Science Projects',
    description: 'Developed end-to-end classification models, credit predictions, and visual dashboards.'
  },
  {
    title: 'Completed Industry Certifications',
    description: 'Earned credentials from Oracle (AI Foundations), IBM (AI Fundamentals), Power BI, Excel, and Infosys Springboard.'
  },
  {
    title: 'Participated in Technical Paper Presentations',
    description: 'Presented statistical modeling papers at national student symposia, winning high placement.'
  }
];

export const education = [
  {
    institution: 'SNS College of Engineering',
    degree: 'B.Tech Artificial Intelligence and Data Science',
    period: '2022 - 2026',
    description: 'Specializing in machine learning methodologies, predictive model architectures, and data structures. Relevant coursework: Deep Learning, Data Structures and Algorithms, Advanced Database Management Systems, and Statistical Inference.',
    skills: ['Machine Learning', 'Data Structures', 'Statistical Modeling'],
    technologies: ['Python', 'SQL', 'R', 'Power BI']
  }
];
