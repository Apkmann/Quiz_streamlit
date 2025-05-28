import streamlit as st
import random
import json
import pandas as pd
from PIL import Image
import time
import base64
from datetime import datetime
random.seed(int(time.time()) % 10000) # For more randomize
# Set up the page configuration
st.set_page_config(
    page_title="TNPSC Quiz",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for better design
def load_css():
    st.markdown("""
    <style>
        .main {
            background-color: #f9f7f0;
            padding: 20px;
        }
        .stButton button {
            width: 100%;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .question-card {
            background-color: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .heading-container {
            text-align: center;
            margin-bottom: 30px;
        }
        .option-container {
            padding: 10px;
            margin: 10px 0;
            border-radius: 10px;
            transition: all 0.2s ease;
        }
        .option-container:hover {
            background-color: #f5f5f5;
        }
        .result-container {
            text-align: center;
            padding: 20px;
            background-color: white;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .feedback-text {
            font-size: 18px;
            margin: 15px 0;
        }
        .progress-container {
            margin: 20px 0;
        }
        .spaced-option {
            margin-bottom: 10px;
        }
        .memory-tip {
            background-color: #e8f4f8;
            padding: 10px;
            border-left: 4px solid #4e8cff;
            margin: 15px 0;
            border-radius: 5px;
        }
        .flashcard {
            perspective: 1000px;
            margin: 20px auto;
            width: 100%;
            max-width: 600px;
            height: 300px;
        }
        .flashcard-inner {
            position: relative;
            width: 100%;
            height: 100%;
            text-align: center;
            transition: transform 0.8s;
            transform-style: preserve-3d;
        }
        .flipped .flashcard-inner {
            transform: rotateY(180deg);
        }
        .flashcard-front, .flashcard-back {
            position: absolute;
            width: 100%;
            height: 100%;
            -webkit-backface-visibility: hidden;
            backface-visibility: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            overflow-y: auto;
        }
        .flashcard-front {
            background-color: #f0f8ff;
            color: black;
        }
        .flashcard-back {
            background-color: #e8f4e8;
            color: black;
            transform: rotateY(180deg);
        }
        .flashcard-content {
            max-width: 90%;
            max-height: 90%;
            font-size: 18px;
        }
        .flashcard-controls {
            margin-top: 20px;
            display: flex;
            justify-content: center;
            gap: 10px;
        }
        .nav-buttons {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin: 20px 0;
        }
        .nav-btn {
            padding: 10px 20px;
            border-radius: 20px;
            background-color: #f0f0f0;
            border: none;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .nav-btn:hover {
            background-color: #e0e0e0;
            transform: translateY(-2px);
        }
        .nav-btn.active {
            background-color: #4e8cff;
            color: white;
        }
        .mastery-progress {
            margin: 15px 0;
            padding: 10px;
            background-color: #f9f9f9;
            border-radius: 10px;
        }
        .export-section {
            margin-top: 20px;
            padding: 15px;
            background-color: #f5f5f5;
            border-radius: 10px;
        }
        .flashcard-deck-selector {
            margin: 20px 0;
            padding: 15px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        /* Animation for new items */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .fade-in {
            animation: fadeIn 0.5s ease-out forwards;
        }
        .correct-answer {
            color: #28a745;
            font-weight: bold;
            margin-top: 5px;
            padding: 5px;
            background-color: #e8f5e9;
            border-radius: 5px;
        }
        .incorrect-answer {
            color: #dc3545;
            font-weight: bold;
            margin-top: 5px;
            padding: 5px;
            background-color: #f8d7da;
            border-radius: 5px;
        }
    </style>
    """, unsafe_allow_html=True)

# Function to create flashcard deck from quiz data
def create_flashcards(data):
    # Convert quiz data to flashcards
    flashcards = []
    for lesson in data:
        for pair in lesson.get("pairs", []):
            flashcard = {
                "front": pair["question"],
                "back": pair["answer"],
                "mastery_level": 0,  # 0-5 scale for spaced repetition
                "last_reviewed": None,
                "due_date": datetime.now().strftime("%Y-%m-%d")
            }
            flashcards.append(flashcard)
    return flashcards

# Function to display flashcards
def display_flashcards(flashcards):
    st.markdown('<div class="heading-container">', unsafe_allow_html=True)
    st.title("📇 Tamil Flashcards")
    st.markdown('</div>', unsafe_allow_html=True)

    # Initialize session state for flashcards
    if 'current_card' not in st.session_state:
        st.session_state.current_card = 0
    if 'is_flipped' not in st.session_state:
        st.session_state.is_flipped = False
    if 'mastery_counts' not in st.session_state:
        st.session_state.mastery_counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for card in flashcards:
            level = card.get("mastery_level", 0)
            st.session_state.mastery_counts[level] = st.session_state.mastery_counts.get(level, 0) + 1

    # Calculate total cards and current position
    total_cards = len(flashcards)
    current_position = st.session_state.current_card + 1

    # Display progress bar
    st.markdown('<div class="progress-container">', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 4])
    with col1:
        st.write(f"Card {current_position}/{total_cards}")
    with col2:
        progress = st.session_state.current_card / total_cards if total_cards > 0 else 0
        st.progress(progress)
    st.markdown('</div>', unsafe_allow_html=True)

    # Display mastery progress
    st.markdown('<div class="mastery-progress">', unsafe_allow_html=True)
    st.markdown("### Mastery Progress")

    # Create mastery level counts
    mastery_data = []
    for level, count in st.session_state.mastery_counts.items():
        mastery_data.append({"Level": f"Level {level}", "Count": count})

    mastery_df = pd.DataFrame(mastery_data)
    st.bar_chart(mastery_df.set_index("Level"))
    st.markdown('</div>', unsafe_allow_html=True)

    # Get current flashcard
    if total_cards > 0:
        card = flashcards[st.session_state.current_card]

        # Display flashcard
        flipped_class = "flipped" if st.session_state.is_flipped else ""
        st.markdown(f'<div class="flashcard {flipped_class}">', unsafe_allow_html=True)
        st.markdown('<div class="flashcard-inner">', unsafe_allow_html=True)

        # Front of card
        st.markdown('<div class="flashcard-front">', unsafe_allow_html=True)
        st.markdown('<div class="flashcard-content">', unsafe_allow_html=True)
        st.markdown(f"<h3>{card['front']}</h3>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Back of card
        st.markdown('<div class="flashcard-back">', unsafe_allow_html=True)
        st.markdown('<div class="flashcard-content">', unsafe_allow_html=True)
        st.markdown(f"<p>{card['back']}</p>", unsafe_allow_html=True)

        # Add memory aid
        memory_aid = create_memory_aid(card['front'], card['back'])
        st.markdown(f'<div class="memory-tip">💡 <b>Memory Tip:</b> {memory_aid}</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Controls
        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            if st.button("⬅️ Previous", key="prev_btn", disabled=(st.session_state.current_card == 0)):
                st.session_state.current_card = max(0, st.session_state.current_card - 1)
                st.session_state.is_flipped = False
                st.rerun()

        with col2:
            if st.button("Flip Card 🔄", key="flip_btn"):
                st.session_state.is_flipped = not st.session_state.is_flipped
                st.rerun()

        with col3:
            if st.button("Next ➡️", key="next_btn", disabled=(st.session_state.current_card >= total_cards - 1)):
                st.session_state.current_card = min(total_cards - 1, st.session_state.current_card + 1)
                st.session_state.is_flipped = False
                st.rerun()

        # Rate knowledge level
        st.markdown("### Rate your mastery of this card")
        mastery_col1, mastery_col2, mastery_col3, mastery_col4, mastery_col5, mastery_col6 = st.columns(6)

        mastery_cols = [mastery_col1, mastery_col2, mastery_col3, mastery_col4, mastery_col5, mastery_col6]
        mastery_labels = ["Don't Know", "Recognize", "Recall with Help", "Recall", "Understand", "Mastered"]

        for i, (col, label) in enumerate(zip(mastery_cols, mastery_labels)):
            with col:
                if st.button(f"{i}", key=f"mastery_{i}", help=label):
                    # Update mastery count
                    old_level = flashcards[st.session_state.current_card].get("mastery_level", 0)
                    st.session_state.mastery_counts[old_level] = max(0, st.session_state.mastery_counts[old_level] - 1)
                    st.session_state.mastery_counts[i] = st.session_state.mastery_counts.get(i, 0) + 1

                    # Update card
                    flashcards[st.session_state.current_card]["mastery_level"] = i
                    flashcards[st.session_state.current_card]["last_reviewed"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    # Move to next card if not at the end
                    if st.session_state.current_card < total_cards - 1:
                        st.session_state.current_card += 1
                        st.session_state.is_flipped = False
                    st.rerun()

        # Export flashcards option
        with st.expander("Export Flashcards"):
            st.markdown("Download your flashcards with mastery data to continue studying later.")
            if st.button("Export as JSON"):
                json_str = json.dumps(flashcards, indent=2, ensure_ascii=False)
                b64 = base64.b64encode(json_str.encode()).decode()
                href = f'<a href="data:application/json;base64,{b64}" download="tamil_flashcards.json">Download JSON File</a>'
                st.markdown(href, unsafe_allow_html=True)
    else:
        st.warning("No flashcards available. Please upload quiz data first.")

    # Return to menu button
    if st.button("Return to Main Menu", key="return_menu"):
        st.session_state.mode = "home"
        st.rerun()

# Function to create mnemonics or memory aids
def create_memory_aid(question, answer):
    # Simple algorithm to create memory aids
    # This is a placeholder - in a real app, you might want more sophisticated logic
    key_terms = []

    # Extract potential key terms (words with more than 4 letters)
    for word in answer.split():
        if len(word) > 4:
            key_terms.append(word)

    # If we found key terms, create a simple memory aid
    if key_terms:
        if len(key_terms) > 3:
            key_terms = key_terms[:3]  # Limit to first 3 key terms

        memory_tip = f"Remember these key terms: {', '.join(key_terms)}"
        return memory_tip

    return "Try to create a mental image or association to remember this answer."

# Function to run the quiz
def run_quiz(data, num_questions=None):
    # Extract all question pairs from all lessons
    all_pairs = []
    for lesson in data:
        all_pairs.extend(lesson.get("pairs", []))

    # If number of questions is specified, limit to that number
    if num_questions and num_questions > 0:
        all_pairs = all_pairs[:num_questions]

    # Store session state
    if 'quiz_data' not in st.session_state:
        st.session_state.quiz_data = all_pairs
        st.session_state.current_question = 0
        st.session_state.correct_count = 0
        st.session_state.answered = False
        st.session_state.total_questions = len(all_pairs)
        st.session_state.show_results = False
        st.session_state.start_time = time.time()
        st.session_state.question_times = []

    # Display quiz header
    with st.container():
        st.markdown('<div class="heading-container">', unsafe_allow_html=True)
        st.title("🎓 Tamil Quiz App")
        st.markdown('</div>', unsafe_allow_html=True)

    # Display progress
    with st.container():
        st.markdown('<div class="progress-container">', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 4])
        with col1:
            st.write(f"Question {st.session_state.current_question + 1}/{st.session_state.total_questions}")
        with col2:
            progress = st.session_state.current_question / st.session_state.total_questions
            st.progress(progress)
        st.markdown('</div>', unsafe_allow_html=True)

    # Display results if quiz is finished
    if st.session_state.show_results:
        show_results()
        return

    # Get current question
    if st.session_state.current_question < st.session_state.total_questions:
        item = st.session_state.quiz_data[st.session_state.current_question]
        display_question(item)
    else:
        st.session_state.show_results = True
        st.rerun()

# Function to display a question
def display_question(item):
    question = item["question"]
    correct_answer = item["answer"]
    options = item["options"]
    correct_option = item.get("correct_option", "")

    # Display question with better styling
    st.markdown('<div class="question-card">', unsafe_allow_html=True)
    st.subheader(f"Question {st.session_state.current_question + 1}")
    st.markdown(f"**{question}**")
    st.markdown('</div>', unsafe_allow_html=True)

    # Display options
    option_letters = ["A", "B", "C", "D"]
    option_dict = {}

    # Map options to letters
    for j, opt in enumerate(options[:4]):
        letter = option_letters[j]
        # Get the value of the first (and only) key in the option dictionary
        option_text = list(opt.values())[0]
        option_dict[letter] = option_text

    # Create answer section
    if not st.session_state.answered:
        for letter in option_letters:
            if letter in option_dict:
                st.markdown(f'<div class="option-container spaced-option">', unsafe_allow_html=True)
                if st.button(f"{letter}) {option_dict[letter]}", key=f"btn_{letter}_{st.session_state.current_question}"):
                    check_answer(letter, correct_option, correct_answer, option_dict)
                    st.session_state.answered = True
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        # After answering, show the options with feedback
        for letter in option_letters:
            if letter in option_dict:
                # Determine button color and feedback
                if st.session_state.user_answer == letter:
                    if letter == correct_option:
                        st.success(f"{letter}) {option_dict[letter]}")
                        st.markdown(f'<div class="correct-answer" style="gap:5px; padding: 0px 10px" >✅ Correct! Answer: {correct_answer}</div>', unsafe_allow_html=True)
                    else:
                        st.error(f"{letter}) {option_dict[letter]}")
                        st.markdown(f'<div class="incorrect-answer">❌ Incorrect. The correct answer is: {correct_answer}</div>', unsafe_allow_html=True)
                elif letter == correct_option:
                    st.success(f"{letter}) {option_dict[letter]}")
                else:
                    st.info(f"{letter}) {option_dict[letter]}")

        # Show explanation if available
        if "explanation" in item:
            with st.expander("Explanation"):
                st.write(item["explanation"])

        # Show memory aid for the answer
        memory_aid = create_memory_aid(question, correct_answer)
        st.markdown(f'<div class="memory-tip">💡 <b>Memory Tip:</b> {memory_aid}</div>', unsafe_allow_html=True)

        # Show next question button
        if st.button("Next Question ➡️", key="next_btn"):
            question_time = time.time() - st.session_state.start_time
            st.session_state.question_times.append(question_time)
            st.session_state.start_time = time.time()
            st.session_state.current_question += 1
            st.session_state.answered = False
            st.rerun()

# Function to check the answer
def check_answer(user_answer, correct_letter, correct_answer, option_dict):
    st.session_state.answered = True
    st.session_state.user_answer = user_answer

    if user_answer == correct_letter:
        st.session_state.correct_count += 1
        st.balloons()  # Visual reward for correct answer
        st.success("✓ Correct! Well done! 🎉")
    else:
        if correct_letter:
            st.error(f"✗ Not quite. The correct answer is {correct_letter}) {option_dict[correct_letter]}")
        else:
            st.error(f"✗ Not quite. The correct answer is: {correct_answer}")

    # Show the full answer for educational purposes
    with st.expander("Learn More About This Answer"):
        st.write(correct_answer)

        # Add visual spacing
        st.write("")

        # Add a visualization or diagram placeholder
        st.markdown("**Visualization helps with memory retention:**")
        st.markdown("Try to visualize this concept or create a mental image to help you remember.")

# Function to display results
def show_results():
    score_percentage = (st.session_state.correct_count / st.session_state.total_questions) * 100
    avg_time = sum(st.session_state.question_times) / len(st.session_state.question_times) if st.session_state.question_times else 0

    st.markdown('<div class="result-container">', unsafe_allow_html=True)
    st.title("🏆 Quiz Completed!")

    # Create a metrics display
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Questions", st.session_state.total_questions)
    col2.metric("Correct Answers", st.session_state.correct_count)
    col3.metric("Score", f"{score_percentage:.1f}%")

    # Show average time per question
    st.metric("Average Time per Question", f"{avg_time:.1f} seconds")

    # Based on score, show different messages
    if score_percentage >= 90:
        st.balloons()
        st.markdown('<p class="feedback-text">🌟 Outstanding! You have excellent knowledge!</p>', unsafe_allow_html=True)
    elif score_percentage >= 70:
        st.markdown('<p class="feedback-text">👏 Great job! You have good understanding!</p>', unsafe_allow_html=True)
    elif score_percentage >= 50:
        st.markdown('<p class="feedback-text">👍 Good effort! Keep practicing to improve!</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="feedback-text">🔄 You might need more practice. Keep going!</p>', unsafe_allow_html=True)

    # Show a visualization of results
    chart_data = pd.DataFrame({
        'Category': ['Correct', 'Incorrect'],
        'Count': [st.session_state.correct_count, st.session_state.total_questions - st.session_state.correct_count]
    })

    st.markdown("### Your Performance")
    st.bar_chart(chart_data.set_index('Category'))

    # Learning tips based on performance
    st.markdown("### Learning Tips")
    if score_percentage < 70:
        st.markdown("""
        - Review the questions you got wrong
        - Create flashcards for difficult concepts
        - Try learning in smaller chunks
        - Practice regularly for better retention
        """)
    else:
        st.markdown("""
        - Great job! To maintain your knowledge:
        - Review periodically
        - Try teaching someone else what you've learned
        - Connect these concepts to real-world examples
        """)

    # Show a restart button
    if st.button("Restart Quiz 🔄"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# Function to display home page
def display_home(data=None):
    st.markdown('<div class="heading-container fade-in">', unsafe_allow_html=True)
    st.title("Welcome to TNPSC Quiz App! 📚")
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="question-card fade-in">
        <h3>🧠 Quiz Mode</h3>
        <p>Test your knowledge with interactive questions and get instant feedback.</p>
        <ul>
            <li>Multiple choice questions</li>
            <li>Detailed explanations</li>
            <li>Progress tracking</li>
            <li>Performance analytics</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

        # Only enable button if data is loaded
        if data is not None:
            if st.button("Start Quiz", key="start_quiz"):
                st.session_state.mode = "quiz"
                st.rerun()
        else:
            st.button("Start Quiz", key="start_quiz", disabled=True)
            st.caption("Please upload a quiz file to enable")

    with col2:
        st.markdown("""
        <div class="question-card fade-in">
        <h3>📇 Flashcards</h3>
        <p>Study with digital flashcards using spaced repetition techniques.</p>
        <ul>
            <li>Interactive flashcards</li>
            <li>Memory enhancement tips</li>
            <li>Mastery tracking</li>
            <li>Exportable progress</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

        # Only enable button if data is loaded
        if data is not None:
            if st.button("Study Flashcards", key="start_flashcards"):
                st.session_state.mode = "flashcards"
                st.rerun()
        else:
            st.button("Study Flashcards", key="start_flashcards", disabled=True)
            st.caption("Please upload a quiz file to enable")

    st.markdown("""
    <div class="question-card fade-in">
    <h3>Benefits of Using This Quiz App:</h3>
    <ul>
        <li>Spaced repetition learning for better memory retention</li>
        <li>Custom memory tips for each question</li>
        <li>Visual learning aids to improve understanding</li>
        <li>Performance analytics to track your progress</li>
        <li>Personalized learning recommendations</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    # Show instructions if no file is uploaded
    if data is None:
        st.write("Please upload your quiz JSON file in the sidebar to start.")

        # Show an example of the expected JSON format
        with st.expander("Expected JSON Format"):
            example = [
                {
                    "lesson_name": "Sample Lesson",
                    "unit": "Unit I: Sample",
                    "pairs": [
                        {
                            "question": "Sample question?",
                            "answer": "Sample answer",
                            "options": [
                                {"A": "Option A"},
                                {"B": "Option B"},
                                {"C": "Option C"},
                                {"D": "Option D"}
                            ],
                            "correct_option": "A",
                            "explanation": "Explanation for the answer",
                            "syllabus_area": "Sample area"
                        }
                    ]
                }
            ]
            st.code(json.dumps(example, indent=2, ensure_ascii=False), language="json")

# Main function to run the app
def main():
    # Load custom CSS
    load_css()

    # Create a sidebar for settings
    st.sidebar.title("Quiz Settings")

    # File uploader in sidebar for JSON file
    uploaded_file = st.sidebar.file_uploader("Upload Quiz JSON file", type="json")

    # Navigation menu in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Navigation")

    # Initialize session state for mode
    if 'mode' not in st.session_state:
        st.session_state.mode = "home"

    # Navigation buttons
    if st.sidebar.button("Home 🏠", key="nav_home"):
        st.session_state.mode = "home"
        st.rerun()

    if st.sidebar.button("Quiz Mode 📝", key="nav_quiz"):
        if uploaded_file is not None:
            st.session_state.mode = "quiz"
            st.rerun()
        else:
            st.sidebar.warning("Please upload a JSON file first.")

    if st.sidebar.button("Flashcards 📇", key="nav_flashcards"):
        if uploaded_file is not None:
            st.session_state.mode = "flashcards"
            st.rerun()
        else:
            st.sidebar.warning("Please upload a JSON file first.")

    # Learning tips in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Learning Tips")
    st.sidebar.info("""
    - Study in a quiet environment
    - Take short breaks between study sessions
    - Use spaced repetition techniques
    - Connect new knowledge with what you already know
    """)

    if uploaded_file is not None:
        try:
            # Load and shuffle the quiz data
            data = json.load(uploaded_file)
            random.shuffle(data)

            # Extract all question pairs for counting
            all_pairs = []
            for lesson in data:
                all_pairs.extend(lesson.get("pairs", []))

            # Number of questions slider
            total_available = len(all_pairs)
            num_questions = st.sidebar.slider(
                "Number of questions to practice",
                min_value=1,
                max_value=total_available,
                value=min(10, total_available),
                step=1
            )

            # Add quiz timer option
            timed_quiz = st.sidebar.checkbox("Enable timed quiz", value=False)
            if timed_quiz:
                time_per_question = st.sidebar.slider(
                    "Seconds per question",
                    min_value=10,
                    max_value=120,
                    value=30,
                    step=5
                )
                st.session_state.time_per_question = time_per_question

            # Add difficulty options
            difficulty = st.sidebar.selectbox(
                "Difficulty",
                ["All", "Easy", "Medium", "Hard"],
                index=0
            )

            # Mode routing
            if st.session_state.mode == "quiz":
                run_quiz(data, num_questions)
            elif st.session_state.mode == "flashcards":
                # Create flashcards from quiz data
                flashcards = create_flashcards(data)
                display_flashcards(flashcards)
            else:  # Home mode
                display_home(data)

        except json.JSONDecodeError:
            st.error("Error: Invalid JSON format in the uploaded file.")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        # Display home screen
        display_home()

# Run the app
if __name__ == "__main__":
    main()
