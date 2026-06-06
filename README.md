# Crowd Level Classification Based on Wi-Fi RSSI

## Overview

Crowd Level Classification Based on Wi-Fi RSSI is a Machine Learning project that estimates crowd density using Wi-Fi signal strength (RSSI) data. The system collects RSSI values, processes the data, and classifies crowd levels into Low, Medium, and High categories.

The project demonstrates how wireless signal information can be used for smart monitoring applications in public spaces, educational institutions, and event venues.

## Features

* Real-time Wi-Fi RSSI data collection
* Data preprocessing and feature extraction
* Crowd level prediction using Machine Learning
* Live monitoring dashboard
* Classification into Low, Medium, and High crowd levels
* Performance evaluation and analysis

## Technologies Used

* Python
* NumPy
* Pandas
* Scikit-learn
* HTML
* CSS
* JavaScript

## Project Structure

```
├── crowd_model.pkl              # Trained machine learning model
├── crowd_model_trainer.py       # Model training script
├── data_collector.py            # RSSI data collection script
├── live_predictor.py            # Real-time prediction system
├── high_crowd.csv              # High crowd dataset
├── medium_crowd.csv            # Medium crowd dataset
├── low_crowd.csv               # Low crowd dataset
├── raw_rssi_data.csv           # Collected RSSI data
├── level.txt                   # Live prediction output
├── index.html                  # Dashboard interface
└── README.md
```

## Workflow

1. Collect Wi-Fi RSSI data.
2. Clean and preprocess the collected data.
3. Extract useful features from RSSI readings.
4. Train a Random Forest classifier.
5. Evaluate model performance.
6. Generate live crowd predictions.
7. Display results through the dashboard.

## Machine Learning Pipeline

* Data Collection
* Data Cleaning and Preprocessing
* Feature Engineering
* Model Training
* Evaluation Pipeline
* Live Prediction

## Results

* Crowd Classification Accuracy: 92%
* Successfully classified crowd density into three categories:

  * Low Crowd
  * Medium Crowd
  * High Crowd

## Applications

* Smart Campus Monitoring
* Public Event Management
* Shopping Mall Analytics
* Crowd Safety Management
* Smart City Infrastructure

## Future Improvements

* Integration with IoT devices
* Cloud deployment
* Mobile application support
* Advanced machine learning models
* Real-time analytics dashboard

## Author

**Tharshan R**

B.Tech Artificial Intelligence and Data Science

Vel Tech Engineering College
