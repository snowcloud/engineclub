{% load markup %}
document.write('<div id="aliss-{{object.id}}">');
document.write('<style>h2.resource-title { font-size: 1.8em; border-top: 1px solid #DEDEDE; padding-bottom: 0.5em;} li.resource-listing-locs { font-size: 0.9em;}\
#aliss-{{object.id}} ul { padding-left: 1em; line-height: 120%;}\
</style>');


{% for resource in curations %}
{% if resource.uri %}
    document.write('<h2 class="resource-title"><a href="{{ resource.uri }}">{{ resource.title }}</a></h2>');
{% else %}
    document.write('<p class="resource-title"><a href="{{base_url}}{% url resource resource.id %}">{{ resource.title }}</a></p>');
{% endif %}

{% if resource.locations %}
document.write('<ul>{% for loc in resource.locations %}<li class="resource-listing-locs">{{ loc }}</li>{% endfor %}</ul>');
{% endif %}
document.write('<p>{{ resource.description|truncatewords:30 }}</p>');
document.write('<p class="resource-listing-meta">');
document.write('<a class="resource-url" href="{{base_url}}{% url resource resource.id %}">more details...</a>');
    {% if resource.uri %}
document.write(' | <a href="{{ resource.uri }}">web site...</a>');
    {% endif %}
document.write('</p>');




{% empty %}
document.write('<p class="line1">no results found</p>');
{% endfor %}
document.write('<p><strong>Powered by the <a href="http://www.aliss.org">ALISS Engine</a>.</strong>');
document.write('</div>');
