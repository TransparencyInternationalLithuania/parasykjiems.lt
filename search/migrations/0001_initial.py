# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'InstitutionKind'
        db.create_table('search_institutionkind', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('search', ['InstitutionKind'])

        # Adding model 'Institution'
        db.create_table('search_institution', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('kind', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['search.InstitutionKind'])),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('address', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('search', ['Institution'])

        # Adding model 'RepresentativeKind'
        db.create_table('search_representativekind', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('search', ['RepresentativeKind'])

        # Adding model 'Representative'
        db.create_table('search_representative', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('kind', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['search.RepresentativeKind'])),
            ('institution', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['search.Institution'])),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('other_contacts', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('search', ['Representative'])

        # Adding model 'Location'
        db.create_table('search_location', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('municipality', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('elderate', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=200, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('street', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=200, blank=True)),
        ))
        db.send_create_signal('search', ['Location'])

        # Adding model 'Territory'
        db.create_table('search_territory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('municipality', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('elderate', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=200, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('street', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=200, blank=True)),
            ('institution', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['search.Institution'])),
            ('numbers', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('search', ['Territory'])


    def backwards(self, orm):
        
        # Deleting model 'InstitutionKind'
        db.delete_table('search_institutionkind')

        # Deleting model 'Institution'
        db.delete_table('search_institution')

        # Deleting model 'RepresentativeKind'
        db.delete_table('search_representativekind')

        # Deleting model 'Representative'
        db.delete_table('search_representative')

        # Deleting model 'Location'
        db.delete_table('search_location')

        # Deleting model 'Territory'
        db.delete_table('search_territory')


    models = {
        'search.institution': {
            'Meta': {'object_name': 'Institution'},
            'address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['search.InstitutionKind']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        'search.institutionkind': {
            'Meta': {'object_name': 'InstitutionKind'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'search.location': {
            'Meta': {'object_name': 'Location'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'elderate': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'municipality': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'})
        },
        'search.representative': {
            'Meta': {'object_name': 'Representative'},
            'email': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['search.Institution']"}),
            'kind': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['search.RepresentativeKind']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'other_contacts': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        'search.representativekind': {
            'Meta': {'object_name': 'RepresentativeKind'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'search.territory': {
            'Meta': {'object_name': 'Territory'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'elderate': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['search.Institution']"}),
            'municipality': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'numbers': ('django.db.models.fields.TextField', [], {}),
            'street': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'})
        }
    }

    complete_apps = ['search']
