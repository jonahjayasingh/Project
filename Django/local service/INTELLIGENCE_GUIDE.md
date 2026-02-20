# 🧠 ServiceFinder: Intelligence Module Implementation Guide

This document outlines the architecture and logic flow for the intelligent core features implemented in the elite services marketplace.

---

## 🏗️ 1. Intelligent Ranking Engine (`intelligence.py`)
The system uses a multi-factor weighted scoring algorithm to rank professionals beyond simple ratings.
- **Formula**: `0.35 × Rating + 0.25 × Completion + 0.20 × Punctuality + 0.10 × Distance + 0.10 × Response Speed`.
- **Logic**: Every professional is dynamically scored during search based on user context (location, requirements).
- **Execution**: The `calculate_ranking_score` function handles normalization and weight application.

## 📍 2. Location Intelligence & Geo-Fencing
- **Haversine Formula**: Precisely calculates the great-circle distance between two points on Earth using lat/lon.
- **Real-time Detection**: The "Intelligence Profile" page utilizes HTML5 Geolocation API to detect and store user coordinates.
- **Contextual Filtering**: Search results are filtered within a 30km radius by default, with nearest providers boosted in rank.

## 🤝 3. Behavioral Recommendation Engine
Proactive recommendations on the dashboard use:
- **Category Affinity**: Services the user has booked or rated previously.
- **Top Performers**: High-rank providers within the user's immediate vicinity.
- **Diversity**: Mixes favorite categories with top-rated new experts.

## 💬 4. Decision-Support AI Chatbot
Upgraded from a simple responder to an intelligent advisor:
- **Constraint Extraction**: Automatically identifies budgets, categories, and locations from natural language.
- **Direct Database Querying**: Uses the ranking engine to recommend a specific expert within the chat flow.
- **Tamil Support**: Provides localized responses for Tamil-speaking users based on their profile settings.

## 💰 5. Cost Transparency & Estimation
- **Pre-booking Estimator**: Embedded in the provider detail page.
- **Dynamic Calculation**: Updates the total price in real-time as users adjust the duration or select "Urgent Mode."
- **Urgent Booking**: A special intelligence feature that adds priority flags to bookings for an additional fee.

## 🔔 6. Integrated Multi-Channel Notifications
- **Status Alerts**: Immediate notifications when a provider accepts, completes, or cancels a job.
- **Engagement Hooks**: Welcome alerts and profile update reminders.
- **Global Context**: Unread counts are synchronized across the entire platform via a Django Context Processor.

---

## 🚀 Setup & Verification
1.  **Migrate Models**: `python manage.py migrate` to enable new memory/geo fields.
2.  **Seeding Intelligence**: Run `seed_experts.py` to populate providers with lat/lon data.
3.  **Update Profile**: Log in and visit `Profile Intelligence` to set your GPS location.
4.  **Explore Chat**: Ask "Who is the best plumber near me?" to see the Decision-Support mode in action.

---
*Note: This platform strictly avoids the Django Admin for data management, utilizing custom CRUD flows for all intelligent operations.*
