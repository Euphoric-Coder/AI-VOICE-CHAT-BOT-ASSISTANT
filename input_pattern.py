# import spacy

# nlp = spacy.load("en_core_web_sm")
pairs = [
    # Question Patterns about the AI
    (
        r"(what is your name|who are you|what are you|state your identification)",
        [
            "I am a basic chatbot.",
        ],
    ),
    (
        r"my name is (.*)",
        [
            "Hello %1, how can I help you today?",
        ],
    ),
    (
        r"how are you",
        [
            "I'm doing well, thank you!",
            "I'm just a computer program, so I don't have feelings, but I'm here to help.",
        ],
    ),
    (
        r"(.*) (good|great|fine)",
        [
            "That's wonderful!",
            "Glad to hear that.",
        ],
    ),
    (
        r"(.*) (bad|not good)",
        [
            "I'm sorry to hear that. How can I help you?",
        ],
    ),
    (
        r"(open|start) (.*)",
        [
            "Opening function: %2",
            "Starting function: %2",
        ],
    ),
    (
        r"launch (.*)",
        [
            "Launching function: %1",
        ],
    ),
    (
        r"initiate (.*)",
        [
            "Initiating function: %1",
        ],
    ),
    (
        r"execute (.*)",
        [
            "Executing function: %1",
        ],
    ),
    (
        r"run (.*)",
        [
            "Running function: %1",
        ],
    ),
    (
        r"activate (.*)",
        [
            "Activating function: %1",
        ],
    ),
    (
        r"fire up (.*)",
        [
            "Firing up function: %1",
        ],
    ),
    (
        r"commence (.*)",
        [
            "Commencing function: %1",
        ],
    ),
    (
        r"trigger (.*)",
        [
            "Triggering function: %1",
        ],
    ),
    (
        r"initiate (.*)",
        [
            "Initiating function: %1",
        ],
    ),
    (
        r"engage (.*)",
        [
            "Engaging function: %1",
        ],
    ),
    (
        r"start up (.*)",
        [
            "Starting up function: %1",
        ],
    ),
    (
        r"begin (.*)",
        [
            "Beginning function: %1",
        ],
    ),
    (
        r"kick off (.*)",
        [
            "Kicking off function: %1",
        ],
    ),
    (
        r"commence (.*)",
        [
            "Commencing function: %1",
        ],
    ),
    (
        r"commence (.*)",
        [
            "Commencing function: %1",
        ],
    ),
    (
        r"initiate (.*)",
        [
            "Initiating function: %1",
        ],
    ),
    (
        r"run (.*)",
        [
            "Running function: %1",
        ],
    ),
    (
        r"start (.*)",
        [
            "Starting function: %1",
        ],
    ),
    (
        r"begin (.*)",
        [
            "Beginning function: %1",
        ],
    ),
    (
        r"activate (.*)",
        [
            "Activating function: %1",
        ],
    ),
    (
        r"fire up (.*)",
        [
            "Firing up function: %1",
        ],
    ),
    (
        r"open (.*)",
        [
            "Opening function: %1",
        ],
    ),
    (
        r"launch (.*)",
        [
            "Launching function: %1",
        ],
    ),
    (
        r"initiate (.*)",
        [
            "Initiating function: %1",
        ],
    ),
    (
        r"execute (.*)",
        [
            "Executing function: %1",
        ],
    ),
    (
        r"run (.*)",
        [
            "Running function: %1",
        ],
    ),
    (
        r"activate (.*)",
        [
            "Activating function: %1",
        ],
    ),
    (
        r"fire up (.*)",
        [
            "Firing up function: %1",
        ],
    ),
    (
        r"commence (.*)",
        [
            "Commencing function: %1",
        ],
    ),
    (
        r"trigger (.*)",
        [
            "Triggering function: %1",
        ],
    ),
    (
        r"initiate (.*)",
        [
            "Initiating function: %1",
        ],
    ),
    (
        r"engage (.*)",
        [
            "Engaging function: %1",
        ],
    ),
    (
        r"start up (.*)",
        [
            "Starting up function: %1",
        ],
    ),
    (
        r"begin (.*)",
        [
            "Beginning function: %1",
        ],
    ),
    (
        r"kick off (.*)",
        [
            "Kicking off function: %1",
        ],
    ),
    (
        r"ignite (.*)",
        [
            "Igniting function: %1",
        ],
    ),
    (
        r"turn on (.*)",
        [
            "Turning on function: %1",
        ],
    ),
    (
        r"enable (.*)",
        [
            "Enabling function: %1",
        ],
    ),
    (
        r"initiate (.*)",
        [
            "Initiating function: %1",
        ],
    ),
    (
        r"execute (.*)",
        [
            "Executing function: %1",
        ],
    ),
    (
        r"invoke (.*)",
        [
            "Invoking function: %1",
        ],
    ),
    (
        r"proceed with (.*)",
        [
            "Proceeding with function: %1",
        ],
    ),
    (
        r"start the (.*)",
        [
            "Starting the function: %1",
        ],
    ),
    (
        r"activate the (.*)",
        [
            "Activating the function: %1",
        ],
    ),
    (
        r"commence the (.*)",
        [
            "Commencing the function: %1",
        ],
    ),
    (
        r"begin the (.*)",
        [
            "Beginning the function: %1",
        ],
    ),
    (
        r"initialize (.*)",
        [
            "Initializing function: %1",
        ],
    ),
    (
        r"turn (.*) on",
        [
            "Turning %1 on",
        ],
    ),
    (
        r"power up (.*)",
        [
            "Powering up %1",
        ],
    ),
    (
        r"ignite (.*)",
        [
            "Igniting %1",
        ],
    ),
    (
        r"start the (.*)",
        [
            "Starting the %1",
        ],
    ),
    (
        r"turn on (.*)",
        [
            "Turning on %1",
        ],
    ),
    (
        r"enable the (.*)",
        [
            "Enabling the %1",
        ],
    ),
    (
        r"initiate the (.*)",
        [
            "Initiating the %1",
        ],
    ),
    (
        r"execute the (.*)",
        [
            "Executing the %1",
        ],
    ),
    (
        r"invoke the (.*)",
        [
            "Invoking the %1",
        ],
    ),
    (
        r"proceed with the (.*)",
        [
            "Proceeding with the %1",
        ],
    ),
    (
        r"ignite the (.*)",
        [
            "Igniting the %1",
        ],
    ),
    (
        r"start up the (.*)",
        [
            "Starting up the %1",
        ],
    ),
    (
        r"begin the (.*)",
        [
            "Beginning the %1",
        ],
    ),
    (
        r"kick off the (.*)",
        [
            "Kicking off the %1",
        ],
    ),
    (
        r"activate the (.*)",
        [
            "Activating the %1",
        ],
    ),
    (
        r"commence the (.*)",
        [
            "Commencing the %1",
        ],
    ),
    (
        r"turn on (.*)",
        [
            "Turning on %1",
        ],
    ),
    (
        r"power up (.*)",
        [
            "Powering up %1",
        ],
    ),
    (
        r"ignite (.*)",
        [
            "Igniting %1",
        ],
    ),
    (
        r"launch the (.*)",
        [
            "Launching the %1",
        ],
    ),
    (
        r"initiate the (.*)",
        [
            "Initiating the %1",
        ],
    ),
    (
        r"execute the (.*)",
        [
            "Executing the %1",
        ],
    ),
    (
        r"run the (.*)",
        [
            "Running the %1",
        ],
    ),
    (
        r"activate the (.*)",
        [
            "Activating the %1",
        ],
    ),
    (
        r"fire up the (.*)",
        [
            "Firing up the %1",
        ],
    ),
    (
        r"commence the (.*)",
        [
            "Commencing the %1",
        ],
    ),
    (
        r"trigger the (.*)",
        [
            "Triggering the %1",
        ],
    ),
    (
        r"initiate the (.*)",
        [
            "Initiating the %1",
        ],
    ),
    (
        r"engage the (.*)",
        [
            "Engaging the %1",
        ],
    ),
    (
        r"start up the (.*)",
        [
            "Starting up the %1",
        ],
    ),
    (
        r"begin the (.*)",
        [
            "Beginning the %1",
        ],
    ),
    (
        r"kick off the (.*)",
        [
            "Kicking off the %1",
        ],
    ),
    (
        r"ignite the (.*)",
        [
            "Igniting the %1",
        ],
    ),
    (
        r"turn on (.*)",
        [
            "Turning on the %1",
        ],
    ),
    (
        r"enable the (.*)",
        [
            "Enabling the %1",
        ],
    ),
    (
        r"initiate the (.*)",
        [
            "Initiating the %1",
        ],
    ),
    (
        r"execute the (.*)",
        [
            "Executing the %1",
        ],
    ),
    (
        r"invoke the (.*)",
        [
            "Invoking the %1",
        ],
    ),
    (
        r"proceed with the (.*)",
        [
            "Proceeding with the %1",
        ],
    ),
    (
        r"ignite the (.*)",
        [
            "Igniting the %1",
        ],
    ),
    (
        r"start up the (.*)",
        [
            "Starting up the %1",
        ],
    ),
    (
        r"begin the (.*)",
        [
            "Beginning the %1",
        ],
    ),
    (
        r"kick off the (.*)",
        [
            "Kicking off the %1",
        ],
    ),
    (
        r"activate the (.*)",
        [
            "Activating the %1",
        ],
    ),
    (
        r"commence the (.*)",
        [
            "Commencing the %1",
        ],
    ),
    (
        r"quit",
        [
            "Goodbye! Have a great day.",
            "Bye for now.",
        ],
    ),
]
