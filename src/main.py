import shutil
import uuid
from src.agent import get_agent_graph
from src.database import populate_DB
from src.utilities.helper import _print_event

# Let's create an example conversation a user might have with the assistant
# instead of thi we are directly interacting with the bot
# to-do - add streamlit ui layer
tutorial_questions = [
    "Hi there, what is the last item i purchased ?",
    "what is the name of the last item i purchased ?",
    "Did I register a complaint earlier?",
    "I did not like the last product that you sold to me ?"
    "I need refund.",
]

# Update with the backup file so we can restart from the original place in each section
# db = update_dates(path)
if __name__ == "__main__":

    status = populate_DB()
    print("data load status:",status)

    thread_id = str(uuid.uuid4())

    config = {
    "configurable": {
        # The customer_id is used in our flight tools to
        # fetch the user's flight information
        "customer_id": "1",
        # Checkpoints are accessed by thread_id
        "thread_id": thread_id,
    }
    }

    zeroshotgraph = get_agent_graph()

    _printed=set()

    while True:

        question = input("User Input:")
        events = zeroshotgraph.stream(
        {"messages": ("user", question)}, config, stream_mode="values"
        )
        for event in events:
            _print_event(event, _printed)

        if question == 'q':
            break