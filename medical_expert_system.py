import threading
import time

from pyknow import DefFacts, Fact, KnowledgeEngine, MATCH, NOT, Rule, W
from websocket_server import WebsocketServer

YES = 'так'
NO = 'ні'
CLIENT = None
MESSAGE_RECEIVED_CONDITION = threading.Condition()
MESSAGE_RECEIVED_TEXT = None
QUESTION_NUMBER = 0


def _read_diets_list() -> list:
    with open('diets.txt') as diets:
        diets_list = diets.read().split('\n')
    return diets_list


def preprocess():
    symptom_map = {}
    d_desc_map = {}
    diets_list = _read_diets_list()
    for diet in diets_list:
        with open('answers/' + diet + '.txt') as symptom_file:
            s_list = symptom_file.read().split('\n')
            symptom_map[str(s_list)] = diet

        with open('diet_descriptions/' + diet + '.txt') as desc_file:
            d_desc_map[diet] = desc_file.read()
    return symptom_map, d_desc_map


def send_to_websocket(text):
    global QUESTION_NUMBER
    print(f'send_to_websocket: {text}')

    # wait for connection
    while not CLIENT:
        print('There is no client, gonna sleep')
        time.sleep(1)

    # if the text is an expert system result then send it without the number
    # if the text is initial message then send it without the number
    # else send it as a question with number
    if text.startswith('Result: '):
        result = text.lstrip('Result: ')
        server.send_message(CLIENT, result + '<br><br> <b>TO CONTINUE, RELOAD THIS PAGE<b>')
    elif text.startswith('Initial: '):
        result = text.lstrip('Initial: ')
        server.send_message(CLIENT, result + '<br><br> <b>TO CONTINUE, SEND SOMETHING <b>')
    else:
        QUESTION_NUMBER += 1
        server.send_message(CLIENT, str(QUESTION_NUMBER) + ') ' + text)

    # wait for answer
    with MESSAGE_RECEIVED_CONDITION:
        MESSAGE_RECEIVED_CONDITION.wait()



    # return answer to rule question
    print()
    print(f'QUESTION = {text}')
    print(f'MESSAGE_RECEIVED_TEXT = {MESSAGE_RECEIVED_TEXT}')
    print()
    return MESSAGE_RECEIVED_TEXT


class Greetings(KnowledgeEngine):
    SYMPTOM_MAP, D_DESC_MAP = preprocess()

    @DefFacts()
    def _initial_action(self):
        send_to_websocket(
            "Initial: Hi! I am Dr.Yar, I am here to help you make your health better. For that you'll have to answer a few "
            "questions about your conditions Do you feel any of the following symptoms:")
        yield Fact(action='find_diet')

    @Rule(Fact(action='find_diet'), NOT(Fact(slimming=W())), salience=1)
    def question_1(self):
        self.declare(Fact(slimming=send_to_websocket('Чи ви хочете схуднути?: ')))

    @Rule(Fact(action='find_diet'), NOT(Fact(vegetarianism=W())), salience=1)
    def question_2(self):
        self.declare(Fact(vegetarianism=send_to_websocket('Чи ви веган?: ')))

    @Rule(Fact(action='find_diet'), NOT(Fact(gluten=W())), salience=1)
    def question_3(self):
        self.declare(Fact(gluten=send_to_websocket('Чи маєте ви непереносимість глютену?: ')))

    @Rule(Fact(action='find_diet'), NOT(Fact(diabetes=W())), salience=1)
    def question_4(self):
        self.declare(Fact(diabetes=send_to_websocket('Чи є у вас діабет?: ')))

    @Rule(Fact(action='find_diet'), NOT(Fact(activity=W())), salience=1)
    def question_5(self):
        self.declare(Fact(activity=send_to_websocket('Чи регулярно ви займаєтеся фізичною активністю?: ')))

    @Rule(Fact(action='find_diet'), NOT(Fact(all_products=W())), salience=1)
    def question_6(self):
        self.declare(Fact(all_products=send_to_websocket('Ви вживаєте продукти без обмежень?: ')))

    @Rule(Fact(action='find_diet'), NOT(Fact(dietary_restrictions=W())), salience=1)
    def question_7(self):
        self.declare(Fact(dietary_restrictions=send_to_websocket('Чи маєте ви особливі дієтичні обмеження?: ')))

    @Rule(Fact(action='find_diet'), NOT(Fact(activity_evaluation=W())), salience=1)
    def question_8(self):
        self.declare(
            Fact(activity_evaluation=send_to_websocket('Ви високо оцінюєте свою активність на роботі чи вдома?: ')))

    @Rule(Fact(action='find_diet'), NOT(Fact(allergy=W())), salience=1)
    def question_9(self):
        self.declare(Fact(allergy=send_to_websocket('Чи маєте ви алергії на певні продукти чи речовини?: ')))

    @Rule(Fact(action='find_diet'), NOT(Fact(unhealthy_food=W())), salience=1)
    def question_10(self):
        self.declare(Fact(unhealthy_food=send_to_websocket('Ви вживаєте нездорову їжу?: ')))

    @Rule(Fact(action='find_diet'), NOT(Fact(muscle_mass=W())), salience=1)
    def question_11(self):
        self.declare(Fact(muscle_mass=send_to_websocket("Чи прагнете ви набрати м'язову масу?: ")))

    @Rule(Fact(action='find_diet'), NOT(Fact(better_health=W())), salience=1)
    def question_12(self):
        self.declare(Fact(better_health=send_to_websocket("Ви маєте за мету покращити своє здоров'я?: ")))

    @Rule(Fact(action='find_diet'), NOT(Fact(medical_restrictions=W())), salience=1)
    def question_13(self):
        self.declare(
            Fact(medical_restrictions=send_to_websocket(
                'Чи є у вас особливі дієтичні обмеження через медичні показання?: '))
        )

    @Rule(Fact(action='find_diet'), NOT(Fact(calories=W())), salience=1)
    def question_14(self):
        self.declare(Fact(calories=send_to_websocket('Чи ви приділяєте увагу кількості споживаних калорій?: ')))

    @Rule(Fact(action='find_diet'), NOT(Fact(organic_products=W())), salience=1)
    def question_15(self):
        self.declare(
            Fact(organic_products=send_to_websocket('Чи ви приділяєте увагу вживанню органічних продуктів?: ')))

    # slimming, vegetarianism, gluten, diabetes, activity, all_products, dietary_restrictions, activity_evaluation,
    # allergy, unhealthy_food, muscle_mass, better_health, medical_restrictions, calories, organic_products
    @Rule(
        Fact(action='find_diet'), Fact(slimming=YES), Fact(vegetarianism=YES), Fact(gluten=YES),
        Fact(diabetes=NO), Fact(activity=YES), Fact(all_products=NO), Fact(dietary_restrictions=YES),
        Fact(activity_evaluation=NO), Fact(allergy=YES), Fact(unhealthy_food=YES), Fact(muscle_mass=NO),
        Fact(better_health=YES), Fact(medical_restrictions=YES), Fact(calories=NO), Fact(organic_products=YES)
    )
    def diet_1(self):
        self.declare(Fact(diet='vegan_diet'))

    @Rule(
        Fact(action='find_diet'), Fact(slimming=YES), Fact(vegetarianism=NO), Fact(gluten=NO),
        Fact(diabetes=NO), Fact(activity=YES), Fact(all_products=NO), Fact(dietary_restrictions=YES),
        Fact(activity_evaluation=YES), Fact(allergy=NO), Fact(unhealthy_food=YES), Fact(muscle_mass=NO),
        Fact(better_health=NO), Fact(medical_restrictions=NO), Fact(calories=NO), Fact(organic_products=NO)
    )
    def diet_2(self):
        self.declare(Fact(diet='usual_diet'))

    @Rule(
        Fact(action='find_diet'), Fact(slimming=YES), Fact(vegetarianism=YES), Fact(gluten=YES),
        Fact(diabetes=NO), Fact(activity=YES), Fact(all_products=NO), Fact(dietary_restrictions=YES),
        Fact(activity_evaluation=NO), Fact(allergy=YES), Fact(unhealthy_food=NO), Fact(muscle_mass=YES),
        Fact(better_health=YES), Fact(medical_restrictions=YES), Fact(calories=YES), Fact(organic_products=YES)
    )
    def diet_3(self):
        self.declare(Fact(diet='gluten_free_diet'))

    @Rule(
        Fact(action='find_diet'), Fact(slimming=YES), Fact(vegetarianism=NO), Fact(gluten=NO),
        Fact(diabetes=YES), Fact(activity=YES), Fact(all_products=NO), Fact(dietary_restrictions=NO),
        Fact(activity_evaluation=YES), Fact(allergy=NO), Fact(unhealthy_food=NO), Fact(muscle_mass=NO),
        Fact(better_health=YES), Fact(medical_restrictions=NO), Fact(calories=YES), Fact(organic_products=NO)
    )
    def diet_4(self):
        self.declare(Fact(diet='diabetic_diet'))

    @Rule(
        Fact(action='find_diet'), Fact(slimming=YES), Fact(vegetarianism=NO), Fact(gluten=NO),
        Fact(diabetes=NO), Fact(activity=YES), Fact(all_products=YES), Fact(dietary_restrictions=NO),
        Fact(activity_evaluation=YES), Fact(allergy=NO), Fact(unhealthy_food=YES), Fact(muscle_mass=NO),
        Fact(better_health=YES), Fact(medical_restrictions=NO), Fact(calories=NO), Fact(organic_products=NO)
    )
    def diet_5(self):
        self.declare(Fact(diet='diet_for_weight_loss'))

    @Rule(Fact(action='find_diet'), Fact(diet=MATCH.diet), salience=-998)
    def diet(self, diet):
        diet_details = self.D_DESC_MAP[diet]
        send_to_websocket('Result: The most probable diet that you have is %s\n' % (
            diet) + 'A short description of the diet is given below :\n' + diet_details + '\n')
        # print('The most probable diet that you have is %s\n' % (diet))
        # print('A short description of the diet is given below :\n')
        # print(diet_details + '\n')

    # slimming, vegetarianism, gluten, diabetes, activity, all_products, dietary_restrictions, activity_evaluation,
    # allergy, unhealthy_food, muscle_mass, better_health, medical_restrictions, calories, organic_products
    @Rule(
        Fact(action='find_diet'),
        Fact(slimming=MATCH.slimming),
        Fact(vegetarianism=MATCH.vegetarianism),
        Fact(gluten=MATCH.gluten),
        Fact(diabetes=MATCH.diabetes),
        Fact(activity=MATCH.activity),
        Fact(all_products=MATCH.all_products),
        Fact(dietary_restrictions=MATCH.dietary_restrictions),
        Fact(activity_evaluation=MATCH.activity_evaluation),
        Fact(allergy=MATCH.allergy),
        Fact(unhealthy_food=MATCH.unhealthy_food),
        Fact(muscle_mass=MATCH.muscle_mass),
        Fact(better_health=MATCH.better_health),
        Fact(medical_restrictions=MATCH.medical_restrictions),
        Fact(calories=MATCH.calories),
        Fact(organic_products=MATCH.organic_products),
        NOT(Fact(diet=MATCH.diet)),
        salience=-999,
    )
    def not_matched(
        self, slimming, vegetarianism, gluten, diabetes, activity, all_products,
        dietary_restrictions, activity_evaluation, allergy, unhealthy_food, muscle_mass,
        better_health, medical_restrictions, calories, organic_products,
    ):
        print('\nDid not find any diet that matches your exact symptoms')
        symptoms = [slimming, vegetarianism, gluten, diabetes, activity, all_products,
                    dietary_restrictions, activity_evaluation, allergy, unhealthy_food, muscle_mass,
                    better_health, medical_restrictions, calories, organic_products]

        max_count = 0
        max_diet = ''

        for key, val in self.SYMPTOM_MAP.items():
            count = sum(1 for i, temp_symptom in enumerate(eval(key)) if temp_symptom == YES and symptoms[i] == YES)
            if count > max_count:
                max_count = count
                max_diet = val

        diet_details = self.D_DESC_MAP[max_diet]
        send_to_websocket('Result: The most probable diet that you have is %s <br>' % (
            max_diet) + 'A short description of the diet is given below :<br>' + diet_details + '<br>')
        # print('')
        # print('The most probable diet that you have is %s\n' % (max_diet))
        # print('A short description of the diet is given below :\n')
        # print(diet_details + '\n')


def run_expert_system():
    print('run')
    engine = Greetings()
    while True:
        engine.reset()
        engine.run()


def new_client(client, server):
    # set a new client info
    global CLIENT
    print("New client connected")
    print(f'new_client = {client}')
    CLIENT = client


def message_received(client, server, message):
    global MESSAGE_RECEIVED_TEXT
    print(f"Received message: {message}")

    # save message
    MESSAGE_RECEIVED_TEXT = message

    # notify Condition that a new message has been received
    with MESSAGE_RECEIVED_CONDITION:
        MESSAGE_RECEIVED_CONDITION.notify()


def client_left(client, server):
    # reset next question QUESTION_NUMBER
    global QUESTION_NUMBER
    QUESTION_NUMBER = 0

    print("Client left")


# create websocket server
server = WebsocketServer(host="0.0.0.0", port=8000)

# websocket event handlers
server.set_fn_new_client(new_client)
server.set_fn_message_received(message_received)
server.set_fn_client_left(client_left)

# start websocket server in a new thread
server_thread = threading.Thread(target=server.run_forever)
server_thread.daemon = True
server_thread.start()

run_expert_system()
