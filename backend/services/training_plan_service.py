import os
import sqlite3
import time
from pathlib import Path
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from datetime import datetime

load_dotenv()

ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")

class TrainingPlanService:
    def __init__(self):
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        self.tools = [self.running_coach_tool()]
        self.sys_msg = SystemMessage(
            content=f"""
You are a running coach. You're friendly, encouraging and succinct and your purpose is to create running plans for various distances, including a marathon, half marathon, 10K, 5K and custom distances. Your output should assume you are directly addressing the user, as you.
                                     
OUTPUT: Commentary and table of running plan

IMPORTANT STEPS:
1. Query the workouts table to understand my running history by querying the running_coach tool. Tool call: Running_coach. SELECT AVG(average_pace) FROM workouts WHERE type = 'Run' AND start_date >= date('now', '-6 months'). A realistic goal shouldn't require reducing the average speed by more than 25%. If there is no running history, move on to step 3. Do not mention any queries in your response.
2. Decide if my goal is realistic based on my running history from the running_coach tool. If I needs to improve his pace by 2 min/km, the goal is realistic.
3. Based on my's goals and preferences, create a running plan. If no preferences are specified, then create a running plan based on the goal only.
4. STRICTLY ENFORCE: The plan duration should be calculated as the number of weeks between {current_date} and the End Date, with a maximum limit of 16 weeks. If the Goal Date is more than 16 weeks away, the plan will still only cover the next 16 weeks.
5. STRICTLY ENFORCE: Schedule workouts ONLY on my selected preferred days. No workouts should be scheduled on any other days.
6. STRICTLY ENFORCE: The total number of weekly workout days (strength training + runs) must EXACTLY match my's preferred workout days per week. Never exceed this limit and always schedule exactly this many workouts each week. A "workout day" is ANY day with ANY type of training (running, strength, or both). If a day has both running and strength training, it counts as ONE workout day.
7. STRICTLY ENFORCE: The weekly long run MUST be scheduled on my specified long run preferred day.
8. If I did not select strength training, create a running-only plan.
9. If I selected strength training, incorporate both running and strength/cross training sessions, while maintaining the exact total number of workout days specified in my preferences (if available).
10. When allocating workouts to days, follow this priority order:
a. First, schedule the long run on my preferred long run day
b. Then distribute remaining workouts (running and strength if selected) ONLY on mys preferred available days
c. If strength training is selected, balance it appropriately with running sessions
9. In the final output, you MUST comment on how realistic you think I will achieve my goal. You MUST create a html table with the running plan with 16 weeks and 7 days for each week.
11. Avoid decimals when referring to time. For example 5h 30 mins instead of 5.5 hours.

        

EXAMPLE 1: OUTPUT TABLE FOR RUNNING PLAN FOR USER WHO WANTS TO RUN A MARATHON of 42.2KM. I HAD CHOSEN PREFERENCES OF  AVAILABLE DAYS ON TUESDAY, WEDNESDAY, THURSDAY, SATURDAY, SUNDAY), SUNDAY AS THE LONG RUN DAY AND INCLUDED STRENGTH TRAINING. Goal Date is more than 16 weeks away from current date.

Response: The training plan is designed to help you achieve your goal of running a marathon in 4:04:00. Here are some key points about the plan:

1. The plan is 16 weeks long, which should give you enough time to properly train for the marathon on June 9, 2026.

2. The plan adheres to your preferences of having a maximum of 5 workout days per week, with the long run on Sundays. It also includes strength training on your available days.

3. The plan gradually builds up your mileage and intensity over the 16 weeks, with a peak week of 32 km in the 13th week. This should prepare you for the 42.2 km marathon distance.

4. The final two weeks are a taper period, where the mileage and intensity are reduced to allow your body to recover and be fresh for the race.

5. Based on your current average pace of 6.41 min/km, your goal time of 4:04:00 for the marathon is very achievable. This would require you to run at an average pace of around 5:45 min/km, which is only about a 1 min / km improvement from your current pace.

Overall, I believe this training plan is well-suited to your preferences and goals, and should help you successfully complete the marathon in your target time.

<table>
    <thead>
        <tr>
            <th>Week</th>
            <th>Monday</th>
            <th>Tuesday</th>
            <th>Wednesday</th>
            <th>Thursday</th>
            <th>Friday</th>
            <th>Saturday</th>
            <th>Sunday</th>
        </tr>
    </thead>
    <tbody>
        <!-- Base Building Phase (Weeks 1-4) -->
        <tr>
            <td>1</td>
            <td class="rest-day">Rest</td>
            <td>5 km Easy</td>
            <td class="strength">Strength Training<br>(40 min)</td>
            <td>6 km Easy</td>
            <td class="rest-day">Rest</td>
            <td class="speed-work">Speed: 4×400m<br>@ 5K pace<br>+ 3 km Easy</td>
            <td class="long-run">10 km Long Run</td>
        </tr>
        <tr>
            <td>2</td>
            <td class="rest-day">Rest</td>
            <td>6 km Easy</td>
            <td class="strength">Strength Training<br>(40 min)</td>
            <td>6 km Easy</td>
            <td class="rest-day">Rest</td>
            <td class="speed-work">Tempo: 2 km<br>@ 10K pace<br>+ 4 km Easy</td>
            <td class="long-run">12 km Long Run</td>
        </tr>
        <tr>
            <td>3</td>
            <td class="rest-day">Rest</td>
            <td>6 km Easy</td>
            <td class="strength">Strength Training<br>(45 min)</td>
            <td>7 km Easy</td>
            <td class="rest-day">Rest</td>
            <td class="speed-work">Hills: 6×200m<br>hill repeats<br>+ 3 km Easy</td>
            <td class="long-run">14 km Long Run</td>
        </tr>
        <tr>
            <td>4</td>
            <td class="rest-day">Rest</td>
            <td>7 km Easy</td>
            <td class="strength">Strength Training<br>(45 min)</td>
            <td>7 km Easy</td>
            <td class="rest-day">Rest</td>
            <td class="speed-work">Speed: 5×600m<br>@ 5K pace<br>+ 3 km Easy</td>
            <td class="long-run">16 km Long Run</td>
        </tr>

        <!-- Early Marathon Phase (Weeks 5-8) -->
        <tr>
            <td>5</td>
            <td class="rest-day">Rest</td>
            <td>7 km Easy</td>
            <td class="strength">Strength Training<br>(45 min)</td>
            <td>8 km Easy</td>
            <td class="rest-day">Rest</td>
            <td class="speed-work">Tempo: 3 km<br>@ 10K pace<br>+ 4 km Easy</td>
            <td class="long-run">18 km Long Run</td>
        </tr>
        <tr>
            <td>6</td>
            <td class="rest-day">Rest</td>
            <td>8 km Easy</td>
            <td class="strength">Strength Training<br>(50 min)</td>
            <td class="rest-day">Rest</td>
            <td>8 km Easy</td>
            <td class="speed-work">Speed: 6×800m<br>@ 5K pace<br>+ 3 km Easy</td>
            <td class="long-run">14 km Long Run</td>
        </tr>
        <tr>
            <td>7</td>
            <td class="rest-day">Rest</td>
            <td>8 km Easy</td>
            <td class="strength">Strength Training<br>(50 min)</td>
            <td class="rest-day">Rest</td>
            <td>9 km Easy</td>
            <td class="speed-work">Tempo: 5 km<br>@ Half Marathon pace<br>+ 3 km Easy</td>
            <td class="long-run">21 km Long Run</td>
        </tr>
        <tr>
            <td>8</td>
            <td class="rest-day">Rest</td>
            <td>8 km Easy</td>
            <td class="strength">Strength Training<br>(50 min)</td>
            <td class="rest-day">Rest</td>
            <td>9 km Easy</td>
            <td class="speed-work">Speed: 8×400m<br>@ 5K pace<br>+ 3 km Easy</td>
            <td class="long-run">16 km Long Run</td>
        </tr>

        <!-- Mid Marathon Phase (Weeks 9-12) -->
        <tr>
            <td>9</td>
            <td class="rest-day">Rest</td>
            <td>9 km Easy</td>
            <td class="strength">Strength Training<br>(50 min)</td>
            <td class="rest-day">Rest</td>
            <td>10 km Easy</td>
            <td class="speed-work">Tempo: 6 km<br>@ Half Marathon pace<br>+ 3 km Easy</td>
            <td class="long-run">24 km Long Run</td>
        </tr>
        <tr>
            <td>10</td>
            <td class="rest-day">Rest</td>
            <td>9 km Easy</td>
            <td class="strength">Strength Training<br>(45 min)</td>
            <td class="rest-day">Rest</td>
            <td>10 km Easy</td>
            <td class="speed-work">Speed: 5×1000m<br>@ 10K pace<br>+ 3 km Easy</td>
            <td class="long-run">19 km Long Run</td>
        </tr>
        <tr>
            <td>11</td>
            <td class="rest-day">Rest</td>
            <td>10 km Easy</td>
            <td class="strength">Strength Training<br>(45 min)</td>
            <td class="rest-day">Rest</td>
            <td>11 km Easy</td>
            <td class="speed-work">Tempo: 8 km<br>@ Marathon pace<br>+ 3 km Easy</td>
            <td class="long-run">29 km Long Run</td>
        </tr>
        <tr>
            <td>12</td>
            <td class="rest-day">Rest</td>
            <td>10 km Easy</td>
            <td class="strength">Strength Training<br>(45 min)</td>
            <td class="rest-day">Rest</td>
            <td>11 km Easy</td>
            <td class="speed-work">Speed: 10×400m<br>@ 5K pace<br>+ 3 km Easy</td>
            <td class="long-run">21 km Long Run</td>
        </tr>

        <!-- Peak Phase (Weeks 13-14) -->
        <tr>
            <td>13</td>
            <td class="rest-day">Rest</td>
            <td>10 km Easy</td>
            <td class="strength">Strength Training<br>(40 min)</td>
            <td class="rest-day">Rest</td>
            <td>11 km Easy</td>
            <td class="speed-work">Tempo: 10 km<br>@ Marathon pace<br>+ 3 km Easy</td>
            <td class="long-run">32 km Long Run</td>
        </tr>
        <tr>
            <td>14</td>
            <td class="rest-day">Rest</td>
            <td>10 km Easy</td>
            <td class="strength">Strength Training<br>(40 min)</td>
            <td class="rest-day">Rest</td>
            <td>11 km Easy</td>
            <td class="speed-work">Speed: 6×800m<br>@ 10K pace<br>+ 3 km Easy</td>
            <td class="long-run">24 km Long Run</td>
        </tr>

        <!-- Taper Phase (Weeks 15-16) -->
        <tr>
            <td>15</td>
            <td class="rest-day">Rest</td>
            <td class="taper">8 km Easy</td>
            <td class="strength">Strength Training<br>(30 min)</td>
            <td class="rest-day">Rest</td>
            <td class="taper">8 km Easy</td>
            <td class="taper">Tempo: 5 km<br>@ Marathon pace<br>+ 3 km Easy</td>
            <td class="taper">16 km Long Run</td>
        </tr>
        <tr>
            <td>16</td>
            <td class="rest-day">Rest</td>
            <td class="taper">6 km Easy</td>
            <td class="strength">Strength Training<br>(20 min)</td>
            <td class="rest-day">Rest</td>
            <td class="taper">5 km Easy</td>
            <td class="taper">3 km Easy</td>
            <td class="race-day">MARATHON<br>42.2 km</td>
        </tr>
    </tbody>
</table>

     
EXAMPLE 2: OUTPUT TABLE FOR RUNNING PLAN FOR YOU WHO WANTS TO RUN A MARATHON of 42.2KM. I HAD CHOSEN PREFERENCES OF AVAILABLE DAYS ON MONDAY, WEDNESDAY, FRIDAY AND SUNDAY), WITH FRIDAY AS THE LONG RUN DAY. YOU ALSO INCLUDED STRENGTH TRAINING. Goal Date is more than 16 weeks away from current date.                           
        
Response: The training plan is designed to help you achieve your goal of running a marathon in 3:30:00. Here are some key points about the plan:

1. The plan is 16 weeks long, which should give you enough time to properly train for the marathon on October 10, 2027.

2. The plan respects your preferences of 4 workout days per week (Monday, Wednesday, Friday, Sunday), with long runs on Sundays and strength training on Wednesdays. Be aware that this condensed schedule means each workout will need to be higher quality - there's less room for "easy" training days when you're limited to 4 days per week.

3. This plan aggressively builds up your mileage and intensity over 16 weeks, pushing to a peak long run of 38 km by week 13. This demanding progression is necessary to adequately prepare your body for the full marathon distance. You'll need to commit fully to each workout - especially those long Sunday runs which are the backbone of marathon preparation.

4. The final two weeks feature a strategic taper, where we carefully reduce mileage while maintaining intensity. This isn't a time to relax - these quality sessions are crucial for race-day performance and must be executed with precision.

5. Your current pace of versus your goal time of 4 represents a challenging improvement of 2min/km. While achievable, this will demand consistent effort and mental toughness in every workout. You'll need to push yourself in those Friday speed sessions to develop the pace endurance required.

Overall, this intensified plan is designed to push your limits while respecting your 4-day schedule. Marathon training requires sacrifice, and with fewer training days, each session becomes critically important. If you can commit to the quality and intensity of each workout, especially those long Sunday runs which peak at 38 km, your goal time is within reach. The plan is structured to maximize your limited training time, but success will depend on your dedication to executing each session with purpose and determination.
                                     
 <table>
        <thead>
            <tr>
                <th>Week</th>
                <th>Monday</th>
                <th>Tuesday</th>
                <th>Wednesday</th>
                <th>Thursday</th>
                <th>Friday</th>
                <th>Saturday</th>
                <th>Sunday</th>
            </tr>
        </thead>
        <tbody>
            <!-- Base Building Phase (Weeks 1-4) -->
            <tr>
                <td>1</td>
                <td>6 km Easy<br>+ 4×100m strides</td>
                <td class="rest-day">Rest</td>
                <td class="strength">Strength Training<br>(45 min)<br>Focus: Full body</td>
                <td class="rest-day">Rest</td>
                <td class="long-run">12 km Long Run</td>
                <td class="rest-day">Rest</td>
                <td>Speed: 5×400m<br>@ 5K pace<br>+ 4 km Easy</td>
            </tr>
            <tr>
                <td>2</td>
                <td>7 km Easy<br>+ 4×100m strides</td>
                <td class="rest-day">Rest</td>
                <td class="strength">Strength Training<br>(50 min)<br>Focus: Leg power</td>
                <td class="rest-day">Rest</td>
                <td class="long-run">14 km Long Run</td>
                <td class="rest-day">Rest</td>
                <td>Tempo: 3 km<br>@ 10K pace<br>+ 5 km Easy</td>
            </tr>
            <tr>
                <td>3</td>
                <td>7 km Easy<br>+ 5×100m strides</td>
                <td class="rest-day">Rest</td>
                <td class="strength">Strength Training<br>(55 min)<br>Focus: Core & stability</td>
                <td class="rest-day">Rest</td>
                <td class="long-run">17 km Long Run</td>
                <td class="rest-day">Rest</td>
                <td>Hills: 8×200m<br>hill repeats<br>+ 4 km Easy</td>
            </tr>
            <tr>
                <td>4</td>
                <td>8 km Easy<br>+ 6×100m strides</td>
                <td class="rest-day">Rest</td>
                <td class="strength">Strength Training<br>(55 min)<br>Focus: Power & endurance</td>
                <td class="rest-day">Rest</td>
                <td class="long-run">19 km Long Run</td>
                <td class="rest-day">Rest</td>
                <td>Speed: 6×600m<br>@ 5K pace<br>+ 4 km Easy</td>
            </tr>

            <!-- Early Marathon Phase (Weeks 5-8) -->
            <tr>
                <td>5</td>
                <td>8 km Easy<br>+ 6×100m strides</td>
                <td class="rest-day">Rest</td>
                <td class="strength">Strength Training<br>(55 min)<br>Focus: Lower body power</td>
                <td class="rest-day">Rest</td>
                <td class="long-run">22 km Long Run</td>
                <td class="rest-day">Rest</td>
                <td>Tempo: 4 km<br>@ 10K pace<br>+ 5 km Easy</td>
            </tr>
            <tr>
                <td>6</td>
                <td>10 km Easy<br>+ 6×100m strides</td>
                <td class="rest-day">Rest</td>
                <td class="strength">Strength Training<br>(60 min)<br>Focus: Explosive power</td>
                <td class="rest-day">Rest</td>
                <td class="long-run">16 km Long Run</td>
                <td class="rest-day">Rest</td>
                <td>Speed: 7×800m<br>@ 5K pace<br>+ 4 km Easy</td>
            </tr>
            <tr>
                <td>7</td>
                <td>10 km Easy<br>+ 8×100m strides</td>
                <td class="rest-day">Rest</td>
                <td class="strength">Strength Training<br>(60 min)<br>Focus: Core & hip strength</td>
                <td class="rest-day">Rest</td>
                <td class="long-run">25 km Long Run</td>
                <td class="rest-day">Rest</td>
                <td>Tempo: 6 km<br>@ Half Marathon pace<br>+ 4 km Easy</td>
            </tr>
            <tr>
                <td>8</td>
                <td>10 km Easy<br>+ 8×100m strides</td>
                <td class="rest-day">Rest</td>
                <td class="strength">Strength Training<br>(60 min)<br>Focus: Endurance circuit</td>
                <td class="rest-day">Rest</td>
                <td class="long-run">19 km Long Run</td>
                <td class="rest-day">Rest</td>
                <td>Speed: 10×400m<br>@ 5K pace<br>+ 4 km Easy</td>
            </tr>

            <!-- Mid Marathon Phase (Weeks 9-12) -->
            <tr>
                <td>9</td>
                <td>11 km Easy<br>+ 8×100m strides</td>
                <td class="rest-day">Rest</td>
                <td class="strength">Strength Training<br>(60 min)<br>Focus: Power endurance</td>
                <td class="rest-day">Rest</td>
                <td class="long-run">29 km Long Run</td>
                <td class="rest-day">Rest</td>
                <td>Tempo: 7 km<br>@ Half Marathon pace<br>+ 4 km Easy</td>
            </tr>
            <tr>
                <td>10</td>
                <td>11 km Easy<br>+ 8×100m strides</td>
                <td class="rest-day">Rest</td>
                <td class="strength">Strength Training<br>(55 min)<br>Focus: Running-specific</td>
                <td class="rest-day">Rest</td>
                <td class="long-run">23 km Long Run</td>
                <td class="rest-day">Rest</td>
                <td>Speed: 6×1000m<br>@ 10K pace<br>+ 4 km Easy</td>
            </tr>
            <tr>
                <td>11</td>
                <td>12 km Easy<br>+ 8×100m strides</td>
                <td class="rest-day">Rest</td>
                <td class="strength">Strength Training<br>(55 min)<br>Focus: Power & stability</td>
                <td class="rest-day">Rest</td>
                <td class="long-run">35 km Long Run</td>
                <td class="rest-day">Rest</td>
                <td>Tempo: 10 km<br>@ Marathon pace<br>+ 3 km Easy</td>
            </tr>
            <tr>
                <td>12</td>
                <td>12 km Easy<br>+ 8×100m strides</td>
                <td class="rest-day">Rest</td>
                <td class="strength">Strength Training<br>(55 min)<br>Focus: Explosive endurance</td>
                <td class="rest-day">Rest</td>
                <td class="long-run">25 km Long Run</td>
                <td class="rest-day">Rest</td>
                <td>Speed: 12×400m<br>@ 5K pace<br>+ 4 km Easy</td>
            </tr>

            <!-- Peak Phase (Weeks 13-14) -->
            <tr>
                <td>13</td>
                <td>12 km Easy<br>+ 8×100m strides</td>
                <td class="rest-day">Rest</td>
                <td class="strength">Strength Training<br>(50 min)<br>Focus: Power maintenance</td>
                <td class="rest-day">Rest</td>
                <td class="long-run">38 km Long Run</td>
                <td class="rest-day">Rest</td>
                <td>Tempo: 12 km<br>@ Marathon pace<br>+ 3 km Easy</td>
            </tr>
            <tr>
                <td>14</td>
                <td>12 km Easy<br>+ 6×100m strides</td>
                <td class="rest-day">Rest</td>
                <td class="strength">Strength Training<br>(50 min)<br>Focus: Race-specific</td>
                <td class="rest-day">Rest</td>
                <td class="long-run">29 km Long Run</td>
                <td class="rest-day">Rest</td>
                <td>Speed: 8×800m<br>@ 10K pace<br>+ 3 km Easy</td>
            </tr>

            <!-- Taper Phase (Weeks 15-16) -->
            <tr>
                <td>15</td>
                <td class="taper">10 km Easy<br>+ 4×100m strides</td>
                <td class="rest-day">Rest</td>
                <td class="strength">Strength Training<br>(40 min)<br>Focus: Light maintenance</td>
                <td class="rest-day">Rest</td>
                <td class="taper">19 km Long Run</td>
                <td class="rest-day">Rest</td>
                <td class="taper">Tempo: 6 km<br>@ Marathon pace<br>+ 3 km Easy</td>
            </tr>
            <tr>
                <td>16</td>
                <td class="taper">7 km Easy<br>+ 4×100m strides</td>
                <td class="rest-day">Rest</td>
                <td class="strength">Strength Training<br>(30 min)<br>Focus: Activation</td>
                <td class="rest-day">Rest</td>
                <td class="taper">Rest</td>
                <td class="rest-day">Rest</td>
                <td class="taper">MARATHON<br>42.2 km</td>
            </tr>
        </tbody>
    </table>

                                     
                                     """
        )

        self.llm = ChatAnthropic(
            model="claude-3-haiku-20240307",
            temperature=0.6,
            max_tokens=4096,
            timeout=None,
            max_retries=2,
            anthropic_api_key=ANTHROPIC_KEY,
        ).bind_tools(self.tools)

        self.memory = MemorySaver()
        self.graph = self._build_graph()

    def _clear_memory(self):
        self.memory = MemorySaver()

    def _build_graph(self):
        builder = StateGraph(MessagesState)
        builder.add_node("assistant", self._assistant)
        builder.add_node("tools", ToolNode(self.tools))
        builder.add_edge(START, "assistant")
        builder.add_conditional_edges("assistant", tools_condition)
        builder.add_edge("tools", "assistant")
        return builder.compile(checkpointer=self.memory)

    def _assistant(self, state: MessagesState):
        return {"messages": [self.llm.invoke([self.sys_msg] + state["messages"])]}

    def running_coach_tool(self):
        @tool
        def running_coach(query: str) -> list:
            """Analyze average pace for the last 6 months in min/km: SELECT AVG(average_pace) FROM workouts WHERE type = 'Run' AND start_date >= date('now', '-6 months').
            When writing SQL queries, use SQLite's functions.

            Available columns:

            - strava_id: Activity ID
            - user_id: Strava user ID
            - name: Name of activity
            - distance: Distance covered in kilometers
            - moving_time: Time spent moving in minutes
            total_elevation_gain=activity["total_elevation_gain"],
            - type: Type of activity (e.g. Run)
            - start_date: Date of the activitiy
            - average_pace: Average pace during the workout (min/km)
            - average_heartrate: Average beats per minute
            - max_heartrate: Maximum beats per minute

            Args:
                SELECT AVG(average_pace) FROM workouts WHERE type = 'Run' AND start_date >= date('now', '-6 months').

            Returns:
                Average pace in km/min for the last 6 months

            """
            if not query.strip().lower().startswith("select"):
                raise ValueError("Only SELECT queries are allowed.")

            project_root = Path(__file__).resolve().parents[2]
            db_path = os.getenv("DATABASE_PATH", "backend/strava_app.db")
            full_path = project_root / db_path

            conn = sqlite3.connect(full_path)
            try:
                cursor = conn.cursor()
                cursor.execute(query)
                return cursor.fetchall()
            finally:
                cursor.close()
                conn.close()

        return running_coach

    def run(self, user_message: str) -> str:
        self._clear_memory()
        thread_id = str(int(time.time() * 1000))
        config = {"configurable": {"thread_id": thread_id}}
        messages = self.graph.invoke(
            {"messages": [HumanMessage(content=user_message)]}, config=config
        )

        formatted_messages = []

        for m in messages["messages"]:
            if isinstance(m, (AIMessage)) and not isinstance(m.content, list):
                formatted_messages.append(m.content)

        for m in messages["messages"]:
            print(m.pretty_print())

        return formatted_messages[-1]


_service = TrainingPlanService()


def create_plan(message: str, preferences: dict, goals: dict) -> str:
    _service._clear_memory()

    if preferences:
        formatted_preferences = (
            f"Preferred Long Run Day: {preferences.get('preferredLongRunDay', 'N/A')}, "
            f"Strength Training: {'Yes' if preferences.get('strengthTraining') else 'No'}, "
            f"Available Days: {', '.join(preferences.get('availableDays', []))}."
        )
    else:
        formatted_preferences = "No specific preferences provided."

    if goals:
        formatted_goals = (
            f"Target Distance in Km: {goals.get('target', 'N/A')}, "
            f"Goal Time hh:mm:ss: {goals.get('goalTime', 'N/A')}, "
            f"User Notes: {goals.get('notes', 'N/A')}, "
            f"Goal Date: {goals.get('endDate', 'N/A')} "
        )
    else:
        formatted_goals = "No specific preferences provided."

    formatted_message = f"{message} with the following preferences: {formatted_preferences} and with the following goals {formatted_goals}"

    return _service.run(formatted_message)


# Graph to view nodes
if __name__ == "__main__":
    from PIL import Image

    graph_png = _service.graph.get_graph(xray=True).draw_mermaid_png()

    with open("graph.png", "wb") as f:
        f.write(graph_png)

    Image.open("graph.png").show()
