from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.cache import cache_control
from django.views.decorators.http import last_modified
from django.db.models import Q
import datetime
import re

from forms import WriteLetterForm
from parasykjiems.search.models import Representative, Institution
from parasykjiems.search.utils import ChoiceState
from parasykjiems.mail.models import Thread, UnconfirmedMessage
import parasykjiems.mail.mail as mail
from parasykjiems.mail import utils


import logging
logger = logging.getLogger(__name__)


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
            mail.submit_message(
                sender_name=form.cleaned_data['name'],
                sender_email=form.cleaned_data['email'],
                recipient=recipient,
                subject=form.cleaned_data['subject'],
                body_text=form.cleaned_data['body'],
                is_public=(form.cleaned_data['kind'] == 'public'))

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


def write_confirm(request):
    choice_state = ChoiceState(request.GET)
    return render(request, 'views/write_confirm.html', {
        'choose_url': choice_state.choose_url(),
        'write_url': choice_state.write_url(),
    })


@cache_control(public=False)
def confirm(request, id, confirm_secret):
    unc_message = get_object_or_404(UnconfirmedMessage,
                                    id=int(id),
                                    confirm_secret=int(confirm_secret))

    if request.method == 'POST':
        thread = mail.confirm_and_send(unc_message)
        if thread.is_public:
            return redirect(reverse(sent, kwargs={'slug': thread.slug}))
        else:
            return redirect(reverse(sent))
    else:
        return render(request, 'views/confirm.html', {
            'message': unc_message,
        })


def sent(request, slug=None):
    if slug:
        thread = get_object_or_404(Thread, slug=slug, is_public=True)
    else:
        thread = None
    return render(request, 'views/sent.html', {'thread': thread})


MAX_THREADS = 40


def thread(request, slug):
    thread = get_object_or_404(Thread, slug=slug, is_public=True)
    all_threads = (Thread.objects
                   .filter(is_public=True)
                   .order_by('-created_at'))
    position = list(all_threads).index(thread)
    page_number = (position // MAX_THREADS) + 1

    return render(request, 'views/thread.html', {
        'thread': thread,
        'page_number': page_number,
    })


def _latest_thread(request, institution_slug=None):
    try:
        return (Thread.objects
                .filter(is_public=True)
                .latest('modified_at')
                .modified_at)
    except ObjectDoesNotExist:
        return datetime.datetime.now()


_SPACES = re.compile(r'\s+')
_FILTER_FIELDS = ['subject', 'sender_name', 'recipient_name']


@last_modified(_latest_thread)
def threads(request):
    threads = (Thread.objects
                   .filter(is_public=True)
                   .order_by('-created_at'))

    if 'q' in request.GET and request.GET['q'].strip() != '':
        words = _SPACES.split(request.GET['q'])

        # Build filter query. Words can be in any order.
        qi = Q()
        qe = Q()
        for field in _FILTER_FIELDS:
            f = field + '__icontains'
            incq = Q()
            exq = Q()
            for w in words:
                # Exclude words that start with a dash.
                if w.startswith('-'):
                    exq |= Q(**{f: w[1:]})
                else:
                    incq &= Q(**{f: w})
            qi |= incq
            qe |= exq
        threads = threads.filter(qi & ~qe)

    pages = Paginator(threads, MAX_THREADS)
    try:
        page_num = int(request.GET.get('p', '1'))
    except ValueError:
        page_num = 1
    if page_num < 1:
        page_num = 1
    if page_num > pages.num_pages:
        page_num = pages.num_pages
    page = pages.page(page_num)
    paginated_threads = page.object_list

    return render(request, 'views/threads.html', {
        'page': page,
        'pages': [pages.page(p) for p in pages.page_range],
        'threads': paginated_threads,
    })


def threads_institution(request, institution_slug):
    institution = get_object_or_404(Institution, slug=institution_slug)
    return redirect(institution.threads_url())
