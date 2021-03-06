from Penger.penger import Penger, Accordance
import tgbotSettings as tS

from time import sleep
import logging

from utils import UserStatuses, interlocutor


# parcipantList = ["some_id"]

p = Penger(token = tS.token)
p.senderWhitelist.append("test")
usersDB = None
tasksDB = None
solutionsDB = None

#
# Create a logger for the bot
#

formatter = logging.Formatter('[%(asctime)s]# %(levelname)-8s %(name)s: %(message)s')

handler = logging.FileHandler("bot.log")
handler.setFormatter(formatter)

log = logging.getLogger("Bot")
log.setLevel(logging.INFO)
log.addHandler(handler)

log.info('Hello!')


def isParcipant(tg_id):
	user = usersDB.getUserByTgId(tg_id)

	if user is None:
		return False
	else:
		return True


def getUser(tg_id):
	return usersDB.getUserByTgId(tg_id)


def isRegistrationEnabled():
	return True


def getUserStatusAsMessage(user):
	userStatus = user.getStatus()
	message = ""

	message += interlocutor.me_command['status'][0]

	if userStatus == UserStatuses.READY:
		message += interlocutor.status['ready'][0]
	elif userStatus == UserStatuses.SENDS_NAME:
		message += interlocutor.status['sends_name'][0]
	elif userStatus == UserStatuses.SENDS_ANSWER:
		message += interlocutor.status['sends_answer'][0]
		message += str(user.getTaskID())
	elif userStatus == UserStatuses.SENDS_TASKID:
		message += interlocutor.status['sends_taskid'][0]
	else:
		message += "Status not defined"

	return message


def printTask(task, user):
	message = ""

	# print('solutions', solutionsDB.isThereSolution(user, task))

	if not solutionsDB.isSolvedTaskByUser(user, task):
		message += task.getTaskAsMessage()

		user.changeStatus(UserStatuses.SENDS_ANSWER)
		user.changeTaskID(task.getID())
		usersDB.updateUser(user)
	else:
		# message += "You have already answered this task"

		message += interlocutor.task_presentation["already_answer"][0]
		message += str(task.getID())
		message += interlocutor.task_presentation["already_answer_1"][0]

		user.changeStatus(UserStatuses.READY)
		usersDB.updateUser(user)

	return message


def answer_stop(user):
	message = interlocutor.others['answer_stop'][0]

	user.changeStatus(UserStatuses.READY)
	usersDB.updateUser(user)
	
	return message


def processUserAnswer(vAnswer, user):
	message = ''

	task = tasksDB.getTaskById(user.getTaskID())

	if task is None:
		message = "This task no longer exists :-("
	else:
		isCorrect, points = task.processAnswer(vAnswer)
		tasksDB.updateCurrentCoastForTask(task)

		user.addPoints(points)
		user.changeStatus(UserStatuses.READY)
		usersDB.updateUser(user)

		solutionsDB.createAndAddNewSolution(user.getID(), task.getID(),
			points, isCorrect)

		message += interlocutor.task_answer['start'][0]
		message += str(task.getID()) + "\n\n"


		if isCorrect:
			message += interlocutor.task_answer['ok'][0]
		else:
			message += interlocutor.task_answer['not_ok'][0]

		message += interlocutor.task_answer['points'][0]
		message += str(points)

	return message


def taskIDEnter(text, user):
	botAnswer = ''

	taskID = interlocutor.getTaskIDFromText(text)

	if taskID is None:
		botAnswer = 'Error: Invalid link or parameter.'
	else:
		task = tasksDB.getTaskById(taskID)
		if task is None:
			botAnswer = 'Ahaha, 404 Error: Task not found.'
		else:
			botAnswer = printTask(task, user)

	return botAnswer


def registerNewUser(tg_id):
	log.info("Registering a new participant (tg-" + str(tg_id) + ")")

	p.sendMessage(tg_id, interlocutor.registration['hello'][0])
	sleep(0.1)

	p.sendMessage(tg_id, "Registration...")
	sleep(0.1)
	user = usersDB.createAndAddNewUser(tg_id)
	p.senderWhitelist.append(tg_id)

	print(user.dumpToDict())

	p.sendMessage(tg_id, interlocutor.registration['enter_name'][0])
	sleep(0.1)
	user.changeStatus(UserStatuses.SENDS_NAME)
	usersDB.updateUser(user)


def registrationClosed(tg_id):
	log.warning("Registration is closed for tg-" + str(tg_id))

	p.sendMessage(tg_id, "Hello!")


# def start_for_parcipant(tg_id):
# 	user = usersDB.getUserByTgId(tg_id)
# 	message = "Hello, "+user.getName()+"!\n\n"
# 	message += interlocutor.start_command["is_regitered"][0]
# 	p.sendMessage(user.tg_id, message)


def start_pCommand(self):
	tg_id = self.data["sender_id"]

	log.info("Starting <start_p> for tg-" + str(tg_id))

	if self.data['text'] == '/start':
		if isRegistrationEnabled():
			registerNewUser(tg_id)
		else:
			registrationClosed(tg_id)


def start_command(self):
	tg_id = self.data["sender_id"]
	user = getUser(tg_id)

	log.info("Starting <start> for user-" + str(user.getID()))
	log.info("<start> ->> user-" + str(user.getID()) + " ->> " + str(self.data))

	command_arr = self.data['text'].split()

	if len(command_arr) == 1:
		log.info("<start> ->> 'hello' for user-" + str(user.getID()))

		message = "Hello, "+user.getName()+"!\n\n"
		message += interlocutor.start_command["is_regitered"][0]
		p.sendMessage(user.tg_id, message)
	else:
		if command_arr[1][:4] == "task":
			print("Parsing start message: ", command_arr[1])

			taskID = interlocutor.getTaskIDFromStart(command_arr[1])

			log.info("<start> ->> task-" + str(taskID) + " for user-" + str(user.getID()))

			if taskID is None:
				log.warning("<start> ->> Invalid task-" + str(taskID) + "; user-" + str(user.getID()))
				p.sendMessage(tg_id, 'Error: Invalid link or parameter.')
			else:
				task = tasksDB.getTaskById(taskID)
				if task is None:
					log.warning("<start> ->> task-" + str(taskID) + " not found; user-" + str(user.getID()))
					p.sendMessage(tg_id, 'Ahaha, 404 Error: Task not found.')
				else:
					log.info("<start> ->> Send task-" + str(taskID) + " to user-" + str(user.getID()))
					response = printTask(task, user)
					p.sendMessage(tg_id, response)


			# print("Task ID:", taskID)
		else:
			log.warning("<start> ->> Invalid parameter; user-" + str(user.getID()))
			p.sendMessage(tg_id, 'I do not understand...')


def help_pCommand(self):
	tg_id = self.data["sender_id"]

	log.info("Starting <help_p> for tg-" + str(tg_id))

	p.sendMessageToChat(self.data, "This is help")


def help_command(self):
	tg_id = self.data["sender_id"]
	user = usersDB.getUserByTgId(tg_id)

	log.info("Starting <help> for user-" + str(user.getID()))

	p.sendMessageToChat(self.data, interlocutor.help_text[0])


def score_command(self):
	tg_id = self.data["sender_id"]
	user = usersDB.getUserByTgId(tg_id)

	log.info("Starting <score> for user-" + str(user.getID()))

	message = ''

	message += interlocutor.me_command['score'][0]
	message += str(user.getScore())

	p.sendMessageToChat(self.data, message)


def me_command(self):
	tg_id = self.data["sender_id"]
	user = usersDB.getUserByTgId(tg_id)

	log.info("Starting <me> for user-" + str(user.getID()))

	message = ''
	
	message += interlocutor.me_command['start'][0]

	message += interlocutor.me_command['name'][0]
	message += user.getName()

	message += getUserStatusAsMessage(user)

	message += interlocutor.me_command['score'][0]
	message += str(user.getScore())

	message += interlocutor.me_command['task'][0]
	message += str(solutionsDB.getNumberOfSolvedSolutionByUser(user))
	message += interlocutor.me_command['task_1'][0]
	message += str(tasksDB.getNumberOfAll())

	# message += interlocutor.me_command['task_2'][0]

	# message += interlocutor.me_command['task_ok'][0]
	# message += str(solutionsDB.getNumberOfSolvedSolutionByUser(user))

	# message += interlocutor.me_command['task_notok'][0]
	# message += str(solutionsDB.getNumberOfUnsolvedSolutionByUser(user))

	p.sendMessageToChat(self.data, message)


def stats_command(self):
	tg_id = self.data["sender_id"]
	user = usersDB.getUserByTgId(tg_id)

	log.info("Starting <stats> for user-" + str(user.getID()))

	message = ''

	message = "TOP-5 BY SCORE\n\n"
	message += "=========\n\n"

	a = usersDB.top10byScoreDict()
	print(a)

	if a is None:
		message += "There are no participants."
	else:
		for x in a.keys():
			u = usersDB.getUserById(x)
			message += u.getName() + ' ---> ' + str(a[x]) + '\n\n'

	p.sendMessageToChat(self.data, message)
	sleep(0.1)

	message = "TOP-5 BY CORRECT DECISIONS\n\n"
	message += "=========\n\n"




def task_command(self):
	tg_id = self.data["sender_id"]
	user = usersDB.getUserByTgId(tg_id)

	log.info("Starting <task> for user-" + str(user.getID()))

	message = ''

	message = interlocutor.task_command["enter"][0]

	user.changeStatus(UserStatuses.SENDS_TASKID)
	usersDB.updateUser(user)

	p.sendMessageToChat(self.data, message)


def empty_P(self):
	tg_id = self.data["sender_id"]

	log.info("Starting <_empty_p> for tg-" + str(tg_id))

	botAnswer = 'I do not understand...'

	p.sendMessageToChat(self.data, botAnswer)


def empty(self):
	tg_id = self.data["sender_id"]
	user = usersDB.getUserByTgId(tg_id)

	log.info("Starting <_empty> for user-" + str(user.getID()))

	message = self.data['text']

	botAnswer = "This is <empty> for parcipant."

	if len(message) > 0:
		if message[0] != "/":

			print(message)
			userStatus = user.getStatus()

			answer = "Status error.\nWrite to tech support - it's interesting."

			if userStatus == UserStatuses.READY:
				answer = interlocutor.others["ready"][0]

			elif userStatus == UserStatuses.SENDS_NAME:
				user.changeName(interlocutor.get_validated_name(message))
				user.changeStatus(UserStatuses.READY)
				usersDB.updateUser(user)
				answer = interlocutor.others["sends_name"][0]

			elif userStatus == UserStatuses.SENDS_ANSWER:
				if message.replace(" ", '').lower() == interlocutor.stop_word:
					answer = answer_stop(user)
				else:
					message = interlocutor.get_validated_answer(message)
					answer = processUserAnswer(message, user)

			elif userStatus == UserStatuses.SENDS_TASKID:
				answer = taskIDEnter(message, user)

			botAnswer = answer

	p.sendMessageToChat(self.data, botAnswer)


p.accordance = [
	Accordance('/start', start_command, 'gWhitelist:all', enableArgument=True,
		ifNotAuthorized = Accordance('/start', start_pCommand, "all:all",
			enableArgument=True)
		),
	Accordance('/help', help_command, 'gWhitelist:all', enableArgument=True,
		ifNotAuthorized = Accordance('/help', help_pCommand, "all:all",
			enableArgument=True)
		),
	Accordance('/me', me_command, 'gWhitelist:all', enableArgument=True),
	Accordance('/score', score_command, 'gWhitelist:all', enableArgument=True),
	Accordance('/stats', stats_command, 'gWhitelist:all', enableArgument=True),
	# Accordance('/task', task_command, 'gWhitelist:all', enableArgument=True)
]

p.emptyAccordance = Accordance('', empty, 'gWhitelist:all', enableArgument=True,
	ifNotAuthorized = Accordance('', empty_P, "all:all", enableArgument=True)
	)

# print(type(p.accordance[0].ifNotAuthorized))
# print(type(p.accordance[0]))
# print(isinstance(p.accordance[0].ifNotAuthorized, Accordance))


def main(u, t, s):
	global usersDB
	global tasksDB
	global solutionsDB
	usersDB = u
	tasksDB = t
	solutionsDB = s

	l = []
	for x in range(1, usersDB.getLastID()+1):
		_id = usersDB.getUserById(x).getTgID()
		l.append(int(_id))

	print(l)
	import sys
	print(sys.getsizeof(l))

	p.senderWhitelist.extend(l)

	while True:
		p.updateAndRespond()
		sleep(10)
		print("senderWhitelist:", p.senderWhitelist)


# if __name__ == '__main__':
# 	main()
