{% load l10n %}
{% localize off %}
{% for NAME, VALUE in JAVASCRIPT_SETTINGS.items %}
	var {{NAME}} = {{VALUE}} ;
{% endfor %}
{% endlocalize %}