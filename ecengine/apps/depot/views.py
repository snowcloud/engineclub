from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from apps.depot.models import Item
from apps.depot.forms import *
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
        
def item_edit(request, object_id):
    pass
    
def item_remove(request, object_id):
    pass
    
def item_add(request):

    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = Item(**form.cleaned_data)
            try:
                item.save()
                return HttpResponseRedirect(reverse('item', args=[item.id]))
            except OperationError:
                pass
            
    else:
        form = ItemForm(initial={'name': 'fred'})
        
    return render_to_response('depot/item_edit.html',
        RequestContext( request, {'form': form,  }))

