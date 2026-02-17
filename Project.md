This project aims to explore the question "How does a player’s recent 3-point makes and attempts over the last N games relate to their next N games’ 3-point makes?".

This is important as fans mainly care about who is hot. Fans might say, "Steph is averaging 7 3 Pointer's Made (3PM) over his last 5 games he surely will get at least 6 next game". Teams mainly care about the volume of shots taken and the players role. A coach might say, "Rui has been on a hot streak with 3PM's made but how much is Lebron's abscence affecting his volume?".

We will dive deep into the data availble and see how closely tethered recent form is to short-term/long-term output. We'll achieve this by using game-level player data creating useful features using SQL and conduct evaluations using Python.


Create a view that has a player game, then the last 5 games stats in terms of average 3pm, 3pa. Consider the impact of minutes on all views and whether min minutes should be applied. exclude the current game in question

# We are testing
“Given we already know the next 10 games’ attempt volume, which rate estimate (season-to-date vs last-10) better predicts the next-10 makes?”


# Add Comments!!!!!!!!!!!!!!