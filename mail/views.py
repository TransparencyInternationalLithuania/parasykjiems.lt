from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from django.http import Http404
from django.views.decorators.cache import cache_control
from django.views.decorators.http import last_modified

from forms import WriteLetterForm
from parasykjiems.search.models import Representative, Institution
from parasykjiems.search.utils import ChoiceState
from parasykjiems.mail.models import Enquiry, Response
import parasykjiems.mail.mail as mail
from parasykjiems.mail import utils


def write_representative(request, slug):
    rep = get_object_or_404(Representative, slug=slug)
    return write(request, rep)


def write_institution(request, slug):
    inst = get_object_or_404(Institution, slug=slug)
    return write(request, inst)


@cache_control(public=False)
def write(request, recipient):
    if request.method == 'POST':
        form = WriteLetterForm(request.POST)
        choice_state = ChoiceState(form['choice_state'].value())
        if form.is_valid():
            mail.submit_enquiry(
                sender_name=form.cleaned_data['name'],
                sender_email=form.cleaned_data['email'],
                recipient=recipient,
                subject=form.cleaned_data['subject'],
                body=form.cleaned_data['body'],
                is_open=form.cleaned_data['is_open'])

            return redirect(reverse(write_confirm) +
                            '?' + choice_state.query_string())
    else:
        choice_state = ChoiceState(request.GET)
        choice_state.add_recipient(recipient)
        form = WriteLetterForm(
            initial={
                'choice_state': choice_state.query_string(),
                'body': utils.letter_body_template(recipient),
            }
        )

    return render(request, 'views/write.html', {
        'recipient': recipient,
        'choose_url': choice_state.choose_url(),
        'form': form,
    })


@cache_control(max_age=60 * 60, public=True)
def write_confirm(request):
    choice_state = ChoiceState(request.GET)
    return render(request, 'views/write_confirm.html', {
        'choose_url': choice_state.choose_url(),
        'write_url': choice_state.write_url(),
    })


@cache_control(public=False)
def confirm(request, id, confirm_hash):
    enquiry = get_object_or_404(Enquiry,
                                id=int(id),
                                confirm_hash=int(confirm_hash),
                                is_sent=False)

    if request.method == 'POST':
        mail.confirm_enquiry(enquiry)
        mail.send_enquiry(enquiry)
        return redirect(reverse(sent, kwargs={'id': enquiry.id}))
    else:
        return render(request, 'views/confirm.html', {
            'enquiry': enquiry,
        })


@cache_control(max_age=60 * 60, public=True)
def sent(request, id):
    enquiry = get_object_or_404(Enquiry, id=id)
    return render(request, 'views/sent.html', {'enquiry': enquiry})


@cache_control(max_age=60 * 60, public=True)
def thread(request, slug):
    enquiry = get_object_or_404(Enquiry,
                                slug=slug,
                                is_sent=True,
                                is_open=True)
    if not enquiry.is_open or not enquiry.is_sent:
        raise Http404()

    responses = Response.objects.filter(parent=enquiry)

    letters = [enquiry] + list(responses)

    return render(request, 'views/thread.html', {
        'page': request.GET.get('p', ''),
        'title': enquiry.subject,
        'letters': letters,
    })


def _latest_letter(request, inst=None):
    return (Enquiry.objects
            .filter(is_open=True, is_sent=True)
            .latest('sent_at')
            .sent_at)


@last_modified(_latest_letter)
@cache_control(max_age=60 * 60 * 24, public=True)
def threads(request, institution_slug=None):
    MAX_THREADS = 10
    if institution_slug:
        institution = get_object_or_404(Institution, slug=institution_slug)
        all_threads = institution.threads
    else:
        all_threads = (Enquiry.objects
                       .filter(is_open=True, is_sent=True)
                       .order_by('-sent_at'))
    pages = Paginator(all_threads, MAX_THREADS)
    try:
        page_num = int(request.GET.get('p', '1'))
    except ValueError:
        page_num = 1
    if page_num < 1:
        page_num = 1
    if page_num > pages.num_pages:
        page_num = pages.num_pages
    page = pages.page(page_num)
    threads = page.object_list

    return render(request, 'views/threads.html', {
        'page': page,
        'threads': threads,
    })
