from functools import partial
from itertools import groupby
from operator import attrgetter

import django.db.models
from django.forms.models import ModelChoiceField, ModelChoiceIterator


# https://simpleisbetterthancomplex.com/tutorial/2019/01/02/how-to-implement-grouped-model-choice-field.html
class GroupedModelChoiceIterator(ModelChoiceIterator):
    """Iterator that groups choices by a given attribute."""

    def __init__(self, field: django.db.models.Field, group_by: callable):
        self.group_by = group_by
        super().__init__(field)

    def __iter__(self):
        if self.field.empty_label is not None:
            yield "", self.field.empty_label
        queryset = self.queryset
        # Can't use iterator() when queryset uses prefetch_related()
        if not queryset._prefetch_related_lookups:
            queryset = queryset.iterator()
        for group, objs in groupby(queryset, self.group_by):
            yield group, [self.choice(obj) for obj in objs]


class GroupedModelChoiceField(ModelChoiceField):
    """A ModelChoiceField that groups choices by a provided attribute."""

    def __init__(self, *args, choices_group_by: str, **kwargs):
        if isinstance(choices_group_by, str):
            choices_group_by = attrgetter(choices_group_by)
        elif not callable(choices_group_by):
            raise TypeError(
                "choices_group_by must either be a str or a callable accepting a single argument"
            )
        self.iterator = partial(GroupedModelChoiceIterator, group_by=choices_group_by)
        super().__init__(*args, **kwargs)
