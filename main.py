import requests
import random
import html

def get_questions():
    url = "https://opentdb.com/api.php?amount=5&type=multiple"
    response = requests.get(url)
    data = response.json()
    questions = data['results']
    return questions

def run_quiz():
    score = 0
    questions = get_questions()

    for i, q in enumerate(questions):
        print(f"\nQ{i+1}: {html.unescape(q['question'])}")
        options = q['incorrect_answers'] + [q['correct_answer']]
        random.shuffle(options)

        for j, opt in enumerate(options):
            print(f"{j+1}. {html.unescape(opt)}")

        try:
            ans = int(input("Your answer (1-4): "))
            if options[ans - 1] == q['correct_answer']:
                print("Correct!")
                score += 1
            else:
                print(f"Wrong! Correct: {q['correct_answer']}")
        except:
            print("Invalid input.")

    print(f"\n Your Final Score: {score}/{len(questions)}")

run_quiz()
