import time
from intellegent_bot import parse_concept_from_text, check_correct_answer
import random

class GamePlay:
    def __init__(self, core) -> None:
        self.__core = core
        self.__current_question = 0
        self.__questions_list = []
        self.__speaker_participant = None

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
        self.__announce_winner()


    def __ask_concept(self):
        self.__core.set_bot_text("Concept", "Suggest a concept for the game, including number of questions if you want.")

        self.__core.show_icon(1, True)
        self.__core.recognize_speech()
        res = ""
        self.__core.insert_player_text("\nConcept suggestion:\n")
        while not self.__core.recognizing_finished():
            time.sleep(0.5)
            res = self.__core.recognized_text()

            # Update the GUI to display the player's text.
            if res:
                self.__core.insert_player_text(res, True)

        # Once listening is done, update the text with the interpreted speech. 
        res = self.__core.recognized_text()
        self.__core.show_icon(1, False)

        # Now, give the recognized text to intellegent boy.
        response = parse_concept_from_text(res)
        if not response:
            # here we need to try again
            self.__core.set_bot_text("Concept", "Sorry, can you try again?")
            time.sleep(2)
            self.__core.insert_player_text("\n\n")
            self.__ask_concept()
        else:
            # we have questions, lets parse them.
            self.__questions_list = response
            self.__core.set_bot_text("Concept", "Cool, let's get started.")

    def __ask_questions(self):
        while self.__current_question < len(self.__questions_list):
            question = self.__questions_list[self.__current_question]
            self.__core.set_bot_text(f"Question {self.__current_question+1}", question)

            # Wait 2 seconds before inspecting hands
            time.sleep(2)

            self.__core.show_icon(1, True, False)
            # Inspect hands.
            raising_hands = []
            while not raising_hands:
                # This is a list of participants (Participant instance)
                raising_hands = self.__core.inspect_participants_hands()
                time.sleep(0.2)
                
            # toggle of hands icon
            self.__core.show_icon(1, False, False)
            # We got participants raising hands, lets choose one randomly.
            chosen_participant = random.choice(raising_hands)
            self.__speaker_participant = chosen_participant
            self.__generate_cards_data()

            # Now, we need an answer
            res = ""
            self.__core.show_icon(1, True)
            self.__core.recognize_speech()
            self.__core.insert_player_text(f"\n\n{chosen_participant.get_name()}:\n")
            while not self.__core.recognizing_finished():
                time.sleep(0.5)
                res = self.__core.recognized_text()
                if res:
                    self.__core.insert_player_text(res, True)

            # Hide mic icon
            self.__core.show_icon(1, False)
            # Toggle of speaker participant.
            self.__speaker_participant = None
            self.__generate_cards_data()
            
            # Get response after interpreting.
            res = self.__core.recognized_text()

            # Now, check answer correctness.
            correctness = check_correct_answer(question, res)

            if correctness == -1: # means we are passing
                self.__core.set_bot_text(f"Question {self.__current_question+1}", "Pass. Moving to next one.")
                self.__current_question += 1
                time.sleep(2.5)

            elif correctness <= 5: # bad answer is equal or less than 5/10
                self.__core.set_bot_text(f"Question {self.__current_question+1}", "Good try, question still not answered.")

                # We loop again to ask the same question.
            else:
                # Good answer
                self.__core.set_bot_text(f"Question {self.__current_question+1}", f"Good answer {chosen_participant.get_name()}, {correctness}/10.")
                
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
            is_speaker = p == self.__speaker_participant
            card = (p.get_picture(), p.get_name(), p.get_points(), is_speaker)
            cards_data.append(card)

        sorted_cards = sorted(cards_data, key=lambda x: x[2], reverse=True)
        self.__core.update_participants_cards(sorted_cards)

    def __get_winners(self):
        participants = self.__core.get_all_participants()

        highest_scorer = max(participants, key=lambda p: p.get_points())
        winners = [p.get_name() for p in participants if p.get_points() == highest_scorer.get_points()]
        return winners
        
    def __announce_winner(self):
        winner_names = self.__get_winners()
        if len(winner_names) == 1:
            self.__core.set_bot_text("Winner", f"The game has ended, and the winner is:\n{winner_names[0]}")
        else:
            self.__core.set_bot_text("Winner", f"The game has ended, with a tie, winners are:\n{", ".join(winner_names)}")
            
