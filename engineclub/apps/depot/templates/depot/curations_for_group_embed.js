{% load markup %}{% for resource in curations %}
document.write('<p class="resource-title"><a href="{{base_url}}{% url resource resource.id %}">{{ resource.title }}</a></p>');
//document.write('<div class="gig-info">{{ gig.public_info|textile|escapejs }}</div>');
{% empty %}
document.write('<p class="line1">no results found</p>');
{% endfor %}
