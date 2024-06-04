import bson.objectid
import bson.timestamp
import typer
from datetime import datetime
from colorama import Fore
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from tabulate import tabulate
import bson
import os

load_dotenv()

app = typer.Typer()

@app.command()
def addtodo():
    while(True):    
        title = input(f"{Fore.RED}*{Fore.RESET}Enter title: ")
        
        if(title == ""):
            print(f"{Fore.RED}Please enter title{Fore.RESET}")
            continue
        
        description = input("Enter description: ")
        priority = input(f"What is prioriy {Fore.RED}(options: 1,2,3,4){Fore.RESET}: ")
                
        if priority not in [1,2,3,4]:
            priority = None
        else:
            priority = int(priority)
            
        
        due_date = input(f"Due date {Fore.RED}(format: YYYY-MM-DD hh:mm:ss){Fore.RESET}: ")

        if(due_date != "" and len(due_date.split(" ")) > 1):
            date = due_date.split(" ")
            if(len(date[0].split("-")) == 3 and len(date[1].split(":")) == 3):        
                due_date = int(datetime.strptime(due_date, '%Y-%m-%d %H:%M:%S').timestamp())
                due_date = bson.timestamp.Timestamp(due_date,1)
            else:
                due_date = None
        else:
            due_date = None
                
        # add to database
        database = mongoConnection()
        todos = database.get_collection('todo')
        
        added = todos.insert_one({
            "title": title,
            "description": description,
            "priority": priority,
            "completed": False,
            "due_date": due_date
        })
        
        if(added.inserted_id):
            print(f"\n{Fore.GREEN}ToDo successfully added.{Fore.RESET}")
        
        add_more = input("\nDo you want to add more todo? (Yes/Y): ")
        
        if(add_more.lower() == "yes" or add_more.lower() == "y"):
            continue
        else:
            break


@app.command()
def showtodo():
    database = mongoConnection()
    
    pipeline = [
        {
            "$set": {
                "due_date": {
                    "$ifNull": [
                        { "$toDate": "$due_date" },
                        None
                    ]
                }
            }
        },
        {
          "$match": {
              "completed": False
          }
        },
        {
            "$project": {
                "title": 1,
                "description": 1,
                "completed": 1,
                "priority": {
                    "$ifNull": ["$priority", None]
                },
                "due_date": 1,
                    
            }  
        },
        {
            "$sort": {
                "priority": -1
            }
        }
    ] 
    
    todos = list(database.todo.aggregate(pipeline))
    
    header = [x.title().replace('_', " ").strip() for x in todos[0].keys()]
    rows =  [x.values() for x in todos];
    
    print(tabulate(rows, header,tablefmt='orgtbl'))
    
    update_todo = input("\nDo you want to mark todo as completed? (Y/N): ");
    
    if(update_todo.lower() == "yes" or update_todo.lower() == "y"):
        _id = input("Please provide Id of todo to mark as completed: ")
        
        if(_id != ""):
            updatetodo(_id, True)
        
@app.command()
def updatetodo(id: str, completed: bool = False):
    
    database = mongoConnection()
    
    all_todo = database.todo.update_one({'_id': bson.ObjectId(id)}, {
        "$set": {
            "completed": completed
        }
    })
    
    print("\n successfully mark completed.")

    return 

@app.command()
def deletetodo(id: str):
    database = mongoConnection()
    
    all_todo = database.todo.delete_one({'_id': bson.ObjectId(id)})
    
    print("\nTodo successfully deleted.")
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