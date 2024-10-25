from core.langchain_prompts import DefaultPrompt

r = DefaultPrompt.invoke(
    {
        "text":"what transportation should i use to go from uttara, dhaka, bangladesh to chittagong, bangladesh? please search on shohoz.com for this"
    }
)

print(r.content)

# from core.langchain_init import tool

# print(tool.run("what transportation should i use to go from uttara, dhaka, bangladesh to chittagong, bangladesh? please search on shohoz.com for this"))
# from core.search_agent import SearchAgent

# from core.search_agent import SearchAgent
# agent = SearchAgent()

# # Example query
# response = agent.ask("what transportation should i use to go from uttara, dhaka, bangladesh to chittagong, bangladesh? what are the fees and estimated time? also tell me schedules")
# print(response)

# from core.serper_agent import agent

# print(
#     agent.run(
#         "What are some restaurants near Mirpur 2, Dhaka, Bangladesh?"
#     )
# )
