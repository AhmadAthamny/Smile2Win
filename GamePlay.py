import time
from intellegent_bot import parse_concept_from_text, check_correct_answer
import re
import random

class GamePlay:
    def __init__(self, core) -> None:
        self.__core = core
        self.__current_question = 0
        self.__questions_list = []

    def start_game(self):
        # We need the cards to be up-to-date.
        self.__generate_cards_data()

        # We first need to specify the concept and generate questions.
        self.__ask_concept()

        # Wait 3 seconds after getting the concept.
        time.sleep(3)

        # Ask questions.
        self.__ask_questions()

        # Ending game
        winner_name = self.__get_winner_name()
        self.__set_bot_text(f"The game has ended, and the winner is:\n{winner_name}")


    def __ask_concept(self):
        self.__core.recognize_speech()

        res = ""
        self.__core.insert_player_text("\n\n")
        while not self.__core.recognizing_finished():
            time.sleep(0.5)
            res = self.__core.recognized_text().replace(res, "")

            # Update the GUI to display the player's text.
            self.__core.insert_player_text(res)

        # Once listening is done, update the text with the interpreted speech. 
        res = self.__core.recognized_text()

        # Now, give the recognized text to intellegent boy.
        response = parse_concept_from_text(res)
        if not response:
            # here we need to try again
            self.__ask_concept()
            self.__core.set_bot_text("Please say the concept you want, again.")
        else:
            # we have questions, lets parse them.
            pattern = r"\d+- (.+?)\n"
            self.__questions_list = re.findall(pattern, response)
            self.__core.set_bot_text("Cool, let's get started.")

    def __ask_questions(self):
        while self.__current_question < len(self.__questions_list):
            question = self.__questions_list[self.__current_question]
            self.__core.set_bot_text(question)

            # Wait 2 seconds before inspecting hands
            time.sleep(2)

            # Inspect hands.
            raising_hands = []
            while not raising_hands:
                # This is a list of participants (Participant instance)
                raising_hands = self.__core.inspect_participants_hands()
                time.sleep(0.2)
            
            # We got participants raising hands, lets choose one randomly.
            chosen_participant = random.choice(raising_hands)

            # Now, we need an answer
            res = ""
            self.__core.recognize_speech()
            self.__core.insert_player_text(f"\n\n{chosen_participant.get_name()}:\n")
            while not self.__core.recognizing_finished():
                time.sleep(0.5)
                res = self.__core.recognized_text().replace(res, "")
                self.__core.insert_player_text(res)
            
            # Get response after interpreting.
            res = self.__core.recognized_text()

            # Now, check answer correctness.
            correctness = check_correct_answer(question, res)

            if correctness <= 5: # bad answer is equal or less than 5/10
                self.__core.set_bot_text("Good try, question still not answered.")

                # We loop again to ask the same question.
            else:
                # Good answer
                self.__core.set_bot_text(f"Good answer {chosen_participant.get_name()}, {correctness}/10.")
                
                # Give points
                chosen_participant.give_points(correctness)

                # Sort players, and update cards.
                self.__generate_cards_data()

                # Move to next question
                self.__current_question += 1
            
            # Sleep before asking same/next question.
            time.sleep(3)


    def __generate_cards_data(self):
        participants = self.__core.get_all_participants()

        cards_data = []
        for p in participants:
            card = (p.get_picture(), p.get_name(), p.get_points())
            cards_data.append(card)

        sorted_cards = sorted(cards_data, key=lambda x: x[2], reverse=True)
        self.__core.update_participants_cards(sorted_cards)

    def __get_winner_name(self):
        participants = self.__core.get_all_participants()

        winner = max(participants, key=lambda p: p.get_points())

        return winner.get_name()