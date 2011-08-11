from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from django.http import Http404

from forms import WriteLetterForm
from parasykjiems.search.models import Representative, Institution
from parasykjiems.mail.models import Enquiry, Response
import parasykjiems.mail.mail as mail


def write_representative(request, slug):
    rep = get_object_or_404(Representative, slug=slug)
    return write(request, rep)


def write_institution(request, slug):
    inst = get_object_or_404(Institution, slug=slug)
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

    request.session['breadcrumb_write'] = request.get_full_path()
    return render(request, 'views/write.html', {
        'recipient': recipient,
        'form': form,
    })


def write_confirm(request):
    return render(request, 'views/write_confirm.html')


def confirm(request, confirm_hash):
    enquiry = get_object_or_404(Enquiry, confirm_hash=confirm_hash)
    if enquiry.is_sent:
        raise Http404()

    if request.method == 'POST':
        mail.confirm_enquiry(enquiry)
        return redirect(reverse(sent, kwargs={'slug': enquiry.slug}))
    else:
        return render(request, 'views/confirm.html', {
            'enquiry': enquiry,
        })


def sent(request, slug):
    enquiry = get_object_or_404(Enquiry, slug=slug)
    return render(request, 'views/sent.html', {'enquiry': enquiry})


def letter(request, slug):
    enquiry = get_object_or_404(Enquiry, slug=slug)
    if not enquiry.is_open or not enquiry.is_sent:
        raise Http404()

    responses = Response.objects.filter(parent=enquiry)

    request.session['breadcrumb_letter'] = request.get_full_path()
    return render(request, 'views/letter.html', {
        'enquiry': enquiry,
        'responses': responses,
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

    request.session['breadcrumb_search'] = None
    request.session['breadcrumb_letters'] = request.get_full_path()
    return render(request, 'views/letters.html', {
        'page': page,
        'letters': letters,
    })
