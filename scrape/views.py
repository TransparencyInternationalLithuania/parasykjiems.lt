import re
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
import models


_CHANGE_ID_RE = re.compile(r'(?P<model>[^_]+)_(?P<id>\d+)')
_MODELS = {'representative': models.RepresentativeChange,
           'institution': models.InstitutionChange}


@login_required(login_url='/admin/', redirect_field_name=None)
def admin_update(request):
    if request.method == 'POST':
        for change_id in request.POST.getlist('apply_change'):
            m = _CHANGE_ID_RE.match(change_id)
            model = _MODELS[m.group('model')]
            change = model.objects.get(id=int(m.group('id')))
            change.apply_change()
        return redirect(reverse(admin_update))
    else:
        changes = []

        for c in models.InstitutionChange.objects.all().order_by(
            'institution__name'):
            change = {'id': 'institution_{}'.format(c.id),
                      'action': 'modify',
                      'institution': c.institution.name,
                      'kind': '',
                      'name_old': '',
                      'name_changed': False}
            for field in ['email', 'phone', 'other_info', 'address']:
                change[field] = getattr(c, field)
                change[field + '_changed'] = \
                    getattr(c, field + '_changed')()
                if change[field + '_changed']:
                    change[field + '_old'] = \
                        getattr(c.institution, field)

            changes.append(change)

        for c in models.RepresentativeChange.objects.all().order_by(
            'institution__name', 'kind__name'):
            change = {'id': 'representative_{}'.format(c.id),
                      'institution': c.institution.name,
                      'kind': c.kind.name,
                      'address_old': '',
                      'address_changed': False}
            if c.delete_rep:
                change['action'] = 'delete'
            elif c.rep:
                change['action'] = 'modify'
            else:
                change['action'] = 'add'

            for field in ['name', 'email', 'phone', 'other_info']:
                change[field] = getattr(c, field)
                change[field + '_changed'] = \
                    getattr(c, field + '_changed')()
                change[field + '_old'] = \
                    getattr(c.rep, field)

            changes.append(change)

        changes.sort(key=lambda c: [c['institution'], c['kind']])

        return render(request, 'views/admin_update.html', {
            'changes': changes,
        })
