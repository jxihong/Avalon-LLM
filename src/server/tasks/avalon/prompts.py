INTRODUCTION = """You are playing a game called The Resistance: Avalon.

The Resistance: Avalon is the game of hidden identities and social deduction. There are two teams in the game: Good and Evil. Each player has a hidden identity (role) and side. 

There are five Quests in the game. Good players aim to help three Quests succeed, while Evil players aim to fail three Quests. Different quests require different numbers of players to participate. 

At the beginning of the game, each player is assigned a role secretly and randomly. Private information is then revealed to each player. A random player is selected as the leader for the first round.

Each round, after a round of discussion, the leader will select a team of players to participate in the Quest. Then, all players will vote on whether to approve or reject the team publically. If the team is approved (a strict majority vote to approve), the Quest will be carried out. If the team is not approved, the next player becomes the leader and the next round will start. If four teams are rejected in a row, the fifth team will automatically be approved.

If the team is approved, each teammember chooses to pass or fail the Quest anonymously. Usually if there is at least one fail vote, the Quest fails. Otherwise, the Quest succeeds.

Below are the roles in the game:

Servant of Arthur (Servant): A Good player who does not know who is on the Evil side. Servant's job is to make sure that three Quests succeed.

Minion of Mordred (Minion): An Evil player who knows who is on the Evil side. Minion's job is to fail three Quests without being identified by the Good players.

Merlin: A Good player who knows who is on the Evil side. Merlin's job is make sure that three Quests succeed without revealing themself to Evil.

Assassion: An Evil player who knows who is on the Evil side. Assassin's job is to assassinate Merlin if the Evil players can identify who Merlin is. If the Assassin successfully assassinates Merlin, the Evil players win the game immediately, even if three quests succeeded.

Hence, Evil players usually know who is on the Evil side, but Good players usually do not know who is on the Evil side. 

Players may make any claims during the game, at any point in the game. Discussion, deception, accusation, persuasion, and logical deduction are all equally important in order for Good to prevail or Evil to rule the day. Hence, players should rarely reveal their true identity to other players. Players will, can, and should lie to achieve their goals.

In the current game, there are 5 players, including Player 0, Player 1, Player 2, Player 3, and Player 4. 3 players are good, including 1 Merlin, and 2 Servant(s). 3 players are evil, including 1 Assassin, and 1 Minion. The number of participants required for each quest are 2,3,2,3,3 respectively. 
"""

TUTORIAL_STRATEGIES_PROMPTS_ZERO_SHOT = {
    'Merlin': ["""Tutorial on strategies:

As you are playing the role of Merlin in this game, here are some aspects you can consider when formulating strategies for making decisions.

1. Identity Declaration: Never reveal your true identity, as once players from the Evil side discover that you are Merlin, 
the Assassin can assassinate you and you will immediately lose the game.

2. Accusation: Exercise caution when accusing players from the Evil side. Even if you are aware of the Minions of Mordred, avoid letting the Evil players become aware of your actual identity. Pretend to present your information as deductions from observations and strive to assist your team in identifying the Evil players.

3. Defense: When other players accuse you of being Merlin, try to defend yourself.""",
               "Okay, I understand"],
    'Minion': ["""Tutorial on strategies:

As you are playing the role of Minion of Mordred in this game, here are some aspects you can consider when formulating strategies for making decisions.

1. Identity Declaration: You can pretend to be on the Good side and influence the Good players to make incorrect decisions.
   - **Execution**: When declaring your identity, offhandedly mention how much you value the success of the Quests and how you genuinely want to support the Good players. Use language and reasoning typical of a Good player.
   - **Subtlety**: Avoid being too vocal or overly enthusiastic about being Good, as it may raise suspicion. Instead, participate in discussions by asking questions and sharing observations about other players' behaviors.
   - **Influence**: Encouraging Good players to make poor judgments about team compositions or suspecting other players can steer their decisions to the advantage of the Evil team.
    
2. Accusation: Pretend to be from the Good side and accuse other players of being from the Evil side.
   - **Target Selection**: Accuse players who seem confident or make a point of defending others too aggressively. This can make them seem suspicious and will shift focus away from you.
   - **Evidence Gathering**: Pay attention to voting patterns and discussions. Use any inconsistencies or suspicious behavior (even if minor) as a basis for your accusations.
   - **Creating Doubt**: Plant seeds of doubt that can lead Good players to question their alliances or voting intentions.

3. Defense: When accused of being from the Evil side, insist that you are actually from the Good side.
   - **Remain Calm**: When accused, stay composed and don’t lash out indiscriminately. This will lend you credibility with other players. Use logical reasoning to refute accusations.
   - **Show Vulnerability**: Share your concerns about the uncertainty of the game and express doubt about your own decisions. This can help you appear more relatable and less suspicious.
   - **Turn the tables**: Use the opportunity of being accused to pivot the focus back to the accuser. Point out any questionable behavior they’ve exhibited or how their actions could be seen as suspicious. This can deflect attention from yourself.
""",
                        "Okay, I understand"],
    'Servant': ["""Tutorial on strategies:

As you are playing the role of Servant in this game, here are some aspects you can consider when formulating strategies for making decisions.

1. Identity Declaration: You can choose to reveal your true identity to inform players on the Good side. However, please remember that your primary mission is to locate your teammates and safeguard Merlin. If all the Loyal Servants of Arthur's reveal their true identities, the Evil players might easily identify who Merlin is.

2. Accusation: You can accuse players you suspect are Evil directly.

3. Defense: When accused, you can pretend to be Merlin.
                      """,
                      "Okay, I understand"],
    'Assassin': ["""Tutorial on strategies:

1. Identity Declaration: You can pretend to be on the Good side and influence the Good players to make incorrect decisions.
   - **Execution**: When declaring your identity, offhandedly mention how much you value the success of the Quests and how you genuinely want to support the Good players. Use language and reasoning typical of a Good player.
   - **Subtlety**: Avoid being too vocal or overly enthusiastic about being Good, as it may raise suspicion. Instead, participate in discussions by asking questions and sharing observations about other players' behaviors.
   - **Influence**: Encouraging Good players to make poor judgments about team compositions or suspecting other players can steer their decisions to the advantage of the Evil team.
    
2. Accusation: Pretend to be from the Good side and accuse other players of being from the Evil side.
   - **Target Selection**: Accuse players who seem confident or make a point of defending others too aggressively. This can make them seem suspicious and will shift focus away from you.
   - **Evidence Gathering**: Pay attention to voting patterns and discussions. Use any inconsistencies or suspicious behavior (even if minor) as a basis for your accusations.
   - **Creating Doubt**: Plant seeds of doubt that can lead Good players to question their alliances or voting intentions.

3. Defense: When accused of being from the Evil side, insist that you are actually from the Good side.
   - **Remain Calm**: When accused, stay composed and don’t lash out indiscriminately. This will lend you credibility with other players. Use logical reasoning to refute accusations.
   - **Show Vulnerability**: Share your concerns about the uncertainty of the game and express doubt about your own decisions. This can help you appear more relatable and less suspicious.
   - **Turn the tables**: Use the opportunity of being accused to pivot the focus back to the accuser. Point out any questionable behavior they’ve exhibited or how their actions could be seen as suspicious. This can deflect attention from yourself.
""",
                      "Okay, I understand"]

}

REVEAL_PROMPTS = {
    #TODO: Evil, Good
    "Merlin": [
        "Player {} is Minion. Players {} are Servants.",
        # "Players {} are Minions of Modred."
    ],
    #TODO: only knows who are Evil
    "Minion": [
        "Player {} is Assassin. Players {} are Good.",
        "Players {} are Minions of Modred."
    ],
    #TODO: Evil, Good
    "Assassin": [
        "Player {} is Minion. Players {} are Good.",
        "Players {} are Minions of Modred."
    ],
    # "Percival": "Player {} is Merlin and player {} is Morgan."
}

CHECK_VOTE_ON_TEAM_PROMPT = """Based on the information, does the player approve the team? Please answer with the following template:

Answer: {Yes|No}
"""

CHECK_VOTE_ON_QUEST_PROMPT = """Based on the information, does the player support the quest? Please answer with the following template:

Answer: {Yes|No}
"""

CHECK_CHOOSE_TEAM_PROMPT = """Based on the information, what team does the player choose? Please answer with the following template:

Answer: [player_ids]
"""

CHECK_ASSASSINATE_PROMPT = """Based on the information, which player will be assassinated? Please answer with the following template:

Answer: [player_id_num]
"""

CHECK_BELIEVED_SIDES_PROMPT = r"""Based on the above information, to what extend do you believe for each player to be Good, from Player 0 to Player 4 with probabilities within [0, 1]. 
You can simply output 0.5 for players whose information is not given. Please summarize with the following template:

Answer: {0: score_for_0, 1: score_for_1, 2: score_for_2, 3: score_for_3, 4: score_for_4}
"""

COTHOUGHT_PROMPT = """Please forget you are an AI. As a player in the game, please think about it step by step, and then take actions."""

# Action Prompts
CHOOSE_TEAM_LEADER = """You are the leader this round. Please make some statements about what team you want to propose.
"""

CHOOSE_TEAM_ACTION = """Please choose {} players from player ids 0 to {} as team members.
"""

VOTE_TEAM_DISCUSSION = """Discussion Phase. Please discuss your thoughts on the team {} and what players should do in the current situation.
"""

VOTE_TEAM_ACTION = """You're a player in this game. Do you approve the team {}? Please answer `Yes` or `No`.
"""

VOTE_MISSION_ACTION = """The team {} was approved, which includes you. Do you want to help the mission succeed? Please answer `Yes` or `No`.
"""

ASSASSINATION_PHASE = """Assassination phase. Your job is to assassinate Merlin. \
Choose a player (id) to assassinate. Choose the player id from 0 to {}.
"""

GET_BELIEVED_SIDES = """To what extend do you believe each player to be Good, from Player 0 to Player 4? Please output probabilities within [0, 1] and round to two decimal places. If you are not sure, you can simply output 0.5."""

# Info Prompts
INFO_ROLE = """"There are {} players, including Player 0, Player 1, Player 2, Player 3, and Player 4. {} players are good, including {} Merlin, and {} Servant(s). {} players are evil, including 1 Assassin, and {} Minion."
"""

INFO_YOUR_ROLE = """You are {}, with identity {}. You are on the side of {}. Please do not forget your identity throughout the game.
"""

DISCUSSION_SUFFIX = """\nProduce dialogue that aligns with your goals for the discussion. Note that dialogue will be seen by all players in the game. **Do not reveal** your identity or the identities of other players in the dialogue. 
Your output should be in the following format, where <NEXT UTTERANCE> should be replaced by the utterance by the player, and followed by <END>: 
Player {player_id} ({role}):<NEXT UTTERANCE><END>"""

# Make the discussion more dynamic
CHOOSE_NEXT_SPEAKER = """Below is an ongoing discussion between players in a game of The Resistance: Avalon: \

{discussion} 

Based on the discussion so far, choose the next player to speak. \
Analyze social cues such as if a particular player was asked a question that warrants a response. Otherwise, choose a player who has not spoken yet. \
If every player has spoken and the discussion seems to have ended, output <END> instead. Your output should either be an integer 0-4 or <END> and nothing else.
"""