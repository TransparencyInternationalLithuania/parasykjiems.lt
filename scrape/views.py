from django.shortcuts import render
import models
from django.contrib.auth.decorators import login_required


@login_required(login_url='/admin/', redirect_field_name=None)
def admin_update(request):
    changes = models.RepresentativeChange.objects.all()
    return render(request, 'views/admin_update.html', {
        'changes': changes,
    })
