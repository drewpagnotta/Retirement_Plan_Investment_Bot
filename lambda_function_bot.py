### Required Libraries ###
from datetime import datetime
from dateutil.relativedelta import relativedelta
import json


### Functionality Helper Functions ###
def parse_int(n):
    """
    Securely converts a non-integer value to integer.
    """
    try:
        return int(n)
    except ValueError:
        return float("nan")


def build_validation_result(is_valid, violated_slot, message_content):
    """
    Define a result message structured as Lex response.
    """
    if message_content is None:
        return {"isValid": is_valid, "violatedSlot": violated_slot}

    return {
        "isValid": is_valid,
        "violatedSlot": violated_slot,
        "message": {"contentType": "PlainText", "content": message_content},
    }

# User input starts here.

def validate_data(first_name, age, investment_amount, risk_level, intent_request):
    """
    Validates the data provided by the user.
    """
    
    # Validate the user is between 0 and 65 years old.
    
    if age is not None:
        age = parse_int(age)
        if age <= 0:
            return build_validation_result(
                False,
                "age",
                "Even though you might be in the womb, you still need to be in this 3D world to invest. "
                "Please wait for your birth day, then try again.",
            )
        elif age >= 65:
            return build_validation_result(
                False,
                "age",
                "You can already retire, hopefully this isn't your first attempt at investing for retirement. "
                "This strategy isn't for you. Good luck.",
            )

    # Validate the investment amount is at least $5,000.
    
    if investment_amount is not None:
        investment_amount = parse_int(investment_amount)
        if investment_amount < 5000:
            return build_validation_result(
                False,
                "investmentAmount",
                "This investment portfolio is for whales, less than $5,000 won't cut it.",
            )
            
    # Validate the risk level from the user.
    
    if risk_level is not None:
        if risk_level is not ["Low", "Medium", "High"]:
            return build_validation_result(
                False,
                "riskLevel",
                "Please type either 'None', 'Low', 'Medium', or 'High'."
            )
            
    # If age, investment_amount, and risk_level are valid, a True is the result.        
    return build_validation_result(True, None, None)
    
### Dialog Actions Helper Functions ###
def get_slots(intent_request):
    """
    Fetch all the slots and their values from the current intent.
    """
    return intent_request["currentIntent"]["slots"]


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    """
    Defines an elicit slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "ElicitSlot",
            "intentName": intent_name,
            "slots": slots,
            "slotToElicit": slot_to_elicit,
            "message": message,
        },
    }


def delegate(session_attributes, slots):
    """
    Defines a delegate slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {"type": "Delegate", "slots": slots},
    }


def close(session_attributes, fulfillment_state, message):
    """
    Defines a close slot type response.
    """

    response = {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": fulfillment_state,
            "message": message,
        },
    }

    return response


"""
Step 3: Enhance the Robo Advisor with an Amazon Lambda Function

In this section, you will create an Amazon Lambda function that will validate the data provided by the user on the Robo Advisor.

1. Start by creating a new Lambda function from scratch and name it `recommendPortfolio`. Select Python 3.7 as runtime.

2. In the Lambda function code editor, continue by deleting the AWS generated default lines of code, then paste in the starter code provided in `lambda_function.py`.

3. Complete the `recommend_portfolio()` function by adding these validation rules:

    * The `age` should be greater than zero and less than 65.
    * The `investment_amount` should be equal to or greater than 5000.

4. Once the intent is fulfilled, the bot should respond with an investment recommendation based on the selected risk level as follows:

    * **none:** "100% bonds (AGG), 0% equities (SPY)"
    * **low:** "60% bonds (AGG), 40% equities (SPY)"
    * **medium:** "40% bonds (AGG), 60% equities (SPY)"
    * **high:** "20% bonds (AGG), 80% equities (SPY)"

> **Hint:** Be creative while coding your solution, you can have all the code on the `recommend_portfolio()` function, or you can split the functionality across different functions, put your Python coding skills in action!

5. Once you finish coding your Lambda function, test it using the sample test events provided for this Challenge.

6. After successfully testing your code, open the Amazon Lex Console and navigate to the `recommendPortfolio` bot configuration, integrate your new Lambda function by selecting it in the “Lambda initialization and validation” and “Fulfillment” sections.

7. Build your bot, and test it with valid and invalid data for the slots.

"""


### Intents Handlers ###
def recommend_portfolio(intent_request):
    """
    Performs dialog management and fulfillment for recommending a portfolio.
    """

    first_name = get_slots(intent_request)["firstName"]
    age = get_slots(intent_request)["age"]
    investment_amount = get_slots(intent_request)["investmentAmount"]
    risk_level = get_slots(intent_request)["riskLevel"]
    source = intent_request["invocationSource"]

            
    # # Output appropriate suggestions for different risk levels.
    
    if source == "DialogCodeHook":
        # Provides basic validation using the input slots.
        
        # Gets all of the slots.
        
        slots = get_slots(intent_request)
        
        # Validates user input via validate_data.
        
        validation_result = validate_data(age, investment_amount, risk_level, intent_request)
        
        # If the input value is invalid, reask to enter input correctly.
        
        if not validation_result["isValid"]:
            slots[validation_result["violatedSlot"]] = None
            
            # Asks for new data to be entered and valid.
            
            return elicit_slot(
                intent_request["sessionAttributes"],
                intent_request["currentIntent"]["name"],
                slots,
                validation_result["violatedSlot"],
                validation_result["message"],
            )
            
         # Fetch current session attributes
         
        output_session_attributes = intent_request["sessionAttributes"]

        # With valid responses, we make suggestions for user based on input.
        
        return delegate(output_session_attributes, get_slots(intent_request))
        
        if risk_level == "None":
            print("100% bonds (AGG), 0% equities (SPY)")
        elif risk_level == "Low":
            print("60% bonds (AAG), 40% equities (SPY)")
        elif risk_level == "Medium":
            print("40% bonds (AGG), 60% equities (SPY)")
        elif risk_level == "High":
            print("20% bonds (AGG), 80% equities (SPY)")
            
        return close(
            intent_request["sessionAttributes"],
            "Fulfilled",
            {
                "contentType": "PlainText",
                "content": """Thank you, Goodbye.""",
            },
        )
            
### Intents Dispatcher ###
def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    intent_name = intent_request["currentIntent"]["name"]

    # Dispatch to bot's intent handlers
    if intent_name == "recommendPortfolio":
        return recommend_portfolio(intent_request)

    raise Exception("Intent with name " + intent_name + " not supported")


### Main Handler ###
def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """

    return dispatch(event)
