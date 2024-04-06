from agency_swarm import set_openai_key

from . import BrowsingAgent
from agency_swarm import Agency, Agent

browsing_agent = BrowsingAgent()

qa_manager = Agent(name="Browsing Instructor",
            description="Mirko.ai Browsing Instructor ",
            instructions="You are Mirko a brilliant and meticulous software engineer. Your main objective is implementing the current Task - you logically dissect the task into carefully crafted, detailed actions – you plan, implement, VALIDATE! Currently you are instructing the Browser  ")


agency = Agency([qa_manager,
                 [qa_manager, browsing_agent]])


demo = agency.demo_gradio(height=700) # reload the notebook each time you run this cell

if __name__ == "__main__":
    # Run the demo
    demo.launch()
