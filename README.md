# AI Renewable Smart Grid

Smart City Solar Energy Control System built for the Energy Conservation Week Hackathon.

The system predicts solar energy generation using machine learning and intelligently distributes renewable power across a smart city grid.

---

## System Overview

The project simulates a smart city energy control center where operators can:

• Predict solar power generation using machine learning  
• Simulate city electricity demand  
• Optimize renewable energy distribution  
• Visualize grid performance through a dashboard  
• Run energy simulations  

This acts as a **digital twin of a solar-powered smart grid.**

---

## Architecture

Weather Data / API
        ↓
Solar Prediction Model (ML)
        ↓
Demand Simulation
        ↓
Energy Optimization
        ↓
Smart Grid Dashboard

---

## Tech Stack

### Machine Learning
Python  
scikit-learn  
pandas  
numpy  

Model: RandomForestRegressor

### Backend
FastAPI  
Uvicorn  

### Frontend
HTML  
CSS  
JavaScript  
Chart.js  

### Visualization
Smart Grid Dashboard

---

## API Example

POST /predict-solar

Request

{
  "irradiation": 900,
  "temperature": 33,
  "module_temp": 47
}

Response

{
  "predicted_solar_power": 1240.78
}

---

## Project Structure
AI_RENEWABLE_GRID
│
├── api
│
├── backend
│ └── services
│
├── ml
│ ├── training
│ ├── inference
│ └── models
│
├── optimization
│
├── simulation
│
├── data
│ ├── raw
│ ├── processed
│ └── simulation
│
├── frontend
│
├── config
│
└── scripts


---

## Features

AI Solar Power Prediction  
Smart Grid Optimization  
Energy Demand Simulation  
Interactive Dashboard  
API-based ML prediction  

---

## Team

Team Strawberry Icecream