import re
import os, openai
from llama_index import GPTSimpleVectorIndex, SimpleDirectoryReader
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
from langchain import OpenAI, SQLDatabase, SQLDatabaseChain
from langchain.prompts.prompt import PromptTemplate

index = None
db_chain = None
db_chain2 = None
# set up the index, either load it from disk to create it on the fly
def initialise_index():
    global index
    global db_chain
    global db_chain2
    # if os.path.exists(os.environ["INDEX_FILE"]):
    #     index = GPTSimpleVectorIndex.load_from_disk(os.environ["INDEX_FILE"])
    # else:
    # documents = SimpleDirectoryReader(os.environ["LOAD_DIR"]).load_data()
    # index = GPTSimpleVectorIndex.from_documents(documents)

    #dburi = "sqlite:///C:/Users/sasachdeva/Desktop/FHL2/CSV/sales_data_database.db"
    dburi = "sqlite:///C:/Users/sasachdeva/Desktop/FHL Projects/FHL4/data/error_logs_database.db"
    db = SQLDatabase.from_uri(dburi)
    llm = OpenAI(temperature = 0)
    _DEFAULT_TEMPLATE = """Given an input question, first create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
    Use the following format:

    Question: "Question here"
    SQLQuery: "SQL Query to run"
    SQLResult: "Result of the SQLQuery"
    Answer: "Final answer here, SQLQuery: 'SQL Query to run'"

    Only use the following tables:

    {table_info}

    If someone asks for the table foobar, they really mean the employee table.

    Question: {input}"""
    PROMPT = PromptTemplate(
        input_variables=["input", "table_info", "dialect"], template=_DEFAULT_TEMPLATE
    )

    db_chain = SQLDatabaseChain(llm = llm, database = db, prompt = PROMPT, verbose = True)
    db_chain2 = SQLDatabaseChain(llm = llm, database = db, verbose = True)

# get path for GUI  
gui_dir = os.path.join(os.path.dirname(__file__), 'gui')  
if not os.path.exists(gui_dir): 
    gui_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gui')

# start server
server = Flask(__name__, static_folder=gui_dir, template_folder=gui_dir)

# initialise index
initialise_index()
print(index)

@server.route('/')
def landing():
    return render_template('index.html')

@server.route('/query', methods=['POST'])
def query():
    global index
    global db_chain
    global db_chain2
    message = ""
    sqlString = ""
    kustoString = ""
    data = request.json
    try:
        index = db_chain.run(data["input"])
        split_string = index.split("SQLQuery:")
        message = split_string[0].strip()
        sqlString = split_string[1].strip()
        kustoString = SQLToKusto(split_string[1].strip())
        # print("SQLString: ", sqlString)
        # print("KustoString: ", kustoString)
    except:
        index2 = db_chain2.run(data["input"])
        message = index2

    response = message
    print("Response: ", response)
    return jsonify({'query': data["input"], 
                    'response': str(message), 
                    'source': "Watchman for service",
                    'sqlString': str(sqlString),
                    'kustoString': str(kustoString) })


def extract_sql_query(index):
    pattern = r"SQLQuery:\s*'([^']+)'"
    match = re.search(pattern, index)
    if match:
        return match.group(1)
    else:
        return None

def SQLToKusto(sqlString):
    # print("Anubhuti "+sqlString)
    prompt1 = """### Write Kusto query for the following SQL query
    #
    #SQL Query: {sqlString}
    #
    #
    """
    prompt2 = """### Write Kusto query for the following SQL query
    #
    # SQL Query: {}
    #
    #
    """.format(sqlString)
    print("prompt2: ", prompt2)
    openai.api_key = os.getenv('OPENAI_API_KEY')
    response = openai.Completion.create(
        model = 'text-davinci-003',
        prompt = prompt2,
        temperature = 0,
        max_tokens = 150,
        top_p = 1.0,
        frequency_penalty = 0,
        presence_penalty = 0,
        stop = ['#', ';']
    )
    res = response['choices'][0]['text']
    print("res: ", res)
    return res
    