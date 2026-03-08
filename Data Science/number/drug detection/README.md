# Drug Detection System

A machine learning project designed to predict the type of drug detected in an individual's system based on physiological and medical parameters.

## Overview

This project utilizes a **Gradient Boosting Classifier** to identify the presence of specific drugs. The model is trained on a dataset containing medical observations and lifestyle factors, providing a diagnostic tool for quick identification in clinical or forensic settings.

## Features

The model uses the following features for prediction:

- **Demographics**: `Age`, `Sex` (Female/Male)
- **Vital Signs**: `Heart Rate`, `Systolic Blood Pressure`
- **Clinical Data**: `Blood pH`, `ALT` (Alanine Aminotransferase), `AST` (Aspartate Aminotransferase), `Creatinine`
- **Exposure**: `Hours Since Use`

## Target Classes

The system can detect the following substances:
- Benzodiazepines
- Cannabis
- Cocaine
- Heroin
- Methamphetamine

## Project Structure

- `Untitled-1.ipynb`: The primary Jupyter notebook containing data preprocessing, exploratory data analysis (EDA), model training, and evaluation.
- `drug_data.csv`: The dataset used for training and testing the model.
- `drug_detection.pkl`: The serialized (pickled) Gradient Boosting model ready for inference.
- `label_encoders.json`: JSON file containing the mapping for categorical features and target labels.
- `venv/`: Python virtual environment containing the necessary dependencies.

## Technologies Used

- **Python**: Core programming language.
- **Scikit-learn**: Machine learning library for model training and preprocessing.
- **Pandas & NumPy**: Data manipulation and numerical computations.
- **Matplotlib & Seaborn**: Data visualization and EDA.

## Getting Started

### Prerequisites

- Python 3.10+
- Jupyter Notebook or VS Code with Jupyter extension

### Installation

1. Clone the repository or navigate to the project folder.
2. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```
3. Install dependencies (if not already present):
   ```bash
   pip install pandas scikit-learn matplotlib seaborn
   ```

### Usage

Open `Untitled-1.ipynb` to explore the training process or use `drug_detection.pkl` in a production script to make predictions on new data.

---
*Note: This project is for educational/demonstration purposes.*
