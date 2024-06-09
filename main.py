from quart import Quart, request, render_template, make_response
from sqlite3 import connect

database = connect("data/database.db")
database.execute("CREATE TABLE IF NOT EXISTS intents (intent TEXT PRIMARY KEY)")
database.execute("CREATE TABLE IF NOT EXISTS inputs (input TEXT UNIQUE, intent TEXT)")

app = Quart(__name__)


@app.get("/v1/intents")
async def get_intents():
    intents = database.execute("SELECT * FROM intents").fetchall()
    return intents


@app.post("/v1/intents")
async def create_intent():
    data = await request.form
    intent = database.execute("INSERT INTO intents VALUES(?)", (data['intent'],)).fetchone()
    database.commit()
    return {"input": intent}


@app.delete("/v1/intents/<intent>")
async def delete_intent(intent):
    intent = database.execute("DELETE FROM intents WHERE intent = ?", (intent,)).fetchone()
    database.execute("DELETE FROM inputs WHERE intent = ?", (intent,))
    database.commit()
    return {"input": intent}


@app.put("/v1/intents")
async def put_intent():
    data = await request.form
    intent = database.execute("UPDATE intents SET intent = ? WHERE input = ?", (data['intent'],
                                                                                data['input'])).fetchone()
    database.commit()
    return {"input": intent}


@app.get("/v1/training")
async def get_training():
    training = database.execute("SELECT * FROM inputs").fetchall()
    return training


@app.post("/v1/training")
async def post_training():
    data = await request.form
    data = database.execute("INSERT INTO inputs VALUES(?, ?)", (data['input'], data['intent'])).fetchone()
    database.commit()
    return {"input": data}


@app.delete("/v1/training/<input>")
async def delete_training(input: str):
    data = database.execute("DELETE FROM inputs WHERE input = ?", (input,)).fetchone()
    database.commit()
    return {"input": data}


@app.put("/v1/training/<input>")
async def put_training(input: str):
    data = await request.get_json()
    intent = database.execute("SELECT * FROM intents WHERE intent = ?", (data['intent'],)).fetchone()
    if not intent:
        database.execute("INSERT INTO intents VALUES(?)", (data['intent'],))
    data = database.execute("UPDATE inputs SET intent = ? WHERE input = ?", (data['intent'], input)).fetchone()
    database.commit()
    return {"input": data}


@app.get("/v1/export/csv")
async def get_csv_export():
    training = database.execute("SELECT * FROM inputs").fetchall()
    csvOutput = "content,label\r\n"
    for row in training:
        csvOutput += f"{row[0].replace(',', '')}, {row[1].replace(',', '')}\r\n"

    return await make_response(csvOutput, 200, {'Content-Type': 'text/csv'})


@app.get("/v1/export/jsonl")
async def get_json_export():
    training = database.execute("SELECT * FROM inputs").fetchall()
    jsonOutput = "\r\n"
    for row in training:
        content = row[0].replace('"', '')
        label = row[1].replace('"', '')
        jsonOutput += f"{{\"content\": \"{content}\", \"label\": \"{label}\"}},\r\n"

    jsonOutput = jsonOutput[:-3] + "\r\n"
    return await make_response(jsonOutput, 200, {'Content-Type': 'application/json'})


@app.route('/')
async def index():
    return await render_template('index.html')


def run() -> None:
    app.run()


run()
