<h1>Smile2Win</h1>
This is a game that's developed completely with Python, where players communicate with the game with their voice only.

<h2>Game Description</h2>
The game's idea is that a group of players sit in front of the camera, they choose a concept, and the game will ask them questions relevant to the chosen concept.  
Whenever someone answers, they get points. At the end of the game, the winners are announced.

<h2>How it works</h2>

1. The participants need to present at the game-setup phase, where they're registered as participants. They can't join after this phase is complete.
2. At the game-setup phase, they need to say their names.
3. One of the participants needs to tell the game which concept they want the questions to be about. They can specify the number of questions they want as well.
4. The game will start asking questions accordingly.
5. A participant needs to raise their hand if they want to answer the question. The first to raise their hand gets to answer first.
6. If the answer is correct, the game continues to the next question, and the player is granted points. The amount of points depends on the correctness of their answer.
7. If the answer's correctness is 50% or less, the game looks for a new answer.
8. The participant can also ask to pass, which means the game will skip the question and move to the next one.
9. Once all questions are answered or passed, the game ends by announcing a winner, or winners if there's a tie.

<h2>Services/Libraries used</h2>

1. For speech recognition, used Azure Speech Recognition cloud service.
2. For video input and webcam, used OpenCV.
3. MediaPipe was used to identify raised hands.
4. face_recognition was used to recognize and encode faces.
5. OpenAI ChatGPT 3.5-turbo to understand recognized speech and to manage the game.

<h2>Installation</h2>

1. Run the following command to install the required packages.

```
pip install -r requirements.txt
```
2. Add a .env file to the project for environment variables, you need the following variables declared:
```python
OPENAI_API_KEY= # OpenAI Key for ChatGPT.
AZURE_SPEECH_KEY= # Azure Speech Recognition
AZURE_REGION= # Azure Service Region 
```
