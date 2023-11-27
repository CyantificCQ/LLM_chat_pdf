import sys
import os
from dotenv import load_dotenv
from openai import OpenAI


class Chat:


    
    def get_path(self):
        import os
        current = os.path.dirname(os.path.realpath("llm_chatbot_fastapi"))
        parent = os.path.dirname(os.path.dirname(current))
        env_path = os.path.join(parent + "\\Secret" + "\\.env")
        sys.path.append(env_path)
        
        if load_dotenv(dotenv_path=env_path):
            api_key = os.getenv("OPENAI_API_KEY")
            return api_key
        else:
            return False
            
    
    def chatbot(self, prompt):

        api_key = self.get_path()

        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
            ])
        
        return response.choices[0].message.content.strip()

if __name__ == "__main__":

    llm_chat = Chat()

    while True:
        user_input = input("Human: ")
        if user_input.lower() in ["quit", "close", 'exit', "bye"]:
            break 
        response = llm_chat.chatbot(user_input)
        print("Chatbot:", response)  # noqa: E999



# def get_path():
#     import os
#     current = os.path.dirname(os.path.realpath("llm_chatbot_fastapi"))
#     parent = os.path.dirname(os.path.dirname(current))
#     env_path = os.path.join(parent + "\\Secret" + "\\.env")can you
#     sys.path.append(env_path)
    
#     if load_dotenv(dotenv_path=env_path):
#         api_key = os.getenv("OPENAI_API_KEY")
#         return api_key
#     else:
#         return False
    

    # if load_dotenv(dotenv_path=env_path) is True:
    #     api_key = os.getenv("OPENAI_API_KEY")
    #     return env_path, api_key
    # else:
    #     return "I cant reach/read whatever the api key"
