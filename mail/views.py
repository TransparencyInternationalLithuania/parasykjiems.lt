from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from django.http import Http404

from forms import WriteLetterForm
from parasykjiems.search.models import Representative, Institution, Location
from parasykjiems.mail.models import Enquiry, Response
import parasykjiems.mail.mail as mail


def write_representative(request, slug):
    rep = get_object_or_404(Representative, slug=slug)
    return write(request, rep)


def write_institution(request, slug):
    inst = get_object_or_404(Institution, slug=slug)
    return write(request, inst)


def write(request, recipient):
    choose_url = ''
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
        if 'inst' in request.GET:
            choose_url = Institution.objects.get(
                id=int(request.GET['inst'])).get_absolute_url()
        elif 'loc' in request.GET:
            choose_url = Location.objects.get(
                id=int(request.GET['loc'])).get_absolute_url()
            if 'n' in request.GET:
                choose_url += request.GET['n'] + '/'
        else:
            choose_url = recipient.get_absolute_url()

        form = WriteLetterForm()

    return render(request, 'views/write.html', {
        'recipient': recipient,
        'choose_url': choose_url,
        'form': form,
    })


def write_confirm(request):
    return render(request, 'views/write_confirm.html')


def confirm(request, id, confirm_hash):
    enquiry = get_object_or_404(Enquiry,
                                id=int(id),
                                confirm_hash=int(confirm_hash),
                                is_sent=False)

    mail.confirm_enquiry(enquiry)

    if request.method == 'POST':
        mail.send_enquiry(enquiry)
        return redirect(reverse(sent, kwargs={'id': enquiry.id}))
    else:
        return render(request, 'views/confirm.html', {
            'enquiry': enquiry,
        })


def sent(request, id):
    enquiry = get_object_or_404(Enquiry, id=id)
    return render(request, 'views/sent.html', {'enquiry': enquiry})


def thread(request, slug):
    enquiry = get_object_or_404(Enquiry, slug=slug)
    if not enquiry.is_open or not enquiry.is_sent:
        raise Http404()

    responses = Response.objects.filter(parent=enquiry)

    letters = [enquiry] + list(responses)

    return render(request, 'views/thread.html', {
        'page': request.GET.get('p', ''),
        'letters': letters,
    })


def letters(request):
    MAX_LETTERS = 5
    all_letters = (Enquiry.objects
                   .filter(is_open=True, is_sent=True)
                   .order_by('-sent_at'))
    pages = Paginator(all_letters, MAX_LETTERS)
    try:
        page_num = int(request.GET.get('p', '1'))
    except ValueError:
        page_num = 1
    if page_num < 1:
        page_num = 1
    if page_num > pages.num_pages:
        page_num = pages.num_pages
    page = pages.page(page_num)
    letters = page.object_list

    return render(request, 'views/letters.html', {
        'page': page,
        'letters': letters,
    })
