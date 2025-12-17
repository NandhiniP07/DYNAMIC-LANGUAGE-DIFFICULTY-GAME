# Dynamic Language Difficulty Game

## Overview
The Dynamic Language Difficulty Game is an adaptive reading comprehension system that uses **NLP techniques** to adjust text difficulty based on user performance. Players read a passage, answer a question, and receive simplified text automatically if they answer incorrectly.

---

## Approach
- **Dataset:** SQuAD (Stanford Question Answering Dataset)
- **Readability Analysis:** Flesch–Kincaid grade using `textstat`
- **Text Simplification:** Transformer-based **T5 (t5-base)** model
- **Answer Preservation:** Key answer sentences remain unchanged
- **GUI:** Interactive Tkinter-based interface

---

## Key Features
- Dynamic difficulty adjustment
- Readability feedback for each passage
- Automatic text simplification on wrong answers
- Progress tracking with multiple rounds

---

## Conclusion
This project demonstrates how **readability analysis and transformer-based text simplification** can be combined to create an adaptive, personalized learning experience that improves reading comprehension through interactive feedback.

---

## Author
**Nandhini P**
