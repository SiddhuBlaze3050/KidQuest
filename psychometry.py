# psychometry.py - Assessment Engine Module (FIXED)
import requests
import json
import time
import random
import traceback
import re
from collections import defaultdict

class AssessmentEngine:
    def __init__(self):
        self.scores = defaultdict(lambda: {"score": 0, "total": 0})  # For standard-type categories
        self.personality_counts = defaultdict(int)                  # e.g., personality_creative
        self.interest_tags = defaultdict(int)                       # e.g., interest_sports
        self.responses = []                                         # Stores all question/answers

    def update_scores(self, question, selected_option):
        category = question["category"].strip().lower()
        qtype = question["type"].strip().lower()
        correct = question.get("correct_answer")

        # --- FIXED: Handle personality questions properly
        if category.startswith("personality_"):
            # For personality questions, we count the selected option, not correctness
            # Map the selected option to personality traits
            self._count_personality_response(question, selected_option)
        elif category.startswith("interest_"):
            # For interest questions, we also count the selected option
            self._count_interest_response(question, selected_option)

        # --- Score standard cognitive categories (concentration, memory, etc.)
        if qtype == "standard":
            self.scores[category]["total"] += 1
            if selected_option == correct:
                self.scores[category]["score"] += 1

        # --- Log every response
        self.responses.append({
            "question": question["question"],
            "selected_option": selected_option,
            "category": category,
            "type": qtype
        })

    def _count_personality_response(self, question, selected_option):
        """Count personality responses based on what the user selected"""
        # Map options to personality types based on the question design
        option_text = question["options"].get(selected_option, "").lower()
        
        # Define keywords that indicate different personality types
        creative_keywords = ["creative", "new ideas", "imagine", "stories", "art", "draw", "paint", "craft", "unique"]
        analytical_keywords = ["analyze", "plan", "organize", "instructions", "carefully", "figure out", "solve", "think", "step by step", "logical"]
        social_keywords = ["friends", "people", "talk", "party", "group", "together", "help others", "share", "included", "everyone"]
        practical_keywords = ["build", "create", "hands-on", "try", "do", "make", "practical", "real", "fix", "tasks", "efficient"]
        
        # Count based on option text content
        if any(keyword in option_text for keyword in creative_keywords):
            self.personality_counts["personality_creative"] += 1
        elif any(keyword in option_text for keyword in analytical_keywords):
            self.personality_counts["personality_analytical"] += 1
        elif any(keyword in option_text for keyword in social_keywords):
            self.personality_counts["personality_social"] += 1
        elif any(keyword in option_text for keyword in practical_keywords):
            self.personality_counts["personality_practical"] += 1
        else:
            # Fallback: use the "correct_answer" mapping for personality questions
            if hasattr(question, 'personality_mapping'):
                personality_type = question['personality_mapping'].get(selected_option)
                if personality_type:
                    self.personality_counts[f"personality_{personality_type}"] += 1
            else:
                # Last resort: increment the category specified in the question
                category = question["category"].strip().lower()
                if category.startswith("personality_"):
                    self.personality_counts[category] += 1

    def _count_interest_response(self, question, selected_option):
        """Count interest responses based on what the user selected"""
        option_text = question["options"].get(selected_option, "").lower()
        
        # Define keywords for different interests
        sports_keywords = ["sports", "soccer", "basketball", "running", "exercise", "game", "play", "team", "drills"]
        arts_keywords = ["art", "paint", "draw", "music", "dance", "creative", "museum", "craft", "sculptures", "film", "mural"]
        technology_keywords = ["robot", "computer", "coding", "technology", "science", "build", "program", "app", "smartphone"]
        nature_keywords = ["nature", "forest", "animals", "outdoors", "camping", "plants", "environment", "birds", "bugs", "garden", "hiking"]
        
        # Count based on option content
        if any(keyword in option_text for keyword in sports_keywords):
            self.interest_tags["interest_sports"] += 1
        elif any(keyword in option_text for keyword in arts_keywords):
            self.interest_tags["interest_arts"] += 1
        elif any(keyword in option_text for keyword in technology_keywords):
            self.interest_tags["interest_technology"] += 1
        elif any(keyword in option_text for keyword in nature_keywords):
            self.interest_tags["interest_nature"] += 1
        else:
            # Fallback: use the category from the question
            category = question["category"].strip().lower()
            if category.startswith("interest_"):
                self.interest_tags[category] += 1

    def get_assessment_results(self):
        results = {}

        # 1. Standard scoring (learning style, concentration, memory)
        for category, stats in self.scores.items():
            if stats["total"] == 0:
                results[category] = 0
            else:
                results[category] = round((stats["score"] / stats["total"]) * 100)

        # 2. Dominant Learning Style
        learning_categories = ["visual_learning", "auditory_learning", "kinesthetic_learning"]
        learning_scores = {
            cat.replace("_learning", ""): self.scores.get(cat, {}).get("score", 0)
            for cat in learning_categories
        }
        if any(learning_scores.values()):
            results["dominant_learning_style"] = max(learning_scores, key=learning_scores.get).capitalize()
        else:
            results["dominant_learning_style"] = "Balanced"

        # 3. FIXED: Dominant Personality
        print(f"DEBUG: Personality counts: {dict(self.personality_counts)}")  # Debug output
        if self.personality_counts:
            dominant_personality = max(self.personality_counts, key=self.personality_counts.get)
            results["dominant_personality"] = dominant_personality.replace("personality_", "").capitalize()
        else:
            results["dominant_personality"] = "Could not determine"

        # 4. FIXED: Top Interest  
        print(f"DEBUG: Interest counts: {dict(self.interest_tags)}")  # Debug output
        if self.interest_tags:
            top_interest = max(self.interest_tags, key=self.interest_tags.get)
            results["top_interest"] = top_interest.replace("interest_", "").capitalize()
        else:
            results["top_interest"] = "Not identified"

        return results

class QuestionGenerator:
    def __init__(self, api_key, api_url):
        self.api_key = api_key
        self.api_url = api_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
    def generate_complete_test(self):
        """Generate all test questions at once using AI"""
        try:
            prompt = """You are a child psychologist designing a playful, scientifically grounded assessment test for children aged 8–14. Create exactly 20 questions to evaluate the following:

            1. Learning Style (Visual, Auditory, Kinesthetic) – 4 questions  
            2. Interests (Sports, Arts, Technology, Nature) – 4 questions  
            3. Personality Type (Creative, Analytical, Social, Practical) – 5 questions  
            4. Concentration Skills – 4 questions  
            5. Memory Skills – 3 question  

            IMPORTANT FORMATTING RULES:
            - Personality and Interest questions should have Type: preference (no single correct answer)
            - Learning style questions should have Type: preference  
            - Concentration and Memory questions should have Type: standard (with correct answers)
            
            Each question must have:
            - A fun, real-world scenario children can relate to
            - One of the following categories EXACTLY:  
            [`visual_learning`, `auditory_learning`, `kinesthetic_learning`,  
            `personality_creative`, `personality_analytical`, `personality_social`, `personality_practical`,  
            `concentration`, `memory`,  
            `interest_sports`, `interest_technology`, `interest_arts`, `interest_nature`] 
            
            Each question should be formatted EXACTLY like this (no asterisks or markdown):
            Question 1: [text]
            Category: [exact_category_from_above]
            Type: [standard/preference]
            A) [option A]
            B) [option B]
            C) [option C]
            D) [option D]
            Correct Answer: [A/B/C/D] (for preference, mark the option that reflects the category)

            
            For personality questions, make sure each option clearly represents the personality type in the category.
            For interest questions, make sure each option clearly represents different interests.For memory questions,try to give General knowledge questions that kids of this age can relate to.
            
            Avoid abstract questions. Use realistic school, hobby, and family-life scenarios. Vary your settings and verbs. Ensure all questions are unique every time.

            """

            prompt += f"\n\n[Random Seed: {random.randint(1, 10000)}]"

            payload = {
                "model": "mistralai/mistral-small-3.2-24b-instruct:free",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 2000,
                "temperature": 1.2,
                "top_p": 0.8
            }
            
            print("Generating complete assessment test with AI...")
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                response_data = response.json()
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    generated_text = response_data['choices'][0]['message']['content']
                    if generated_text:
                        questions = self.parse_complete_test(generated_text)
                        if len(questions) >= 10:  # Ensure we have enough questions
                            print(f"AI generated {len(questions)} assessment questions successfully!")
                            return questions
                        else:
                            print("AI didn't generate enough questions, using fallback...")
            else:
                print(f"OpenRouter API Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"Error generating AI questions: {e}")
        
        # Return fallback questions if AI generation fails
        print("Using fallback assessment questions...")
        return self.get_fallback_questions()
    
    def parse_complete_test(self, generated_text):
        """Parse the complete generated test into structured format"""
        questions = []
        current_question = {}
        option_letters = {"A", "B", "C", "D"}
        
        print("DEBUG: Starting to parse AI generated text...")
        print(f"DEBUG: Generated text length: {len(generated_text)}")

        try:
            # Clean up the text first - remove all markdown formatting
            clean_text = re.sub(r'\*+', '', generated_text)  # Remove asterisks
            clean_text = re.sub(r'`+', '', clean_text)       # Remove backticks
            
            # Split by lines and clean up
            lines = []
            for line in clean_text.strip().split('\n'):
                cleaned_line = line.strip()
                if cleaned_line and not cleaned_line.startswith('---'):  # Skip separator lines
                    lines.append(cleaned_line)
            
            print(f"DEBUG: Processing {len(lines)} non-empty lines")
            
            for i, line in enumerate(lines):
                print(f"DEBUG: Line {i}: {line}")
                
                # Match question patterns more flexibly
                question_match = re.match(r'^Question\s*\d*\s*:', line, re.IGNORECASE)
                if question_match:
                    # Save previous question if valid
                    if current_question and self.is_valid_question(current_question):
                        questions.append(current_question.copy())
                        print(f"DEBUG: Added valid question: {current_question.get('question', '')[:50]}...")
                    
                    # Start new question
                    current_question = {"options": {}}
                    # Extract question text after the colon
                    question_text = line.split(":", 1)[1].strip() if ":" in line else line
                    current_question["question"] = question_text
                    print(f"DEBUG: Started new question: {question_text[:50]}...")

                elif line.startswith("Category:"):
                    # Extract category, handle various formats
                    cat_text = line.replace("Category:", "").strip()
                    # Remove any remaining formatting
                    cat_text = re.sub(r'[\[\]`\(\)\*]', '', cat_text).strip()
                    # If it's a list format, take the first item
                    if ',' in cat_text:
                        cat_text = cat_text.split(',')[0].strip()
                    current_question["category"] = cat_text
                    print(f"DEBUG: Set category: {cat_text}")

                elif line.startswith("Type:"):
                    qtype = line.replace("Type:", "").strip().lower()
                    # Remove any formatting
                    qtype = re.sub(r'[\[\]`\(\)\*]', '', qtype).strip()
                    current_question["type"] = qtype
                    print(f"DEBUG: Set type: {qtype}")

                elif re.match(r'^[A-D]\)', line):
                    # Extract option
                    option_letter = line[0].upper()
                    option_text = line[2:].strip()
                    if option_letter in option_letters and option_text:
                        current_question["options"][option_letter] = option_text
                        print(f"DEBUG: Added option {option_letter}: {option_text[:30]}...")

                elif re.match(r"Correct Answer\s*:?", line, re.IGNORECASE):
                    # Extract answer
                    answer_text = re.sub(r"^Correct Answer\s*:?", "", line, flags=re.IGNORECASE).strip()
                    if "N/A" in answer_text.upper() or "NONE" in answer_text.upper():
                        current_question["correct_answer"] = "N/A"
                    else:
                        answer_match = re.search(r'([A-D])', answer_text.upper())
                        if answer_match:
                            correct_answer = answer_match.group(1)
                            current_question["correct_answer"] = correct_answer
                        else:
                            # If no valid answer found, set to N/A for preference questions
                            current_question["correct_answer"] = "N/A"
                    print(f"DEBUG: Set correct answer: {current_question.get('correct_answer', 'None')}")

            # Don't forget the last question
            if current_question and self.is_valid_question(current_question):
                questions.append(current_question)
                print(f"DEBUG: Added final question: {current_question.get('question', '')[:50]}...")

        except Exception as e:
            print(f"ERROR: Exception during parsing: {e}")
            print(f"ERROR: Traceback: {traceback.format_exc()}")

        print(f"DEBUG: Successfully parsed {len(questions)} questions")
        
        if len(questions) < 10:
            print("WARNING: AI output could not be parsed into enough questions.")
            print("DEBUG: Raw AI output:")
            print(generated_text)
            print("DEBUG: Parsed questions so far:")
            for i, q in enumerate(questions):
                print(f"Question {i+1}: {q}")

        return questions
    
    def is_valid_question(self, question):
        """Validate if a question has all required fields"""
        required_fields = ["question", "options", "correct_answer", "category", "type"]
        valid_categories = [
            'visual_learning', 'auditory_learning', 'kinesthetic_learning', 'concentration', 'memory',
            'personality_creative', 'personality_analytical', 'personality_social', 'personality_practical',
            'interest_sports', 'interest_technology', 'interest_arts', 'interest_nature'
        ]
        
        # Check all required fields exist
        for field in required_fields:
            if field not in question:
                print(f"DEBUG: Question missing field: {field}")
                return False
        
        # Check we have 4 options
        if len(question.get("options", {})) != 4:
            print(f"DEBUG: Question has {len(question.get('options', {}))} options, need 4")
            return False
        
        # Check correct answer is valid (allow N/A for preference questions)
        correct_answer = question.get("correct_answer")
        qtype = question.get("type", "").lower()
        
        if qtype == "preference":
            # For preference questions, correct_answer can be N/A or any valid option
            if correct_answer not in ["N/A", "A", "B", "C", "D"]:
                print(f"DEBUG: Invalid correct answer for preference question: {correct_answer}")
                return False
        else:
            # For standard questions, correct answer must be in options
            if correct_answer not in question.get("options", {}):
                print(f"DEBUG: Correct answer '{correct_answer}' not in options")
                return False
        
        # Check category is valid
        if question.get("category") not in valid_categories:
            print(f"DEBUG: Invalid category: {question.get('category')}")
            return False
            
        # Check type is valid
        if question.get("type") not in ["standard", "preference"]:
            print(f"DEBUG: Invalid type: {question.get('type')}")
            return False
        
        return True
    
    def get_fallback_questions(self):
        """FIXED: Fallback questions with proper personality mapping"""
        return [
            # Learning Style (Visual, Auditory, Kinesthetic) – 4 questions
           {
            "question": "You need to remember a list of groceries. What do you do?",
            "options": {
                "A": "Draw a picture of each item",
                "B": "Say the list out loud repeatedly",
                "C": "Act out picking up each item",
                "D": "Write the list in your notebook"
            },
            "correct_answer": "A",
            "category": "visual_learning",
            "type": "preference"
            },
            {
            "question": "How do you prefer to learn a new dance?",
            "options": {
                "A": "Watch a video of the dance",
                "B": "Listen to instructions",
                "C": "Try the moves yourself",
                "D": "Read about the steps"
            },
            "correct_answer": "C",
            "category": "kinesthetic_learning",
            "type": "preference"
            },
            {
            "question": "What helps you best when studying for a test?",
            "options": {
                "A": "Color-coded notes and charts",
                "B": "Explaining the topic aloud",
                "C": "Walking while memorizing",
                "D": "Taking practice quizzes"
            },
            "correct_answer": "A",
            "category": "visual_learning",
            "type": "preference"
            },
            {
            "question": "Your teacher tells a story in class. What do you enjoy most?",
            "options": {
                "A": "Watching the teacher act it out",
                "B": "Listening to the story being told",
                "C": "Acting it out with classmates",
                "D": "Drawing what happens in the story"
            },
            "correct_answer": "B",
            "category": "auditory_learning",
            "type": "preference"
            },
            # Personality Type (Creative, Analytical, Social, Practical) – 5 questions
            {
                "question": "When working on a group project, you like to:",
                "options": {
                    "A": "Come up with new ideas",
                    "B": "Organize and plan everything",
                    "C": "Make sure everyone gets along",
                    "D": "Build or create the final product"
                },
                "correct_answer": "A",
                "category": "personality_creative",
                "type": "preference"
            },
            {
                "question": "You are given a puzzle to solve. What is your first step?",
                "options": {
                    "A": "Think of creative solutions",
                    "B": "Analyze the pieces carefully",
                    "C": "Ask friends for help",
                    "D": "Start putting pieces together right away"
                },
                "correct_answer": "B",
                "category": "personality_analytical",
                "type": "preference"
            },
            {
                "question": "At a party, you are most likely to:",
                "options": {
                    "A": "Tell stories or jokes",
                    "B": "Help organize games",
                    "C": "Talk to as many people as possible",
                    "D": "Set up decorations"
                },
                "correct_answer": "C",
                "category": "personality_social",
                "type": "preference"
            },
            {
                "question": "When you get a new toy or gadget, you:",
                "options": {
                    "A": "Imagine new ways to use it",
                    "B": "Read the instructions carefully",
                    "C": "Show it to your friends",
                    "D": "Figure out how it works by trying it"
                },
                "correct_answer": "D",
                "category": "personality_practical",
                "type": "preference"
            },
            {
                "question": "Your teacher asks you to decorate the classroom. You:",
                "options": {
                    "A": "Draw colorful posters",
                    "B": "Plan where everything should go",
                    "C": "Invite classmates to help",
                    "D": "Hang up decorations and arrange desks"
                },
                "correct_answer": "A",
                "category": "personality_creative",
                "type": "preference"
            },

            # Interests (Sports, Arts, Technology, Nature) – 4 questions
            {
            "question": "Which activity sounds most fun to you?",
            "options": {
                "A": "Playing soccer with friends",
                "B": "Painting a colorful picture",
                "C": "Building a robot",
                "D": "Exploring a forest"
            },
            "correct_answer": "A",
            "category": "interest_sports",
            "type": "preference"
            },
            {
            "question": "If you could spend a whole day doing anything, what would you choose?",
            "options": {
                "A": "Visiting an art museum",
                "B": "Coding a new game",
                "C": "Having a picnic in the park",
                "D": "Hosting a party with friends"
            },
            "correct_answer": "B",
            "category": "interest_technology",
            "type": "preference"
            },
            {
            "question": "Which club would you join at school?",
            "options": {
                "A": "Drama or art club",
                "B": "Science or robotics club",
                "C": "Nature explorers club",
                "D": "Student council"
            },
            "correct_answer": "A",
            "category": "interest_arts",
            "type": "preference"
            },
            {
            "question": "What would you do on a school field trip?",
            "options": {
                "A": "Play sports in the open",
                "B": "Draw pictures of nature",
                "C": "Look at plants and insects",
                "D": "Take notes on the environment"
            },
            "correct_answer": "C",
            "category": "interest_nature",
            "type": "preference"
            },

            # Concentration Skills – 4 questions
            {
            "question": "Which number is missing? 3, 6, 9, __, 15",
            "options": {
                "A": "10",
                "B": "11",
                "C": "12",
                "D": "13"
            },
            "correct_answer": "C",
            "category": "concentration",
            "type": "standard"
            },
            {
            "question": "Find the odd one out: apple, banana, carrot, grape",
            "options": {
                "A": "apple",
                "B": "banana",
                "C": "carrot",
                "D": "grape"
            },
            "correct_answer": "C",
            "category": "concentration",
            "type": "standard"
            },
            {
            "question": "Which shape is different: circle, square, triangle, apple",
            "options": {
                "A": "circle",
                "B": "square",
                "C": "triangle",
                "D": "apple"
            },
            "correct_answer": "D",
            "category": "concentration",
            "type": "standard"
            },
            {
            "question": "Which direction is opposite of East?",
            "options": {
                "A": "North",
                "B": "West",
                "C": "South",
                "D": "East"
            },
            "correct_answer": "B",
            "category": "concentration",
            "type": "standard"
            },

            # Memory Skills – 3 questions
        {
        "question": "You just saw a picture with the Eiffel Tower, Taj Mahal, and Great Wall of China. Which monument is in India?",
        "options": {
            "A": "Eiffel Tower",
            "B": "Taj Mahal",
            "C": "Great Wall of China",
            "D": "Leaning Tower of Pisa"
        },
        "correct_answer": "B",
        "category": "memory",
        "type": "standard"
        },
        {
        "question": "Your teacher said: The Earth orbits the Sun, plants make food through photosynthesis, and water boils at 100°C. What is the boiling point of water?",
        "options": {
            "A": "50°C",
            "B": "90°C",
            "C": "100°C",
            "D": "120°C"
        },
        "correct_answer": "C",
        "category": "memory",
        "type": "standard"
        },
        {
            "question": "You read this in a book: Mahatma Gandhi led India's freedom movement, the telephone was invented by Alexander Graham Bell, and Neil Armstrong was the first person on the moon. Who invented the telephone?",
            "options": {
                "A": "Thomas Edison",
                "B": "Alexander Graham Bell",
                "C": "Isaac Newton",
                "D": "Albert Einstein"
            },
            "correct_answer": "B",
            "category": "memory",
            "type": "standard"
        }   
        ]
    
    def generate_feedback(self, assessment_results):
        """Generate personalized feedback using AI"""
        try:
            learning_style = assessment_results['learning_style']
            personality_type = assessment_results['personality_type']
            concentration = assessment_results['concentration_level']
            memory = assessment_results['memory_strength']
            top_interest = assessment_results.get('top_interest', 'Not identified')

            prompt = f"""Create a personalized, encouraging feedback report for a child (age 8-14) based on their assessment results:

    Learning Style: {learning_style}
    Personality Type: {personality_type}
    Top Interest: {top_interest}
    Concentration Level: {concentration}%
    Memory Strength: {memory}%

    The feedback should:
    1. Explain what their learning style means in simple terms
    3. Give practical tips for studying and learning
    4. Highlight their personality strengths
    5. Mention their top interest and suggest related activities
    6. Provide suggestions for improvement areas (concentration, memory)
    7. Be written in a friendly, age-appropriate tone
    8. Be around 100-150 words,no need of high spacing or line breaks,no more than 15 lines in total
    9. Return the entire response in HTML format (with <h3>, <ul>, <li>, <p>, or <b> tags as appropriate,do not use the tag <html>)

    Make it personal and actionable for the child and their parents.Try not to use the name of the child in the response.Only wishes is necessary"""

            payload = {
                "model": "mistralai/mistral-small-3.2-24b-instruct:free",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 500,
                "temperature": 1.0,
                "top_p": 0.8
            }

            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=30)

            if response.status_code == 200:
                response_data = response.json()
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    feedback = response_data['choices'][0]['message']['content']
                    if feedback:
                        return feedback.strip()

        except Exception as e:
            print(f"Error generating AI feedback: {e}")

        # Fallback feedback
        return self.get_fallback_feedback(assessment_results)

    
    def get_fallback_feedback(self, results):
        """Generate fallback feedback if AI fails"""
        learning_style = results['learning_style']
        personality_type = results['personality_type']
        concentration = results['concentration_level']
        memory = results['memory_strength']
        top_interest = results.get('top_interest', 'Not identified')

        feedback = f"""
        <h3>🌟 Great job completing your assessment! 🌟</h3>
        <p><b>Your Learning Style:</b> {learning_style}</p>
        <ul>
        """

        if "Visual" in learning_style:
            feedback += "<li>You learn best with pictures, diagrams, and colors. Try using drawings, mind maps, and flashcards when you study!</li>"
        elif "Auditory" in learning_style:
            feedback += "<li>You learn best by listening and talking. Try reading aloud, discussing topics, or making up songs to remember things!</li>"
        elif "Kinesthetic" in learning_style:
            feedback += "<li>You learn best by doing and moving. Try hands-on activities, building models, or acting things out!</li>"
        else:
            feedback += "<li>You have a balanced learning style. You can use both pictures and sounds to help you learn!</li>"

        feedback += "</ul>"

        feedback += f"<p><b>Your Personality:</b> {personality_type}</p><ul>"
        personality_descriptions = {
            'Creative': "You love to imagine and create! Try art, stories, or creative projects.",
            'Analytical': "You enjoy solving problems and figuring things out. Puzzles and science experiments are great for you.",
            'Social': "You love being with people and working in teams. Group projects and games are perfect for you.",
            'Practical': "You like real-world activities and building things. Try hands-on projects and experiments."
        }
        feedback += f"<li>{personality_descriptions.get(personality_type, 'You have a unique personality!')}</li></ul>"

        feedback += f"<p><b>Your Top Interest:</b> {top_interest}</p>"
        if top_interest != "Not identified":
            feedback += f"<ul><li>Explore more about {top_interest.lower()}! Join clubs, try new activities, or read about it.</li></ul>"

        feedback += f"<p><b>Your Skills:</b></p><ul>"
        feedback += f"<li>🎯 <b>Concentration:</b> {concentration}% - "
        if concentration >= 80:
            feedback += "Excellent focus! Keep it up!"
        elif concentration >= 60:
            feedback += "Good focus! Try taking short breaks while studying."
        else:
            feedback += "Try studying in a quiet place and take breaks every 15-20 minutes."
        feedback += "</li>"

        feedback += f"<li>🧠 <b>Memory:</b> {memory}% - "
        if memory >= 80:
            feedback += "Amazing memory skills!"
        elif memory >= 60:
            feedback += "Good memory! Repeat information to remember it better."
        else:
            feedback += "Try using stories or songs to help remember things."
        feedback += "</li></ul>"

        feedback += "<p>Keep being awesome and never stop learning! 🚀</p>"
        return feedback

class PsychometryService:
    def __init__(self, api_key, api_url):
        self.api_key = api_key
        self.api_url = api_url
        self.question_generator = QuestionGenerator(api_key, api_url)
        self.assessment_engine = None
        
    def initialize_assessment(self):
        """Initialize a new assessment session"""
        self.assessment_engine = AssessmentEngine()
        test_questions = self.question_generator.generate_complete_test()
        random.shuffle(test_questions)
        return test_questions
    
    def process_answer(self, question, selected_option):
        """Process a user's answer"""
        if self.assessment_engine is None:
            raise ValueError("Assessment not initialized")
        
        self.assessment_engine.update_scores(question, selected_option)
    
    def get_results(self):
        """Get final assessment results"""
        if self.assessment_engine is None:
            raise ValueError("Assessment not initialized")
        
        # Get raw results from assessment engine
        raw_results = self.assessment_engine.get_assessment_results()
        
        # Calculate percentages for detailed scores
        detailed_scores = {}
        for category, stats in self.assessment_engine.scores.items():
            if stats["total"] > 0:
                percentage = (stats["score"] / stats["total"]) * 100
                detailed_scores[category] = {
                    'score': stats["score"],
                    'total': stats["total"],
                    'percentage': round(percentage, 1)
                }
            else:
                detailed_scores[category] = {'score': 0, 'total': 0, 'percentage': 0}
        
        # Add personality and interest scores
        personality_scores = {
            'Creative': 0,
            'Analytical': 0,
            'Social': 0,
            'Practical': 0
        }
        
        for category, count in self.assessment_engine.personality_counts.items():
            key = category.replace("personality_", "").capitalize()
            if key in personality_scores:
                personality_scores[key] = count
        
        # Compile final results
        results = {
            'learning_style': raw_results.get('dominant_learning_style', 'Balanced'),
            'personality_type': raw_results.get('dominant_personality', 'Not identified'),
            'top_interest': raw_results.get('top_interest', 'Not identified'),
            'concentration_level': detailed_scores.get('concentration', {}).get('percentage', 0),
            'memory_strength': detailed_scores.get('memory', {}).get('percentage', 0),
            'detailed_scores': detailed_scores,
            'personality_breakdown': personality_scores
        }
        
        # Generate feedback
        feedback = self.question_generator.generate_feedback(results)
        results['feedback'] = feedback
        
        return results
    
    def get_response_summary(self):
        """Get summary of all responses"""
        if self.assessment_engine is None:
            return []
        
        return self.assessment_engine.responses