# -*- coding: utf-8 -*-
from celery import shared_task, group

from osmcha.changeset import Analyse, ChangesetList

from os.path import join

import requests

import re

from django.conf import settings

from .models import Changeset, SuspicionReasons, Import


@shared_task
def create_changeset(changeset_id):
    """Analyse and create the changeset in the database."""
    ch = Analyse(changeset_id)
    ch.full_analysis()

    # remove suspicion_reasons and empty values from dict
    ch_dict = ch.__dict__.copy()
    for key in ch.__dict__:
        if ch.__dict__.get(key) == '':
            ch_dict.pop(key)
    ch_dict.pop('suspicion_reasons')

    #save changeset
    changeset = Changeset(**ch_dict)
    changeset.save()

    if ch.suspicion_reasons:
        for reason in ch.suspicion_reasons:
            reason, created = SuspicionReasons.objects.get_or_create(name=reason)
            reason.changesets.add(changeset)

    print('{c[id]} created'.format(c=ch_dict))


@shared_task
def get_filter_changeset_file(url, geojson_filter=settings.CHANGESETS_FILTER):
    """Filter the changesets of the replication file by the area defined in the
    GeoJSON file.
    """
    cl = ChangesetList(url, geojson_filter)
    group(create_changeset.s(c) for c in cl.changesets)()


def format_url(n):
    """Return the url of a replication file."""
    n = str(n)
    base_url = 'http://planet.openstreetmap.org/replication/changesets/'
    return join(base_url, '00%s' % n[0], n[1:4], '%s.osm.gz' % n[4:])


@shared_task
def import_replications(start, end):
    """Recieves a start and a end number and import each replication file in
    this interval.
    """
    Import(start=start, end=end).save()
    urls = [format_url(n) for n in range(start, end + 1)]
    group(get_filter_changeset_file.s(url) for url in urls)()


@shared_task
def fetch_latest():
    try:
        last_import = Import.objects.all().order_by('-end')[0].end
    except:
        last_import = None
    state = requests.get('http://planet.openstreetmap.org/replication/changesets/state.yaml').content
    print 'got state'
    regex = re.compile(r'sequence: (.*)')
    sequence = int(regex.findall(state)[0])
    if last_import:
        start = last_import + 1
    else:
        start = sequence - 1000
    print "calling import_replication %d %d" % (start, sequence,)
    import_replications(start, sequence)
