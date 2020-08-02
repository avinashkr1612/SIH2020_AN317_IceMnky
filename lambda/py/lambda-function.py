import random
import logging
import json
import prompts
import ask_sdk_core
import api_request
import requests

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractRequestInterceptor, AbstractResponseInterceptor)
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput

#this module checks whether a device supports apl or not
from ask_sdk_core.utils import get_supported_interfaces


from ask_sdk_model.ui import SimpleCard
from ask_sdk_model.interfaces.alexa.presentation.apl import (RenderDocumentDirective)

from ask_sdk_model import Response

from typing import Dict, Any

sb = SkillBuilder()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# APL Path goes here
how_to_reach_intent_APL = "howToReachIntentTemplate.json"
launch_request_json = "./apl-list/launchRequestTemplate.json"


# Tokens used when sending the APL directives
HELLO_WORLD_TOKEN = "helloworldToken"

def _load_apl_document(file_path):
    # type: (str) -> Dict[str, Any]
    """Load the apl json document at the path into a dict object."""
    with open(file_path) as f:
        return json.load(f)


# Built-in Intent Handlers
class GetWelcomeMessage(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (is_request_type("LaunchRequest")(handler_input))
        
    def handle(self, handler_input):
        data = handler_input.attributes_manager.request_attributes["_"]
        speak_output = data[prompts.GET_WELCOME_MESSAGE]
        template = _load_apl_document(launch_request_json)
        response_builder = handler_input.response_builder
        if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
            response_builder.add_directive(
                RenderDocumentDirective(
                    token=HELLO_WORLD_TOKEN,
                    document=template['document'],
                    datasources=template['datasources']
                )
            )
        response_builder = handler_input.response_builder
        return response_builder.speak(speak_output).response


     
class destinationhistory(AbstractRequestHandler):
    def can_handle(self, handler_input):
        
        return is_intent_name("destinationhistory")(handler_input)

    def handle(self, handler_input):
        
        data = handler_input.attributes_manager.request_attributes["_"]
        print("@@@@")
        slots = handler_input.request_envelope.request.intent.slots
        slotID = slots['place'].resolutions.resolutions_per_authority[0].values[0].value.id
        print("@@@@")
        r = api_request.getReqest(slotID).json()
        print("response printed here")
        
        speak_output = r[0]['destination_history']
        response_builder = handler_input.response_builder
        return response_builder.speak(speak_output).response
        
class destinationdescription(AbstractRequestHandler):
    def can_handle(self, handler_input):
        
        return is_intent_name("destinationdescription")(handler_input)

    def handle(self, handler_input):
        
        data = handler_input.attributes_manager.request_attributes["_"]
        slots = handler_input.request_envelope.request.intent.slots
        slotID = slots['place'].resolutions.resolutions_per_authority[0].values[0].value.id
        r = api_request.getReqest(slotID).json()
        print("response printed here")
        
        speak_output = r[0]['destination_description']
        response_builder = handler_input.response_builder
        return response_builder.speak(speak_output).response

class thingstodo(AbstractRequestHandler):
    def can_handle(self, handler_input):
        
        return is_intent_name("thingstodo")(handler_input)

    def handle(self, handler_input):
        
        data = handler_input.attributes_manager.request_attributes["_"]
        slots = handler_input.request_envelope.request.intent.slots
        slotID = slots['place'].resolutions.resolutions_per_authority[0].values[0].value.id
        r = api_request.getReqest(slotID).json()
        print("response printed here")
        
        speak_output = r[0]['things_to_do']
        response_builder = handler_input.response_builder
        return response_builder.speak(speak_output).response
           
           
class entryprerequisites(AbstractRequestHandler):
    def can_handle(self, handler_input):
        
        return is_intent_name("entryprerequisites")(handler_input)

    def handle(self, handler_input):
        
        data = handler_input.attributes_manager.request_attributes["_"]
        slots = handler_input.request_envelope.request.intent.slots
        slotID = slots['place'].resolutions.resolutions_per_authority[0].values[0].value.id
        r = api_request.getReqest(slotID).json()
        print("response printed here")
        
        speak_output = r[0]['entry_prerequisites']
        response_builder = handler_input.response_builder
        return response_builder.speak(speak_output).response
   
class recfordiffabled(AbstractRequestHandler):
    def can_handle(self, handler_input):
        
        return is_intent_name("recfordiffabled")(handler_input)

    def handle(self, handler_input):
        
        data = handler_input.attributes_manager.request_attributes["_"]
        slots = handler_input.request_envelope.request.intent.slots
        slotID = slots['place'].resolutions.resolutions_per_authority[0].values[0].value.id
        r = api_request.getReqest(slotID).json()
        print("response printed here")
        
        speak_output = r[0]['rec_for_diff_abled']
        response_builder = handler_input.response_builder
        return response_builder.speak(speak_output).response
      
class policies(AbstractRequestHandler):
    def can_handle(self, handler_input):
        
        return is_intent_name("policies")(handler_input)

    def handle(self, handler_input):
        
        data = handler_input.attributes_manager.request_attributes["_"]
        slots = handler_input.request_envelope.request.intent.slots
        slotID = slots['place'].resolutions.resolutions_per_authority[0].values[0].value.id
        r = api_request.getReqest(slotID).json()
        print("response printed here")
        
        speak_output = r[0]['policies']
        response_builder = handler_input.response_builder
        return response_builder.speak(speak_output).response

class timingstovisit(AbstractRequestHandler):
    def can_handle(self, handler_input):
        
        return is_intent_name("timingstovisit")(handler_input)

    def handle(self, handler_input):
        
        data = handler_input.attributes_manager.request_attributes["_"]
        slots = handler_input.request_envelope.request.intent.slots
        slotID = slots['place'].resolutions.resolutions_per_authority[0].values[0].value.id
        r = api_request.getReqest(slotID).json()
        print("response printed here")
        
        speak_output = r[0]['timings_to_visit']
        response_builder = handler_input.response_builder
        return response_builder.speak(speak_output).response
        
class similarplaces(AbstractRequestHandler):
    def can_handle(self, handler_input):
        
        return is_intent_name("similarplaces")(handler_input)

    def handle(self, handler_input):
        
        data = handler_input.attributes_manager.request_attributes["_"]
        slots = handler_input.request_envelope.request.intent.slots
        slotID = slots['place'].resolutions.resolutions_per_authority[0].values[0].value.id
        r = api_request.getReqest(slotID).json()
        print("response printed here")
        
        speak_output = r[0]['similar_places']
        response_builder = handler_input.response_builder
        return response_builder.speak(speak_output).response        
           
                
class HowToReachIntent(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("HowToReachIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        # print("called how to reach intent");
        # logger.info("In HowToReachHandler")

        data = handler_input.attributes_manager.request_attributes["_"]
        slots = handler_input.request_envelope.request.intent.slots
        slotID = slots['place'].resolutions.resolutions_per_authority[0].values[0].value.id
        r = api_request.getReqest(slotID).json()
        

        speak_output = r[0]['how_to_reach']
        response_builder = handler_input.response_builder
    
        
        if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
            response_builder.add_directive(
                RenderDocumentDirective(
                    token=HELLO_WORLD_TOKEN,
                    document=_load_apl_document(how_to_reach_intent_APL)
                )
            )
            # Tailor the speech for a device with a screen
            speak_output += ("You should now also see my greeting on the screen.")
        
        else:
            # User's device does not support APL, so tailor the speech to
            # this situation
            speak_output += ("This example would be more interesting on a "
                             "device with a screen, such as an Echo Show or "
                             "Fire TV.")
        
        return response_builder.speak(speak_output).response

class SOScreateEmergencyList(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("SOScreateEmergencyList")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        # print("called how to reach intent");
        # logger.info("In HowToReachHandler")

        data = handler_input.attributes_manager.request_attributes["_"]
        slots = handler_input.request_envelope.request.intent.slots
        # deviceID = handler_input.request_envelope.context

        step1 = handler_input.__dict__
        step2 = step1['request_envelope'].__dict__
        step3 = step2['session'].__dict__
        step4 = step3['user'].__dict__
        userID = step4['user_id']

        print(userID)
        
        phoneNumber =  slots["phoneNumber"].value
        URL = "https://mjnwo2r1m9.execute-api.us-east-1.amazonaws.com/dev/addToSosGroup"
        
        PARAMS = {'usrID':userID,'phNO':phoneNumber} 
        res = requests.get(url = URL, params = PARAMS)
        print("@@@@@response")
        print(res)

        speak_output = "we have add the number to database"

        response_builder = handler_input.response_builder
        if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
            response_builder.add_directive(
                RenderDocumentDirective(
                    token=HELLO_WORLD_TOKEN,
                    document=_load_apl_document(how_to_reach_intent_APL)
                )
            )
            # Tailor the speech for a device with a screen
            
        else:
            # User's device does not support APL, so tailor the speech to
            # this situation
            speak_output += ("This example would be more interesting on a "
                             "device with a screen, such as an Echo Show or "
                             "Fire TV.")
        
        return response_builder.speak(speak_output).response



class SOSaskForHelp(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("SOSaskForHelp")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        # print("called how to reach intent");
        # logger.info("In HowToReachHandler")

        step1 = handler_input.__dict__
        step2 = step1['request_envelope'].__dict__
        step3 = step2['session'].__dict__
        step4 = step3['user'].__dict__
        userID = step4['user_id']

  
        

        URL = "https://mjnwo2r1m9.execute-api.us-east-1.amazonaws.com/dev/ask-for-help"
        
        PARAMS = {'usrID':userID} 
        
        res = requests.get(url = URL, params = PARAMS)
        # print("@@@@@response")
        # print(res)

        speak_output = "we have asked for help in your preset contact list"

        response_builder = handler_input.response_builder
        if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
            response_builder.add_directive(
                RenderDocumentDirective(
                    token=HELLO_WORLD_TOKEN,
                    document=_load_apl_document(how_to_reach_intent_APL)
                )
            )
            # Tailor the speech for a device with a screen
            
        else:
            # User's device does not support APL, so tailor the speech to
            # this situation
            speak_output += ("This example would be more interesting on a "
                             "device with a screen, such as an Echo Show or "
                             "Fire TV.")
        
        return response_builder.speak(speak_output).response













class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In HelpIntentHandler")

        # get localization data
        data = handler_input.attributes_manager.request_attributes["_"]

        speech = data[prompts.HELP_MESSAGE]
        reprompt = data[prompts.HELP_REPROMPT]
        handler_input.response_builder.speak(speech).ask(
            reprompt).set_card(SimpleCard(
                data[prompts.SKILL_NAME], speech))
        return handler_input.response_builder.response


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In CancelOrStopIntentHandler")

        # get localization data
        data = handler_input.attributes_manager.request_attributes["_"]

        speech = data[prompts.STOP_MESSAGE]
        handler_input.response_builder.speak(speech)
        return handler_input.response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")

        # get localization data
        data = handler_input.attributes_manager.request_attributes["_"]

        speech = data[prompts.FALLBACK_MESSAGE]
        reprompt = data[prompts.FALLBACK_REPROMPT]
        handler_input.response_builder.speak(speech).ask(
            reprompt)
        return handler_input.response_builder.response


class LocalizationInterceptor(AbstractRequestInterceptor):
    def process(self, handler_input):
        locale = handler_input.request_envelope.request.locale
        logger.info("Locale is {}".format(locale[:2]))

        # localized strings stored in language_strings.json
        with open("language_strings.json") as language_prompts:
            language_data = json.load(language_prompts)
        # set default translation data to broader translation
        data = language_data[locale[:2]]
        # if a more specialized translation exists, then select it instead
        # example: "fr-CA" will pick "fr" translations first, but if "fr-CA" translation exists,
        #          then pick that instead
        if locale in language_data:
            data.update(language_data[locale])
        handler_input.attributes_manager.request_attributes["_"] = data


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In SessionEndedRequestHandler")

        logger.info("Session ended reason: {}".format(
            handler_input.request_envelope.request.reason))
        return handler_input.response_builder.response


# Exception Handler
class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch all exception handler, log exception and
    respond with custom message.
    """

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.info("In CatchAllExceptionHandler")
        logger.error(exception, exc_info=True)

        handler_input.response_builder.speak("Exception Message").ask(
            "help Prompt")

        return handler_input.response_builder.response


# Request and Response loggers
class RequestLogger(AbstractRequestInterceptor):
    def process(self, handler_input):
        # type: (HandlerInput) -> None
        logger.debug("Alexa Request: {}".format(
            handler_input.request_envelope.request))


class ResponseLogger(AbstractResponseInterceptor):
    """Log the alexa responses."""

    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        logger.debug("Alexa Response: {}".format(response))


# Register intent handlers
sb.add_request_handler(GetWelcomeMessage())
sb.add_request_handler(HowToReachIntent())
sb.add_request_handler(destinationdescription())
sb.add_request_handler(destinationhistory())
sb.add_request_handler(entryprerequisites())
sb.add_request_handler(policies())
sb.add_request_handler(timingstovisit())
sb.add_request_handler(recfordiffabled())
sb.add_request_handler(thingstodo())
sb.add_request_handler(similarplaces())

sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

# Register exception handlers
sb.add_exception_handler(CatchAllExceptionHandler())

# Register request and response interceptors
sb.add_global_request_interceptor(LocalizationInterceptor())
sb.add_global_request_interceptor(RequestLogger())
sb.add_global_response_interceptor(ResponseLogger())

# Handler name that is used on AWS lambda
lambda_handler = sb.lambda_handler()