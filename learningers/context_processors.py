from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm

def javascript_settings(request):
    return {'JAVASCRIPT_SETTINGS': {            
            'AP_DEFAULT_APPLET_WIDTH':settings.AP_DEFAULT_APPLET_WIDTH, 
            'AP_DEFAULT_APPLET_HEIGHT':settings.AP_DEFAULT_APPLET_HEIGHT,
            'AP_DEFAULT_APPLET_X_SPACING':settings.AP_DEFAULT_APPLET_X_SPACING, 
            'AP_DEFAULT_APPLET_Y_SPACING':settings.AP_DEFAULT_APPLET_Y_SPACING,
            } }

def login_form(request):
    return { 'login_form': AuthenticationForm(request) }
    
    