import re
from .User import UserStatuses

maxLengthOfName = 32
maxLengthOfAnswer = 32
stop_word = "стоп"

langs = ('rus')

registration = {
	"hello": [
		"Приветствую тебя!\nНастало время зарегистрироваться на QR-квест :-)"
		],
	"enter_name": [
		"Как тебя зовут?"
	],
	"happy_reg": [
		"Круто! Теперь ты участник QR-квеста - поздравляю!"
	],
	"happy_reg_bonus": [
		"Cчитай, что нулевое (мы же - айтишники) задание ты выполнил.\nЗа успешное выполнения заданий тебе будут начисляться баллы." + \
		"И вот первое начисление..."
	],
	"happy_reg_bonus_1": [
		"Еее))\n\nУзнать сумму своих баллов можно следующими способами:\n > командой /score\n> кнопкой 'Мои баллы'\n> напечатай мне букву 'Я'"
	]
}

start_command = {
	"is_regitered": [
		"Ты уже зарегистрирован на QR-квест :-)\nМожешь приступать к выполнению тасков."
	]
}

help_text = [
	"Здесь описываются доступные тебе команды\n\n" + \
	"-----\n\n" + \
	"Самая первая команда:\n\n" + \
	"/start - регистрация на QR-квест и/или приветствие от бота.\n\n" + \
	"-----\n\n" + \
	"Следующими командами ты можешь посмотреть различную информацию о себе и соревновании:\n\n" + \
	"/me - вывод информации о тебе; вывод твоей статистики.\n\n" + \
	"/score - вывод твоего текущего количества баллов.\n\n" + \
	"/stats - вывод общей статистики по соревнованию"
]

task_presentation = {
	"start": [
		"Таск №"
	],
	"start_1": [
		"\n\n\n"
	],
	"answer_start": [
		"\nОтправь "
	],
	"answer_plain_abc": [
		"слово.\n"
	],
	"answer_send": [
		"Чтобы ответить, отправь его мне"
	],
	"answer_stop": [
		'\n\n! Отправь слово "стоп", чтобы выйти из режима ответа'
	],
	"already_answer": [
		"Ты уже отвечал на этот таск (№"
	],
	"already_answer_1": [
		")\n\nПонимаю твое рвение отправить на него ответ еще раз,\nно увы - так нельзя. Программа такая."
	],
}

task_answer = {
	"start": [
		"Я проверил твой ответ на таск №"
	],
	"ok": [
		"Отлично!\nТвой ответ сошелся с моими ожиданиями XD"
	],
	"not_ok": [
		"Увы...\n Здесь ты допустил ошибку :("
	],
	"points": [
		"\n\nЗа этот таск я тебе начисляю столько баллов:\n->      "
	]
}

status = {
	"ready": [
		"Готов к решению тасков"
	],
	"sends_name": [
		"Отправляет свое имя"
	],
	"sends_answer": [
		"Отправляет ответ на таск №"
	],
	"sends_taskid": [
		"Отправляет номер таска"
	]
}

me_command = {
	"start": [
		"Информация о тебе:\n\n"
	],
	"name": [
		"Для всех участников тебя зовут:\n-> "
	],
	"status": [
		"\n\nТвой текущий статус:\n-> "
	],
	"score": [
		"\n\nТвой текущий счет:\n-> "
	],
	"task": [
		"\n\nТы ответил на тасков:\n-> "
	],
	"task_1": [
		" из "
	],
	"task_2": [
		"\n\nИз них:"
	],
	"task_ok": [
		"\nПравильно: "
	],
	"task_notok": [
		"\nНеправильно: "
	],
	"rating": [
		""
	]
}

task_command = {
	"enter": [
		"Введи номер таска:"
	]
}

others = {
	"ready": [
		"Хмм.. Это мне пока трудно понять. Может быть когда-нибудь я научусь общаться не по программе..." + \
		"\n\n В любом случае команда /help может тебе помочь))"
	],
	"sends_name": [
		"Принято! Теперь я знаю как к тебе обращаться.\n\n" + \
		"Меня можешь звать просто - Собеседник.\n" + \
		"Или - Бот.\n" + \
		"Или все таки Собеседник??\n\n" + \
		"Хмм, не знаю... У меня одновременно и много имен, и имени нет.\n" + \
		"Так и существую ;-)"
	],
	"answer_stop": [
		"Ок.\nНе волнуйся, ты сможешь снова вызвать этот таск и ответить на него тогда, когда тебе будет удобно."
	]
}

errors = {
	"test": "Test Error, ahahaha!"
}


def get_validated_name(text):
	if len(text) > maxLengthOfName: 
		return text[:maxLengthOfName]
	else:
		return text


def get_validated_answer(text):
	if len(text) > maxLengthOfAnswer: 
		return text[:maxLengthOfAnswer]
	else:
		return text


def getTaskIDFromText(text):
	response = None
	text = get_validated_answer(text)

	if str(text).isdigit():
		response = int(text)

	return response


def getTaskIDFromStart(start_message_argument):
		response = None

		if re.match("^task_\\d{,4}$", start_message_argument):
			task_number = start_message_argument[5:]
			if task_number.isdigit():
				response = int(task_number)

		return response
