import streamlit as st
import google.generativeai as genai
from langchain.memory import ConversationBufferMemory
import os
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Google Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize Generative Model
model = genai.GenerativeModel('gemini-pro')

# Database setup
conn = sqlite3.connect("user_data.db")
cursor = conn.cursor()

# Create table for user information
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        name TEXT PRIMARY KEY, 
        bmi REAL, 
        fitness_goal TEXT
    )
""")
conn.commit()

# Create table for chat history
cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        user_name TEXT,
        message TEXT,
        role TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_name) REFERENCES users(name)
    )
""")
conn.commit()

# Initialize session memory
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "calorie_log" not in st.session_state:
    st.session_state.calorie_log = pd.DataFrame(columns=["Food", "Calories"])

# Function to get user info from database
def get_user_info(name):
    cursor.execute("SELECT bmi, fitness_goal FROM users WHERE name=?", (name,))
    return cursor.fetchone()

# Function to save user info
def save_user_info(name, bmi, fitness_goal):
    cursor.execute("INSERT OR REPLACE INTO users (name, bmi, fitness_goal) VALUES (?, ?, ?)", 
                   (name, bmi, fitness_goal))
    conn.commit()

# Function to get user chat history
def get_chat_history(name):
    cursor.execute("SELECT message, role FROM chat_history WHERE user_name=? ORDER BY timestamp", (name,))
    return cursor.fetchall()

# Function to save chat history
def save_chat_history(name, role, message):
    cursor.execute("INSERT INTO chat_history (user_name, role, message) VALUES (?, ?, ?)", 
                   (name, role, message))
    conn.commit()

# Function to get gym advice
def get_gym_advice(user_input, name):
    st.session_state.memory.chat_memory.add_user_message(user_input)
    history = st.session_state.memory.load_memory_variables({})["history"]

    user_data = get_user_info(name)
    if user_data:
        bmi, fitness_goal = user_data
        user_profile = f"User's Name: {name}\nBMI: {bmi}\nFitness Goal: {fitness_goal}"
    else:
        user_profile = f"User's Name: {name}\n(No previous data found)"
    
    prompt = f"""
    You are a professional gym trainer named **FitCoach**. Your job is to provide personalized, actionable, and motivating advice.
    
    ### User Profile:
    {user_profile}
    
    ### Conversation History:
    {history}

    ### User's Current Question:
    {user_input}

    Provide a structured response, keeping it friendly, supportive, and professional.
    """

    response = model.generate_content(prompt)
    st.session_state.memory.chat_memory.add_ai_message(response.text)
    save_chat_history(name, "assistant", response.text)  # Save assistant's response
    return response.text

# BMI Calculation
def calculate_bmi(weight, height):
    if height == 0:
        return None, "Invalid height"
    bmi = weight / ((height / 100) ** 2)
    category = ("Underweight" if bmi < 18.5 else "Normal" if bmi < 24.9 else 
                "Overweight" if bmi < 29.9 else "Obese")
    return round(bmi, 2), category

# Calorie Tracking
def track_calories(food, calories):
    new_entry = pd.DataFrame({"Food": [food], "Calories": [calories]})
    st.session_state.calorie_log = pd.concat([st.session_state.calorie_log, new_entry], ignore_index=True)

# Display Calorie Progress
def display_progress():
    if not st.session_state.calorie_log.empty:
        plt.figure(figsize=(10, 5))
        plt.plot(st.session_state.calorie_log.index, st.session_state.calorie_log["Calories"], marker="o")
        plt.title("Daily Calorie Intake Over Time")
        plt.xlabel("Entry")
        plt.ylabel("Calories")
        st.pyplot(plt)

# Streamlit App UI
st.title("🏋️ Personal Gym Instructor Chatbot")

# User Identification
st.sidebar.header("User Information")
name = st.sidebar.text_input("Enter your name:", key="name_input")

if name:
    user_data = get_user_info(name)
    if user_data:
        st.sidebar.success(f"Welcome back, {name}! Your fitness goal: {user_data[1]}")
    else:
        st.sidebar.info(f"Hi {name}, please enter your details for personalized fitness advice.")

    weight = st.sidebar.number_input("Enter your weight (kg):", min_value=0.0, key="weight_input")
    height = st.sidebar.number_input("Enter your height (cm):", min_value=0.0, key="height_input")
    fitness_goal = st.sidebar.text_input("Enter your fitness goal (e.g., 'Lose weight', 'Gain muscle'):", key="goal_input")

    if st.sidebar.button("Save Information", key="save_info_button"):
        bmi, category = calculate_bmi(weight, height)
        if bmi:
            save_user_info(name, bmi, fitness_goal)
            st.sidebar.success(f"Your details have been saved! BMI: {bmi} ({category})")

# Display Previous Conversations
if name:
    chat_history = get_chat_history(name)
    if chat_history:
        for message, role in chat_history:
            st.markdown(f"**{role.capitalize()}:** {message}")

# Chat Interface
st.header("💬 Chat with FitCoach")

if user_input := st.chat_input("Ask me anything about fitness, workouts, or diet:"):
    if not name:
        st.warning("Please enter your name in the sidebar to continue.")
    else:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        
        response = get_gym_advice(user_input, name)
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)

# Display Calorie Progress
st.header("📊 Your Calorie Intake Progress")
display_progress()

