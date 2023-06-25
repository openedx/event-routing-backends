import logging, json
from enum import Enum
from tokenize import String
from event_routing_backends.campus_il.configuration import config

class FieldTypes(Enum):
    TEXT = 'Text'
    LANG = 'Language'
    
class MOEMapping():

    def __init__(self):
        pass

    def map_event(self, event=None, event_str = ''):
        event = json.loads(event_str) if event_str else event

        # Mapping logic to convert to external organization JSON format
        external_event = {
            "id": event.get("id", ""),
            "timestamp": event.get("timestamp", ""),
            "version": event.get("version", ""),
            
            
            "actor": {
                "objectType": event["actor"]["object_type"],
                "account": self.__add_field_if_exist(event["actor"]["account"], {
                    "homePage": FieldTypes.TEXT,
                    "name": FieldTypes.TEXT,
                })
            },
            
            
            "verb": {
                "id": event["verb"]["id"],
                "display": event["verb"]["display"]
            },

         
            "object": {
                "objectType": event["object"]["object_type"],
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
                    "duration": FieldTypes.TEXT,
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
              
        # Convert to JSON string
        external_event = self.__map_fields_data(external_event)

        return external_event


    def __map_fields_data(sel, event):

        # Create a mapping dictionary for verbs
        verb_mapping = {
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
        
        for field_name, field_type in fieldsTypes.items():
            if field_name in section:
                #if field_type is FieldTypes.OBJ:
                #    _output[field_name] = self.__add_field_if_exist(section[field_name])
                if field_type is FieldTypes.LANG:
                    _output[field_name] = self.__gt_object_definition_name(section[field_name])
                else:
                    _output[field_name] = section[field_name]
        
        return _output
    
    def __gt_object_definition_name(self, value):
        _output = {}
        
        if type(value) is dict:
            for key in value:
                _lang = key.split('-')[0]
                _output[_lang] = value[key]
        
        return _output