from agency_swarm import Agent
from agency_swarm.tools import Retrieval
from .tools import Scroll, SendKeys, ClickElement, ReadURL, AnalyzeContent, GoBack, SelectDropdown, \
    SolveCaptcha, ExportFile
from .tools.util.selenium import set_selenium_config


class BrowsingAgent(Agent):

    def __init__(self, selenium_config=None, **kwargs):
        # Initialize tools in kwargs if not present
        if 'tools' not in kwargs:
            kwargs['tools'] = []
        # Add required tools
        kwargs['tools'].extend([Scroll, SendKeys, ClickElement, ReadURL, AnalyzeContent, GoBack, SelectDropdown,
                                SolveCaptcha, ExportFile, Retrieval])

        if 'description' not in kwargs:
            kwargs['description'] = "This agent is equipped with specialized tools to navigate and search the web effectively."

        # Set instructions
        if 'instructions' not in kwargs:
            kwargs['instructions'] = ("""You are an advanced browsing agent equipped with specialized tools to navigate 
and search the web effectively. Your primary objective is to fulfill the user's requests by efficiently 
utilizing these tools. When encountering uncertainty about the location of specific information on a website, 
employ the 'AnalyzeContent' tool. Remember, you can only open and interact with 1 web page at a time. Do not try to read 
or click on multiple links. Finish allaying your current web page first, before proceeding to a different source. 
Don't try to guess the direct url, always perform a google search if applicable, or return to your previous search results. 
In case if you need to analyze the full web page, use the 'ExportFile' tool to add it to myfiles_browser for further analysis."""
                                  .replace("\n", ""))

        if selenium_config is not None:
            set_selenium_config(selenium_config)

        # Initialize the parent class
        super().__init__(**kwargs)


