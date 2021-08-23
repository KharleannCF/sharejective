from telegram.ext import (
    Updater,
    MessageHandler,
    Filters,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
)
from uuid import uuid4
from telegram import (
    ForceReply,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from threading import Event
import threading
import pymongo
from bson.objectid import ObjectId
import datetime
import os
from dotenv import load_dotenv
import requests


def unsubscribe(update, context):
    users.find_one_and_update(
        {"chatId": update.effective_chat.id}, {"subscribed": False}
    )

def petitionThread(link):
    while True:
        requests.get(link)
        event.wait(600)



def start(update, context):
    users.insert(
        {
            "chatId": update.effective_chat.id,
            "name": update.message.from_user.name,
            "subscribed": True,
        }
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Soy Sharejective, tu aliado en tus objetivos.",
    )
    event.wait(1)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Para comenzar vamos a crear una tarea, para hacer esto puedes toca el botón de "Agregar Tarea" que aparece abajo',
    )
    event.wait(1.5)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Tambien puedes iniciar la creación de una tarea respondiendo al próximo mensaje.",
    )
    event.wait(1.5)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Tambien puedes iniciar la creación de una tarea respondiendo al próximo mensaje.",
    )
    event.wait(1)
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Tarea:", reply_markup=ForceReply()
    )


def getAllTask(update, context):
    taskList = col.find({"chatId": update.effective_chat.id})
    for task in taskList:
        editTaskKeyboard = [
            [
                InlineKeyboardButton(
                    "Completar",
                    callback_data=f"TASK>complete>{task['_id']}>{task['task']}",
                ),
                InlineKeyboardButton(
                    "Editar", callback_data=f"TASK>edit>{task['_id']}>{task['task']}"
                ),
                InlineKeyboardButton(
                    "Borrar", callback_data=f"TASK>delete>{task['_id']}>{task['task']}"
                ),
            ],
        ]
        text = "esta completada" if task["complete"] else "no esta completada"
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"{task['task']} actualmente {text}",
            reply_markup=InlineKeyboardMarkup(editTaskKeyboard),
        )
        event.wait(0.75)
    return


def addTask(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Tarea:", reply_markup=ForceReply()
    )


def normal_message(update, context):
    if update.message.reply_to_message:
        messageReply(update, context)
        return
    if update.message.text == "Listar Tareas":
        # listar tareas
        getAllTask(update, context)
    elif update.message.text == "Agregar Tarea":
        addTask(update, context)
    elif update.message.text == "Info":
        infoMessage(update, context)

def infoMessage(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Este Bot fue creado por Kharleann Cabrera, puedes encontrarme por @KharleannCF en la mayoria de las redes sociales."
    )
    event.wait(1)
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Puedes escribirme cualquier duda, recomendación o feedback, todo será bien recibido."
    )
    event.wait(1)
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="tambien puedes escribirme a khakan@hotmail.es para consultas más personales."
    )
    event.wait(1)
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Muchas gracias por usar mi chatbot."
    )
    event.wait(1)
    basicStateMessage(update, context)


def button(update, context) -> None:
    query = update.callback_query
    task = {}
    if "but-" in query.data:
        task = col.find_one({"_id": usersActualTasks[update.effective_chat.id]["id"]})
    if query.data == "but-repeat":
        query.edit_message_text(
            text=f"Escogiste cambiar la frecuencia de la tarea {usersActualTasks[update.effective_chat.id]['task']}"
        )
        taskText = task["task"]
        if task["repeat"]:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Cambiaste {taskText} para ser una tarea no repetida",
            )
            col.find_one_and_update(
                {"_id": usersActualTasks[update.effective_chat.id]["id"]},
                {"$set": {"repeat": False}},
            )
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Cambiaste {taskText} para ser una tarea repetida",
            )
            col.find_one_and_update(
                {"_id": usersActualTasks[update.effective_chat.id]["id"]},
                {"$set": {"repeat": True}},
            )

    elif query.data == "but-time":
        query.edit_message_text(
            text=f"Escogiste configurar un recordatorio para que te recordemos está tarea {usersActualTasks[update.effective_chat.id]['task']}"
        )
        if task["time"] == "":
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Actualmente fijaste una hora para el recordatorio de esta tarea.",
            )
            event.wait(1)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"pero... podemos solucionar esto!",
            )
            event.wait(0.7)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Por favor dime en cuantas horas te gustaria el recordatorio.",
            )
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Toma en cuenta que a las 00:00 UTC los recordatorios serán eliminados.",
            )

            event.wait(0.7)
            event.wait(0.7)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"responde el siguiente mensaje usando un número entre 0 y 24.",
            )
            event.wait(1)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Hora:",
                reply_markup=ForceReply(),
            )
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Lastimosamente por ahora no podemos cambiar los recordatorios :( ",
            )
            basicStateMessage(update, context)
    elif query.data == "but-completed":
        query.edit_message_text(
            text=f"Escogiste cambiar el estado de la tarea {usersActualTasks[update.effective_chat.id]['task']}"
        )
        completeTask(update, context)

    elif query.data == "but-why":
        query.edit_message_text(
            text=f"Escogiste cambiar la motivación de esta tarea '{usersActualTasks[update.effective_chat.id]['task']}'"
        )
        if task["motive"] == "":
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Actualmente no me contaste tu motivación.",
            )
            event.wait(0.7)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Cuando las cosas se pongan difíciles siempre podemos recordar esto.",
            )
            event.wait(1)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Para qué quieres '{usersActualTasks[update.effective_chat.id]['task']}'",
            )
            event.wait(1)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Motivo:",
                reply_markup=ForceReply(),
            )
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Actualmente tu motivación para esta tarea es",
            )
            event.wait(0.7)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f" {task['motive']}.",
            )
            event.wait(1)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Sin embargo esto evolucionó.",
            )
            event.wait(0.8)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"¡Eso es genial!",
            )
            event.wait(1)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"¿Cuál es tu motivo?",
            )
            event.wait(0.5)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Motivo:",
                reply_markup=ForceReply(),
            )
    elif query.data == "but-no-conf":
        basicStateMessage(update, context)
    elif "TASK>" in query.data:
        taskData = query.data.split(">")
        action = taskData[1]
        usersActualTasks[update.effective_chat.id] = {
            "id": ObjectId(taskData[2]),
            "task": taskData[3],
        }
        print(taskData, usersActualTasks[update.effective_chat.id]["id"])
        task = col.find_one({"_id": usersActualTasks[update.effective_chat.id]["id"]})
        print(task)
        if action == "delete":
            deleteTask(update, context)
        elif action == "edit":
            editTask(update, context)
        elif action == "complete":
            completeTask(update, context)


def editTask(update, context):
    reply_markup = InlineKeyboardMarkup(editTaskKeyboard)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Deseas configurar alguna de estas opciones?",
        reply_markup=reply_markup,
    )


def deleteTask(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Dame un segundo para borrar la tarea."
    )
    col.delete_one({"_id": usersActualTasks[update.effective_chat.id]["id"]})
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Listo, un pendiente menos que realizar."
    )
    event.wait(1)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Ahora tenemos que regresar al trabajo, queda mucho por hacer.",
    )
    event.wait(1)
    basicStateMessage(update, context)


def changeTaskStatus(taskText, chatID, status):
    col.find_one_and_update(
        {"chatId": chatID, "task": taskText},
        {"$set": {"complete": status}},
    )


def completeTask(update, context):
    task = col.find_one({"_id": usersActualTasks[update.effective_chat.id]["id"]})
    print(task)
    taskText = task["task"]
    if task["complete"]:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Marcaste '{taskText}' como tarea no completada",
        )
        event.wait(1)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"En las configuraciones de la tarea puedes solicitar que te la recordemos a diario.",
        )
        changeTaskStatus(task["task"], update.effective_chat.id, False)

    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"¡Felicidades completaste '{taskText}'!",
        )
        changeTaskStatus(task["task"], update.effective_chat.id, True)
        basicStateMessage(update, context)


def messageReply(update, context):
    if update.message.reply_to_message.text == "Tarea:":
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="Procederemos a guardar la tarea"
        )
        saveTask(update.effective_chat.id, update.message.text)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Puedes configurar la tarea a continuación",
        )
        event.wait(0.5)
        reply_markup = InlineKeyboardMarkup(editTaskKeyboard)
        update.message.reply_text(
            "Deseas configurar alguna de estas opciones?", reply_markup=reply_markup
        )
    elif update.message.reply_to_message.text == "Hora:":
        time = update.message.text
        try:
            hour = int(time)
        except:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Hubo algún problema recibiendo la hora.",
            )
            event.wait(0.7)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"responde el siguiente mensaje usando un número.",
            )
            event.wait(1)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Hora:",
                reply_markup=ForceReply(),
            )
            return
        setReminder(update, context)
        col.find_one_and_update(
            {"_id": usersActualTasks[update.effective_chat.id]["id"]},
            {"$set": {"time": f"{hour}:0"}},
        )
        basicStateMessage(update, context)
    elif update.message.reply_to_message.text == "Motivo:":
        col.find_one_and_update(
            {"_id": usersActualTasks[update.effective_chat.id]["id"]},
            {"$set": {"motive": f"{update.message.text}"}},
        )
        basicStateMessage(update, context)


def basicStateMessage(update, context):
    generalMenu = ReplyKeyboardMarkup(GeneralTaskKeyboard)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Que deseas hacer por ahora?",
        reply_markup=generalMenu,
    )


def saveTask(chatId, task):
    taskDic = {
        "chatId": chatId,
        "task": task,
        "repeat": False,
        "motive": "",
        "complete": False,
        "time": "",
    }
    inserted = col.insert_one(taskDic)
    usersActualTasks[chatId] = {
        "id": inserted.inserted_id,
        "task": task,
    }
    return inserted


def setReminder(update, context):
    seconds = int(update.message.text) * 3600
    queuer.run_once(reminderTask(update, context), when=seconds)


def reminderTask(update, context):

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"¡Hey, me pediste que te recordara { usersActualTasks[update.effective_chat.id]['task']} ahora!",
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=f"¡Es hora de trabajar!"
    )
    basicStateMessage(update, context)


def put(update, context):
    key = str(uuid4())
    value = update.message.text.partition(" ")[2]
    context.user_data[key] = value
    update.message.reply_text(key)


def get(update, context):
    key = context.args[0]
    value = context.user_data.get(key, "Not found")
    update.message(reply_text(value))


def dailyReminder(context: CallbackContext):
    subscribedUsers = users.find({"subscribed": True})
    for user in users:
        tasks = col.find({"chatId": user["chatId"], "complete": False})
        context.bot.send_message(
            chat_id=user["chatId"],
            text="Tienes las siguientes tareas pendientes de ayer",
        )
        for task in tasks:
            context.bot.send_message(chat_id=user["chatId"], text=task["task"])
    generalMenu = ReplyKeyboardMarkup(GeneralTaskKeyboard)
    context.bot.send_message(
        chat_id=user["chatId"], text="Es hora de trabajar", reply_markup=generalMenu
    )


start_handler = CommandHandler("start", start)
unsubscribe_handler = CommandHandler("Desubscribir", unsubscribe)
echo_handler = MessageHandler(Filters.text & (~Filters.command), normal_message)


if __name__ == "__main__":
    load_dotenv()
    TOKEN= os.getenv("TOKEN")
    updater = Updater(token=TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(echo_handler)
    dispatcher.add_handler(unsubscribe_handler)
    dispatcher.add_handler(CallbackQueryHandler(button))
    event = Event()
    queuer = updater.job_queue
    conn_str = os.getenv("ATLAS")
    client = pymongo.MongoClient(conn_str, serverSelectionTimeoutMS=5000)
    db = client["ShareJective"]
    try:
        print(client.server_info())
    except:
        print("There was an error connecting with the database.")
    col = db["Tasks"]
    users = db["Users"]
    """
    Tarea Dictionary: {
        action: job that must be done,
        completed: If the action is completed
        recurrent: if the task can be repeated
        chatID: the id of the user that created the task
        time: reminder time of the action
    }
    """
    usersActualTasks = {}
    editTaskKeyboard = [
        [
            InlineKeyboardButton("Repetición", callback_data="but-repeat"),
            InlineKeyboardButton("Hora", callback_data="but-time"),
            InlineKeyboardButton("Completada", callback_data="but-completed"),
        ],
        [
            InlineKeyboardButton("Por qué haces la tarea?", callback_data="but-why"),
            InlineKeyboardButton("No", callback_data="but-no-conf"),
        ],
    ]
    testkeys = []
    testkeys.append([])
    for i in range(200):
        testkeys[0].append(KeyboardButton(text=str(i)))
    GeneralTaskKeyboard = [
        [
            KeyboardButton(text="Listar Tareas"),
            KeyboardButton(text="Agregar Tarea"),
        ],
        [KeyboardButton(text="Info")],
    ]
    queuer.run_daily(
        dailyReminder,
        days=(0, 1, 2, 3, 4, 5, 6),
        time=datetime.time(hour=6, minute=00, second=00),
    )
    PORT = 443
    #updater.start_polling()
    HEROKULINK = os.getenv("HEROKULINK")
    PORT = int(os.environ.get("PORT", "8443"))
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN,
                          webhook_url=HEROKULINK+TOKEN)
    #updater.start_webhook(listen="0.0.0.0", port=int(PORT), url_path=TOKEN)
    demon = threading.Thread(target=petitionThread, args=(HEROKULINK,), daemon=True)
    demon.start()
    updater.idle()
