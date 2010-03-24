from django.utils import translation

from haystack import indexes


class TransSearchIndex(indexes.SearchIndex):
    """
    A version of SearchIndex for language-specific objects that have a 
    "langauge" attribute.
    
    This class ensures that all prepared fields are prepared with the system
    language set to the language of the object.
    """
    def prepare(self, obj):
        current_language = translation.get_language()
        translation.activate(obj.language)
        ret = super(TransSearchIndex, self).prepare(obj)
        translation.activate(current_language)
        return ret
