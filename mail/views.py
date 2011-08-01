from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse

from forms import WriteLetterForm
from parasykjiems.search.models import Representative, Institution
from parasykjiems.mail.models import Enquiry
import parasykjiems.mail.mail as mail


def write_representative(request, id):
    rep = get_object_or_404(Representative, id=id)
    return write(request, rep)


def write_institution(request, id):
    inst = get_object_or_404(Institution, id=id)
    return write(request, inst)


def write(request, recipient):
    if request.method == 'POST':
        form = WriteLetterForm(request.POST)
        if form.is_valid():
            mail.submit_enquiry(
                sender_name=form.cleaned_data['name'],
                sender_email=form.cleaned_data['email'],
                recipient=recipient,
                subject=form.cleaned_data['subject'],
                body=form.cleaned_data['body'],
                is_open=form.cleaned_data['is_open'])

            return redirect(reverse(write_confirm))
    else:
        form = WriteLetterForm()

    return render(request, 'write.html', {
        'recipient': recipient,
        'form': form,
    })


def write_confirm(request):
    return render(request, 'write-confirm.html')


def confirm(request, unique_hash):
    enquiry = get_object_or_404(Enquiry, unique_hash=unique_hash)
    return render(request, 'confirm.html', {
        'enquiry': enquiry,
    })
