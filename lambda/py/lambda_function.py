import random
import logging
import json
import prompts
import ask_sdk_core
import api_request
import requests
import time
import math
from datetime import datetime

import boto3
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractRequestInterceptor, AbstractResponseInterceptor)
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model.ui import AskForPermissionsConsentCard
from ask_sdk_core.utils import get_supported_interfaces
from ask_sdk_model.ui import SimpleCard
from ask_sdk_model.ui import StandardCard
from ask_sdk_core.utils import is_intent_name, get_dialog_state, get_slot_value
from ask_sdk_model.dialog import ElicitSlotDirective
from ask_sdk_model import Response, Intent
from ask_sdk_model import Response, DialogState
from ask_sdk_model.ui import Image
from ask_sdk_model import IntentConfirmationStatus
from ask_sdk_model.interfaces.alexa.presentation.apl import (RenderDocumentDirective)
from typing import Dict, Any


from get_data import get_user_phone_emergency_number
from get_data import add_user_phone_number
from get_data import resolve_place
from get_data import add_latest_place_to_user
from get_data import get_latest_place_with_fallback

import googlemaps
from googlemaps_helpers.directions import directions

sb = SkillBuilder()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
sns=boto3.client('sns', region_name='us-east-1')
google_maps_client = googlemaps.Client(key='API_KEY_HERE')

# APLtemplate Path goes here
how_to_reach_intent_APL = "./apl-list/howToReachIntentTemplate.json"
launch_request_json = "./apl-list/launchRequestTemplate.json"
state_plces_json = "./apl-list/statePlacesTemplate.json"
destination_description_json = "./apl-list/destinationDescriptionTemplate.json"
destination_history_json = "./apl-list/destinationHistoryTemplate.json"
prequisites_Policies_json= "./apl-list/prequisitesAndPoliciesTemplates.json"
rec_For_abled_json= "./apl-list/recForDisabledTemplate.json"
seasons_To_Visit_json= "./apl-list/seasonsToVisitTemplate.json"
similar_Places_To_Visit_json= "./apl-list/similarPlacesToVisitTemplate.json"
SOS_ask_For_Help_json= "./apl-list/SOSaskForHelpTemplate.json"
SOS_create_Emergency_List_json= "./apl-list/SOScreateEmergencyListTemplate.json"
state_Places_json= "./apl-list/statePlacesTemplate.json"
things_To_Do_json= "./apl-list/thingsToDoTemplate.json"
timings_to_Visit_json= "./apl-list/timingstoVisitTemplate.json"
visa_Needs_json= "./apl-list/visaNeedsTemplate.json"
visit_In_Season_json= "./apl-list/visitInSeasonTemplate.json"
my_Location_json= "./apl-list/myLocationTemplate.json"

# Tokens used when sending the APL directives
HELLO_WORLD_TOKEN = "helloworldToken"

def _load_apl_document(file_path):
    # type: (str) -> Dict[str, Any]
    """Load the apl json document at the path into a dict object."""
    with open(file_path) as f:
        return json.load(f)
        
def build_standard_card(title, text, image_id):
    return StandardCard(title, text, Image(
        'https://source.unsplash.com/{0}/720x480'.format(image_id),
        'https://source.unsplash.com/{0}/1200x800'.format(image_id),
    ))


def resolve_in_session_or_input_and_elicit(handler_input,
                                           slot_name,
                                           elicit_text,
                                           elicit_prompt,
                                           intent_name):
    session_attr = handler_input.attributes_manager.session_attributes

    slot_value = session_attr.get(slot_name, None)
    slot_value = get_slot_value(handler_input, slot_name) or slot_value 
    session_attr[slot_name] = slot_value

    if slot_value is None:
        return None, handler_input.response_builder.speak(elicit_text).ask(elicit_prompt).add_directive(
            directive=ElicitSlotDirective(updated_intent=Intent(
                name=intent_name,
                confirmation_status=IntentConfirmationStatus.NONE
            ), 
            slot_to_elicit=slot_name,
        )).response

    return slot_value, None


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
        return response_builder.speak(speak_output).set_card(
            build_standard_card(
                'Welcome',
                speak_output,
                'SSTIrc87ziI',
            ),
        ).response

class destinationhistory(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("destinationhistory")(handler_input)

    def handle(self, handler_input):
        data = handler_input.attributes_manager.request_attributes["_"]
        slots = handler_input.request_envelope.request.intent.slots
        slotID = slots['place'].resolutions.resolutions_per_authority[0].values[0].value.id
        r = api_request.getReqest(slotID)
        print("response printed here")
            
        speak_output = r[0]['destination_history']
        dest_name = r[0]['destination_name']
    
        template = _load_apl_document(destination_history_json)
        template['datasources']['bodyTemplate6Data']['title'] = "History of {}".format(dest_name)
        template['datasources']['bodyTemplate6Data']['textContent']['primaryText']['text'] = speak_output
        
        response_builder = handler_input.response_builder
        if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
            response_builder.add_directive(
                RenderDocumentDirective(
                    token=HELLO_WORLD_TOKEN,
                    document=template['document'],
                    datasources=template['datasources']
                    )
                )

        return response_builder.speak(speak_output).set_card(
            build_standard_card(
                'History',
                speak_output,
                'BCEexmxL9EQ',
            ),
        ).response

        
class destinationdescription(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("destinationdescription")(handler_input) and get_dialog_state(
            handler_input=handler_input) == DialogState.COMPLETED

    def handle(self, handler_input):
        response_builder = handler_input.response_builder

        place, elicit = resolve_in_session_or_input_and_elicit(
            handler_input,
            'place',
            'We need the name of the place to describe it.',
            'Please say the name of the place that I have to describe.',
            'destinationdescription',
        )
        
        if place is None:
            return elicit
        else:
            place_id = resolve_place(place)
            result = api_request.getReqest(place_id)
            
            if len(result) < 1:
                speak_output = (
                    "Sorry, we don't have information about your destination."
                )

                return response_builder.speak(speak_output).response
            else:
                speak_output = result[0]['destination_description']
                dest_name = result[0]['destination_name']

                template = _load_apl_document(destination_description_json)

                template['datasources']['bodyTemplate6Data']['title'] = (
                    "Description Of {}".format(dest_name)
                )
    
                template['datasources']['bodyTemplate6Data']['textContent']['primaryText']['text'] = (
                    speak_output
                )

                if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
                    response_builder.add_directive(
                        RenderDocumentDirective(
                            token=HELLO_WORLD_TOKEN,
                            document=template['document'],
                            datasources=template['datasources'],
                        ),
                    )

                return response_builder.speak(speak_output).set_card(
                    build_standard_card(
                        'Description',
                        speak_output,
                        'BCEexmxL9EQ',
                    ),
                ).response

class thingstodo(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("thingstodo")(handler_input) and get_dialog_state(
            handler_input=handler_input) == DialogState.COMPLETED

    def handle(self, handler_input):
        response_builder = handler_input.response_builder

        place, elicit = resolve_in_session_or_input_and_elicit(
            handler_input,
            'place',
            'We need the name of the place to tell you things that you can do there.',
            'Please say the name of the place.',
            'thingstodo',
        )

        if place is None:
            return elicit
        else:
            place_id = resolve_place(place)
            result = api_request.getReqest(place_id)
            # assert False, result
            if len(result) < 1:
                speak_output = (
                    "Sorry, we don't have information about your destination."
                )

                return response_builder.speak(speak_output).response
            else:
                speak_output = result[0]['things_to_do']
                dest_name = result[0]['destination_name']

                template = _load_apl_document(things_To_Do_json)

                template['datasources']['bodyTemplate6Data']['title'] = (
                    "Things To Do At  {}".format(dest_name)
                )

                template['datasources']['bodyTemplate6Data']['textContent']['primaryText']['text'] = (
                    speak_output
                )

                if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
                    response_builder.add_directive(
                        RenderDocumentDirective(
                            token=HELLO_WORLD_TOKEN,
                            document=template['document'],
                            datasources=template['datasources'],
                        )
                    )

                return response_builder.speak(speak_output).set_card(
                    build_standard_card(
                        'Local Attractions',
                        speak_output,
                        '8tMxz9MRJHc',
                    ),
                ).response


class entryprerequisites(AbstractRequestHandler):
    def can_handle(self, handler_input):
        
        return is_intent_name("entryprerequisites")(handler_input)

    def handle(self, handler_input):
        
        data = handler_input.attributes_manager.request_attributes["_"]
        slots = handler_input.request_envelope.request.intent.slots
        slotID = slots['place'].resolutions.resolutions_per_authority[0].values[0].value.id
        r = api_request.getReqest(slotID)
        print("response printed here")
        
        speak_output = r[0]['entry_prerequisites']
        dest_name = r[0]['destination_name']
    
        template = _load_apl_document(prequisites_Policies_json)
        template['datasources']['bodyTemplate6Data']['title'] = "Entry Prequisits to visit {}".format(dest_name)
        template['datasources']['bodyTemplate6Data']['textContent']['primaryText']['text'] = speak_output
        
        response_builder = handler_input.response_builder
        if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
            response_builder.add_directive(
                RenderDocumentDirective(
                    token=HELLO_WORLD_TOKEN,
                    document=template['document'],
                    datasources=template['datasources']
                    )
                )
                
        return response_builder.speak(speak_output).set_card(
            build_standard_card(
                'Ticket Cost',
                speak_output,
                'XL1YpEnVLb0',
            ),
        ).response
   
class recfordiffabled(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("recfordiffabled")(handler_input)

    def handle(self, handler_input):
        
        data = handler_input.attributes_manager.request_attributes["_"]
        slots = handler_input.request_envelope.request.intent.slots
        slotID = slots['place'].resolutions.resolutions_per_authority[0].values[0].value.id
        r = api_request.getReqest(slotID)
        print("response printed here")
        
        speak_output = r[0]['rec_for_diff_abled']
        response_builder = handler_input.response_builder
        if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
            response_builder.add_directive(
                RenderDocumentDirective(
                    token=HELLO_WORLD_TOKEN,
                    document=_load_apl_document(rec_For_abled_json)
                )
            ) 
        return response_builder.speak(speak_output).set_card(
            build_standard_card(
                'Facilities',
                speak_output,
                '0nkFvdcM-X4',
            ),
        ).response
      
class policies(AbstractRequestHandler):
    def can_handle(self, handler_input):
        
        return is_intent_name("policies")(handler_input)

    def handle(self, handler_input):
        
        data = handler_input.attributes_manager.request_attributes["_"]
        slots = handler_input.request_envelope.request.intent.slots
        slotID = slots['place'].resolutions.resolutions_per_authority[0].values[0].value.id
        r = api_request.getReqest(slotID)
        print("response printed here")
        
        speak_output = r[0]['policies']
        response_builder = handler_input.response_builder
        if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
            response_builder.add_directive(
                RenderDocumentDirective(
                    token=HELLO_WORLD_TOKEN,
                    document=_load_apl_document(prequisites_Policies_json)
                )
            )            
        return response_builder.speak(speak_output).set_card(
            build_standard_card(
                'Policies',
                speak_output,
                'oMqswmrie4Y',
            ),
        ).response

class timingstovisit(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("timingstovisit")(handler_input)

    def handle(self, handler_input):
        
        data = handler_input.attributes_manager.request_attributes["_"]
        slots = handler_input.request_envelope.request.intent.slots
        slotID = slots['place'].resolutions.resolutions_per_authority[0].values[0].value.id
        r = api_request.getReqest(slotID)
        print("response printed here")
        
        speak_output = r[0]['timings_to_visit']
        response_builder = handler_input.response_builder
        if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
            response_builder.add_directive(
                RenderDocumentDirective(
                    token=HELLO_WORLD_TOKEN,
                    document=_load_apl_document(timings_to_Visit_json)
                )
            )           
        return response_builder.speak(speak_output).set_card(
            build_standard_card(
                'Timings to Visit',
                speak_output,
                'VmcIMhuWCac',
            ),
        ).response
            
        
class similarplaces(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("similarplaces")(handler_input)

    def handle(self, handler_input):
        
        data = handler_input.attributes_manager.request_attributes["_"]
        slots = handler_input.request_envelope.request.intent.slots
        slotID = slots['place'].resolutions.resolutions_per_authority[0].values[0].value.id
        r = api_request.getReqest(slotID)
        print("response printed here")
        
        speak_output = r[0]['similar_places']
        response_builder = handler_input.response_builder
        if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
            response_builder.add_directive(
                RenderDocumentDirective(
                    token=HELLO_WORLD_TOKEN,
                    document=_load_apl_document(similar_Places_To_Visit_json)
                )
            )          
        return response_builder.speak(speak_output).set_card(
            build_standard_card(
                'Similar Places',
                speak_output,
                'qaZofx5ePm8',
            ),
        ).response   

class seasontovisit(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("seasontovisit")(handler_input)

    def handle(self, handler_input):
        
        data = handler_input.attributes_manager.request_attributes["_"]
        slots = handler_input.request_envelope.request.intent.slots
        slotID = slots['place'].resolutions.resolutions_per_authority[0].values[0].value.id
        r = api_request.getReqest(slotID)
        print("response printed here")
        
        speak_output = r[0]['season']
        response_builder = handler_input.response_builder
        if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
            response_builder.add_directive(
                RenderDocumentDirective(
                    token=HELLO_WORLD_TOKEN,
                    document=_load_apl_document(seasons_To_Visit_json)
                )
            )            
        return response_builder.speak(speak_output).set_card(
            build_standard_card(
                'Best Season to Visit', 
                 speak_output,
                'vngzm4P2BTs',
            ),
        ).response


class HowToReachIntent(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("HowToReachIntent")(handler_input) and get_dialog_state(
            handler_input=handler_input) == DialogState.COMPLETED

    def handle(self, handler_input):
        response_builder = handler_input.response_builder

        place, elicit = resolve_in_session_or_input_and_elicit(
            handler_input,
            'place',
            'We need your destination to help you with that.',
            'Please say your destination.',
            'HowToReachIntent',
        )

        if place is None:
            return elicit
        else:
            place_id = resolve_place(place)
            result = api_request.getReqest(place_id)

            if len(result) < 1:
                speak_output = (
                    "Sorry, we don't have information about your destination."
                )

                return response_builder.speak(speak_output).response
            else:
                speak_output = result[0]['how_to_reach']
                dest_name = result[0]['destination_name']
                template = _load_apl_document(how_to_reach_intent_APL)

                template['datasources']['bodyTemplate6Data']['title'] = (
                    "How to Reach {}".format(dest_name)
                )

                template['datasources']['bodyTemplate6Data']['textContent']['primaryText']['text'] = (
                    speak_output
                )

                response_builder = handler_input.response_builder
                if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
                    response_builder.add_directive(
                        RenderDocumentDirective(
                            token=HELLO_WORLD_TOKEN,
                            document=template['document'],
                            datasources=template['datasources']
                        )
                    )
        
                return response_builder.speak(speak_output).set_card(
                    build_standard_card(
                        'Nearest Commute',
                        speak_output,
                        'kq8iWoh5-mU',
                    ),
                ).response


class SOScreateEmergencyList(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("SOScreateEmergencyList")(handler_input)

    def handle(self, handler_input):
        response_builder = handler_input.response_builder

        data = handler_input.attributes_manager.request_attributes["_"]
        slots = handler_input.request_envelope.request.intent.slots
        phoneNumber = slots["phoneNumber"].value

        user = "STANDARD_USER_ID"
        add_user_phone_number(user, phoneNumber)

        speak_output = "Added your phone number to emergency contact list."
        # template = _load_apl_document(SOS_create_Emergency_List_json)
        # template['datasources']['bodyTemplate6Data']['title'] = "SOS emergency"
        # template['datasources']['bodyTemplate6Data']['textContent']['primaryText']['text'] = speak_output
        
        # response_builder = handler_input.response_builder
        # if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
        #     response_builder.add_directive(
        #         RenderDocumentDirective(
        #             token=HELLO_WORLD_TOKEN,
        #             document=template['document'],
        #             datasources=template['datasources']
        #         )
        #     )

        # if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
        #     response_builder.add_directive(
        #         RenderDocumentDirective(
        #             token=HELLO_WORLD_TOKEN,
        #             document=_load_apl_document(SOS_create_Emergency_List_json)
        #         )
        #     )

        return response_builder.speak(speak_output).set_card(
            build_standard_card(
                'SOS Emergency Contact',
                speak_output,
                'HbyYFFokvm0',
            ),
        ).response


class stateplaces(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("stateplaces")(handler_input)

    def handle(self, handler_input):
        data = handler_input.attributes_manager.request_attributes["_"]


        # r = api_request.getReqest(slotID)
        speak_output = "you can visit taj mahal red fort lal quila qutub minar etc etc"

        template = _load_apl_document(state_Places_json)
        template['datasources']['bodyTemplate6Data']['title'] = "Top places to visit in"
        template['datasources']['bodyTemplate6Data']['textContent']['primaryText']['text'] = speak_output
        
        response_builder = handler_input.response_builder
        if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
            response_builder.add_directive(
                    RenderDocumentDirective(
                        token=HELLO_WORLD_TOKEN,
                        document=template['document'],
                        datasources=template['datasources']
                    )
                )
        return response_builder.speak(speak_output).set_card(
            build_standard_card(
                'Best places',
                speak_output,
                'ocknLIiMB3s',
            ),
        ).response
            
class visaneeds(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("visaneeds")(handler_input)
    def handle(self, handler_input):
        data = handler_input.attributes_manager.request_attributes["_"]
        slots = handler_input.request_envelope.request.intent.slots
        slotID = slots['country'].resolutions.resolutions_per_authority[0].values[0].value.id
        r = api_request.getReqest(slotID)

        try:
            speak_output = r[0]['visa_needs']
        except Exception as err:
            logging.error(err)
            speak_output = 'Something went wrong'

    
            template = _load_apl_document(visa_Needs_json)
            template['datasources']['bodyTemplate6Data']['title'] = "Visa needs to visit India"
            template['datasources']['bodyTemplate6Data']['textContent']['primaryText']['text'] = speak_output
        
            response_builder = handler_input.response_builder
            if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
                response_builder.add_directive(
                    RenderDocumentDirective(
                        token=HELLO_WORLD_TOKEN,
                        document=template['document'],
                        datasources=template['datasources']
                    )
                )
        return response_builder.speak(speak_output).set_card(
            build_standard_card(
                'Visa Need',
                speak_output,
                'eUjufrdx_bM',
            ),
        ).response

class SOSAskForHelp(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("SOSaskForHelp")(handler_input)

    def handle(self, handler_input):
        user = "STANDARD_USER_ID"
        phone = get_user_phone_emergency_number(user)
        response_builder = handler_input.response_builder

        if phone is None:
            speak_output = (
                "Sorry, we could not find your emergency contact on our Skill."
            )
        else:
            numbers = list(set(list(filter(None, phone.split(';')))))
    
            for number in numbers:
                if not number:
                    continue

                if not number.startswith('+91'):
                    number = '+91' + str(number)
    
                sns.publish(
                    TopicArn='TOPIC_ARN_GOES_HERE',
                    Message=json.dumps({ 'phone': number, 'message': (
                        "Hey!, your friend Avinash, on a trip to Taj Mahal has raised "
                        "an emergency alarm. His current location is Taj Mahal, please "
                        "contact the nearest hospital, with contact number: +919625250931 "
                    )}),
                )

            speak_output = (
                "We have alerted all your emergency contacts."
            )

            template = _load_apl_document(SOS_ask_For_Help_json)
            template['datasources']['bodyTemplate6Data']['title'] = "SOS"
            template['datasources']['bodyTemplate6Data']['textContent']['primaryText']['text'] = speak_output
        
            response_builder = handler_input.response_builder
            if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
                 response_builder.add_directive(
                     RenderDocumentDirective(
                         token=HELLO_WORLD_TOKEN,
                         document=template['document'],
                         datasources=template['datasources']
                     )
                 )

        return response_builder.speak(speak_output).set_card(
            build_standard_card(
                'SOS',
                speak_output,
                'lyiKExA4zQA',
            ),
        ).response


class GetMyLocationHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("MyLocation")(handler_input)

    def handle(self, handler_input):
        response_builder = handler_input.response_builder

        speak_output = ("where are you")
      
        if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
            response_builder.add_directive(
                RenderDocumentDirective(
                    token=HELLO_WORLD_TOKEN,
                    document=_load_apl_document(my_Location_json)
                )
            )
        
        return response_builder.speak(speak_output).set_card(
            AskForPermissionsConsentCard(permissions=[
                "read::alexa:device:all:address",
            ]), build_standard_card(
                'My Location',
                speak_output,
                'BJXAxQ1L7dI',
            ),
        ).response

        # return response.response


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
    """Log the alexa requests."""

    def process(self, handler_input):
        # type: (HandlerInput) -> None
        logger.debug("Alexa Request: {}".format(
            handler_input.request_envelope.request))


class ResponseLogger(AbstractResponseInterceptor):
    """Log the alexa responses."""

    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        logger.debug("Alexa Response: {}".format(response))


class SetupTour(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("SetupTour")(handler_input)

    def handle(self, handler_input):
        data = handler_input.attributes_manager.request_attributes["_"]
        slots = handler_input.request_envelope.request.intent.slots
        location = slots['location'].slot_value.value

        # Add to database.
        user = "STANDARD_USER_ID"
        add_latest_place_to_user(user, location)

        speak_output = """
        That sounds like a great idea! I can help you throughtout your stay with
        information such visitation timings, visa requiements and emergencies to
        name a few. Please don't forget to update your emergency contacts.
        """.format(location)

        response_builder = handler_input.response_builder
        template = _load_apl_document(state_plces_json)
        template['datasources']['listTemplate2Metadata']['title'] = (
            "Places You Can Visit In {0}"
        ).format(location)

        if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
            response_builder.add_directive(
                RenderDocumentDirective(
                    token=HELLO_WORLD_TOKEN,
                    document=template['document'],
                    datasources=template['datasources']
                ),
            )

        return response_builder.speak(speak_output).set_card(
            build_standard_card(
                'Setting Up Your Tour',
                speak_output,
                'qyAka7W5uMY',
            ),
        ).response


class restaurants(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("restaurants")(handler_input)

    def handle(self, handler_input):
        speak_output=("There are multiple restaurants nearby like YES Restaurant, Joney's place, The Hippie Cafe and many more")
        response_builder = handler_input.response_builder
        return response_builder.speak(speak_output).set_card(
            build_standard_card(
                'Nearby Restaurants',
                speak_output,
                'yzM66Y_D3Dc',
            ),
        ).response.response
        
class policestation(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("policestation")(handler_input)

    def handle(self, handler_input):
        speak_output=("The nearest police station Sarkhej police station is 350 meters away.")
        response_builder = handler_input.response_builder
        return response_builder.speak(speak_output).set_card(
            build_standard_card(
                'Nearby Policestation',
                speak_output,
                'T0_zDzxYvRM',
            ),
        ).response.response


def get_duration(start, end):
    try:
        directions_result = google_maps_client.directions(
            start,
            end,
            departure_time=datetime.now(),
        )
    except:
        directions_result = []

    if len(directions_result) == 0:
        try:
            directions_result = google_maps_client.directions(
                start+', India', end+', India',
                departure_time=datetime.now(),
            )
        except:
            directions_result = []

        if len(directions_result) == 0:   
            return None

    leg = directions_result[0]['legs'][0]
    summary = directions_result[0]['summary']
    duration=leg['duration_in_traffic']['text']

    to_say = (
        "Right now, it takes "+duration+" to get from "+start+" to "+end+", via "+summary
    )

    return to_say


class StepByStepNavigation(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("navigation")(handler_input)

    def handle(self, handler_input):
        response_builder = handler_input.response_builder
        place = get_slot_value(handler_input, 'place')

        speak_output = get_duration(
            get_slot_value(handler_input, 'fromCity'),
            get_slot_value(handler_input, 'toCity'),
        )

        return response_builder.speak(speak_output).set_card(
            build_standard_card(
                'Navigation',
                speak_output,
                'w1dYzfBctLc',
            ),
        ).response


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
sb.add_request_handler(SOScreateEmergencyList())
sb.add_request_handler(SOSAskForHelp())
sb.add_request_handler(GetMyLocationHandler())
sb.add_request_handler(stateplaces())
sb.add_request_handler(seasontovisit())
sb.add_request_handler(visaneeds())
sb.add_request_handler(restaurants())
sb.add_request_handler(policestation())
sb.add_request_handler(StepByStepNavigation())

sb.add_request_handler(SetupTour())

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
def lambda_handler(event, context):
    print("event", event)
    return (sb.lambda_handler())(event, context)
