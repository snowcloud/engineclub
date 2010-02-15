from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from apps.depot.models import Item
from apps.depot.forms import *
from mongoengine.queryset import OperationError

def item_index(request):

    objects = Item.objects
    return render_to_response('depot/item_list.html',
        RequestContext( request, { 'objects': objects }))


def item_detail(request, object_id):

    objects = Item.objects(id=object_id)
    print objects[0].name
    
    return render_to_response('depot/item_detail.html',
        RequestContext( request, { 'object': objects[0] }))
        
def item_add(request):

    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = Item(**form.cleaned_data)
            try:
                item.save()
            except OperationError:
                pass
            # post = form.save(commit=False)
            # post.author = request.user
            # post.slug = slugify(post.title)
            # post.publish = datetime.datetime.now()
            # post.ct_group = group
            # post.save()
            
            return HttpResponseRedirect('/depot/item/')
    else:
        form = ItemForm(initial={'name': 'fred'})
        
    return render_to_response('depot/item_edit.html',
        RequestContext( request, {'form': form,  }))

