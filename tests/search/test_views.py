from search.models import (
    Institution, InstitutionKind, Representative, RepresentativeKind
)


def test_institution(app):
    ministerija = Institution.objects.create(
        name='Ministerija',
        kind=InstitutionKind.objects.create(name='ministerija', ordinal=1),
        slug='ministerija',
    )

    representative = Representative.objects.create(
        name='Vardas Pavardenis',
        kind=RepresentativeKind.objects.create(name='ministras', ordinal=1),
        institution=ministerija,
        email='vardas.pavardenis@example.com',
        slug='',
    )

    resp = app.get('/institution/%s/' % ministerija.slug)
    assert resp.status_code == 200
    assert ministerija.name in resp.content
    assert representative.name in resp.content
