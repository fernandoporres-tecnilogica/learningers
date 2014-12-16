from django.db import models

def previous_version_instance(model_class, data):
    args = {}
    # update (or finish creating)
    for key,value in data.items():
        field = model_class._meta.get_field(key)
        if not field:
            continue
        if isinstance(field, models.ManyToManyField):
            # can't add m2m until parent is saved
            continue
        elif isinstance(field, models.ForeignKey):
            rel_instance = field.rel.to.objects.get(pk=value)
            args[key] = rel_instance
        elif isinstance(field, models.OneToOneField) and isinstance(value,dict):
            rel_instance = previous_version_instance(field.rel.to, value)
            args[key] = rel_instance
        else:
            args[key] = value

    instance = model_class(**args)
    return instance