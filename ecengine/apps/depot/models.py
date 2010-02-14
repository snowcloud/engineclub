from django.db import models

class TestItem(models.Model):

    idx = models.AutoField(primary_key=True)
    name = models.CharField(blank=True, max_length=80)
    
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        pass
        # print 'saving'
        
    def __unicode__(self):
        return '%s: %s' % (self.idx, self.name)
     
