# models

class TagProcessor(object):
    """docstring for TagProcessor"""
    def __init__(self, tags):
        super(TagProcessor, self).__init__()
        self.tags = tags

    def split(self, option):
        if option:
            new_tags = []
            for tag in self.tags:
                if tag.strip():
                    tag = tag.replace(';', ',')
                    new_tags.extend([t.strip() for t in tag.split(',')])
            self.tags = new_tags
        return self

    def lower(self, option, exceptions):
        if option:
            new_tags = []
            for tag in self.tags:
                new_tags.append(tag if tag in exceptions else tag.lower())
            self.tags = new_tags
        return self
