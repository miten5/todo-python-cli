import typer
from colorama import Fore
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from tabulate import tabulate
import os

load_dotenv()

app = typer.Typer()

@app.command()
def addtodo():
    while(True):    
        title = input("Enter title: ")
        description = input("Enter description: ")
        priority = input(f"What is prioriy {Fore.RED}(options: 1,2,3,4 or Enter to skip){Fore.RESET}: ")
        due_date = input(f"Due date {Fore.RED}(eg. DD/MM/YYYY hh:mm or Enter to skip){Fore.RESET}: ")
        
        # print("\n")
        add_more = input("\nDo you want to add more todo? (Yes/Y): ")
        
        if(add_more.lower() == "yes" or add_more.lower() == "y"):
            continue
        else:
            break
    
    print(f"{Fore.GREEN}{title}{Fore.RESET}")


@app.command()
def showtodo():
    database = mongoConnection()
    
    todos = database.get_collection('todo').find()
    
    header = [x.title().replace('_', " ").strip() for x in todos[0].keys()]
    rows =  [x.values() for x in todos]
    
    print(tabulate(rows, header,tablefmt='orgtbl'))
    
@app.command()
def updatetodo(id: str, completed: bool = False):
    return 

@app.command()
def deleretodo(id: str):
    return

def mongoConnection():
    # Create a new client and connect to the server
    client = MongoClient(os.environ['MONGOURL'])
    try:
        return client.get_database('todoApp')

    except Exception as e:
        print(e)
    
# App will run from here...
if __name__ == "__main__":
    app()