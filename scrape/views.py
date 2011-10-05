import re
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
import models


_CHANGE_PARAM_RE = re.compile(r'change_(\d)')


@login_required(login_url='/admin/', redirect_field_name=None)
def admin_update(request):
    if request.method == 'POST':
        for change_id in request.POST.getlist('apply_change'):
            print change_id
            change = models.RepresentativeChange.objects.get(
                id=int(change_id))
            change.apply_change()
        return redirect(reverse(admin_update))
    else:
        changes = models.RepresentativeChange.objects.all().order_by(
            'institution', 'kind_name')
        return render(request, 'views/admin_update.html', {
            'changes': changes,
        })
