# -*- coding: utf-8 -*-

import logging
import json
import random
import math
import requests
import re


from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractRequestInterceptor, AbstractResponseInterceptor)
from ask_sdk_core.utils import is_request_type, is_intent_name, viewport
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model.ui import SimpleCard
from ask_sdk_model import Response
from ask_sdk_model.interfaces.alexa.presentation.apl import (
    RenderDocumentDirective, ExecuteCommandsDirective, SpeakItemCommand,
    AutoPageCommand, HighlightMode)

from typing import Dict, Any


SKILL_NAME = "Noticias México"
WELCOME_MESSAGE = ("<speak>Bienvenido a la Skill de Noticias México, aquí encontrarás noticias nacionales, internacionales, deportes, tecnología y más. <break time=\"500ms\"/> Si necesitas ayuda, solo dí: 'Ayuda'. ¿Qué deseas realizar? </speak>")
HELP_MESSAGE = ('''<speak> 
<p>Si deseas noticias, de alguna de estas fuentes: 'El Informador', 'El Universal', 'Reforma' o 'Expansión'; puedes decir: <break time=\"500ms\"/> </p> 
<p>"Alexa, abre Noticias México y Dame noticias sobre El Informador"</p> 
<p>"Dame noticias de deportes"</p> 
<p>"Quiero las noticias "</p> 
<p>etc.</p> 
¿Qué deseas realizar?
</speak>''')
HELP_REPROMPT = (HELP_MESSAGE)
STOP_MESSAGE = "Gracias por usar esta skill. ¡Adiós! "
EXCEPTION_MESSAGE = "No entendí muy bien, ¿Qué deseas realizar?"

MAX_NOTICIAS = 5


sb = SkillBuilder()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def apl_img_title_text(title, text):
    return {
    "json" :"apl_img_title_text.json",
                    "datasources" : {
                    "bodyTemplate1Data": {
                        "type": "object",
                        "objectId": "bt1Sample",
                        "backgroundImage": {
                            "contentDescription": None,
                            "smallSourceUrl": None,
                            "largeSourceUrl": None,
                            "sources": [
                                {
                                    "url": "https://observatoriotecnologico.org.mx/assets/img/alexa/noticias_back.jpg",
                                    "size": "small",
                                    "widthPixels": 0,
                                    "heightPixels": 0
                                },
                                {
                                    "url": "https://observatoriotecnologico.org.mx/assets/img/alexa/noticias_back.jpg",
                                    "size": "large",
                                    "widthPixels": 0,
                                    "heightPixels": 0
                                }
                            ]
                        },
                        "title": title,
                        "textContent": {
                            "primaryText": {
                                "type": "PlainText",
                                "text": text
                            }
                        },
                        "logoUrl": "https://observatoriotecnologico.org.mx/assets/img/alexa/noticias_icon.png"
                    }
                }
            }
            
def apl_title_hint(title, text):
    return {
    "json" :"apl_title_hint.json",
                    "datasources" : {
                    "bodyTemplate6Data": {
                        "type": "object",
                        "objectId": "bt6Sample",
                        "backgroundImage": {
                            "contentDescription": None,
                            "smallSourceUrl": None,
                            "largeSourceUrl": None,
                            "sources": [
                                {
                                    "url": "https://d2o906d8ln7ui1.cloudfront.net/images/BT6_Background.png",
                                    "size": "small",
                                    "widthPixels": 0,
                                    "heightPixels": 0
                                },
                                {
                                    "url": "https://d2o906d8ln7ui1.cloudfront.net/images/BT6_Background.png",
                                    "size": "large",
                                    "widthPixels": 0,
                                    "heightPixels": 0
                                }
                            ]
                        },
                        "image": {
                            "contentDescription": None,
                            "smallSourceUrl": None,
                            "largeSourceUrl": None,
                            "sources": [
                                {
                                    "url": "http://images.media-allrecipes.com/userphotos/250x250/303241.jpg",
                                    "size": "small",
                                    "widthPixels": 0,
                                    "heightPixels": 0
                                },
                                {
                                    "url": "http://images.media-allrecipes.com/userphotos/250x250/303241.jpg",
                                    "size": "large",
                                    "widthPixels": 0,
                                    "heightPixels": 0
                                }
                            ]
                        },
                        "textContent": {
                            "primaryText": {
                                "type": "PlainText",
                                "text": title
                            }
                        },
                        "logoUrl": "https://d2o906d8ln7ui1.cloudfront.net/images/cheeseskillicon.png",
                        "hintText": text
                    }
                }
            }
            
def apl_img_title_text_speech(title, text):
    return {
    "json" :"apl_img_title_text_speech.json",
                    "datasources" : {
                    "bodyTemplate1Data": {
                        "type": "object",
                        "objectId": "bt1Sample",
                        "backgroundImage": {
                            "contentDescription": None,
                            "smallSourceUrl": None,
                            "largeSourceUrl": None,
                            "sources": [
                                {
                                    "url": "https://www.macobserver.com/wp-content/uploads/2017/12/news-apps-rss-logo-1200x806.png",
                                    "size": "small",
                                    "widthPixels": 0,
                                    "heightPixels": 0
                                },
                                {
                                    "url": "https://www.macobserver.com/wp-content/uploads/2017/12/news-apps-rss-logo-1200x806.png",
                                    "size": "large",
                                    "widthPixels": 0,
                                    "heightPixels": 0
                                }
                            ]
                        },
                        "title": title,
                        "textContent": {
                            "primaryText": {
                                "type": "PlainText",
                                "text": text
                            }
                        },
                        "logoUrl": "https://observatoriotecnologico.org.mx/assets/img/alexa/calculo_icon.png"
                    }
                }
            }

def _load_apl_document(file_path):
    # type: (str) -> Dict[str, Any]
    """Load the apl json document at the path into a dict object."""
    with open(file_path) as f:
        return json.load(f)

# Built-in Intent Handlers
class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In LaunchRequest")

        speech = WELCOME_MESSAGE

        apl = apl_img_title_text("Bienvenido", re.sub('<[^<]+>', "",WELCOME_MESSAGE))

        if viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_LANDSCAPE_LARGE or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_LANDSCAPE_MEDIUM or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_ROUND_SMALL or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.TV_LANDSCAPE_XLARGE or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.MOBILE_LANDSCAPE_SMALL:
            handler_input.response_builder.speak(speech).add_directive(
                RenderDocumentDirective(document=_load_apl_document(apl["json"]),datasources=apl["datasources"])
            ).set_should_end_session(False)
        else:
            handler_input.response_builder.speak(speech).set_card(SimpleCard(SKILL_NAME, re.sub('<[^<]+>', "",speech))).set_should_end_session(False)
            
        #handler_input.response_builder.speak(speech).ask(speech).set_card(
        #    SimpleCard(SKILL_NAME, speech))
        return handler_input.response_builder.response


class NoticiasPortadaIntentHandler(AbstractRequestHandler):
    """Handler for Device Information Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("noticias_portada")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("noticias_portada")

        card_title = "Noticias"
        card_content = "Estas son las noticias"
        
        attribute_manager = handler_input.attributes_manager
        session_attr = attribute_manager.session_attributes
        
        #session_attributes = {"valor_anterior":MAX_NOTICIAS, "noticias":None}
        session_attr["valor_anterior"] = MAX_NOTICIAS
        session_attr["noticias"] = None
        
        data = None
        try:
            resp = requests.get('http://observatoriotecnologico.org.mx:8111/rss/noticias/portada')
            data = resp.json() 
            tema = 'Las noticias de hoy'
            
            accion = ""
            if len(data) <= MAX_NOTICIAS:
                session_attributes = {"valor_anterior": 0, "noticias":None}
                accion = "<s>Estas fueron las noticias de hoy. ¿Qué más deseas realizar?</s>"
            else:
                accion = "<s>¿Deseas seguir escuchando?</s>"
                
            speechSSML = ""
            
            card_content = ""
            for idx, noticia in enumerate(data):
                if idx < MAX_NOTICIAS:
                    card_content = card_content +"<b>"+ noticia['title'] + "</b><br>"+noticia['summary']+"<br><br>"
                    speechSSML = speechSSML + '''
    '''+ ('<s><say-as interpret-as="expletive">.</say-as></s>' if idx > 0 else '') +'''
    <p>'''+noticia['title']+'''
    <s><emphasis level="reduced">'''+noticia['summary']+'''</emphasis></s>
    </p>'''
            
            speechSSML = speechSSML + '''<audio src='soundbank://soundlibrary/ui/gameshow/amzn_ui_sfx_gameshow_neutral_response_03'/>
    '''+accion
    
            if len(data) > MAX_NOTICIAS:
                del data[0: MAX_NOTICIAS]
                #session_attributes = {"valor_anterior": MAX_NOTICIAS, "noticias":data, "count":len(data)}
                session_attr["valor_anterior"] = MAX_NOTICIAS
                session_attr["noticias"] = data
                #session_attr["count"] = len(data)
        
        except:
            print("Ocurrio algo inesperado")
            speech = "<speak>No entendí la pregunta. ¿Qué más deseas realizar?</speak>"
            #session_attributes = {"valor_anterior": 0, "noticias":data}
            session_attr["valor_anterior"] = 0
            session_attr["noticias"] = data
        
        
        speech = 'En '+tema+ "<audio src=\'soundbank://soundlibrary/ui/gameshow/amzn_ui_sfx_gameshow_outro_01\'/>"
        

        if viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_LANDSCAPE_LARGE or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_LANDSCAPE_MEDIUM or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_ROUND_SMALL or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.TV_LANDSCAPE_XLARGE or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.MOBILE_LANDSCAPE_SMALL:
            apl = apl_img_title_text('En '+tema, card_content)
            handler_input.response_builder.speak("<speak>"+speech+speechSSML+"</speak>").add_directive(
                RenderDocumentDirective(document=_load_apl_document(apl["json"]),datasources=apl["datasources"])
                ).set_should_end_session(False)
            
        else:
            handler_input.response_builder.speak("<speak>"+speech+speechSSML+"</speak>").set_card(SimpleCard(SKILL_NAME, re.sub('<[^<]+>', "",speech))).set_should_end_session(False)
            
            
        return handler_input.response_builder.response
        
        
class NoticiasCategoriaIntentHandler(AbstractRequestHandler):
    """Handler for Device Information Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("noticias_categoria")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("noticias_categoria")

        card_title = "Noticias"
        card_content = "Estas son las noticias"
        
        attribute_manager = handler_input.attributes_manager
        session_attr = attribute_manager.session_attributes
        
        #session_attributes = {"valor_anterior":MAX_NOTICIAS, "noticias":None}
        session_attr["valor_anterior"] = MAX_NOTICIAS
        session_attr["noticias"] = None
        slots = handler_input.request_envelope.request.intent.slots
        
        try:
            categoria_nombre = str(slots['categoria'].resolutions.resolutions_per_authority[0].values[0].value.name)
            categoria_id = str(slots['categoria'].resolutions.resolutions_per_authority[0].values[0].value.id)
        except:
            categoria_nombre= None
            categoria_id = None
            
        if categoria_nombre is None:
            handler_input.response_builder.speak(HELP_MESSAGE).ask(HELP_REPROMPT).set_card(SimpleCard(SKILL_NAME, re.sub('<[^<]+>', "",HELP_MESSAGE))).set_should_end_session(False)
            return handler_input.response_builder.response  
        
        data = None
        try:
            resp = requests.get('http://observatoriotecnologico.org.mx:8111/rss/noticias/categoria/'+categoria_id)
            data = resp.json() 
            tema = '"'+categoria_nombre+'"'
            
            accion = ""
            if len(data) <= MAX_NOTICIAS:
                session_attributes = {"valor_anterior": 0, "noticias":None}
                accion = "<s>Estas fueron las noticias de hoy. ¿Qué más deseas realizar?</s>"
            else:
                accion = "<s>¿Deseas seguir escuchando?</s>"
                
            speechSSML = ""
            
            card_content = ""
            for idx, noticia in enumerate(data):
                if idx < MAX_NOTICIAS:
                    card_content = card_content +"<b>"+ noticia['title'] + "</b><br>"+noticia['summary']+"<br><br>"
                    speechSSML = speechSSML + '''
    '''+ ('<s><say-as interpret-as="expletive">.</say-as></s>' if idx > 0 else '') +'''
    <p>'''+noticia['title']+'''
    <s><emphasis level="reduced">'''+noticia['summary']+'''</emphasis></s>
    </p>'''
            
            speechSSML = speechSSML + '''<audio src='soundbank://soundlibrary/ui/gameshow/amzn_ui_sfx_gameshow_neutral_response_03'/>
    '''+accion
    
            if len(data) > MAX_NOTICIAS:
                del data[0: MAX_NOTICIAS]
                #session_attributes = {"valor_anterior": MAX_NOTICIAS, "noticias":data, "count":len(data)}
                session_attr["valor_anterior"] = MAX_NOTICIAS
                session_attr["noticias"] = data
                #session_attr["count"] = len(data)
        
        except:
            print("Ocurrio algo inesperado")
            speech = "<speak>No entendí la pregunta. ¿Qué más deseas realizar?</speak>"
            #session_attributes = {"valor_anterior": 0, "noticias":data}
            session_attr["valor_anterior"] = 0
            session_attr["noticias"] = data
        
        
        speech = 'En '+tema+ "<audio src=\'soundbank://soundlibrary/ui/gameshow/amzn_ui_sfx_gameshow_outro_01\'/>"
        

        if viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_LANDSCAPE_LARGE or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_LANDSCAPE_MEDIUM or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_ROUND_SMALL or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.TV_LANDSCAPE_XLARGE or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.MOBILE_LANDSCAPE_SMALL:
            apl = apl_img_title_text('En '+tema, card_content)
            handler_input.response_builder.speak("<speak>"+speech+speechSSML+"</speak>").add_directive(
                RenderDocumentDirective(document=_load_apl_document(apl["json"]),datasources=apl["datasources"])
                ).set_should_end_session(False)
            
        else:
            handler_input.response_builder.speak("<speak>"+speech+speechSSML+"</speak>").set_card(SimpleCard(SKILL_NAME, re.sub('<[^<]+>', "",speech))).set_should_end_session(False)
            
            
        return handler_input.response_builder.response        
        
        
class NoticiasFuenteIntentHandler(AbstractRequestHandler):
    """Handler for Device Information Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("noticias_fuente")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("noticias_fuente")

        card_title = "Noticias"
        card_content = "Estas son las noticias"
        
        attribute_manager = handler_input.attributes_manager
        session_attr = attribute_manager.session_attributes
        
        #session_attributes = {"valor_anterior":MAX_NOTICIAS, "noticias":None}
        session_attr["valor_anterior"] = MAX_NOTICIAS
        session_attr["noticias"] = None
        slots = handler_input.request_envelope.request.intent.slots
        
        try:
            fuente_nombre = str(slots['fuente'].resolutions.resolutions_per_authority[0].values[0].value.name)
            fuente_id = str(slots['fuente'].resolutions.resolutions_per_authority[0].values[0].value.id)
        except:
            fuente_nombre= None
            fuente_id = None
            
        if fuente_nombre is None:
            handler_input.response_builder.speak(HELP_MESSAGE).ask(HELP_REPROMPT).set_card(SimpleCard(SKILL_NAME, re.sub('<[^<]+>', "",HELP_MESSAGE))).set_should_end_session(False)
            return handler_input.response_builder.response  
        
        data = None
        try:
            resp = requests.get('http://observatoriotecnologico.org.mx:8111/rss/noticias/portada/fuente/'+fuente_id)
            data = resp.json() 
            tema = '"'+fuente_nombre+'"'
            
            accion = ""
            if len(data) <= MAX_NOTICIAS:
                session_attributes = {"valor_anterior": 0, "noticias":None}
                accion = "<s>Estas fueron las noticias de hoy. ¿Qué más deseas realizar?</s>"
            else:
                accion = "<s>¿Deseas seguir escuchando?</s>"
                
            speechSSML = ""
            
            card_content = ""
            for idx, noticia in enumerate(data):
                if idx < MAX_NOTICIAS:
                    card_content = card_content +"<b>"+ noticia['title'] + "</b><br>"+noticia['summary']+"<br><br>"
                    speechSSML = speechSSML + '''
    '''+ ('<s><say-as interpret-as="expletive">.</say-as></s>' if idx > 0 else '') +'''
    <p>'''+noticia['title']+'''
    <s><emphasis level="reduced">'''+noticia['summary']+'''</emphasis></s>
    </p>'''
            
            speechSSML = speechSSML + '''<audio src='soundbank://soundlibrary/ui/gameshow/amzn_ui_sfx_gameshow_neutral_response_03'/>
    '''+accion
    
            if len(data) > MAX_NOTICIAS:
                del data[0: MAX_NOTICIAS]
                #session_attributes = {"valor_anterior": MAX_NOTICIAS, "noticias":data, "count":len(data)}
                session_attr["valor_anterior"] = MAX_NOTICIAS
                session_attr["noticias"] = data
                #session_attr["count"] = len(data)
        
        except:
            print("Ocurrio algo inesperado")
            speech = "<speak>No entendí la pregunta. ¿Qué más deseas realizar?</speak>"
            #session_attributes = {"valor_anterior": 0, "noticias":data}
            session_attr["valor_anterior"] = 0
            session_attr["noticias"] = data
        
        
        speech = 'En '+tema+ "<audio src=\'soundbank://soundlibrary/ui/gameshow/amzn_ui_sfx_gameshow_outro_01\'/>"
        

        if viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_LANDSCAPE_LARGE or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_LANDSCAPE_MEDIUM or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_ROUND_SMALL or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.TV_LANDSCAPE_XLARGE or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.MOBILE_LANDSCAPE_SMALL:
            apl = apl_img_title_text('En '+tema, card_content)
            handler_input.response_builder.speak("<speak>"+speech+speechSSML+"</speak>").add_directive(
                RenderDocumentDirective(document=_load_apl_document(apl["json"]),datasources=apl["datasources"])
                ).set_should_end_session(False)
            
        else:
            handler_input.response_builder.speak("<speak>"+speech+speechSSML+"</speak>").set_card(SimpleCard(SKILL_NAME, re.sub('<[^<]+>', "",speech))).set_should_end_session(False)
            
            
        return handler_input.response_builder.response        
        
        
class NoticiasFuenteCategoriaIntentHandler(AbstractRequestHandler):
    """Handler for Device Information Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("noticias_fuente_categoria")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("noticias_fuente_categoria")

        card_title = "Noticias"
        card_content = "Estas son las noticias"
        
        attribute_manager = handler_input.attributes_manager
        session_attr = attribute_manager.session_attributes
        
        #session_attributes = {"valor_anterior":MAX_NOTICIAS, "noticias":None}
        session_attr["valor_anterior"] = MAX_NOTICIAS
        session_attr["noticias"] = None
        slots = handler_input.request_envelope.request.intent.slots
        
        try:
            fuente_nombre = str(slots['fuente'].resolutions.resolutions_per_authority[0].values[0].value.name)
            fuente_id = str(slots['fuente'].resolutions.resolutions_per_authority[0].values[0].value.id)
        except:
            fuente_nombre= None
            fuente_id = None
            
        if fuente_nombre is None:
            handler_input.response_builder.speak(HELP_MESSAGE).ask(HELP_REPROMPT).set_card(SimpleCard(SKILL_NAME, re.sub('<[^<]+>', "",HELP_MESSAGE))).set_should_end_session(False)
            return handler_input.response_builder.response  
            
        try:
            categoria_nombre = str(slots['categoria'].resolutions.resolutions_per_authority[0].values[0].value.name)
            categoria_id = str(slots['categoria'].resolutions.resolutions_per_authority[0].values[0].value.id)
        except:
            categoria_nombre= None
            categoria_id = None
            
        if categoria_nombre is None:
            handler_input.response_builder.speak(HELP_MESSAGE).ask(HELP_REPROMPT).set_card(SimpleCard(SKILL_NAME, re.sub('<[^<]+>', "",HELP_MESSAGE))).set_should_end_session(False)
            return handler_input.response_builder.response  
        
        data = None
        try:
            resp = requests.get('http://observatoriotecnologico.org.mx:8111/rss/noticias/fuente/categoria/'+fuente_id+'/'+categoria_id)
            data = resp.json() 
            tema = '"'+categoria_nombre+'" en "'+fuente_nombre+"'"
            
            accion = ""
            if len(data) <= MAX_NOTICIAS:
                session_attributes = {"valor_anterior": 0, "noticias":None}
                accion = "<s>Estas fueron las noticias de hoy. ¿Qué más deseas realizar?</s>"
            else:
                accion = "<s>¿Deseas seguir escuchando?</s>"
                
            speechSSML = ""
            
            card_content = ""
            for idx, noticia in enumerate(data):
                if idx < MAX_NOTICIAS:
                    card_content = card_content +"<b>"+ noticia['title'] + "</b><br>"+noticia['summary']+"<br><br>"
                    speechSSML = speechSSML + '''
    '''+ ('<s><say-as interpret-as="expletive">.</say-as></s>' if idx > 0 else '') +'''
    <p>'''+noticia['title']+'''
    <s><emphasis level="reduced">'''+noticia['summary']+'''</emphasis></s>
    </p>'''
            
            speechSSML = speechSSML + '''<audio src='soundbank://soundlibrary/ui/gameshow/amzn_ui_sfx_gameshow_neutral_response_03'/>
    '''+accion
    
            if len(data) > MAX_NOTICIAS:
                del data[0: MAX_NOTICIAS]
                #session_attributes = {"valor_anterior": MAX_NOTICIAS, "noticias":data, "count":len(data)}
                session_attr["valor_anterior"] = MAX_NOTICIAS
                session_attr["noticias"] = data
                #session_attr["count"] = len(data)
        
        except:
            print("Ocurrio algo inesperado")
            speech = "<speak>No entendí la pregunta. ¿Qué más deseas realizar?</speak>"
            #session_attributes = {"valor_anterior": 0, "noticias":data}
            session_attr["valor_anterior"] = 0
            session_attr["noticias"] = data
        
        
        speech = tema+ "<audio src=\'soundbank://soundlibrary/ui/gameshow/amzn_ui_sfx_gameshow_outro_01\'/>"
        

        if viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_LANDSCAPE_LARGE or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_LANDSCAPE_MEDIUM or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_ROUND_SMALL or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.TV_LANDSCAPE_XLARGE or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.MOBILE_LANDSCAPE_SMALL:
            apl = apl_img_title_text(tema, card_content)
            handler_input.response_builder.speak("<speak>"+speech+speechSSML+"</speak>").add_directive(
                RenderDocumentDirective(document=_load_apl_document(apl["json"]),datasources=apl["datasources"])
                ).set_should_end_session(False)
            
        else:
            handler_input.response_builder.speak("<speak>"+speech+speechSSML+"</speak>").set_card(SimpleCard(SKILL_NAME, re.sub('<[^<]+>', "",speech))).set_should_end_session(False)
            
            
        return handler_input.response_builder.response     


class ContinuarIntentHandler(AbstractRequestHandler):
    """Handler for Device Information Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("continuar")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("continuar")

        card_title = "Noticias"
        card_content = "Estas son las noticias"
        
        attribute_manager = handler_input.attributes_manager
        session_attr = attribute_manager.session_attributes
        
        #session_attributes = {"valor_anterior":MAX_NOTICIAS, "noticias":None}
        #session_attr["valor_anterior"] = MAX_NOTICIAS
        #session_attr["noticias"] = None
        
        data = None
        try:
            #resp = requests.get('http://observatoriotecnologico.org.mx:8111/rss/noticias/portada')
            #data = resp.json() 
            data = session_attr["noticias"]
            tema = 'Continuamos..'
            
            accion = ""
            if len(data) <= MAX_NOTICIAS:
                session_attributes = {"valor_anterior": 0, "noticias":None}
                accion = "<s>Estas fueron las noticias de hoy. ¿Qué más deseas realizar?</s>"
            else:
                accion = "<s>¿Deseas seguir escuchando?</s>"
                
            speechSSML = ""
            
            card_content = ""
            for idx, noticia in enumerate(data):
                if idx < MAX_NOTICIAS:
                    card_content = card_content +"<b>"+ noticia['title'] + "</b><br>"+noticia['summary']+"<br><br>"
                    speechSSML = speechSSML + '''
    '''+ ('<s><say-as interpret-as="expletive">.</say-as></s>' if idx > 0 else '') +'''
    <p>'''+noticia['title']+'''
    <s><emphasis level="reduced">'''+noticia['summary']+'''</emphasis></s>
    </p>'''
            
            speechSSML = speechSSML + '''<audio src='soundbank://soundlibrary/ui/gameshow/amzn_ui_sfx_gameshow_neutral_response_03'/>
    '''+accion
    
            if len(data) > MAX_NOTICIAS:
                del data[0: MAX_NOTICIAS]
                #session_attributes = {"valor_anterior": MAX_NOTICIAS, "noticias":data, "count":len(data)}
                session_attr["valor_anterior"] = MAX_NOTICIAS
                session_attr["noticias"] = data
                #session_attr["count"] = len(data)
        
        except:
            print("Ocurrio algo inesperado")
            speech = "<speak>No entendí la pregunta. ¿Qué más deseas realizar?</speak>"
            #session_attributes = {"valor_anterior": 0, "noticias":data}
            session_attr["valor_anterior"] = 0
            session_attr["noticias"] = data
        
        
        speech = tema
        

        if viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_LANDSCAPE_LARGE or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_LANDSCAPE_MEDIUM or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_ROUND_SMALL or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.TV_LANDSCAPE_XLARGE or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.MOBILE_LANDSCAPE_SMALL:
            apl = apl_img_title_text('En '+tema, card_content)
            handler_input.response_builder.speak("<speak>"+speech+speechSSML+"</speak>").add_directive(
                RenderDocumentDirective(document=_load_apl_document(apl["json"]),datasources=apl["datasources"])
                ).set_should_end_session(False)
            
        else:
            handler_input.response_builder.speak("<speak>"+speech+speechSSML+"</speak>").set_card(SimpleCard(SKILL_NAME, re.sub('<[^<]+>', "",speech))).set_should_end_session(False)
            
            
        return handler_input.response_builder.response        
        
        
class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ( is_intent_name("AMAZON.HelpIntent")(handler_input) or
                is_intent_name("noticias_ayuda")(handler_input) )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In HelpIntentHandler")

        handler_input.response_builder.speak(HELP_MESSAGE).ask(
            HELP_REPROMPT).set_card(SimpleCard(
                SKILL_NAME, re.sub('<[^<]+>', "",HELP_MESSAGE))).set_should_end_session(False)
        return handler_input.response_builder.response


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input) or
                is_intent_name("salir")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In CancelOrStopIntentHandler")

        handler_input.response_builder.speak(STOP_MESSAGE).set_should_end_session(True)
        return handler_input.response_builder.response


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

        handler_input.response_builder.speak(EXCEPTION_MESSAGE).ask(
            HELP_REPROMPT)

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


# Register intent handlers
sb.add_request_handler(LaunchRequestHandler())

sb.add_request_handler(NoticiasPortadaIntentHandler())
sb.add_request_handler(NoticiasCategoriaIntentHandler())
sb.add_request_handler(NoticiasFuenteIntentHandler())
sb.add_request_handler(NoticiasFuenteCategoriaIntentHandler())
sb.add_request_handler(ContinuarIntentHandler())


sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

# Register exception handlers
sb.add_exception_handler(CatchAllExceptionHandler())

# TODO: Uncomment the following lines of code for request, response logs.
# sb.add_global_request_interceptor(RequestLogger())
# sb.add_global_response_interceptor(ResponseLogger())

# Handler name that is used on AWS lambda
lambda_handler = sb.lambda_handler()
