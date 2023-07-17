import logging, json, re
from enum import Enum
from tokenize import String
from event_routing_backends.campus_il.configuration import config
from common.djangoapps.student.models import CourseAccessRole
from social_django.models import UserSocialAuth

class FieldTypes(Enum):
    TEXT = 'Text'
    LANG = 'Language'
    DURATION = 'Duration'
    IDENTIFIER = 'identifier'
    OBJ = 'Object'

class MOEMapping():

    def __init__(self):
        pass

    def map_event(self, event=None, event_str = ''):
        event = json.loads(event_str) if event_str else event
        logging.info(f'qwer111 CampusIL event: {event}')
        # Mapping logic to convert to external organization JSON format
        external_event = {
            "id": event.get("id", ""),
            "timestamp": event.get("timestamp", ""),
            "version": event.get("version", ""),
            
            
            "actor": {
                "objectType": event["actor"].get("object_type", event["actor"]["objectType"]),
                "account": self.__add_field_if_exist(event["actor"]["account"], {
                    "homePage": FieldTypes.IDENTIFIER,
                    "name": FieldTypes.TEXT,
                })
            },
            
            "verb": {
                "id": event["verb"]["id"],
                "display": event["verb"]["display"]
            },

         
            "object": {
                "objectType": event["object"].get("object_type", event["object"]["objectType"]),
                "id": event["object"]["id"],
                "definition": self.__add_field_if_exist(event["object"]["definition"], {
                    "type": FieldTypes.TEXT,
                    "name": FieldTypes.LANG,
                    "description": FieldTypes.LANG
                })
            },
            #result
            #context
        }
        
        # add result
        if "result" in event:
            
            external_event["result"] = self.__add_field_if_exist(event["result"], {
                    "success": FieldTypes.TEXT,
                    "completion": FieldTypes.TEXT,
                    "duration": FieldTypes.DURATION,
                })
            if "score" in event["result"]:
                external_event["result"]["score"] = self.__add_field_if_exist(event["result"]["score"], {
                    "scaled": FieldTypes.TEXT,
                    "raw": FieldTypes.TEXT,
                    "min": FieldTypes.TEXT,
                    "max": FieldTypes.TEXT,
                })
            if "extensions" in event["result"]:
                external_event["result"]["extensions"] = event["result"]["extensions"]
        
        # add context
        if "context" in event:
            for parent in event.get("context", {}).get("contextActivities", {}).get("parent", []):
                _parent = self.__add_field_if_exist(parent, {
                        "id": FieldTypes.TEXT,
                        "objectType": FieldTypes.TEXT,
                    })
                if "definition" in parent:
                    _parent["definition"] = self.__add_field_if_exist(parent["definition"], {
                            "name": FieldTypes.LANG,
                            "type": FieldTypes.TEXT,
                        })
                external_event.setdefault("context", {}).setdefault("contextActivities", {}).setdefault("parent", []).append(_parent)  
        
        # add instructor information
        external_event.setdefault("context", {})["instructor"] = self.__get_intrsuctor_node("ccx-v1:TO+CO777+Month_777+ccx@9")
        
        # Convert to JSON string
        external_event = self.__map_fields_data(external_event)

        return external_event


    def __map_fields_data(sel, event):

        # Create a mapping dictionary for verbs
        verb_mapping = {
            "http://adlnet.gov/expapi/verbs/registered": "https://lxp.education.gov.il/xapi/moe/verbs/join",
            "http://id.tincanapi.com/verb/unregistered": "https://lxp.education.gov.il/xapi/moe/verbs/leave",
            "http://adlnet.gov/expapi/verbs/attempted": "https://lxp.education.gov.il/xapi/moe/verbs/attempted",
            "http://adlnet.gov/expapi/verbs/answered": "https://lxp.education.gov.il/xapi/moe/verbs/answered",
            "https://w3id.org/xapi/acrossx/verbs/evaluated": "https://lxp.education.gov.il/xapi/moe/verbs/scored",
            "http://adlnet.gov/expapi/verbs/completed": "https://lxp.education.gov.il/xapi/moe/verbs/completed",
            "https://w3id.org/xapi/video/verbs/played": "https://lxp.education.gov.il/xapi/moe/verbs/played",
            "https://w3id.org/xapi/video/verbs/paused": "https://lxp.education.gov.il/xapi/moe/verbs/paused",
            "https://w3id.org/xapi/video/verbs/seeked": "https://lxp.education.gov.il/xapi/moe/verbs/watched"
        }

        # Create a mapping dictionary for activities
        activity_mapping = {
            "http://adlnet.gov/expapi/activities/question": "https://lxp.education.gov.il/xapi/moe/activities/question",
            "https://w3id.org/xapi/video/activity-type/video": "https://lxp.education.gov.il/xapi/moe/activities/video",
            "http://adlnet.gov/expapi/activities/course": "https://lxp.education.gov.il/xapi/moe/activities/course"
        }

        # Perform the mapping
        mapped_data = event.copy()

        # Map the verb
        if "verb" in event:
            verb_id = event["verb"]["id"]
            if verb_id in verb_mapping:
                mapped_data["verb"]["id"] = verb_mapping[verb_id]

        # Map the activity
        if "object" in event:
            if "id" in event["object"]:
                activity_id = event["object"]["id"]
                if activity_id in activity_mapping:
                    mapped_data["object"]["id"] = activity_mapping[activity_id]

        return mapped_data
    
    def __add_field_if_exist(self, section, fieldsTypes):
        _output = {}
        _extensions_section = 'extensions'
        
        for field_name, field_type in fieldsTypes.items():
            if field_name in section:
                #if field_type is FieldTypes.OBJ:
                #    _output[field_name] = self.__add_field_if_exist(section[field_name])
                if field_type is FieldTypes.LANG:
                    _output[field_name] = self.__get_object_definition_name(section[field_name])
                elif field_type is FieldTypes.IDENTIFIER:
                    _output[field_name] = self.__get_user_id_identifier(section["name"])
                else:
                    _output[field_name] = section[field_name]
            elif field_type is FieldTypes.DURATION:
                _seconds = int(section.get(_extensions_section, {}).get(config.Get("MAPPING_EXTENSIONS_TIME"), 0))
                _output[field_name] = self.__convert_seconds_to_hms(_seconds)
        
        return _output
    
    def __get_object_definition_name(self, value):
        _output = {}
        
        if type(value) is dict:
            for key in value:
                _lang = key.split('-')[0]
                _output[_lang] = value[key]
        
        return _output
    
    def __get_user_id_identifier(self, number):
        if re.match(r'^[0-9]+$', number):
            return config.Get("MAPPING_IDENTIFIER_MOE")
        elif re.match(r'^[0-9a-fA-F]+$', number):
            return config.Get("MAPPING_IDENTIFIER_CAMPUSIL")
        else:
            return config.Get("MAPPING_IDENTIFIER_UNKNOWN")
    
    def __convert_seconds_to_hms(self, seconds):
        seconds = 0 if seconds is None else seconds
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        hours_str = f'{hours}H' if hours > 0 else ''
        minutes_str = f'{minutes:02d}M' if minutes > 0 else ''
        seconds_str = f'{seconds:02d}.00S'
        
        duration_string = f"PT{hours_str}{minutes_str}{seconds_str}"
        return duration_string
    
    def __get_intrsuctor_node(self, course_id):
        
        teacher_course_role = CourseAccessRole.objects.filter(
            course_id=course_id,
            role='staff',
        ).exclude(
            user__email__endswith='campus.gov.il'
        ).first()
        
        logging.info(f"Teacher of CCX: {teacher_course_role}")
        
        # get teacher's IDM
        if teacher_course_role:
            social_auth = UserSocialAuth.objects.filter(user__id=teacher_course_role.user.id, provider='tpa-saml', uid__startswith='moe-edu-idm:').first()
            
            logging.info(f"Teacher of CCX social_auth: {social_auth}")
            if social_auth:
                anonymous_id = social_auth.uid.split(':')[1]
                logging.info(f"Teacher of CCX anonymous_id: {anonymous_id}")
                
                return {
                    "objectType": "Agent",
                    "account": {
                        "homePage": config.Get("MAPPING_IDENTIFIER_MOE"),
                        "name": anonymous_id
                    }
                }
        
        return None