from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from depot.models import Item
from depot.forms import *
from mongoengine.queryset import OperationError, MultipleObjectsReturned, DoesNotExist

def get_one_or_404(**kwargs):
    try:
       object = Item.objects.get(**kwargs)
       return object
    except (MultipleObjectsReturned, DoesNotExist):
        raise Http404
    
    
def item_index(request):

    objects = Item.objects
    return render_to_response('depot/item_list.html',
        RequestContext( request, { 'objects': objects }))


def item_detail(request, object_id):

    object = get_one_or_404(id=object_id)

    return render_to_response('depot/item_detail.html',
        RequestContext( request, { 'object': object }))
        

@login_required
def item_edit(request, object_id):
    pass
    
@login_required
def item_remove(request, object_id):
    
    object = get_one_or_404(id=object_id)
    object.delete()
    return HttpResponseRedirect(reverse('item-list'))
    
@login_required
def item_add(request):

    popup = request.REQUEST.get('popup', '')
    if popup:
        formclass = ShortItemForm
        template_extends = 'base_popup.html'
    else:       
        formclass= ItemForm
        template_extends = 'base.html'
    template = 'depot/item_edit.html'

    if request.method == 'POST':
        form = formclass(request.POST)
        if form.is_valid():
            item = Item(**form.cleaned_data)
            item.author = str(request.user.id)
            try:
                item.save()
                if popup:
                    return HttpResponseRedirect(reverse('item-popup-close'))
                return HttpResponseRedirect(reverse('item', args=[item.id]))
            except OperationError:
                pass
            
    else:
        description= request.GET.get('t', '').replace('||', '\n')
        initial = {
            'url': request.GET.get('page', ''),
            'title': request.GET.get('title', ''),
            'description': description[:1250]
            }
        form = formclass(initial=initial)
    
    return render_to_response(template,
        RequestContext( request, {'form': form, 'template_extends': template_extends, 'popup': popup }))

def popup_close(request):
    pass