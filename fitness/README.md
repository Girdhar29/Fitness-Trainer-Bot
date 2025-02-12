# Personal Gym Instructor Chatbot

A personal gym instructor chatbot developed using Streamlit and Google Gemini, offering personalized fitness advice, BMI calculation, calorie tracking, and progress visualization. 

## Features
- **Personalized Fitness Guidance**: Get structured fitness advice based on your profile (BMI, fitness goal).
- **BMI Calculation**: Enter your weight and height to calculate BMI and receive health assessments.
- **Calorie Tracking**: Log food intake and track calorie progress with visual graphs.
- **Chat History**: Chat with FitCoach and revisit past conversations for continuous guidance.

## Installation

1. Clone the repository:
    ```bash
    git clone <repository_url>
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up environment variables:
    - Create a `.env` file in the root directory.
    - Add your Google Gemini API key in the `.env` file:
      ```
      GOOGLE_API_KEY=<your_api_key>
      ```

4. Run the app:
    ```bash
    streamlit run app.py
    ```

## Usage

1. Enter your name, weight, height, and fitness goal in the sidebar.
2. Chat with FitCoach to get personalized fitness advice.
3. Track your calorie intake and monitor progress over time.
